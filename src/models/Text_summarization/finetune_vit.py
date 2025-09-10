#Configurations and Hyperparameters
OUTPUT_DIR = '/data/vit5_finetuned/'
batch_size = 2
learning_rate = 5e-5
num_train_epochs = 3
weight_decay = 0.01
logging_steps = 500
save_steps = 500    
eval_steps = 500
warmup_steps = 500

MODEL_NAME = "VietAI/vit5-large-vietnews-summarization"
DATA_PATH = "data/processed_data/processed_data.json"  
TEXT_FIELD = "input"               
TARGET_FIELD = "target"            

PREFIX = "vietnews: "             
MAX_SOURCE_LEN = 512
MAX_TARGET_LEN = 128
SEED = 42
encoder_max_length = MAX_SOURCE_LEN
decoder_max_length = MAX_TARGET_LEN


# Import Libraries
import os
from dataclasses import dataclass
from typing import Dict, List, Optional
import evaluate
import numpy as np
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
)
from datasets import load_dataset
import re
import numpy as np

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("VietAI/vit5-large-vietnews-summarization")  
model = AutoModelForSeq2SeqLM.from_pretrained("VietAI/vit5-large-vietnews-summarization")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# from collections import Counter
# import random

# def preview_examples(ds, name, n=3, text_key=TEXT_FIELD, target_key=TARGET_FIELD, max_chars=200):
#     print(f"\n=== {name} (size={len(ds)}) ===")
#     for i in random.sample(range(len(ds)), k=min(n, len(ds))):
#         ex = ds[i]
#         x = str(ex.get(text_key, ""))[:max_chars].replace("\n", " ")
#         y = str(ex.get(target_key, ""))[:max_chars].replace("\n", " ")
#         print(f"\n-- idx {i} --")
#         print(f"INPUT  ({len(ex.get(text_key,''))} chars): {x}{'…' if len(ex.get(text_key,''))>max_chars else ''}")
#         print(f"TARGET ({len(ex.get(target_key,''))} chars): {y}{'…' if len(ex.get(target_key,''))>max_chars else ''}")

# def split_stats(ds, text_key=TEXT_FIELD, target_key=TARGET_FIELD):
#     n = len(ds)
#     empty_x = sum(1 for ex in ds if not str(ex.get(text_key, "")).strip())
#     empty_y = sum(1 for ex in ds if not str(ex.get(target_key, "")).strip())
#     len_x = [len(str(ex.get(text_key, ""))) for ex in ds]
#     len_y = [len(str(ex.get(target_key, ""))) for ex in ds]

#     def _pct(x): return f"{100.0*x/n:.2f}%" if n else "0%"
#     stats = {
#         "num_samples": n,
#         "empty_inputs": f"{empty_x} ({_pct(empty_x)})",
#         "empty_targets": f"{empty_y} ({_pct(empty_y)})",
#         "input_len_avg": sum(len_x)/n if n else 0,
#         "input_len_min": min(len_x) if n else 0,
#         "input_len_max": max(len_x) if n else 0,
#         "target_len_avg": sum(len_y)/n if n else 0,
#         "target_len_min": min(len_y) if n else 0,
#         "target_len_max": max(len_y) if n else 0,
#     }
#     return stats

# def print_stats(name, ds):
#     s = split_stats(ds)
#     print(f"\n--- Stats: {name} ---")
#     for k,v in s.items():
#         print(f"{k:>16}: {v}")


# Data Preparation
dataset = load_dataset("json", data_files=DATA_PATH)  

def _clean_text(s):
    if s is None: return ""
    s = str(s).replace("\u00a0", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n\n", s.strip())
    return s

def build_input_target(example):
    content = _clean_text(example.get("content", ""))
    desc    = _clean_text(example.get("description", "")) 

    # input = prefix + title + content
    inp = f"{content}".strip()
    return { "input": inp, "target": desc }

# Tạo cột input/target
dataset = dataset.map(build_input_target)

# Lọc bỏ các mẫu thiếu target rỗng
def has_target(example):
    return bool(example.get("target", "").strip())

dataset = dataset.filter(has_target)

# Split dataset
full = dataset["train"]
splits = full.train_test_split(test_size=0.2, seed=SEED)
train_dataset = splits["train"]
tmp = splits["test"].train_test_split(test_size=0.5, seed=SEED)
val_dataset = tmp["train"]
test_dataset = tmp["test"]

# print(f"Train size: {len(train_dataset)}")
# print(f"Validation size: {len(val_dataset)}")
# print(f"Test size: {len(test_dataset)}")

# Preview a few raw examples
# preview_examples(train_dataset, "TRAIN", n=3)
# preview_examples(val_dataset,   "VAL",   n=3)
# preview_examples(test_dataset,  "TEST",  n=3)


# Format data for model
def process_data_to_model_inputs(batch):
    sources = batch[TEXT_FIELD]
    targets = batch[TARGET_FIELD]

    inputs = tokenizer(
        sources,
        padding="max_length",
        truncation=True,
        max_length=encoder_max_length,
    )
    outputs = tokenizer(
        targets,
        padding="max_length",
        truncation=True,
        max_length=decoder_max_length,
    )

    batch["input_ids"] = inputs["input_ids"]
    batch["attention_mask"] = inputs["attention_mask"]
    batch["decoder_input_ids"] = outputs["input_ids"]

    # labels với pad=-100 để mask loss
    pad_id = tokenizer.pad_token_id
    labels = []
    for seq in outputs["input_ids"]:
        labels.append([-100 if t == pad_id else t for t in seq])
    batch["labels"] = labels

    batch["decoder_attention_mask"] = outputs["attention_mask"]
    return batch
# only use 32 training examples for notebook - DELETE LINE FOR FULL TRAINING
# train_data = train_dataset.select(range(200))

train_data_batch = train_dataset.map(
    process_data_to_model_inputs, 
    batched=True, 
    batch_size=batch_size, 

    remove_columns=train_dataset.column_names,
)

train_data_batch.set_format(
    type="torch", columns=["input_ids", "attention_mask", "decoder_input_ids", "decoder_attention_mask", "labels"],
)

val_data_batch = val_dataset.map(
    process_data_to_model_inputs, 
    batched=True, 
    batch_size=batch_size, 
    remove_columns=val_dataset.column_names,
)
val_data_batch.set_format(
    type="torch", columns=["input_ids", "attention_mask", "decoder_input_ids", "decoder_attention_mask", "labels"],
)


# Data Collator
data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model
)


# Compute Metrics
# load rouge for validation
rouge = evaluate.load("rouge")

def _to_int_ids(arr):
    if isinstance(arr, tuple): arr = arr[0]
    if isinstance(arr, np.ndarray): arr = arr.tolist()
    cleaned = []
    for seq in arr:
        cleaned.append([int(t) for t in seq])
    return cleaned

def token_accuracy(pred_ids, label_ids, pad_id=-100):
    correct, total = 0, 0
    for p, l in zip(pred_ids, label_ids):
        for pp, ll in zip(p, l):
            if ll == pad_id: 
                continue
            total += 1
            if pp == ll:
                correct += 1
    return correct / total if total > 0 else 0.0

def _ensure_2d(arr):
    import numpy as _np
    if isinstance(arr, tuple):
        arr = arr[0]
    if hasattr(arr, "cpu"): 
        arr = arr.cpu().numpy()
    arr = _np.asarray(arr, dtype=object)

    if arr.ndim == 3:
        arr = arr[:, 0, :]
  
    return arr.tolist()

def sanitize_token_ids(arr, *, pad_id: int, vocab_size: int, replace_neg_with_pad: bool):
    """
    Returns: list[list[int]] with ids in [0, vocab_size-1]
    - replace_neg_with_pad=True: negatives (e.g. -100) -> pad_id
    - floats -> round()
    - >vocab_size-1 -> pad_id (hoặc bạn có thể clip)
    """
    cleaned = []
    for seq in arr:
        row = []
        for tok in seq:
            try:
                t = int(round(float(tok)))
            except Exception:
                t = pad_id

            if replace_neg_with_pad and t < 0:
                t = pad_id
            if t >= vocab_size:
                t = pad_id
            if t < 0:
                t = pad_id

            row.append(t)
        cleaned.append(row)
    return cleaned

def compute_metrics(eval_preds):
    preds_raw, labels_raw = eval_preds

    pad_id = tokenizer.pad_token_id if tokenizer.pad_token_id is not None else 0
    vocab_size = getattr(tokenizer, "vocab_size", None)
    if vocab_size is None:
        vocab_size = 32128

    pred_ids  = _ensure_2d(preds_raw)
    label_ids = _ensure_2d(labels_raw)

    pred_ids  = sanitize_token_ids(pred_ids,  pad_id=pad_id, vocab_size=vocab_size, replace_neg_with_pad=False)
    label_ids = sanitize_token_ids(label_ids, pad_id=pad_id, vocab_size=vocab_size, replace_neg_with_pad=True)

    preds_txt = tokenizer.batch_decode(pred_ids,  skip_special_tokens=True)
    refs_txt  = tokenizer.batch_decode(label_ids, skip_special_tokens=True)

    # ROUGE-2 (F1)
    out = rouge.compute(predictions=preds_txt, references=refs_txt, rouge_types=["rouge2"])
    r2 = out["rouge2"]
    if isinstance(r2, (float, np.floating)):
        r2_f1 = float(r2)
    elif isinstance(r2, dict) and "fmeasure" in r2:
        r2_f1 = float(r2["fmeasure"])
    else:
        r2_f1 = float(np.mean(out["rouge2"])) if isinstance(out["rouge2"], list) else 0.0

    correct, total = 0, 0
    for p, l in zip(pred_ids, label_ids):
        for pp, ll in zip(p, l):
            if ll == pad_id: 
                continue
            total += 1
            if pp == ll:
                correct += 1
    acc = correct / total if total > 0 else 0.0

    return {
        "rouge2_f1": round(r2_f1, 4),
        "val_acc": round(acc, 4),  
    }


# # Training
# training_args = Seq2SeqTrainingArguments(
#     output_dir=OUTPUT_DIR,
#     overwrite_output_dir=True,
#     eval_strategy="epoch",   # "no" | "steps" | "epoch"
#     save_strategy="epoch",
#     logging_strategy="epoch",
#     # eval_steps=eval_steps,
#     # logging_steps=logging_steps,
#     # save_steps=save_steps,
#     save_total_limit=3,
#     num_train_epochs=num_train_epochs,
#     per_device_train_batch_size=batch_size,   
#     per_device_eval_batch_size=batch_size,
#     gradient_accumulation_steps=8,   
#     learning_rate=learning_rate,
#     weight_decay=weight_decay,
#     warmup_ratio=0.1,
#     lr_scheduler_type="linear",
#     predict_with_generate=True,
#     generation_max_length=MAX_TARGET_LEN,
#     fp16=torch.cuda.is_available(),
#     report_to=[]  # set to ["wandb"] if you use Weights & Biases
# )

# # -----------------------
# # Trainer
# # -----------------------
# trainer = Seq2SeqTrainer(
#     model=model,
#     args=training_args,
#     train_dataset=train_data_batch,
#     eval_dataset=val_data_batch,
#     tokenizer=tokenizer,
#     data_collator=data_collator,
#     compute_metrics=compute_metrics
# )
# trainer.train()


training_args = Seq2SeqTrainingArguments(

    # Core parameters
    output_dir= OUTPUT_DIR,
    per_device_train_batch_size=batch_size,
    per_device_eval_batch_size=batch_size,
    predict_with_generate=True,
    # evaluate_during_training=True,
    do_train=True,
    eval_strategy="epoch",      
    save_strategy="epoch",     
    eval_on_start=True,         
    do_eval=True,   
    learning_rate=learning_rate,
    generation_max_length=MAX_TARGET_LEN,   

    # Regularzation & Optimization
    gradient_accumulation_steps=8,
    lr_scheduler_type="linear",
    # warmup_ratio=0.1,
    # warmup_steps=warmup_steps,
    weight_decay=weight_decay,

    # Logging & saving
    logging_strategy="steps",
    logging_steps=logging_steps,

    save_total_limit=5,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
    greater_is_better=False,

    warmup_steps=3000,  
    num_train_epochs=num_train_epochs, 
    overwrite_output_dir=True,
    fp16=True, 

    # eval_strategy="steps",        # "no" | "steps" | "epoch"
    # eval_steps=eval_steps,
    # logging_strategy="steps",
    # logging_steps=logging_steps,
    # save_strategy="steps",
    # save_steps=save_steps,
    
)

# instantiate trainer
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    compute_metrics=compute_metrics,
    train_dataset=train_data_batch,
    eval_dataset=val_data_batch,
)
trainer.train()


# Save the model
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR) 
from transformers import GenerationConfig
model.generation_config.save_pretrained(OUTPUT_DIR)

# Evaluate on the test set
test_data_batch = test_dataset.map(
    process_data_to_model_inputs,
    batched=True, batch_size=batch_size,
    remove_columns=test_dataset.column_names,
)
test_data_batch.set_format(
    type="torch",
    columns=["input_ids", "attention_mask", "decoder_input_ids", "decoder_attention_mask", "labels"],
)

test_metrics = trainer.evaluate(eval_dataset=test_data_batch, max_length=MAX_TARGET_LEN, num_beams=1)
print("\n[TEST METRICS]")
print(test_metrics)

# Example inference
def generate_summary(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=encoder_max_length).to(device)
    outputs = model.generate(
        input_ids=inputs["input_ids"], 
        attention_mask=inputs["attention_mask"], 
        max_length=decoder_max_length, 
        num_beams=4, 
        early_stopping=True
    )
    summary = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return summary

text = "Hôm nay, trời đẹp và nắng ấm. Chúng ta sẽ đi dạo trong công viên và tận hưởng không khí trong lành."
summary = generate_summary(text)
print("Summary:", summary)