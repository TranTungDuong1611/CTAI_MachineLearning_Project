#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import os
import sys
import json
import numpy as np
sys.path.append(os.getcwd())

from scipy.sparse import csr_matrix, hstack
# from joblib import load as joblib_load
import pandas as pd
import joblib

MODEL_DIR = "results/models/Text_Classification"


def load_artifacts(model_dir: str):
    """Load toàn bộ artifact cần thiết."""
    def p(name): return os.path.join(model_dir, name)

    tfidf_path = p("tfidf_vectorizer.pkl")
    scaler_path = p("statistical_scaler.pkl")
    statfeat_path = p("stat_features.pkl")
    le_path = p("label_encoder.pkl")

    # model có thể là .pkl hoặc .joblib
    model_path = p("stacking_model.pkl")
    if not os.path.exists(model_path):
        alt = p("stacking_model.joblib")
        if os.path.exists(alt):
            model_path = alt

    needed = [tfidf_path, scaler_path, statfeat_path, le_path, model_path]
    missing = [q for q in needed if not os.path.exists(q)]
    if missing:
        raise FileNotFoundError("Thiếu artifact: " + ", ".join(missing))

    tfidf = joblib.load(tfidf_path)
    tfidf = joblib.load(tfidf_path)
    scaler = joblib.load(scaler_path)
    stat_features = joblib.load(statfeat_path)
    label_encoder = joblib.load(le_path)
    model = joblib.load(model_path)
    if not isinstance(stat_features, (list, tuple)) or len(stat_features) == 0:
        raise ValueError("stat_features.pkl không hợp lệ.")

    return tfidf, scaler, stat_features, label_encoder, model


# ---- Trích xuất đặc trưng thống kê ----
def compute_text_stats(text: str) -> dict:
    t = text or ""
    words = t.split()
    avg_word_length = float(np.mean([len(w) for w in words])) if words else 0.0

    import re
    return {
        "text_length": len(t),
        "word_count": len(words),
        "avg_word_length": avg_word_length,
        "sentence_count": len(re.findall(r"[.!?]+", t)),
        "exclamation_count": t.count("!"),
        "question_count": t.count("?"),
        "comma_count": t.count(","),
        "uppercase_ratio": (sum(1 for c in t if c.isupper()) / len(t)) if len(t) > 0 else 0.0,
        "number_count": len(re.findall(r"\d", t)),
        "special_char_count": len(re.findall(r"[^\w\s]", t)),
    }




def make_features_one(text: str, tfidf, scaler, stat_features_order):
    X_text = tfidf.transform([text])  # (1, V)

    stats_all = compute_text_stats(text)

    scaler_cols = getattr(scaler, "feature_names_in_", None)
    cols = list(scaler_cols) if scaler_cols is not None else list(stat_features_order)

    stats_df = pd.DataFrame([{k: stats_all[k] for k in cols}], columns=cols)

    X_stats_scaled = scaler.transform(stats_df)  
    X_stats_sparse = csr_matrix(X_stats_scaled)

    X = hstack([X_text, X_stats_sparse], format="csr")
    return X



def predict_one(text: str, topk: int = 1):
    tfidf, scaler, stat_features, le, model = load_artifacts(MODEL_DIR)
    X = make_features_one(text, tfidf, scaler, stat_features)

    y_id = model.predict(X)[0]
    label = le.inverse_transform([y_id])[0]

    result = {"text": text, "pred_label": label}

    if topk and hasattr(model, "decision_function"):
        scores = model.decision_function(X).ravel()
        classes_ids = getattr(model, "classes_", np.arange(len(le.classes_)))
        pairs = list(zip([le.inverse_transform([cid])[0] for cid in classes_ids], scores))
        pairs.sort(key=lambda x: x[1], reverse=True)
        result["topk"] = pairs[:topk]

    return result


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="Đoạn văn cần dự đoán")
    g.add_argument("--interactive", action="store_true", help="Bật chế độ nhập nhiều dòng")
    ap.add_argument("--topk", type=int, default=0)
    args = ap.parse_args()

    if args.text:
        res = predict_one(args.text, topk=args.topk)
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    print(">> Interactive mode (Ctrl+C để thoát).")
    while True:
        try:
            line = input("\nNhập văn bản: ").strip()
            if not line:
                break
            res = predict_one(line, topk=args.topk)
            print(json.dumps(res, ensure_ascii=False, indent=2))
        except (KeyboardInterrupt, EOFError):
            print("-"*100)
            break


if __name__ == "__main__":
    main()
