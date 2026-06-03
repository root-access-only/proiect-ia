"""Common data structures and utilities for TSP solvers.

Provides a uniform `TSPResult` returned by every algorithm, distance-matrix I/O,
random-instance generation and a tour-cost helper. All algorithms minimize the
closed-tour cost on a symmetric distance matrix.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple


@dataclass
class TSPResult:
    """Outcome of a TSP run with enough metadata for cross-algorithm comparison.

    Attributes:
        algorithm: Short algorithm name (``"BKT"``, ``"NN"``, ``"HC"``, ...).
        tour: Permutation of city indices, length ``N``. The tour is implicitly
            closed (last city connects back to ``tour[0]``).
        cost: Total cost of the closed tour.
        elapsed: Wall-clock seconds spent in the solver.
        iterations: Algorithm-specific iteration counter (nodes expanded for
            BKT, accepted moves for SA, generations for GA, etc.).
        history: Optional list of ``(iteration, best_cost_so_far)`` checkpoints
            usable for convergence plots.
        params: Echo of the parameters the user passed in.
    """

    algorithm: str
    tour: List[int]
    cost: float
    elapsed: float
    iterations: int = 0
    history: List[Tuple[int, float]] = field(default_factory=list)
    params: dict = field(default_factory=dict)

    def closed_tour(self) -> List[int]:
        """Return ``tour`` with the start city appended for display."""
        return self.tour + [self.tour[0]]

    def summary(self) -> str:
        """One-line human-readable summary."""
        return (
            f"[{self.algorithm}] cost={self.cost:.2f} "
            f"time={self.elapsed:.4f}s iters={self.iterations}"
        )


def tour_cost(tour: Sequence[int], matrix: Sequence[Sequence[float]]) -> float:
    """Compute the closed-tour cost of ``tour`` on the given distance matrix."""
    total = 0.0
    n = len(tour)
    for i in range(n):
        total += matrix[tour[i]][tour[(i + 1) % n]]
    return total


def generate_random_matrix(
    n: int,
    low: int = 1,
    high: int = 100,
    seed: int | None = None,
) -> List[List[int]]:
    """Create a symmetric NxN distance matrix with integer weights in [low, high]."""
    rng = random.Random(seed)
    m = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = rng.randint(low, high)
            m[i][j] = d
            m[j][i] = d
    return m


def load_matrix(path: str | Path) -> Tuple[int, List[List[int]]]:
    """Read a TSP instance file (first line ``N``, then ``N`` rows of ``N`` ints)."""
    path = Path(path)
    lines = [ln.strip() for ln in path.read_text().splitlines() if ln.strip()]
    n = int(lines[0])
    matrix = [[int(x) for x in lines[i + 1].split()] for i in range(n)]
    return n, matrix


def save_matrix(matrix: Sequence[Sequence[int]], path: str | Path) -> None:
    """Write a distance matrix in the lab-standard text format."""
    path = Path(path)
    n = len(matrix)
    lines = [str(n)]
    for row in matrix:
        lines.append(" ".join(str(v) for v in row))
    path.write_text("\n".join(lines) + "\n")


def two_opt_swap(tour: Sequence[int], i: int, j: int) -> List[int]:
    """Return ``tour`` with the segment between ``i`` and ``j`` reversed."""
    return list(tour[:i]) + list(reversed(tour[i:j + 1])) + list(tour[j + 1:])


def random_pair(n: int, rng: random.Random) -> Tuple[int, int]:
    """Sample two distinct indices ``i < j`` from ``range(n)``."""
    i, j = sorted(rng.sample(range(n), 2))
    return i, j


def now() -> float:
    """Monotonic high-resolution clock wrapper."""
    return time.perf_counter()


def safe_iterable(value) -> Iterable:
    """Yield from ``value`` if iterable, else yield ``value`` once."""
    if value is None:
        return ()
    if hasattr(value, "__iter__"):
        return value
    return (value,)
