"""Side-by-side runner for the five TSP algorithms with plotting helpers."""
from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np

from .common import TSPResult, generate_random_matrix
from .bkt import solve_bkt
from .nn import solve_nn_multistart
from .hc import solve_hc
from .sa import solve_sa
from .ga import solve_ga


ALGO_COLORS = {
    "BKT": "#1f77b4",
    "NN-multi": "#ff7f0e",
    "HC-steepest": "#2ca02c",
    "HC-random_restart": "#17becf",
    "SA": "#d62728",
    "GA": "#9467bd",
}


def run_all(
    matrix: Sequence[Sequence[float]],
    bkt_mode: str = "toate",
    bkt_time: float = 15.0,
    hc_restarts: int = 5,
    sa_iters: int = 20_000,
    ga_generations: int = 200,
    ga_population: int = 100,
    seed: int = 42,
) -> dict[str, TSPResult]:
    """Run every algorithm on the same matrix and return a name -> result map."""
    n = len(matrix)
    out: dict[str, TSPResult] = {}

    if n <= 13 or bkt_mode != "toate":
        out["BKT"] = solve_bkt(matrix, mode=bkt_mode, time_limit=bkt_time)
    out["NN-multi"] = solve_nn_multistart(matrix)
    out["HC-steepest"] = solve_hc(matrix, variant="steepest", seed=seed)
    out["HC-random_restart"] = solve_hc(
        matrix, variant="random_restart", restarts=hc_restarts, seed=seed
    )
    out["SA"] = solve_sa(matrix, iterations=sa_iters, seed=seed)
    out["GA"] = solve_ga(
        matrix,
        population_size=ga_population,
        generations=ga_generations,
        seed=seed,
    )
    return out


def plot_convergence(results: dict[str, TSPResult], out_path: str | Path) -> Path:
    """Plot each algorithm's best-cost history on a single figure."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for name, res in results.items():
        if not res.history:
            continue
        xs = [h[0] for h in res.history]
        ys = [h[1] for h in res.history]
        ax.plot(xs, ys, marker="o", markersize=3, label=f"{name} (cost={res.cost:.1f})",
                color=ALGO_COLORS.get(name))
    ax.set_xlabel("Iteration / step")
    ax.set_ylabel("Best cost so far")
    ax.set_title("TSP - convergence by algorithm")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()
    out_path = Path(out_path)
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    return out_path


def plot_cost_time(results: dict[str, TSPResult], out_path: str | Path) -> Path:
    """Plot final cost (bars) and elapsed time (line) per algorithm."""
    names = list(results.keys())
    costs = [results[n].cost for n in names]
    times = [results[n].elapsed for n in names]

    fig, ax1 = plt.subplots(figsize=(10, 6))
    colors = [ALGO_COLORS.get(n, "#888") for n in names]
    bars = ax1.bar(names, costs, color=colors, alpha=0.75)
    ax1.set_ylabel("Final cost (lower is better)")
    ax1.set_xlabel("Algorithm")
    ax1.set_title("TSP - cost vs time per algorithm")
    for bar, c in zip(bars, costs):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f"{c:.1f}", ha="center", va="bottom", fontsize=9)

    ax2 = ax1.twinx()
    ax2.plot(names, times, color="black", marker="D", linewidth=2,
             label="Elapsed time (s)")
    ax2.set_ylabel("Time (s)")
    ax2.legend(loc="upper right")
    fig.tight_layout()
    out_path = Path(out_path)
    fig.savefig(out_path, dpi=110)
    plt.close(fig)
    return out_path


def scalability_experiment(
    sizes: Sequence[int] = (5, 8, 10, 12, 15, 20),
    bkt_limit: int = 13,
    seed: int = 42,
    out_dir: str | Path = "output",
) -> dict[str, list[tuple[int, float, float]]]:
    """Run NN, HC, SA, GA over multiple instance sizes; BKT only up to ``bkt_limit``.

    Returns:
        Mapping ``algorithm -> [(N, cost, elapsed), ...]``.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True, parents=True)

    data: dict[str, list[tuple[int, float, float]]] = {
        "BKT": [], "NN-multi": [], "HC-steepest": [], "SA": [], "GA": []
    }

    for n in sizes:
        matrix = generate_random_matrix(n, seed=seed + n)
        if n <= bkt_limit:
            r = solve_bkt(matrix, mode="toate", time_limit=30.0)
            data["BKT"].append((n, r.cost, r.elapsed))
        r = solve_nn_multistart(matrix); data["NN-multi"].append((n, r.cost, r.elapsed))
        r = solve_hc(matrix, variant="steepest", seed=seed); data["HC-steepest"].append((n, r.cost, r.elapsed))
        r = solve_sa(matrix, iterations=max(5000, 1000 * n), seed=seed); data["SA"].append((n, r.cost, r.elapsed))
        r = solve_ga(matrix, generations=max(100, 10 * n), seed=seed); data["GA"].append((n, r.cost, r.elapsed))

    # Plot
    fig, (ax_t, ax_c) = plt.subplots(1, 2, figsize=(14, 5))
    for name, series in data.items():
        if not series:
            continue
        xs = [s[0] for s in series]
        costs = [s[1] for s in series]
        times = [s[2] for s in series]
        color = ALGO_COLORS.get(name)
        ax_t.semilogy(xs, times, marker="o", label=name, color=color)
        ax_c.plot(xs, costs, marker="o", label=name, color=color)
    ax_t.set_xlabel("N (cities)"); ax_t.set_ylabel("Time (s, log)")
    ax_t.set_title("Scalability - runtime"); ax_t.grid(True, which="both", alpha=0.3); ax_t.legend()
    ax_c.set_xlabel("N (cities)"); ax_c.set_ylabel("Final cost")
    ax_c.set_title("Scalability - solution quality"); ax_c.grid(True, alpha=0.3); ax_c.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "scalability.png", dpi=110)
    plt.close(fig)
    return data
