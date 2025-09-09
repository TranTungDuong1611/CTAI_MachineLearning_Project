#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import numpy as np
from scipy import sparse
import joblib


from sklearn.ensemble import StackingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix


def _to_dense(X):
    # dùng khi pipeline có FunctionTransformer(_to_dense)
    try:
        return X.todense()
    except Exception:
        return X

def identity(x):
    return x

def train_and_evaluate(feature_dir: str, results_dir: str, cv: int = 6):
    # Load data
    Xtr_combined = sparse.load_npz(os.path.join(feature_dir, "Xtr_combined.npz"))
    Xte_combined = sparse.load_npz(os.path.join(feature_dir, "Xte_combined.npz"))
    y_train = np.load(os.path.join(feature_dir, "y_train.npy"))
    y_test = np.load(os.path.join(feature_dir, "y_test.npy"))

    # Base models
    svm_base = LinearSVC(C=1.0, loss="squared_hinge", random_state=42, max_iter=1500, dual=False)
    lr_base = LogisticRegression(C=1.0, max_iter=1000, random_state=42)

    rf_pipe = Pipeline([
        ("to_dense", FunctionTransformer(_to_dense, accept_sparse=True)),
        ("rf", RandomForestClassifier(n_estimators=302, random_state=42, n_jobs=-1))
    ])

    base_models = [
        ("svm", svm_base),
        ("lr", lr_base),
        ("rf", rf_pipe),
    ]

    # Meta learner
    meta_learner = LinearSVC(C=1.5, loss="squared_hinge", random_state=42, max_iter=1000, dual=False)

    # Stacking classifier
    stacking = StackingClassifier(
        estimators=base_models,
        final_estimator=meta_learner,
        cv=cv,
        n_jobs=-1
    )

    # Train & predict
    stacking.fit(Xtr_combined, y_train)
    y_pred_train = stacking.predict(Xtr_combined)
    y_pred_test = stacking.predict(Xte_combined)

    acc_train = accuracy_score(y_train, y_pred_train)
    acc_test = accuracy_score(y_test, y_pred_test)
    f1_macro = f1_score(y_test, y_pred_test, average="macro")
    f1_weighted = f1_score(y_test, y_pred_test, average="weighted")

    print("="*72)
    print("Acc train stack:", f"{acc_train:.4f}")
    print("Acc test  stack:", f"{acc_test:.4f}")
    print("F1-macro       :", f"{f1_macro:.4f}")
    print("F1-weighted    :", f"{f1_weighted:.4f}")
    print("\nClassification report:\n", classification_report(y_test, y_pred_test))
    print("Confusion matrix:\n", confusion_matrix(y_test, y_pred_test))

    # Save model
    os.makedirs(results_dir, exist_ok=True)
    out_path = os.path.join(results_dir, "stacking_model.joblib")
    joblib.dump(stacking, out_path)
    print("\nSaved model ->", out_path)


def parse_args():
    p = argparse.ArgumentParser(description="Train stacking model from precomputed features")
    p.add_argument("--features", type=str, required=True, help="Directory with precomputed features (npz, npy)")
    p.add_argument("--results", type=str, default="./results", help="Directory to save model & reports")
    p.add_argument("--cv", type=int, default=6, help="CV folds for stacking")
    return p.parse_args()


def main():
    args = parse_args()
    train_and_evaluate(args.features, args.results, args.cv)


if __name__ == "__main__":
    main()
