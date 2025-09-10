#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import sys
from typing import Optional

import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
)

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                         "vit5_finetuned"))

DEVICE = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")

try:
    tokenizer = AutoTokenizer.from_pretrained(OUTPUT_DIR, use_fast=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(OUTPUT_DIR).to(DEVICE)
    model.eval()
except Exception as e:
    print(f"[startup] Failed to load model/tokenizer from {OUTPUT_DIR}: {e}", file=sys.stderr)
    raise

@torch.inference_mode()
def summarize_one(
    text: str,
    in_max_len: int = 512,
    out_max_len: int = 128,
    num_beams: int = 4,
    no_repeat_ngram_size: int = 3,
    do_sample: bool = False,
    temperature: float = 1.0,
) -> str:
    """
    Tóm tắt 1 văn bản, trả về chuỗi summary.
    """
    if text is None:
        text = ""
    enc = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding="max_length",
        max_length=in_max_len,
    ).to(DEVICE)

    gen_ids = model.generate(
        input_ids=enc["input_ids"],
        attention_mask=enc.get("attention_mask", None),
        max_length=out_max_len,
        num_beams=num_beams,
        no_repeat_ngram_size=no_repeat_ngram_size,
        early_stopping=True,
        do_sample=do_sample,
        temperature=temperature,
    )
    summary = tokenizer.decode(gen_ids[0], skip_special_tokens=True)
    return summary

def main():
    ap = argparse.ArgumentParser(description="Summarization inference (JSON I/O).")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", type=str, help="Đoạn văn cần tóm tắt")
    g.add_argument("--interactive", action="store_true", help="Nhập nhiều dòng (Ctrl+C để thoát)")
    ap.add_argument("--in_max_len", type=int, default=512, help="Độ dài tối đa đầu vào (tokenized)")
    ap.add_argument("--out_max_len", type=int, default=128, help="Độ dài tối đa đầu ra (tokenized)")
    ap.add_argument("--beams", type=int, default=4, help="num_beams cho beam search")
    ap.add_argument("--nrng", type=int, default=3, help="no_repeat_ngram_size")
    ap.add_argument("--sample", action="store_true", help="Bật sampling (mặc định tắt)")
    ap.add_argument("--temp", type=float, default=1.0, help="temperature khi sampling")

    args = ap.parse_args()

    if args.text:
        s = summarize_one(
            args.text,
            in_max_len=args.in_max_len,
            out_max_len=args.out_max_len,
            num_beams=args.beams,
            no_repeat_ngram_size=args.nrng,
            do_sample=args.sample,
            temperature=args.temp,
        )
        print(json.dumps({"text": args.text, "summary": s}, ensure_ascii=False, indent=2))
        return

    print(">> Interactive mode (Ctrl+C để thoát).")
    try:
        while True:
            line = input("\nNhập văn bản: ").strip()
            if not line:
                continue
            s = summarize_one(
                line,
                in_max_len=args.in_max_len,
                out_max_len=args.out_max_len,
                num_beams=args.beams,
                no_repeat_ngram_size=args.nrng,
                do_sample=args.sample,
                temperature=args.temp,
            )
            print(json.dumps({"text": line, "summary": s}, ensure_ascii=False, indent=2))
    except (KeyboardInterrupt, EOFError):
        print("\n[exit] Bye!")

if __name__ == "__main__":
    main()
