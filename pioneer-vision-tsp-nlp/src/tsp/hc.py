"""Hill-climbing variants for TSP with a 2-opt neighborhood."""
from __future__ import annotations

import random
from typing import Sequence

from .common import TSPResult, now, tour_cost, two_opt_swap


def _initial_tour(n: int, rng: random.Random, init: str, matrix) -> list[int]:
    if init == "nn":
        from .nn import solve_nn
        return solve_nn(matrix, start=rng.randrange(n)).tour
    tour = list(range(n))
    rng.shuffle(tour)
    return tour


def solve_hc(
    matrix: Sequence[Sequence[float]],
    variant: str = "steepest",
    restarts: int = 1,
    max_iter: int = 10_000,
    init: str = "random",
    seed: int | None = None,
) -> TSPResult:
    """Hill-climbing with steepest, stochastic or random-restart variants.

    Args:
        matrix: Symmetric NxN distance matrix.
        variant: ``"steepest"`` evaluates every 2-opt neighbor and picks the
            best; ``"stochastic"`` picks randomly among improving moves;
            ``"random_restart"`` repeats steepest from new random starts.
        restarts: Used with ``"random_restart"``; ignored otherwise.
        max_iter: Hard ceiling on improvement steps per restart.
        init: ``"random"`` permutation or ``"nn"`` (nearest-neighbor warm start).
        seed: RNG seed for reproducibility.

    Returns:
        ``TSPResult`` with the best tour found.
    """
    rng = random.Random(seed)
    n = len(matrix)
    if n == 0:
        return TSPResult("HC", [], 0.0, 0.0, 0, [], {"variant": variant})

    t0 = now()
    best_tour: list[int] = []
    best_cost = float("inf")
    total_iters = 0
    history: list[tuple[int, float]] = []

    runs = restarts if variant == "random_restart" else 1
    for run in range(runs):
        current = _initial_tour(n, rng, init, matrix)
        current_cost = tour_cost(current, matrix)

        for it in range(max_iter):
            total_iters += 1
            improved = False

            if variant == "stochastic":
                candidates = []
                for i in range(n - 1):
                    for j in range(i + 1, n):
                        new_tour = two_opt_swap(current, i, j)
                        c = tour_cost(new_tour, matrix)
                        if c < current_cost:
                            candidates.append((c, new_tour))
                if candidates:
                    c, new_tour = rng.choice(candidates)
                    current, current_cost = new_tour, c
                    improved = True
            else:
                best_neighbor = None
                best_nc = current_cost
                for i in range(n - 1):
                    for j in range(i + 1, n):
                        new_tour = two_opt_swap(current, i, j)
                        c = tour_cost(new_tour, matrix)
                        if c < best_nc:
                            best_nc = c
                            best_neighbor = new_tour
                if best_neighbor is not None:
                    current, current_cost = best_neighbor, best_nc
                    improved = True

            if current_cost < best_cost:
                best_cost = current_cost
                best_tour = current[:]
                history.append((total_iters, best_cost))

            if not improved:
                break

    return TSPResult(
        algorithm=f"HC-{variant}",
        tour=best_tour,
        cost=best_cost,
        elapsed=now() - t0,
        iterations=total_iters,
        history=history,
        params={
            "variant": variant,
            "restarts": restarts,
            "max_iter": max_iter,
            "init": init,
            "seed": seed,
        },
    )
