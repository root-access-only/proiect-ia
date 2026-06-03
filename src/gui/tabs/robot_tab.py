"""Robot + Vision tab.

Left panel: connection config, parameter sliders, status + event log.
Right panel: live camera frame (annotated by the detector).
"""
from __future__ import annotations

import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

import numpy as np

try:
    import cv2
    from PIL import Image, ImageTk
except Exception:  # pragma: no cover - import guards for environments w/o CV
    cv2 = None
    Image = ImageTk = None

from src.robot import (
    CoppeliaSimDriver,
    SimulatorError,
    NavigationConfig,
    NavigationController,
    NavigationEvent,
    NavigationState,
    TrafficVision,
)


class RobotTab(ttk.Frame):
    """Tk tab that exposes the robot navigation controller live."""

    def __init__(self, master):
        super().__init__(master, padding=12)
        self.driver: Optional[CoppeliaSimDriver] = None
        self.controller: Optional[NavigationController] = None
        self.thread: Optional[threading.Thread] = None
        self.cfg = NavigationConfig()
        self._frame_lock = threading.Lock()
        self._latest_frame_img: Optional[ImageTk.PhotoImage] = None

        self._build()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build(self) -> None:
        ttk.Label(self, text="Pioneer P3-DX - Navigatie cu OpenCV", style="Header.TLabel").pack(anchor="w")

        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, pady=8)
        body.columnconfigure(0, weight=0)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        # Left controls
        controls = ttk.LabelFrame(body, text="Configurare & control", padding=10)
        controls.grid(row=0, column=0, sticky="nsw", padx=(0, 8))

        # CoppeliaSim connection
        conn = ttk.LabelFrame(controls, text="Conexiune CoppeliaSim", padding=8)
        conn.pack(fill="x", pady=(0, 8))

        self.host_var = tk.StringVar(value="localhost")
        self.port_var = tk.StringVar(value="23000")
        ttk.Label(conn, text="Host:").grid(row=0, column=0, sticky="w")
        ttk.Entry(conn, textvariable=self.host_var, width=16).grid(row=0, column=1, sticky="we", padx=4)
        ttk.Label(conn, text="Port:").grid(row=1, column=0, sticky="w")
        ttk.Entry(conn, textvariable=self.port_var, width=16).grid(row=1, column=1, sticky="we", padx=4)
        conn.columnconfigure(1, weight=1)

        # Parameter knobs
        params = ttk.LabelFrame(controls, text="Parametri navigatie", padding=8)
        params.pack(fill="x", pady=(0, 8))

        self.v_cruise_var = tk.DoubleVar(value=self.cfg.v_cruise)
        self.v_slow_var = tk.DoubleVar(value=self.cfg.v_slow)
        self.v_max_var = tk.DoubleVar(value=self.cfg.v_max)
        self.stop_pause_var = tk.DoubleVar(value=self.cfg.stop_pause_s)
        self.emerg_var = tk.DoubleVar(value=self.cfg.emergency_distance)
        self.avoid_var = tk.DoubleVar(value=self.cfg.avoid_distance)
        self.gain_var = tk.DoubleVar(value=self.cfg.braitenberg_gain)
        self.min_conf_var = tk.DoubleVar(value=self.cfg.sign_min_conf)
        self.min_area_var = tk.IntVar(value=self.cfg.detection_min_area)

        for row, (label, var, frm, to, res) in enumerate([
            ("v_cruise (rad/s)", self.v_cruise_var, 0.2, 4.0, 0.1),
            ("v_slow (rad/s)", self.v_slow_var, 0.1, 3.0, 0.1),
            ("v_max (rad/s)", self.v_max_var, 1.0, 8.0, 0.1),
            ("stop pauza (s)", self.stop_pause_var, 0.5, 6.0, 0.1),
            ("emergency dist (m)", self.emerg_var, 0.1, 1.0, 0.05),
            ("avoid dist (m)", self.avoid_var, 0.2, 1.5, 0.05),
            ("Braitenberg gain", self.gain_var, 0.5, 10.0, 0.1),
            ("Min confidence", self.min_conf_var, 0.1, 0.95, 0.05),
        ]):
            ttk.Label(params, text=label).grid(row=row, column=0, sticky="w")
            s = ttk.Scale(params, from_=frm, to=to, variable=var, orient="horizontal", length=180)
            s.grid(row=row, column=1, sticky="we", padx=4)
            ttk.Label(params, textvariable=var, width=6).grid(row=row, column=2, sticky="w")
        params.columnconfigure(1, weight=1)

        ttk.Label(params, text="Min area det. (px):").grid(row=99, column=0, sticky="w")
        ttk.Entry(params, textvariable=self.min_area_var, width=8).grid(row=99, column=1, sticky="w")

        # Buttons
        actions = ttk.Frame(controls)
        actions.pack(fill="x", pady=8)
        self.btn_connect = ttk.Button(actions, text="Conecteaza", command=self.connect)
        self.btn_connect.grid(row=0, column=0, padx=2, pady=2, sticky="we")
        self.btn_start = ttk.Button(actions, text="Start navigatie", command=self.start_nav, state="disabled")
        self.btn_start.grid(row=0, column=1, padx=2, pady=2, sticky="we")
        self.btn_stop = ttk.Button(actions, text="Stop navigatie", command=self.stop_nav, state="disabled")
        self.btn_stop.grid(row=1, column=0, padx=2, pady=2, sticky="we")
        self.btn_dump = ttk.Button(actions, text="Salveaza cadru", command=self.save_frame, state="disabled")
        self.btn_dump.grid(row=1, column=1, padx=2, pady=2, sticky="we")
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)

        ttk.Button(controls, text="Genereaza texturi semne", command=self.generate_signs).pack(fill="x", pady=(0, 6))

        # Status + event log
        status = ttk.LabelFrame(controls, text="Stare & evenimente", padding=8)
        status.pack(fill="both", expand=True)

        self.state_var = tk.StringVar(value=NavigationState.IDLE.value)
        ttk.Label(status, text="Stare curenta:").grid(row=0, column=0, sticky="w")
        ttk.Label(status, textvariable=self.state_var, font=("Segoe UI", 10, "bold"),
                  foreground="#0066aa").grid(row=0, column=1, sticky="w")

        self.detect_var = tk.StringVar(value="-")
        ttk.Label(status, text="Detectii curente:").grid(row=1, column=0, sticky="w")
        ttk.Label(status, textvariable=self.detect_var, wraplength=240).grid(row=1, column=1, sticky="w")

        self.log = tk.Text(status, height=14, width=44, font=("Consolas", 9))
        self.log.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=4)
        status.rowconfigure(2, weight=1)
        status.columnconfigure(1, weight=1)

        # Right: camera view
        right = ttk.LabelFrame(body, text="Camera robot + detectii", padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        self.camera_label = ttk.Label(right, text="(camera offline)\nConecteaza-te la CoppeliaSim si porneste simularea.")
        self.camera_label.pack(fill="both", expand=True, padx=8, pady=8)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------
    def connect(self) -> None:
        try:
            self.driver = CoppeliaSimDriver(
                host=self.host_var.get(),
                port=int(self.port_var.get()),
            )
        except SimulatorError as exc:
            messagebox.showerror("CoppeliaSim", str(exc))
            return
        except Exception as exc:
            messagebox.showerror("CoppeliaSim", f"Eroare conexiune: {exc}")
            return

        self.btn_start.configure(state="normal")
        self.btn_dump.configure(state="normal")
        self._append_log("[OK] conectat la CoppeliaSim")

    def _gather_cfg(self) -> NavigationConfig:
        return NavigationConfig(
            v_cruise=float(self.v_cruise_var.get()),
            v_slow=float(self.v_slow_var.get()),
            v_max=float(self.v_max_var.get()),
            stop_pause_s=float(self.stop_pause_var.get()),
            yield_pause_s=max(0.5, float(self.stop_pause_var.get()) * 0.5),
            emergency_distance=float(self.emerg_var.get()),
            avoid_distance=float(self.avoid_var.get()),
            braitenberg_gain=float(self.gain_var.get()),
            sign_min_conf=float(self.min_conf_var.get()),
            detection_min_area=int(self.min_area_var.get()),
        )

    def start_nav(self) -> None:
        if self.driver is None or self.thread and self.thread.is_alive():
            return
        cfg = self._gather_cfg()
        vision = TrafficVision(
            min_area=cfg.detection_min_area,
            max_area_ratio=cfg.detection_max_area_ratio,
            debug=True,
        )
        try:
            self.driver.start()
        except SimulatorError as exc:
            messagebox.showerror("CoppeliaSim", str(exc))
            return
        self.controller = NavigationController(
            self.driver, vision=vision, cfg=cfg,
            on_event=self._on_event, on_frame=self._on_frame,
        )
        self.thread = threading.Thread(target=self.controller.run, daemon=True)
        self.thread.start()
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self._append_log("[RUN] navigatie pornita")

    def stop_nav(self) -> None:
        if self.controller:
            self.controller.stop()
        if self.driver:
            try:
                self.driver.stop()
            except Exception:
                pass
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self._append_log("[STOP] navigatie oprita")

    def save_frame(self) -> None:
        if self.driver is None:
            return
        rgb = self.driver.grab_image()
        if rgb is None:
            messagebox.showwarning("Camera", "Nu s-a putut captura cadrul. Verifica vision sensor in scena.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
        if not path:
            return
        if cv2 is None:
            from PIL import Image as PILImage
            PILImage.fromarray(rgb).save(path)
        else:
            cv2.imwrite(path, cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR))
        self._append_log(f"[FRAME] salvat: {path}")

    def generate_signs(self) -> None:
        from src.robot import sign_generator
        paths = sign_generator.generate_all()
        self._append_log(f"[SIGNS] generate {len(paths)} texturi in data/signs/")
        messagebox.showinfo("Texturi semne",
                            f"S-au generat {len(paths)} fisiere PNG in data/signs/.\n"
                            "Importa-le pe forme tip Cuboid in CoppeliaSim (Texture -> Load).")

    # ------------------------------------------------------------------
    # Callbacks (run in worker thread - schedule onto Tk thread)
    # ------------------------------------------------------------------
    def _on_event(self, ev: NavigationEvent) -> None:
        ts = time.strftime("%H:%M:%S", time.localtime(ev.timestamp))
        line = f"{ts} [{ev.state.value}] {ev.text}\n"
        self.after(0, lambda: self._on_event_main(ev, line))

    def _on_event_main(self, ev: NavigationEvent, line: str) -> None:
        self.state_var.set(ev.state.value)
        self.detect_var.set(", ".join(ev.detections) if ev.detections else "-")
        self._append_log(line.rstrip())

    def _on_frame(self, frame_bgr: np.ndarray | None, detections) -> None:
        if frame_bgr is None or ImageTk is None:
            return
        with self._frame_lock:
            rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb)
            pil = pil.resize((640, 480))
            self.after(0, lambda p=pil: self._update_camera(p))

    def _update_camera(self, pil_image) -> None:
        self._latest_frame_img = ImageTk.PhotoImage(pil_image)
        self.camera_label.configure(image=self._latest_frame_img, text="")

    def _append_log(self, msg: str) -> None:
        self.log.insert("end", msg + "\n")
        self.log.see("end")
        if int(self.log.index("end-1c").split(".")[0]) > 500:
            self.log.delete("1.0", "200.0")

    def on_close(self) -> None:
        try:
            self.stop_nav()
        except Exception:
            pass
