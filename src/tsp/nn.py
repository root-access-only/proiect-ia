"""Nearest-Neighbor greedy heuristic for TSP (single start + multistart)."""
from __future__ import annotations

from typing import Sequence

from .common import TSPResult, now, tour_cost


def solve_nn(matrix: Sequence[Sequence[float]], start: int = 0) -> TSPResult:
    """Build a tour by always moving to the nearest unvisited city.

    Args:
        matrix: Symmetric NxN distance matrix.
        start: Starting city index.

    Returns:
        ``TSPResult`` with ``iterations == N`` (number of greedy picks).
    """
    n = len(matrix)
    if n == 0:
        return TSPResult("NN", [], 0.0, 0.0, 0, [], {"start": start})

    t0 = now()
    visited = [False] * n
    visited[start] = True
    tour = [start]
    current = start
    cost = 0.0
    history = [(0, 0.0)]

    for step in range(n - 1):
        best_j, best_d = -1, float("inf")
        for j in range(n):
            if visited[j]:
                continue
            d = matrix[current][j]
            if d < best_d:
                best_d = d
                best_j = j
        tour.append(best_j)
        visited[best_j] = True
        cost += best_d
        current = best_j
        history.append((step + 1, cost))

    cost += matrix[current][start]
    history.append((n, cost))

    return TSPResult(
        algorithm="NN",
        tour=tour,
        cost=cost,
        elapsed=now() - t0,
        iterations=n,
        history=history,
        params={"start": start},
    )


def solve_nn_multistart(
    matrix: Sequence[Sequence[float]],
    starts: int | None = None,
) -> TSPResult:
    """Run NN from multiple starting cities and keep the best tour.

    Args:
        matrix: Symmetric NxN distance matrix.
        starts: Number of starting cities to try (``None`` means all ``N``).

    Returns:
        Best ``TSPResult`` found across the runs; ``params['per_start']`` lists
        the cost obtained from every start.
    """
    n = len(matrix)
    if n == 0:
        return TSPResult("NN-multi", [], 0.0, 0.0, 0, [], {})

    starts = starts or n
    starts = min(starts, n)
    t0 = now()

    best_tour: list[int] = []
    best_cost = float("inf")
    per_start: list[float] = []
    history: list[tuple[int, float]] = []

    for s in range(starts):
        r = solve_nn(matrix, start=s)
        per_start.append(r.cost)
        if r.cost < best_cost:
            best_cost = r.cost
            best_tour = r.tour
        history.append((s + 1, best_cost))

    return TSPResult(
        algorithm="NN-multi",
        tour=best_tour,
        cost=best_cost,
        elapsed=now() - t0,
        iterations=starts,
        history=history,
        params={"starts": starts, "per_start": per_start},
    )
