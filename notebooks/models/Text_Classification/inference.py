#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Inference cho Text Classification.
Tự động:
- load model: stacking_model.joblib (hoặc .pkl nếu bạn đổi tên)
- load label_encoder.pkl (nếu có) để map id -> label
- (tuỳ chọn) load tfidf_vectorizer.pkl nếu model không phải Pipeline end-to-end

Cách dùng:
  python inference.py --title "Tiêu đề" --desc "Mô tả" --content "Nội dung"
  # hoặc truyền 1 chuỗi text duy nhất
  python inference.py --text "Bài báo đầy đủ ..."

Có thể đổi thư mục model:
  python inference.py --text "..." --model-dir results/models/Text_Classification
"""

from __future__ import annotations
import argparse
from pathlib import Path
import sys
import json
import numpy as np

try:
    import joblib
except Exception:
    # phòng khi bạn dùng pickle
    import pickle as joblib  # type: ignore

def load_artifacts(model_dir: str | Path):
    model_dir = Path(model_dir)
    # model
    model = None
    for name in ["stacking_model.joblib", "stacking_model.pkl", "model.joblib", "model.pkl"]:
        p = model_dir / name
        if p.exists():
            model = joblib.load(p)
            break
    if model is None:
        sys.exit(f"[ERR] Không tìm thấy file model (.joblib/.pkl) trong {model_dir}")

    # label encoder (tuỳ chọn)
    le = None
    le_path = model_dir / "label_encoder.pkl"
    if le_path.exists():
        le = joblib.load(le_path)

    # tfidf (tuỳ chọn nếu model không phải pipeline end-to-end)
    vec = None
    vec_path = model_dir / "tfidf_vectorizer.pkl"
    if vec_path.exists():
        try:
            vec = joblib.load(vec_path)
        except Exception:
            vec = None

    return model, le, vec


def compose_text(title: str = "", desc: str = "", content: str = "", text: str = "") -> str:
    if text and (title or desc or content):
        # nếu user truyền cả --text và title/desc/content -> ưu tiên text
        return text.strip()
    if text:
        return text.strip()
    parts = [title.strip(), desc.strip(), content.strip()]
    return " ".join([p for p in parts if p])


def predict_one(model, label_encoder, vectorizer, text: str):
    """
    Cố gắng dự đoán theo 2 chế độ:
    - Nếu model là Pipeline end-to-end: model.predict([text])
    - Nếu không: dùng vectorizer.transform trước rồi model.predict
    """
    x_raw = [text]

    # 1) thử predict trực tiếp (model có thể là Pipeline)
    try:
        y_pred = model.predict(x_raw)
    except Exception:
        # 2) fallback: cần vectorize
        if vectorizer is None:
            raise RuntimeError(
                "Model không phải Pipeline end-to-end và không có tfidf_vectorizer.pkl để biến đổi input."
            )
        X = vectorizer.transform(x_raw)
        y_pred = model.predict(X)

    pred = y_pred[0]

    # map id -> label nếu có label_encoder
    if label_encoder is not None:
        try:
            pred_label = label_encoder.inverse_transform([pred])[0]
        except Exception:
            # trường hợp model trả string rồi thì khỏi cần inverse
            pred_label = pred
    else:
        pred_label = pred

    # lấy xác suất nếu có
    proba = None
    try:
        # nhiều model sklearn có predict_proba
        probs = model.predict_proba(x_raw) if "X" not in locals() else model.predict_proba(X)
        proba = float(np.max(probs))
    except Exception:
        try:
            # LinearSVC… không có proba, có decision_function
            scores = model.decision_function(x_raw) if "X" not in locals() else model.decision_function(X)
            # chuẩn hoá “độ tin” đơn giản
            if scores.ndim == 1:
                proba = float(1 / (1 + np.exp(-scores[0])))
            else:
                proba = float(np.max(scores))
        except Exception:
            proba = None

    return pred_label, proba


def main():
    ap = argparse.ArgumentParser(description="Text classification inference")
    ap.add_argument("--model-dir", type=str, default="results/models/Text_Classification",
                    help="Thư mục chứa model & artifact (.joblib/.pkl)")
    ap.add_argument("--title", type=str, default="", help="Tiêu đề bài báo")
    ap.add_argument("--desc", type=str, default="", help="Mô tả/ngắn gọn")
    ap.add_argument("--content", type=str, default="", help="Nội dung bài báo")
    ap.add_argument("--text", type=str, default="", help="Truyền cả bài báo dưới dạng 1 chuỗi duy nhất")
    ap.add_argument("--json", action="store_true", help="In kết quả dạng JSON")
    args = ap.parse_args()

    model, label_encoder, vectorizer = load_artifacts(args.model_dir)
    text = compose_text(args.title, args.desc, args.content, args.text)
    if not text:
        sys.exit("[ERR] Chưa truyền nội dung. Dùng --text hoặc --title/--desc/--content.")

    label, score = predict_one(model, label_encoder, vectorizer, text)

    if args.json:
        print(json.dumps({"label": str(label), "score": score}, ensure_ascii=False))
    else:
        print("Predicted label:", label)
        if score is not None:
            print("Confidence/score:", score)


if __name__ == "__main__":
    main()
