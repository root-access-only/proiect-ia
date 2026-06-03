"""Plot helpers for the NLP experiments."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

from .pipeline import NLPResult


def plot_confusion(result: NLPResult, out_path: str | Path) -> Path:
    """Heatmap of the confusion matrix."""
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(
        result.confusion,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=result.target_names,
        yticklabels=result.target_names,
        ax=ax,
        cbar=False,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(
        f"Confusion - {result.config.dataset} / {result.config.classifier} "
        f"(acc={result.accuracy:.3f}, F1={result.f1:.3f})"
    )
    plt.setp(ax.get_xticklabels(), rotation=40, ha="right")
    fig.tight_layout()
    out_path = Path(out_path)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path


def plot_classifier_comparison(
    results: Iterable[NLPResult], out_path: str | Path
) -> Path:
    """Bar chart comparing accuracy / precision / recall / F1 across runs."""
    results = list(results)
    names = [f"{r.config.classifier}\n{r.config.dataset}" for r in results]
    metrics = ["accuracy", "precision", "recall", "f1"]
    values = np.array(
        [[getattr(r, m) for m in metrics] for r in results]
    )

    x = np.arange(len(names))
    width = 0.18
    fig, ax = plt.subplots(figsize=(11, 6))
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]
    for i, m in enumerate(metrics):
        ax.bar(x + (i - 1.5) * width, values[:, i], width=width, label=m, color=colors[i])
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("NLP classifier comparison")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)
    fig.tight_layout()
    out_path = Path(out_path)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path


def plot_param_sweep(
    sweep: Sequence[tuple[str, float]], title: str, out_path: str | Path
) -> Path:
    """Line plot of a single varying parameter against accuracy."""
    xs = [s[0] for s in sweep]
    ys = [s[1] for s in sweep]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs, ys, marker="o", color="#1f77b4")
    ax.set_xlabel("Parameter value")
    ax.set_ylabel("Accuracy")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    for x, y in zip(xs, ys):
        ax.text(x, y + 0.005, f"{y:.3f}", ha="center", fontsize=9)
    fig.tight_layout()
    out_path = Path(out_path)
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path
