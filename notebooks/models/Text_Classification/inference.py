#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Infer 1 đoạn văn -> dự đoán chủ đề (label) bằng mô hình Stacking đã train.

Yêu cầu các artifact có sẵn (đúng thư mục + tên file):
- tfidf_vectorizer.pkl
- statistical_scaler.pkl
- stat_features.pkl            # danh sách & thứ tự các đặc trưng thống kê đã dùng khi train
- label_encoder.pkl
- stacking_model.pkl           # hoặc stacking_model.joblib

Ví dụ:
python infer_one_text.py \
  --model_dir "/Users/anhquan/Workspace/CTAI_MachineLearning_Project/results/models/Text_Classification" \
  --text "Ngày hôm nay VN-Index tăng mạnh do nhóm ngân hàng..."

Chế độ tương tác (nhập nhiều dòng):
python infer_one_text.py --model_dir ".../Text_Classification" --interactive
"""

import argparse
import os
import sys
import json
import numpy as np

from scipy.sparse import csr_matrix, hstack
from joblib import load as joblib_load


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

    tfidf = joblib_load(tfidf_path)
    scaler = joblib_load(scaler_path)
    stat_features = joblib_load(statfeat_path)  # list[str] theo đúng thứ tự khi train
    label_encoder = joblib_load(le_path)
    model = joblib_load(model_path)

    # Kiểm tra tối thiểu
    if not isinstance(stat_features, (list, tuple)) or len(stat_features) == 0:
        raise ValueError("stat_features.pkl không hợp lệ (cần list tên cột theo đúng thứ tự).")

    return tfidf, scaler, stat_features, label_encoder, model


# ---- Trích xuất đặc trưng thống kê (phải khớp công thức khi train) ----
def compute_text_stats(text: str) -> dict:
    t = text or ""
    # các công thức giống lúc train
    text_length = len(t)
    words = t.split()
    word_count = len(words)
    avg_word_length = float(np.mean([len(w) for w in words])) if words else 0.0

    # đếm câu & ký tự
    import re
    sentence_count = len(re.findall(r"[.!?]+", t))
    exclamation_count = t.count("!")
    question_count = t.count("?")
    comma_count = t.count(",")
    uppercase_ratio = (sum(1 for c in t if c.isupper()) / len(t)) if len(t) > 0 else 0.0
    number_count = len(re.findall(r"\d", t))
    special_char_count = len(re.findall(r"[^\w\s]", t))

    return {
        "text_length": text_length,
        "word_count": word_count,
        "avg_word_length": avg_word_length,
        "sentence_count": sentence_count,
        "exclamation_count": exclamation_count,
        "question_count": question_count,
        "comma_count": comma_count,
        "uppercase_ratio": uppercase_ratio,
        "number_count": number_count,
        "special_char_count": special_char_count,
    }


def make_features_one(text: str, tfidf, scaler, stat_features_order):
    """Tạo đặc trưng kết hợp cho 1 văn bản: TF-IDF + stats (đúng thứ tự cột)."""
    # TF-IDF
    X_text = tfidf.transform([text])  # (1, V)

    # Stats: tính tất cả rồi sắp theo đúng order đã lưu
    stats_all = compute_text_stats(text)
    try:
        stats_vec = np.array([[stats_all[k] for k in stat_features_order]], dtype=float)  # (1, K)
    except KeyError as e:
        raise KeyError(f"Thiếu đặc trưng {e} trong compute_text_stats. "
                       f"Hãy đảm bảo stat_features.pkl & hàm compute_text_stats khớp lúc train.")

    X_stats_scaled = scaler.transform(stats_vec)           # (1, K)
    X_stats_sparse = csr_matrix(X_stats_scaled)

    # Kết hợp
    X = hstack([X_text, X_stats_sparse], format="csr")
    return X


def predict_one(text: str, model_dir: str, topk: int = 0):
    """Dự đoán 1 câu; trả về nhãn dự đoán & (tuỳ chọn) top-k margin."""
    tfidf, scaler, stat_features, le, model = load_artifacts(model_dir)
    X = make_features_one(text, tfidf, scaler, stat_features)

    y_id = model.predict(X)[0]
    label = le.inverse_transform([y_id])[0]

    result = {"text": text, "pred_label": label}

    # Nếu muốn xem margin/score top-k (LinearSVC không có predict_proba)
    if topk and hasattr(model, "decision_function"):
        scores = model.decision_function(X).ravel()  # shape (C,)
        # map id -> label
        if hasattr(model, "classes_"):
            classes_ids = model.classes_
        else:
            # fallback: lấy từ label encoder (thứ tự phải khớp lúc train model)
            classes_ids = np.arange(len(le.classes_))
        pairs = list(zip([le.inverse_transform([cid])[0] for cid in classes_ids], scores))
        pairs.sort(key=lambda x: x[1], reverse=True)
        result["topk"] = pairs[:topk]

    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model_dir", required=True, help="Thư mục chứa các artifact *.pkl")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text", help="Đoạn văn cần dự đoán")
    g.add_argument("--interactive", action="store_true", help="Bật chế độ nhập nhiều dòng")
    ap.add_argument("--topk", type=int, default=0, help="Hiển thị top-k theo margin (LinearSVC)")
    args = ap.parse_args()

    if args.text is not None:
        res = predict_one(args.text, args.model_dir, topk=args.topk)
        # In đẹp
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return

    # interactive
    print(">> Interactive mode (gõ trống hoặc Ctrl+C để thoát).")
    while True:
        try:
            line = input("\nNhập văn bản: ").strip()
            if not line:
                break
            res = predict_one(line, args.model_dir, topk=args.topk)
            print(json.dumps(res, ensure_ascii=False, indent=2))
        except (KeyboardInterrupt, EOFError):
            print("-"*100)
            break


if __name__ == "__main__":
    main()
