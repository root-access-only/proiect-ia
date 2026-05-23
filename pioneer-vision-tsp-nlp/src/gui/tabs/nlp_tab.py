"""NLP tab: configure dataset + classifier + vectorizer, train, predict, plot."""
from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List

import matplotlib
matplotlib.use("Agg")
from PIL import Image, ImageTk

from src.nlp import NLPConfig, NLPRunner, list_datasets
from src.nlp.plots import plot_confusion, plot_classifier_comparison

OUTPUT = Path(__file__).resolve().parents[3] / "output"
OUTPUT.mkdir(exist_ok=True, parents=True)


class NLPTab(ttk.Frame):
    """Tk tab driving the text classification pipeline."""

    def __init__(self, master):
        super().__init__(master, padding=12)
        self.last_results = []
        self.last_image = None
        self._build()

    def _build(self) -> None:
        ttk.Label(self, text="NLP - clasificare de texte (3 dataset-uri Engleza)", style="Header.TLabel").pack(anchor="w")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=8)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left = ttk.Frame(body)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 8))

        # Dataset + classifier
        cfg = ttk.LabelFrame(left, text="Configurare", padding=8)
        cfg.pack(fill="x", pady=(0, 8))

        self.dataset_var = tk.StringVar(value="20newsgroups")
        ttk.Label(cfg, text="Dataset:").grid(row=0, column=0, sticky="w")
        ttk.Combobox(cfg, textvariable=self.dataset_var,
                     values=[d.name for d in list_datasets()], width=18).grid(row=0, column=1, sticky="we")

        self.classifier_var = tk.StringVar(value="logreg")
        ttk.Label(cfg, text="Classifier:").grid(row=1, column=0, sticky="w")
        ttk.Combobox(cfg, textvariable=self.classifier_var,
                     values=["nb", "svm", "logreg", "rf"], width=18).grid(row=1, column=1, sticky="we")

        self.vec_var = tk.StringVar(value="tfidf")
        ttk.Label(cfg, text="Vectorizer:").grid(row=2, column=0, sticky="w")
        ttk.Combobox(cfg, textvariable=self.vec_var,
                     values=["tfidf", "bow"], width=18).grid(row=2, column=1, sticky="we")

        self.ngram_min_var = tk.IntVar(value=1)
        self.ngram_max_var = tk.IntVar(value=2)
        ttk.Label(cfg, text="ngram_range:").grid(row=3, column=0, sticky="w")
        ngf = ttk.Frame(cfg); ngf.grid(row=3, column=1, sticky="we")
        ttk.Entry(ngf, textvariable=self.ngram_min_var, width=4).pack(side="left")
        ttk.Label(ngf, text=" - ").pack(side="left")
        ttk.Entry(ngf, textvariable=self.ngram_max_var, width=4).pack(side="left")

        self.max_features_var = tk.IntVar(value=20000)
        ttk.Label(cfg, text="max_features:").grid(row=4, column=0, sticky="w")
        ttk.Entry(cfg, textvariable=self.max_features_var, width=10).grid(row=4, column=1, sticky="w")

        self.sample_var = tk.IntVar(value=5000)
        ttk.Label(cfg, text="sample size:").grid(row=5, column=0, sticky="w")
        ttk.Entry(cfg, textvariable=self.sample_var, width=10).grid(row=5, column=1, sticky="w")

        self.test_var = tk.DoubleVar(value=0.2)
        ttk.Label(cfg, text="test fraction:").grid(row=6, column=0, sticky="w")
        ttk.Entry(cfg, textvariable=self.test_var, width=10).grid(row=6, column=1, sticky="w")

        self.stopwords_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(cfg, text="Stop words (English)", variable=self.stopwords_var).grid(row=7, column=0, columnspan=2, sticky="w")
        self.sublinear_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(cfg, text="sublinear_tf", variable=self.sublinear_var).grid(row=8, column=0, columnspan=2, sticky="w")

        cfg.columnconfigure(1, weight=1)

        # Actions
        act = ttk.LabelFrame(left, text="Actiuni", padding=8)
        act.pack(fill="x", pady=(0, 8))
        ttk.Button(act, text="Antreneaza & evalueaza", command=self.train_eval).pack(fill="x", pady=2)
        ttk.Button(act, text="Compara 4 clasificatori", command=self.compare_classifiers).pack(fill="x", pady=2)
        ttk.Button(act, text="Salveaza raport", command=self.save_report).pack(fill="x", pady=2)

        # Predict
        pred = ttk.LabelFrame(left, text="Predictie text liber", padding=8)
        pred.pack(fill="both", expand=True)
        self.text_in = tk.Text(pred, height=6, width=34)
        self.text_in.pack(fill="x")
        ttk.Button(pred, text="Classify", command=self.predict_text).pack(fill="x", pady=2)
        self.pred_var = tk.StringVar(value="(predictie aici)")
        ttk.Label(pred, textvariable=self.pred_var, wraplength=260, foreground="#0066aa").pack(fill="x")

        # Right: results pane
        right = ttk.Frame(body)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=2)
        right.rowconfigure(1, weight=3)
        right.columnconfigure(0, weight=1)

        report_frame = ttk.LabelFrame(right, text="Raport clasificare", padding=8)
        report_frame.grid(row=0, column=0, sticky="nsew")
        self.report = tk.Text(report_frame, font=("Consolas", 9))
        self.report.pack(fill="both", expand=True)

        plot_frame = ttk.LabelFrame(right, text="Vizualizari", padding=8)
        plot_frame.grid(row=1, column=0, sticky="nsew", pady=(8, 0))
        self.plot_label = ttk.Label(plot_frame, text="(ruleaza experimentul pentru a vedea graficele)")
        self.plot_label.pack(fill="both", expand=True)
        picker = ttk.Frame(plot_frame)
        picker.pack(fill="x")
        ttk.Button(picker, text="Confusion matrix", command=lambda: self._show("nlp_confusion.png")).pack(side="left", padx=4)
        ttk.Button(picker, text="Comparare clasificatori", command=lambda: self._show("nlp_compare.png")).pack(side="left", padx=4)

    # ------------------------------------------------------------------
    def _gather_cfg(self) -> NLPConfig:
        return NLPConfig(
            dataset=self.dataset_var.get(),
            classifier=self.classifier_var.get(),
            vectorizer=self.vec_var.get(),
            ngram_min=int(self.ngram_min_var.get()),
            ngram_max=int(self.ngram_max_var.get()),
            max_features=int(self.max_features_var.get()) or None,
            sample=int(self.sample_var.get()) or None,
            test_size=float(self.test_var.get()),
            stop_words="english" if self.stopwords_var.get() else None,
            sublinear_tf=bool(self.sublinear_var.get()),
        )

    def train_eval(self) -> None:
        cfg = self._gather_cfg()
        self._set_busy("Antrenez modelul, asteapta...")

        def worker():
            try:
                runner = NLPRunner(cfg)
                result = runner.run(progress_cb=lambda m: self.after(0, lambda mm=m: self._set_busy(mm)))
                plot_confusion(result, OUTPUT / "nlp_confusion.png")
                self.after(0, lambda r=result: self._on_result(r))
            except Exception as exc:
                self.after(0, lambda e=exc: messagebox.showerror("NLP", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def compare_classifiers(self) -> None:
        base = self._gather_cfg()
        classifiers = ["nb", "svm", "logreg", "rf"]
        self._set_busy("Compar 4 clasificatori...")

        def worker():
            try:
                results = []
                for clf in classifiers:
                    cfg = NLPConfig(**{**base.__dict__, "classifier": clf})
                    self.after(0, lambda c=clf: self._set_busy(f"Antrenez {c}..."))
                    runner = NLPRunner(cfg)
                    res = runner.run()
                    results.append(res)
                plot_classifier_comparison(results, OUTPUT / "nlp_compare.png")
                self.last_results = results
                self.after(0, lambda: self._show("nlp_compare.png"))
                self.after(0, lambda r=results: self._on_compare(r))
            except Exception as exc:
                self.after(0, lambda e=exc: messagebox.showerror("NLP", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def predict_text(self) -> None:
        text = self.text_in.get("1.0", "end").strip()
        if not text:
            return
        cfg = self._gather_cfg()
        self._set_busy("Antrenez & prezic...")

        def worker():
            try:
                runner = NLPRunner(cfg)
                pred = runner.predict(text)
                label = pred["labels"][0]
                self.after(0, lambda l=label: self.pred_var.set(f"Predictie: {l}"))
                self.after(0, lambda: self._set_busy("OK"))
            except Exception as exc:
                self.after(0, lambda e=exc: messagebox.showerror("NLP", str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def save_report(self) -> None:
        text = self.report.get("1.0", "end")
        if not text.strip():
            messagebox.showwarning("NLP", "Nu exista raport de salvat.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt")
        if not path:
            return
        Path(path).write_text(text, encoding="utf-8")

    def _on_result(self, result) -> None:
        self.report.delete("1.0", "end")
        self.report.insert("end", f"Dataset:     {result.config.dataset}\n")
        self.report.insert("end", f"Classifier:  {result.config.classifier}\n")
        self.report.insert("end", f"Vectorizer:  {result.config.vectorizer} (ngram {result.config.ngram_min}-{result.config.ngram_max})\n")
        self.report.insert("end", f"Train docs:  {result.n_train}\n")
        self.report.insert("end", f"Test docs:   {result.n_test}\n\n")
        self.report.insert("end", f"Accuracy:    {result.accuracy:.4f}\n")
        self.report.insert("end", f"Precision:   {result.precision:.4f}\n")
        self.report.insert("end", f"Recall:      {result.recall:.4f}\n")
        self.report.insert("end", f"F1 macro:    {result.f1:.4f}\n")
        self.report.insert("end", f"Train time:  {result.elapsed_train:.3f}s\n")
        self.report.insert("end", f"Eval time:   {result.elapsed_eval:.3f}s\n\n")
        self.report.insert("end", result.report)
        self._show("nlp_confusion.png")
        self._set_busy("Gata")

    def _on_compare(self, results) -> None:
        self.report.delete("1.0", "end")
        self.report.insert("end", "Comparare clasificatori\n" + "=" * 40 + "\n")
        for r in results:
            self.report.insert(
                "end",
                f"{r.config.classifier:6s}  acc={r.accuracy:.4f}  "
                f"P={r.precision:.3f}  R={r.recall:.3f}  F1={r.f1:.3f}  "
                f"train={r.elapsed_train:.2f}s\n"
            )

    def _show(self, name: str) -> None:
        path = OUTPUT / name
        if not path.exists():
            return
        pil = Image.open(path)
        pil.thumbnail((860, 460))
        self.last_image = ImageTk.PhotoImage(pil)
        self.plot_label.configure(image=self.last_image, text="")

    def _set_busy(self, message: str) -> None:
        self.report.delete("1.0", "1.end")
        self.report.insert("1.0", f"[status] {message}\n")
