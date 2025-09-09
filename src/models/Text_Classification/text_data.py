#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, Iterable, Tuple, List

import numpy as np
import pandas as pd
from scipy import sparse

import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer


# -----------------------------
# Param dataclasses
# -----------------------------

@dataclass
class TFIDFParams:
    max_features: int = 15000
    min_df: int = 2
    max_df: float = 0.85
    ngram_min: int = 1
    ngram_max: int = 3
    lowercase: bool = True


@dataclass
class SplitParams:
    test_size: float = 0.25
    random_state: int = 42


# -----------------------------
# Utilities & dataset builders
# -----------------------------

def load_json_file(path: str) -> pd.DataFrame:
    """Load a JSON or JSONL into a DataFrame. If the top-level is a dict, wrap into a list."""
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
        try:
            data = json.loads(raw)
            if isinstance(data, dict):
                data = [data]
        except json.JSONDecodeError:
            data = [json.loads(line) for line in raw.splitlines() if line.strip()]
    return pd.DataFrame(data)


def normalize_subcat(meta_df: pd.DataFrame) -> pd.DataFrame:
    if "subcat" not in meta_df.columns:
        meta_df["subcat"] = np.nan
        return meta_df

    col = meta_df["subcat"]
    logging.info(
        "Blank counts before normalize -> None:%d | NaN:%d | Empty:%d",
        int((col.apply(lambda x: x is None)).sum()),
        int(col.isna().sum()),
        int((col.astype(str).str.strip() == "").sum()),
    )

    meta_df["subcat"] = meta_df["subcat"].replace(
        {"": np.nan, " ": np.nan, "nan": np.nan, "None": np.nan}
    )
    meta_df["subcat"] = meta_df["subcat"].where(~meta_df["subcat"].isna(), np.nan)

    logging.info(
        "subcat value counts (including NaN):\n%s",
        meta_df["subcat"].value_counts(dropna=False).to_string(),
    )
    return meta_df


def build_dataset(df: pd.DataFrame, target_col: str = "cat") -> pd.DataFrame:
    """Flatten metadata (if present), keep core columns, and log target distribution."""
    if "metadata" in df.columns:
        meta_df = pd.json_normalize(df["metadata"])
        meta_df = normalize_subcat(meta_df)
        df_merge = pd.concat([df.drop(columns=["metadata"]), meta_df], axis=1)
    else:
        df_merge = df.copy()

    expected_cols = ["title_clean", "desc_clean", "content_clean", target_col]
    missing = [c for c in expected_cols if c not in df_merge.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df_new = df_merge[expected_cols].copy()
    logging.info("Target '%s' unique: %s", target_col, df_new[target_col].unique())
    logging.info("Target distribution:\n%s", df_new[target_col].value_counts().to_string())
    return df_new.rename(columns={target_col: "cat"})


def build_text_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for c in ["title_clean", "desc_clean", "content_clean"]:
        df[c] = df[c].fillna("").astype(str)
    df["text"] = df["title_clean"] + " " + df["desc_clean"] + " " + df["content_clean"]
    return df


def encode_labels(df: pd.DataFrame) -> Tuple[np.ndarray, LabelEncoder]:
    le = LabelEncoder()
    y = le.fit_transform(df["cat"].astype(str))
    return y, le


def split_text_and_labels(
    text_series: pd.Series, y: np.ndarray, split_params: SplitParams
) -> Tuple[pd.Series, pd.Series, np.ndarray, np.ndarray]:
    X_train, X_test, y_train, y_test = train_test_split(
        text_series, y,
        test_size=split_params.test_size,
        random_state=split_params.random_state,
        stratify=y
    )
    return X_train, X_test, y_train, y_test


def fit_tfidf(
    X_train_text: pd.Series, X_test_text: pd.Series, tfidf_params: TFIDFParams
) -> Tuple[sparse.csr_matrix, sparse.csr_matrix, TfidfVectorizer, List[str]]:
    vectorizer = TfidfVectorizer(
        max_features=tfidf_params.max_features,
        min_df=tfidf_params.min_df,
        max_df=tfidf_params.max_df,
        ngram_range=(tfidf_params.ngram_min, tfidf_params.ngram_max),
        lowercase=tfidf_params.lowercase,
    )
    Xtr = vectorizer.fit_transform(X_train_text)
    Xte = vectorizer.transform(X_test_text)
    feature_names = vectorizer.get_feature_names_out().tolist()
    return Xtr, Xte, vectorizer, feature_names


def extract_text_statistics(df_text_only: pd.DataFrame) -> pd.DataFrame:
    """Compute statistical features from a DataFrame that contains only 'text' column."""
    if "text" not in df_text_only.columns:
        raise ValueError("DataFrame must include a 'text' column for statistics.")
    df = df_text_only.copy()
    df["text_length"] = df["text"].map(lambda x: len(x))
    df["word_count"] = df["text"].map(lambda x: len(x.split()) if x else 0)
    df["avg_word_length"] = df["text"].map(lambda x: (np.mean([len(w) for w in x.split()]) if x.split() else 0.0))
    df["sentence_count"] = df["text"].str.count(r"[.!?]+")
    df["exclamation_count"] = df["text"].str.count(r"!")
    df["question_count"] = df["text"].str.count(r"\?")
    df["comma_count"] = df["text"].str.count(r",")
    df["uppercase_ratio"] = df["text"].map(lambda x: (sum(1 for c in x if c.isupper()) / len(x)) if len(x) > 0 else 0.0)
    df["number_count"] = df["text"].str.count(r"\d")
    df["special_char_count"] = df["text"].str.count(r"[^\w\s]")
    return df.drop(columns=["text"])


def get_stat_feature_names() -> List[str]:
    return [
        "text_length",
        "word_count",
        "avg_word_length",
        "sentence_count",
        "exclamation_count",
        "question_count",
        "comma_count",
        "uppercase_ratio",
        "number_count",
        "special_char_count",
    ]


def split_stats_by_indices(
    df_stats: pd.DataFrame, train_idx: pd.Index, test_idx: pd.Index
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    X_train_stats = df_stats.loc[train_idx]
    X_test_stats = df_stats.loc[test_idx]
    return X_train_stats, X_test_stats


def fit_scale_stats(
    X_train_stats: pd.DataFrame, X_test_stats: pd.DataFrame
) -> Tuple[sparse.csr_matrix, sparse.csr_matrix, StandardScaler]:
    scaler = StandardScaler()
    Xtr_scaled = scaler.fit_transform(X_train_stats)
    Xte_scaled = scaler.transform(X_test_stats)
    return sparse.csr_matrix(Xtr_scaled), sparse.csr_matrix(Xte_scaled), scaler


def hstack_features(
    Xtr_tfidf: sparse.csr_matrix, Xtr_stats: sparse.csr_matrix,
    Xte_tfidf: sparse.csr_matrix, Xte_stats: sparse.csr_matrix
) -> Tuple[sparse.csr_matrix, sparse.csr_matrix]:
    Xtr_combined = sparse.hstack([Xtr_tfidf, Xtr_stats], format="csr")
    Xte_combined = sparse.hstack([Xte_tfidf, Xte_stats], format="csr")
    return Xtr_combined, Xte_combined


# -----------------------------
# End-to-end (with saving)
# -----------------------------

def build_and_save_features_from_csv(
    csv_path: str,
    outdir: str = "output_nlp_features",
    tfidf_params: TFIDFParams = TFIDFParams(),
    split_params: SplitParams = SplitParams(),
) -> Dict[str, Any]:
    df_raw = pd.read_csv(csv_path) if str(csv_path).lower().endswith(".csv") else load_json_file(csv_path)
    df = build_dataset(df_raw, target_col="cat")
    df = build_text_column(df)

    # Labels
    y, label_encoder = encode_labels(df)

    # Split
    X_train, X_test, y_train, y_test = split_text_and_labels(df["text"], y, split_params)
    X_train_text = X_train.reset_index(drop=True)
    X_test_text = X_test.reset_index(drop=True)

    # TF-IDF
    Xtr_tfidf, Xte_tfidf, vectorizer, tfidf_feature_names = fit_tfidf(X_train_text, X_test_text, tfidf_params)

    # Stats
    df_stats_full = extract_text_statistics(df[["text"]])
    stat_feature_names = get_stat_feature_names()
    X_train_stats_df, X_test_stats_df = split_stats_by_indices(df_stats_full, X_train.index, X_test.index)

    Xtr_stats, Xte_stats, scaler = fit_scale_stats(X_train_stats_df, X_test_stats_df)

    # Combine
    Xtr_combined, Xte_combined = hstack_features(Xtr_tfidf, Xtr_stats, Xte_tfidf, Xte_stats)

    # Save artifacts
    Path(outdir).mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, f"{outdir}/tfidf_vectorizer.joblib")
    joblib.dump(scaler, f"{outdir}/stats_scaler.joblib")
    joblib.dump(label_encoder, f"{outdir}/label_encoder.joblib")

    np.save(f"{outdir}/y_train.npy", y_train)
    np.save(f"{outdir}/y_test.npy", y_test)

    sparse.save_npz(f"{outdir}/Xtr_tfidf.npz", Xtr_tfidf)
    sparse.save_npz(f"{outdir}/Xte_tfidf.npz", Xte_tfidf)
    sparse.save_npz(f"{outdir}/Xtr_stats.npz", Xtr_stats)
    sparse.save_npz(f"{outdir}/Xte_stats.npz", Xte_stats)
    sparse.save_npz(f"{outdir}/Xtr_combined.npz", Xtr_combined)
    sparse.save_npz(f"{outdir}/Xte_combined.npz", Xte_combined)

    with open(f"{outdir}/tfidf_feature_names.json", "w", encoding="utf-8") as f:
        json.dump(tfidf_feature_names, f, ensure_ascii=False, indent=2)
    with open(f"{outdir}/stat_feature_names.json", "w", encoding="utf-8") as f:
        json.dump(stat_feature_names, f, ensure_ascii=False, indent=2)

    return {
        "vectorizer": vectorizer,
        "scaler": scaler,
        "label_encoder": label_encoder,
        "tfidf_feature_names": tfidf_feature_names,
        "stat_feature_names": stat_feature_names,
        "Xtr_tfidf": Xtr_tfidf,
        "Xte_tfidf": Xte_tfidf,
        "Xtr_stats": Xtr_stats,
        "Xte_stats": Xte_stats,
        "Xtr_combined": Xtr_combined,
        "Xte_combined": Xte_combined,
        "y_train": y_train,
        "y_test": y_test,
    }


# -----------------------------
# CLI
# -----------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build TF-IDF + statistical features from CSV/JSONL.")
    p.add_argument("--input", required=True, help="Path to CSV or JSONL file.")
    p.add_argument("--outdir", default="output_nlp_features", help="Output directory.")
    p.add_argument("--test_size", type=float, default=0.25)
    p.add_argument("--random_state", type=int, default=42)
    p.add_argument("--max_features", type=int, default=15000)
    p.add_argument("--min_df", type=int, default=2)
    p.add_argument("--max_df", type=float, default=0.85)
    p.add_argument("--ngram_min", type=int, default=1)
    p.add_argument("--ngram_max", type=int, default=3)
    return p.parse_args()


def main():
    args = parse_args()
    tfidf_params = TFIDFParams(
        max_features=args.max_features,
        min_df=args.min_df,
        max_df=args.max_df,
        ngram_min=args.ngram_min,
        ngram_max=args.ngram_max,
    )
    split_params = SplitParams(test_size=args.test_size, random_state=args.random_state)

    artifacts = build_and_save_features_from_csv(
        csv_path=args.input,
        outdir=args.outdir,
        tfidf_params=tfidf_params,
        split_params=split_params,
    )

    print("✅ Done. Shapes:")
    print(" - Xtr_tfidf:", artifacts["Xtr_tfidf"].shape)
    print(" - Xte_tfidf:", artifacts["Xte_tfidf"].shape)
    print(" - Xtr_stats:", artifacts["Xtr_stats"].shape)
    print(" - Xte_stats:", artifacts["Xte_stats"].shape)
    print(" - Xtr_combined:", artifacts["Xtr_combined"].shape)
    print(" - Xte_combined:", artifacts["Xte_combined"].shape)
    print("\nArtifacts saved to:", Path(args.outdir).resolve())


if __name__ == "__main__":
    main()
