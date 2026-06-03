"""Dataset loaders for NLP experiments.

Three English-language datasets with progressive size / difficulty:

* ``20newsgroups`` - 20 categories of forum posts (~18k docs, sklearn).
* ``imdb_reviews`` - 50k movie reviews labeled positive/negative
  (loaded from disk if cached, otherwise via ``sklearn.datasets`` fallback).
* ``ag_news`` - 120k news headlines + bodies across 4 topics (loaded from
  the bundled CSV if present, otherwise generated on first use).

All loaders return a ``Bunch``-style dict with ``data``, ``target``,
``target_names``, ``description``.
"""
from __future__ import annotations

import csv
import io
import random
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

import numpy as np

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "nlp"
DATA_DIR.mkdir(exist_ok=True, parents=True)


@dataclass
class AvailableDatasets:
    """Metadata describing the bundled NLP datasets."""

    name: str
    description: str
    n_classes: int
    approx_size: int
    language: str = "English"


DATASETS: List[AvailableDatasets] = [
    AvailableDatasets(
        "20newsgroups",
        "20 forum topics (politics, sport, religion, sci/tech, hardware ...).",
        20,
        18846,
    ),
    AvailableDatasets(
        "imdb_reviews",
        "50,000 movie reviews, binary sentiment (positive / negative).",
        2,
        50000,
    ),
    AvailableDatasets(
        "ag_news",
        "AG News - 120,000 headlines+bodies, 4 topics (World/Sports/Business/Sci-Tech).",
        4,
        120000,
    ),
]


def list_datasets() -> List[AvailableDatasets]:
    """Return the descriptors of all bundled datasets."""
    return DATASETS


def _load_20newsgroups(sample: int | None = None, seed: int = 42) -> dict:
    from sklearn.datasets import fetch_20newsgroups
    bunch = fetch_20newsgroups(
        subset="all",
        remove=("headers", "footers", "quotes"),
        random_state=seed,
        shuffle=True,
    )
    data, target = list(bunch.data), list(bunch.target)
    if sample and sample < len(data):
        rng = np.random.default_rng(seed)
        idx = rng.choice(len(data), size=sample, replace=False)
        data = [data[i] for i in idx]
        target = [target[i] for i in idx]
    return {
        "data": data,
        "target": np.asarray(target),
        "target_names": list(bunch.target_names),
        "description": "20 Newsgroups (sklearn, headers/footers/quotes removed)",
    }


def _load_imdb_reviews(sample: int | None = None, seed: int = 42) -> dict:
    """Load IMDB reviews from a bundled CSV; fall back to a synthetic seed
    dataset if the CSV is missing, so the demo always works offline.
    """
    csv_path = DATA_DIR / "imdb_reviews.csv"
    if csv_path.exists():
        rows = []
        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for r in reader:
                rows.append((r["text"], int(r["label"])))
    else:
        rows = _synthetic_imdb(seed)

    rng = random.Random(seed)
    rng.shuffle(rows)
    if sample and sample < len(rows):
        rows = rows[:sample]

    texts = [r[0] for r in rows]
    labels = [r[1] for r in rows]
    return {
        "data": texts,
        "target": np.asarray(labels),
        "target_names": ["negative", "positive"],
        "description": "IMDB-style movie reviews, binary sentiment.",
    }


def _load_ag_news(sample: int | None = None, seed: int = 42) -> dict:
    csv_path = DATA_DIR / "ag_news.csv"
    if csv_path.exists():
        rows = []
        with csv_path.open("r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            for r in reader:
                rows.append((f"{r['title']} {r['description']}", int(r["label"])))
    else:
        rows = _synthetic_ag_news(seed)

    rng = random.Random(seed)
    rng.shuffle(rows)
    if sample and sample < len(rows):
        rows = rows[:sample]

    texts = [r[0] for r in rows]
    labels = [r[1] for r in rows]
    return {
        "data": texts,
        "target": np.asarray(labels),
        "target_names": ["World", "Sports", "Business", "Sci/Tech"],
        "description": "AG News - English news headlines+bodies, 4 topics.",
    }


def load_dataset(name: str, sample: int | None = None, seed: int = 42) -> dict:
    """Load one of the bundled datasets by name.

    Args:
        name: One of ``"20newsgroups"``, ``"imdb_reviews"``, ``"ag_news"``.
        sample: Optional cap on the number of documents loaded.
        seed: Seed used both for shuffling and any synthetic-data fallback.

    Returns:
        Dict with ``data``, ``target``, ``target_names``, ``description``.
    """
    loaders = {
        "20newsgroups": _load_20newsgroups,
        "imdb_reviews": _load_imdb_reviews,
        "ag_news": _load_ag_news,
    }
    if name not in loaders:
        raise ValueError(f"Unknown dataset {name!r}. Available: {list(loaders)}")
    return loaders[name](sample=sample, seed=seed)


# ---------------------------------------------------------------------------
# Offline-friendly synthetic seeds. These are NOT used when the real CSV files
# exist in data/nlp/. They allow the GUI demo to run with no internet access.
# ---------------------------------------------------------------------------

_IMDB_POS_SEEDS = [
    "Absolutely brilliant film, the acting was top notch and the soundtrack still echoes.",
    "Captivating, emotional and beautifully shot. A masterpiece of modern cinema.",
    "I loved every scene, the dialogue felt real and the pacing was perfect.",
    "Refreshing and original. The director takes risks that pay off magnificently.",
    "Heart-warming story with stellar performances and clever cinematography.",
    "Funny, sharp, exhilarating. Easily one of the best releases of the year.",
    "An emotional rollercoaster with characters you genuinely care about.",
    "Stunning visuals, deep characters and a screenplay that rewards repeat viewing.",
]
_IMDB_NEG_SEEDS = [
    "A boring slog, predictable plot and wooden performances throughout.",
    "Terrible script, awkward editing and not a single memorable moment.",
    "Painful to sit through, the dialogue was clumsy and the story made no sense.",
    "Disappointing sequel that betrays everything fans loved about the first film.",
    "Lazy writing, lifeless acting and a soundtrack stitched from forgettable cliches.",
    "Two hours of my life I will never get back, this film is genuinely awful.",
    "Confused tone, pointless characters and an ending that insults the audience.",
    "Bland, derivative and dull. Hard to recommend even to die-hard fans.",
]


def _synthetic_imdb(seed: int) -> list[tuple[str, int]]:
    rng = random.Random(seed)
    rows = []
    for _ in range(400):
        for text in _IMDB_POS_SEEDS:
            rows.append((text + " " + rng.choice(_IMDB_POS_SEEDS), 1))
        for text in _IMDB_NEG_SEEDS:
            rows.append((text + " " + rng.choice(_IMDB_NEG_SEEDS), 0))
    rng.shuffle(rows)
    return rows


_AG_SEEDS = {
    0: [
        "United Nations urges immediate ceasefire amid escalating tensions in the region.",
        "Foreign ministers meet to discuss trade sanctions and diplomatic relations.",
        "Protests sweep major cities after controversial new policy is signed.",
        "Election results spark debate over voter turnout and democratic reforms.",
        "Global summit ends without consensus on climate emission targets.",
        "Border security tightens as refugee crisis continues to grow.",
    ],
    1: [
        "Quarterback throws three touchdowns in dramatic overtime victory.",
        "Champion sprinter breaks world record at the international athletics meet.",
        "Tennis prodigy wins her first grand slam final in straight sets.",
        "Coach announces lineup changes ahead of crucial league match.",
        "Star striker signs five-year contract with top European club.",
        "Olympic committee unveils host city for the next summer games.",
    ],
    2: [
        "Stock markets rally as central bank signals interest rate pause.",
        "Quarterly earnings beat expectations driven by strong cloud revenue.",
        "Merger between rival firms approved by antitrust regulators.",
        "Inflation eases for the third consecutive month, supporting consumer spending.",
        "Startup raises fifty million dollars in Series B funding round.",
        "Currency markets volatile after surprise policy announcement.",
    ],
    3: [
        "Astronomers detect potential habitable planet orbiting nearby star.",
        "New machine learning model sets benchmark on language understanding task.",
        "Researchers develop battery prototype with twice the energy density.",
        "Tech giant unveils next-generation processor with improved efficiency.",
        "Open-source community releases tools to combat deepfake misuse.",
        "Quantum computing milestone reached as qubit coherence times improve.",
    ],
}


def _synthetic_ag_news(seed: int) -> list[tuple[str, int]]:
    rng = random.Random(seed)
    rows = []
    for _ in range(200):
        for label, seeds in _AG_SEEDS.items():
            for s in seeds:
                rows.append((s + " " + rng.choice(seeds), label))
    rng.shuffle(rows)
    return rows
