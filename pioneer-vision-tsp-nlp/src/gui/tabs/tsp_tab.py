"""TSP tab: configure an instance, run all 5 algorithms, view metrics + plots."""
from __future__ import annotations

import json
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import Dict, Optional

import matplotlib
matplotlib.use("Agg")  # off-screen rendering for embedding via PhotoImage
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image, ImageTk  # noqa: E402

from src.tsp import (
    generate_random_matrix,
    load_matrix,
    save_matrix,
    plot_convergence,
    plot_cost_time,
    run_all,
    scalability_experiment,
)

OUTPUT = Path(__file__).resolve().parents[3] / "output"
OUTPUT.mkdir(exist_ok=True, parents=True)
DATA_DIR = Path(__file__).resolve().parents[3] / "data" / "tsp"
DATA_DIR.mkdir(exist_ok=True, parents=True)


class TSPTab(ttk.Frame):
    """Tk tab for the five TSP algorithms."""

    def __init__(self, master):
        super().__init__(master, padding=12)
        self.matrix: Optional[list[list[int]]] = None
        self.matrix_path: Optional[Path] = None
        self.results: Dict[str, object] = {}
        self.preview_img = None
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="Travelling Salesman - BKT, NN, HC, SA, GA", style="Header.TLabel").pack(anchor="w")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=8)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 8))

        # Instance
        inst = ttk.LabelFrame(left, text="Instanta TSP", padding=8)
        inst.pack(fill="x", pady=(0, 8))
        self.n_var = tk.IntVar(value=10)
        self.seed_var = tk.IntVar(value=42)
        ttk.Label(inst, text="N orase:").grid(row=0, column=0, sticky="w")
        ttk.Entry(inst, textvariable=self.n_var, width=8).grid(row=0, column=1, sticky="w", padx=4)
        ttk.Label(inst, text="Seed:").grid(row=1, column=0, sticky="w")
        ttk.Entry(inst, textvariable=self.seed_var, width=8).grid(row=1, column=1, sticky="w", padx=4)
        ttk.Button(inst, text="Genereaza aleator", command=self.gen_matrix).grid(row=2, column=0, columnspan=2, sticky="we", pady=2)
        ttk.Button(inst, text="Incarca .txt", command=self.load_matrix).grid(row=3, column=0, columnspan=2, sticky="we", pady=2)
        ttk.Button(inst, text="Salveaza .txt", command=self.save_matrix).grid(row=4, column=0, columnspan=2, sticky="we", pady=2)

        # Algorithm params
        params = ttk.LabelFrame(left, text="Parametri algoritmi", padding=8)
        params.pack(fill="x", pady=(0, 8))

        self.bkt_mode_var = tk.StringVar(value="toate")
        ttk.Label(params, text="BKT mod:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(params, textvariable=self.bkt_mode_var, width=10,
                     values=["toate", "prima", "timp", "y_solutii"]).grid(row=0, column=1, sticky="w")
        self.bkt_time_var = tk.DoubleVar(value=15.0)
        ttk.Label(params, text="BKT timp(s):").grid(row=1, column=0, sticky="w")
        ttk.Entry(params, textvariable=self.bkt_time_var, width=8).grid(row=1, column=1, sticky="w")

        self.hc_restarts_var = tk.IntVar(value=5)
        ttk.Label(params, text="HC restarts:").grid(row=2, column=0, sticky="w")
        ttk.Entry(params, textvariable=self.hc_restarts_var, width=8).grid(row=2, column=1, sticky="w")

        self.sa_iter_var = tk.IntVar(value=20000)
        ttk.Label(params, text="SA iter:").grid(row=3, column=0, sticky="w")
        ttk.Entry(params, textvariable=self.sa_iter_var, width=8).grid(row=3, column=1, sticky="w")

        self.ga_pop_var = tk.IntVar(value=120)
        ttk.Label(params, text="GA pop:").grid(row=4, column=0, sticky="w")
        ttk.Entry(params, textvariable=self.ga_pop_var, width=8).grid(row=4, column=1, sticky="w")

        self.ga_gen_var = tk.IntVar(value=300)
        ttk.Label(params, text="GA gen:").grid(row=5, column=0, sticky="w")
        ttk.Entry(params, textvariable=self.ga_gen_var, width=8).grid(row=5, column=1, sticky="w")

        # Actions
        act = ttk.LabelFrame(left, text="Actiuni", padding=8)
        act.pack(fill="x")
        ttk.Button(act, text="Ruleaza toti algoritmii", command=self.run_all).pack(fill="x", pady=2)
        ttk.Button(act, text="Scalabilitate (N = 5..20)", command=self.run_scalability).pack(fill="x", pady=2)
        ttk.Button(act, text="Salveaza raport JSON", command=self.save_report).pack(fill="x", pady=2)

        # Right: results + image preview
        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        # Table
        cols = ("algorithm", "cost", "time_s", "iters")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=8)
        for c, w in zip(cols, (200, 100, 100, 100)):
            self.tree.heading(c, text=c)
            self.tree.column(c, width=w, anchor="center")
        self.tree.grid(row=0, column=0, sticky="we")

        # Plot preview
        preview = ttk.LabelFrame(right, text="Vizualizare", padding=8)
        preview.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.preview_label = ttk.Label(preview, text="(ruleaza algoritmii pentru a vedea graficele)")
        self.preview_label.pack(fill="both", expand=True)

        # Plot picker
        picker = ttk.Frame(preview)
        picker.pack(fill="x")
        ttk.Button(picker, text="Convergenta", command=lambda: self._show_image("convergence.png")).pack(side="left", padx=4)
        ttk.Button(picker, text="Cost vs timp", command=lambda: self._show_image("cost_time.png")).pack(side="left", padx=4)
        ttk.Button(picker, text="Scalabilitate", command=lambda: self._show_image("scalability.png")).pack(side="left", padx=4)

    # ------------------------------------------------------------------
    def gen_matrix(self) -> None:
        n = max(2, int(self.n_var.get()))
        seed = int(self.seed_var.get())
        self.matrix = generate_random_matrix(n, seed=seed)
        self.matrix_path = None
        messagebox.showinfo("TSP", f"Matrice {n}x{n} generata (seed={seed}).")

    def load_matrix(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("All", "*.*")],
                                          initialdir=str(DATA_DIR))
        if not path:
            return
        n, mat = load_matrix(path)
        self.matrix = mat
        self.matrix_path = Path(path)
        self.n_var.set(n)
        messagebox.showinfo("TSP", f"Incarcat {n}x{n} din {Path(path).name}.")

    def save_matrix(self) -> None:
        if self.matrix is None:
            messagebox.showwarning("TSP", "Genereaza/incarca o matrice mai intai.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialdir=str(DATA_DIR))
        if not path:
            return
        save_matrix(self.matrix, path)
        self.matrix_path = Path(path)
        messagebox.showinfo("TSP", f"Salvat in {path}")

    def run_all(self) -> None:
        if self.matrix is None:
            self.gen_matrix()
        params = dict(
            bkt_mode=self.bkt_mode_var.get(),
            bkt_time=float(self.bkt_time_var.get()),
            hc_restarts=int(self.hc_restarts_var.get()),
            sa_iters=int(self.sa_iter_var.get()),
            ga_population=int(self.ga_pop_var.get()),
            ga_generations=int(self.ga_gen_var.get()),
            seed=int(self.seed_var.get()),
        )

        def worker():
            try:
                results = run_all(self.matrix, **params)
                plot_convergence(results, OUTPUT / "convergence.png")
                plot_cost_time(results, OUTPUT / "cost_time.png")
                self.after(0, lambda: self._on_results(results))
            except Exception as exc:
                self.after(0, lambda e=exc: messagebox.showerror("TSP", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def run_scalability(self) -> None:
        def worker():
            try:
                scalability_experiment(out_dir=OUTPUT)
                self.after(0, lambda: self._show_image("scalability.png"))
            except Exception as exc:
                self.after(0, lambda e=exc: messagebox.showerror("TSP", str(e)))
        threading.Thread(target=worker, daemon=True).start()

    def save_report(self) -> None:
        if not self.results:
            messagebox.showwarning("TSP", "Nu sunt rezultate de salvat.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".json")
        if not path:
            return
        payload = {
            name: {
                "cost": r.cost, "time_s": r.elapsed, "iterations": r.iterations,
                "tour": r.tour, "params": r.params,
            }
            for name, r in self.results.items()
        }
        Path(path).write_text(json.dumps(payload, indent=2))

    def _on_results(self, results) -> None:
        self.results = results
        for row in self.tree.get_children():
            self.tree.delete(row)
        for name, r in results.items():
            self.tree.insert("", "end", values=(name, f"{r.cost:.2f}", f"{r.elapsed:.4f}", r.iterations))
        self._show_image("convergence.png")

    def _show_image(self, name: str) -> None:
        path = OUTPUT / name
        if not path.exists():
            messagebox.showinfo("TSP", f"Fisierul {name} nu exista inca. Ruleaza experimentul.")
            return
        pil = Image.open(path)
        pil.thumbnail((860, 520))
        self.preview_img = ImageTk.PhotoImage(pil)
        self.preview_label.configure(image=self.preview_img, text="")
