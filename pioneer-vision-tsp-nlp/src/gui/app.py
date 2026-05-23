"""Main Tkinter application. Three tabs: Robot, TSP, NLP.

Run via the project root:
    python -m src.gui.app
"""
from __future__ import annotations

import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.gui.tabs.robot_tab import RobotTab
from src.gui.tabs.tsp_tab import TSPTab

try:
    from src.gui.tabs.nlp_tab import NLPTab
    _NLP_AVAILABLE = True
    _NLP_ERROR = None
except ImportError as _exc:
    NLPTab = None
    _NLP_AVAILABLE = False
    _NLP_ERROR = str(_exc)


def _configure_style(root: tk.Tk) -> None:
    style = ttk.Style(root)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    style.configure("TNotebook.Tab", padding=(20, 8), font=("Segoe UI", 10, "bold"))
    style.configure("TLabel", font=("Segoe UI", 10))
    style.configure("Header.TLabel", font=("Segoe UI", 13, "bold"), foreground="#114488")
    style.configure("Status.TLabel", font=("Consolas", 9), foreground="#445566")
    style.configure("TButton", padding=(10, 4))


class MainApp(tk.Tk):
    """Top-level Tk application."""

    def __init__(self):
        super().__init__()
        self.title("AI Lab Project - Pioneer P3-DX, TSP & NLP")
        self.geometry("1280x820")
        self.minsize(1100, 720)
        _configure_style(self)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.robot_tab = RobotTab(notebook)
        notebook.add(self.robot_tab, text="  Robot Pioneer + Vision  ")

        self.tsp_tab = TSPTab(notebook)
        notebook.add(self.tsp_tab, text="  TSP - BKT/NN/HC/SA/GA  ")

        if _NLP_AVAILABLE:
            self.nlp_tab = NLPTab(notebook)
            notebook.add(self.nlp_tab, text="  NLP - Text Classification  ")
        else:
            placeholder = ttk.Frame(notebook, padding=20)
            ttk.Label(
                placeholder,
                text=(
                    "NLP tab indisponibil - lipseste 'scikit-learn'.\n\n"
                    "Instaleaza:\n    pip install scikit-learn nltk\n\n"
                    f"Eroare originala:\n  {_NLP_ERROR}"
                ),
                font=("Segoe UI", 10),
                justify="left",
            ).pack(anchor="w")
            notebook.add(placeholder, text="  NLP (indisponibil)  ")
            self.nlp_tab = None

        status = ttk.Label(
            self,
            text="Proiect IA - simulare CoppeliaSim + OpenCV, algoritmi TSP, clasificare text NLP",
            style="Status.TLabel",
            anchor="w",
        )
        status.pack(fill="x", padx=10, pady=(0, 6))

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self) -> None:
        try:
            self.robot_tab.on_close()
        except Exception:
            pass
        self.destroy()


def main() -> None:
    app = MainApp()
    app.mainloop()


if __name__ == "__main__":
    main()
