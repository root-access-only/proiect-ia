"""Backtracking with branch-and-bound pruning and configurable stop modes."""
from __future__ import annotations

import sys
from typing import Sequence

from .common import TSPResult, now


def solve_bkt(
    matrix: Sequence[Sequence[float]],
    mode: str = "toate",
    time_limit: float = 30.0,
    y_solutions: int = 100,
) -> TSPResult:
    """Solve TSP exactly with backtracking and four stop modes.

    Modes:
        ``"prima"`` - return as soon as the first complete tour is found.
        ``"toate"`` - explore the whole space with branch-and-bound (optimal).
        ``"timp"`` - stop after ``time_limit`` seconds, return best so far.
        ``"y_solutii"`` - stop after ``y_solutions`` complete tours have been
            found, return the best among them.

    Args:
        matrix: Symmetric distance matrix (NxN).
        mode: One of the strings above.
        time_limit: Used only when ``mode == "timp"``.
        y_solutions: Used only when ``mode == "y_solutii"``.

    Returns:
        A populated ``TSPResult``.
    """
    n = len(matrix)
    if n == 0:
        return TSPResult("BKT", [], 0.0, 0.0, 0, [], {"mode": mode})

    state = {
        "best_cost": sys.maxsize,
        "best_tour": [],
        "solutions": 0,
        "stop": False,
        "nodes": 0,
        "start": now(),
        "history": [],
    }

    visited = [False] * n
    visited[0] = True

    def _rec(current: int, tour: list[int], cost: float) -> None:
        if state["stop"]:
            return

        if mode == "timp" and (now() - state["start"]) >= time_limit:
            state["stop"] = True
            return

        if len(tour) == n:
            total = cost + matrix[current][tour[0]]
            state["solutions"] += 1
            if total < state["best_cost"]:
                state["best_cost"] = total
                state["best_tour"] = tour[:]
                state["history"].append((state["nodes"], total))
            if mode == "prima":
                state["stop"] = True
            elif mode == "y_solutii" and state["solutions"] >= y_solutions:
                state["stop"] = True
            return

        for nxt in range(n):
            if state["stop"]:
                return
            if visited[nxt]:
                continue
            new_cost = cost + matrix[current][nxt]
            if new_cost >= state["best_cost"]:
                continue
            visited[nxt] = True
            tour.append(nxt)
            state["nodes"] += 1
            _rec(nxt, tour, new_cost)
            tour.pop()
            visited[nxt] = False

    _rec(0, [0], 0.0)
    elapsed = now() - state["start"]

    return TSPResult(
        algorithm="BKT",
        tour=state["best_tour"] or [0],
        cost=float(state["best_cost"]) if state["best_tour"] else float("inf"),
        elapsed=elapsed,
        iterations=state["nodes"],
        history=state["history"],
        params={
            "mode": mode,
            "time_limit": time_limit,
            "y_solutions": y_solutions,
            "solutions_found": state["solutions"],
        },
    )
