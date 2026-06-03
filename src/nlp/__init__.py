"""NLP text classification suite.

Provides three English datasets, a parameterizable pipeline supporting four
classifiers, evaluation utilities and comparison plots.
"""
from .datasets import (
    list_datasets,
    load_dataset,
    AvailableDatasets,
)
from .pipeline import NLPConfig, NLPRunner, NLPResult

__all__ = [
    "list_datasets",
    "load_dataset",
    "AvailableDatasets",
    "NLPConfig",
    "NLPRunner",
    "NLPResult",
]
