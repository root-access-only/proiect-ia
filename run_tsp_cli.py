"""Headless TSP runner.

Useful for sanity checks and for screenshots in the report.

Examples:
    python run_tsp_cli.py --n 10 --seed 42
    python run_tsp_cli.py --file data/tsp/orase10.txt --bkt-mode toate
"""
from __future__ import annotations

import argparse
from pathlib import Path

from src.tsp import (
    generate_random_matrix,
    load_matrix,
    plot_convergence,
    plot_cost_time,
    run_all,
)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10, help="instance size (if no --file)")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--file", type=str, help="load matrix from text file")
    ap.add_argument("--bkt-mode", default="toate", choices=["toate", "prima", "timp", "y_solutii"])
    ap.add_argument("--bkt-time", type=float, default=15.0)
    ap.add_argument("--out", type=str, default="output")
    args = ap.parse_args()

    if args.file:
        n, matrix = load_matrix(args.file)
        print(f"Incarcat instanta {args.file} (N={n})")
    else:
        n = args.n
        matrix = generate_random_matrix(n, seed=args.seed)
        print(f"Generata instanta aleator N={n} seed={args.seed}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    results = run_all(matrix, bkt_mode=args.bkt_mode, bkt_time=args.bkt_time, seed=args.seed)
    print("\nRezultate:")
    for name, r in results.items():
        print(f"  {r.summary()}")

    conv = plot_convergence(results, out / "convergence.png")
    bars = plot_cost_time(results, out / "cost_time.png")
    print(f"\nGrafice scrise in: {conv}, {bars}")


if __name__ == "__main__":
    main()
