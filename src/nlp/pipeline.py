"""Parameterizable scikit-learn pipeline for text classification."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier

from .datasets import load_dataset


@dataclass
class NLPConfig:
    """Configuration of the text classification experiment.

    Attributes:
        dataset: Dataset name, see :func:`nlp.datasets.list_datasets`.
        classifier: ``"nb"``, ``"svm"``, ``"logreg"`` or ``"rf"``.
        vectorizer: ``"tfidf"`` or ``"bow"``.
        ngram_min, ngram_max: N-gram range.
        max_features: Vocabulary cap (``None`` = unlimited).
        min_df, max_df: Document frequency filters.
        stop_words: ``"english"`` or ``None``.
        sublinear_tf: Use ``log(1 + tf)`` (TF-IDF only).
        test_size: Fraction of documents reserved for testing.
        sample: Cap the number of documents loaded (``None`` = all).
        seed: Random state for splitting and any RNG-using classifier.
    """

    dataset: str = "20newsgroups"
    classifier: str = "logreg"
    vectorizer: str = "tfidf"
    ngram_min: int = 1
    ngram_max: int = 2
    max_features: int | None = 20000
    min_df: int = 2
    max_df: float = 0.95
    stop_words: str | None = "english"
    sublinear_tf: bool = True
    test_size: float = 0.2
    sample: int | None = 5000
    seed: int = 42


@dataclass
class NLPResult:
    """Output of a single NLP run."""

    config: NLPConfig
    accuracy: float
    precision: float
    recall: float
    f1: float
    elapsed_train: float
    elapsed_eval: float
    confusion: np.ndarray
    target_names: List[str]
    report: str
    n_train: int
    n_test: int
    extras: Dict[str, Any] = field(default_factory=dict)


def _build_vectorizer(cfg: NLPConfig):
    common = dict(
        ngram_range=(cfg.ngram_min, cfg.ngram_max),
        max_features=cfg.max_features,
        min_df=cfg.min_df,
        max_df=cfg.max_df,
        stop_words=cfg.stop_words,
    )
    if cfg.vectorizer == "bow":
        return CountVectorizer(**common)
    return TfidfVectorizer(sublinear_tf=cfg.sublinear_tf, norm="l2", **common)


def _build_classifier(cfg: NLPConfig):
    if cfg.classifier == "nb":
        return MultinomialNB()
    if cfg.classifier == "svm":
        return LinearSVC(C=1.0, random_state=cfg.seed)
    if cfg.classifier == "rf":
        return RandomForestClassifier(
            n_estimators=200, n_jobs=-1, random_state=cfg.seed
        )
    return LogisticRegression(
        max_iter=2000, n_jobs=-1, random_state=cfg.seed, C=1.0
    )


class NLPRunner:
    """Drives a single experiment end-to-end."""

    def __init__(self, cfg: NLPConfig):
        self.cfg = cfg

    def run(self, progress_cb=None) -> NLPResult:
        """Load data, train, evaluate and return an :class:`NLPResult`."""
        cfg = self.cfg

        if progress_cb:
            progress_cb("Loading dataset...")
        bunch = load_dataset(cfg.dataset, sample=cfg.sample, seed=cfg.seed)
        X_raw, y, names = bunch["data"], bunch["target"], bunch["target_names"]

        if progress_cb:
            progress_cb(f"Splitting {len(X_raw)} documents...")
        X_train_raw, X_test_raw, y_train, y_test = train_test_split(
            X_raw, y, test_size=cfg.test_size, random_state=cfg.seed,
            stratify=y if len(set(y.tolist())) > 1 else None,
        )

        if progress_cb:
            progress_cb("Vectorizing text...")
        vec = _build_vectorizer(cfg)
        X_train = vec.fit_transform(X_train_raw)
        X_test = vec.transform(X_test_raw)

        if progress_cb:
            progress_cb(f"Training {cfg.classifier} classifier...")
        clf = _build_classifier(cfg)
        t0 = time.perf_counter()
        clf.fit(X_train, y_train)
        train_time = time.perf_counter() - t0

        if progress_cb:
            progress_cb("Evaluating on test split...")
        t0 = time.perf_counter()
        y_pred = clf.predict(X_test)
        eval_time = time.perf_counter() - t0

        acc = accuracy_score(y_test, y_pred)
        p = precision_score(y_test, y_pred, average="macro", zero_division=0)
        r = recall_score(y_test, y_pred, average="macro", zero_division=0)
        f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)
        cm = confusion_matrix(y_test, y_pred)
        report = classification_report(
            y_test, y_pred, target_names=names, zero_division=0
        )

        return NLPResult(
            config=cfg,
            accuracy=acc,
            precision=p,
            recall=r,
            f1=f1,
            elapsed_train=train_time,
            elapsed_eval=eval_time,
            confusion=cm,
            target_names=names,
            report=report,
            n_train=len(X_train_raw),
            n_test=len(X_test_raw),
            extras={
                "vocab_size": getattr(vec, "vocabulary_", {}).__len__()
                if hasattr(vec, "vocabulary_") else None,
                "classifier_repr": clf.__class__.__name__,
            },
        )

    def predict(self, text: str | Sequence[str]) -> Dict[str, Any]:
        """Convenience: train once on the configured dataset and classify ``text``."""
        cfg = self.cfg
        bunch = load_dataset(cfg.dataset, sample=cfg.sample, seed=cfg.seed)
        X_raw, y, names = bunch["data"], bunch["target"], bunch["target_names"]

        vec = _build_vectorizer(cfg)
        X = vec.fit_transform(X_raw)
        clf = _build_classifier(cfg)
        clf.fit(X, y)

        if isinstance(text, str):
            inputs = [text]
        else:
            inputs = list(text)
        Xq = vec.transform(inputs)
        preds = clf.predict(Xq)
        labels = [names[int(p)] for p in preds]
        return {"texts": inputs, "labels": labels, "indices": preds.tolist()}
