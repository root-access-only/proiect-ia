"""Simulated annealing for TSP with configurable cooling schedule."""
from __future__ import annotations

import math
import random
from typing import Sequence

from .common import TSPResult, now, tour_cost, two_opt_swap


def _cool(T: float, schedule: str, alpha: float, delta: float, step: int, T0: float) -> float:
    if schedule == "geometric":
        return T * alpha
    if schedule == "linear":
        return max(0.0, T - delta)
    if schedule == "logarithmic":
        return T0 / math.log(2 + step)
    return T * alpha


def solve_sa(
    matrix: Sequence[Sequence[float]],
    T_max: float = 1000.0,
    T_min: float = 1e-3,
    alpha: float = 0.995,
    delta: float = 1.0,
    schedule: str = "geometric",
    iterations: int = 50_000,
    init: str = "nn",
    seed: int | None = None,
) -> TSPResult:
    """Simulated annealing with the Metropolis acceptance criterion.

    Args:
        matrix: Symmetric NxN distance matrix.
        T_max: Starting temperature.
        T_min: Stop when temperature falls below this.
        alpha: Cooling factor for the geometric schedule.
        delta: Step size for the linear schedule.
        schedule: ``"geometric"``, ``"linear"`` or ``"logarithmic"``.
        iterations: Hard cap on the number of moves attempted.
        init: ``"random"`` or ``"nn"`` (warm start via Nearest-Neighbor).
        seed: RNG seed for reproducibility.

    Returns:
        ``TSPResult`` with full convergence history.
    """
    rng = random.Random(seed)
    n = len(matrix)
    if n == 0:
        return TSPResult("SA", [], 0.0, 0.0, 0, [], {})

    t0 = now()

    if init == "nn":
        from .nn import solve_nn
        current = solve_nn(matrix, start=rng.randrange(n)).tour
    else:
        current = list(range(n))
        rng.shuffle(current)

    current_cost = tour_cost(current, matrix)
    best_tour = current[:]
    best_cost = current_cost
    history = [(0, best_cost)]

    T = T_max
    accepted = 0
    rejected = 0
    for step in range(iterations):
        if T < T_min:
            break

        i, j = sorted(rng.sample(range(n), 2))
        if j - i < 1:
            continue
        candidate = two_opt_swap(current, i, j)
        cand_cost = tour_cost(candidate, matrix)
        dE = cand_cost - current_cost

        if dE <= 0 or rng.random() < math.exp(-dE / max(T, 1e-12)):
            current = candidate
            current_cost = cand_cost
            accepted += 1
            if current_cost < best_cost:
                best_cost = current_cost
                best_tour = current[:]
                history.append((step, best_cost))
        else:
            rejected += 1

        T = _cool(T, schedule, alpha, delta, step, T_max)

    return TSPResult(
        algorithm="SA",
        tour=best_tour,
        cost=best_cost,
        elapsed=now() - t0,
        iterations=accepted + rejected,
        history=history,
        params={
            "T_max": T_max,
            "T_min": T_min,
            "alpha": alpha,
            "delta": delta,
            "schedule": schedule,
            "iterations": iterations,
            "init": init,
            "seed": seed,
            "accepted": accepted,
            "rejected": rejected,
        },
    )
