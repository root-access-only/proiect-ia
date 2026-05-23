"""High-level navigation controller for the Pioneer P3-DX.

Combines:
  * **Reactive obstacle avoidance** (Braitenberg + emergency stop using sonars).
  * **Vision-based traffic-rule compliance** (stop, yield, speed limit, lights).
  * A small **finite-state machine** so the robot can resume cruising after the
    rule that triggered it is no longer in force.

The controller is intentionally synchronous and tick-based; it is meant to be
driven from a worker thread by the Tk GUI which polls events at ~10-20 Hz.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np

from .simulator import CoppeliaSimDriver, SimulatorError
from .vision import Detection, TrafficVision


class NavigationState(str, Enum):
    """High-level FSM states."""

    IDLE = "idle"
    CRUISE = "cruise"
    SLOW = "slow"
    STOPPED_AT_SIGN = "stopped_at_sign"
    WAIT_FOR_GREEN = "wait_for_green"
    AVOIDING = "avoiding"
    EMERGENCY_STOP = "emergency_stop"
    TURNING_LEFT = "turning_left"
    TURNING_RIGHT = "turning_right"


@dataclass
class NavigationEvent:
    """One-line journal entry for the GUI to display."""

    timestamp: float
    text: str
    state: NavigationState
    detections: List[str] = field(default_factory=list)


@dataclass
class NavigationConfig:
    """All knobs in one place so the GUI can expose them as sliders/entries."""

    v_cruise: float = 2.0
    v_slow: float = 0.8
    v_max: float = 4.0
    stop_pause_s: float = 2.5
    yield_pause_s: float = 1.2
    speed_limits: Dict[str, float] = field(
        default_factory=lambda: {
            "speed_limit_30": 1.0,
            "speed_limit_50": 1.6,
            "speed_limit_80": 2.4,
        }
    )
    emergency_distance: float = 0.35
    avoid_distance: float = 0.55
    braitenberg_gain: float = 4.0
    turn_duration_s: float = 1.6
    turn_speed: float = 1.8
    detection_min_area: int = 600
    detection_max_area_ratio: float = 0.5
    sign_min_conf: float = 0.55
    front_sonars: Tuple[int, ...] = (2, 3, 4, 5)
    left_sonars: Tuple[int, ...] = (0, 1)
    right_sonars: Tuple[int, ...] = (6, 7)
    tick_period: float = 0.08


class NavigationController:
    """Drive a Pioneer P3-DX based on sonar + camera signals.

    Args:
        driver: A connected :class:`CoppeliaSimDriver`.
        vision: Configured :class:`TrafficVision` instance.
        cfg: Navigation configuration.
        on_event: Optional callback ``fn(event: NavigationEvent)`` invoked
            whenever the controller changes state or detects something.
        on_frame: Optional callback ``fn(annotated_bgr_image)`` invoked once
            per tick with the (possibly None) latest camera frame.
    """

    def __init__(
        self,
        driver: CoppeliaSimDriver,
        vision: TrafficVision | None = None,
        cfg: NavigationConfig | None = None,
        on_event: Optional[Callable[[NavigationEvent], None]] = None,
        on_frame: Optional[Callable[[np.ndarray | None, List[Detection]], None]] = None,
    ):
        self.driver = driver
        self.cfg = cfg or NavigationConfig()
        self.vision = vision or TrafficVision(
            min_area=self.cfg.detection_min_area,
            max_area_ratio=self.cfg.detection_max_area_ratio,
        )
        self.on_event = on_event
        self.on_frame = on_frame

        self.state = NavigationState.IDLE
        self.target_speed = self.cfg.v_cruise
        self._stopped_until = 0.0
        self._stop_sign_consumed: set[Tuple[int, int]] = set()
        self._turn_until = 0.0
        self._mandatory_consumed: set[Tuple[int, int]] = set()
        self._running = False
        self._events: List[NavigationEvent] = []
        self.last_detections: List[Detection] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run(self) -> None:
        """Blocking control loop. Call ``stop()`` from another thread to exit."""
        self._running = True
        self._emit("Navigation started", NavigationState.CRUISE)
        self.state = NavigationState.CRUISE
        try:
            while self._running:
                self.step()
                time.sleep(self.cfg.tick_period)
        finally:
            self.driver.set_velocity(0.0, 0.0)
            self._emit("Navigation stopped", NavigationState.IDLE)

    def stop(self) -> None:
        """Request the control loop to exit at the next tick."""
        self._running = False

    def step(self) -> None:
        """One control tick. Public to allow GUI-driven single-stepping."""
        sonars = self.driver.read_sonars()
        frame = self.driver.grab_image()
        detections = self.vision.detect(_to_bgr(frame)) if frame is not None else []
        self.last_detections = detections

        if self.on_frame:
            self.on_frame(self.vision.debug_frame if self.vision.debug else frame, detections)

        self._react_to_world(sonars, detections)

    # ------------------------------------------------------------------
    # Internal state machine
    # ------------------------------------------------------------------
    def _react_to_world(
        self,
        sonars: List[Tuple[bool, float]],
        detections: List[Detection],
    ) -> None:
        cfg = self.cfg
        now = time.time()

        front_dist = self._min_distance(sonars, cfg.front_sonars)
        left_dist = self._min_distance(sonars, cfg.left_sonars)
        right_dist = self._min_distance(sonars, cfg.right_sonars)

        # ---- Emergency: very close obstacle ----
        if front_dist < cfg.emergency_distance:
            self._transition(NavigationState.EMERGENCY_STOP, f"Obstacol < {cfg.emergency_distance:.2f} m", detections)
            self.driver.set_velocity(0.0, 0.0)
            return

        # ---- Active turn maneuver (triggered by mandatory_left / mandatory_right) ----
        if self.state in (NavigationState.TURNING_LEFT, NavigationState.TURNING_RIGHT):
            if now < self._turn_until:
                spin = cfg.turn_speed
                if self.state == NavigationState.TURNING_LEFT:
                    self.driver.set_velocity(-spin, spin)
                else:
                    self.driver.set_velocity(spin, -spin)
                return
            else:
                self._transition(NavigationState.CRUISE, "Viraj terminat - reiau cruise", detections)

        # ---- Time-based pauses (stop / yield / red light) ----
        if self.state == NavigationState.STOPPED_AT_SIGN:
            if now >= self._stopped_until:
                self._transition(NavigationState.CRUISE, "Repornire dupa stop/yield", detections)
            else:
                self.driver.set_velocity(0.0, 0.0)
                return

        if self.state == NavigationState.WAIT_FOR_GREEN:
            if self._has_label(detections, "traffic_light_green"):
                self._transition(NavigationState.CRUISE, "Semafor verde - repornesc", detections)
            elif self._has_label(detections, "traffic_light_yellow") and now >= self._stopped_until:
                self._transition(NavigationState.SLOW, "Semafor galben - rulez cu prudenta", detections)
            else:
                self.driver.set_velocity(0.0, 0.0)
                return

        # ---- React to high-confidence detections ----
        red_light = self._find(detections, "traffic_light_red")
        yellow_light = self._find(detections, "traffic_light_yellow")
        green_light = self._find(detections, "traffic_light_green")
        stop_sign = self._find(detections, "stop")
        yield_sign = self._find(detections, "yield")
        no_entry = self._find(detections, "no_entry")

        speed_target = self.cfg.v_cruise
        for label, v in cfg.speed_limits.items():
            if self._find(detections, label):
                speed_target = min(speed_target, v)

        # No-entry / red light => full stop until cleared
        if red_light and red_light.confidence >= cfg.sign_min_conf:
            self._stopped_until = now + 0.5
            self._transition(NavigationState.WAIT_FOR_GREEN, "Semafor rosu - opresc", detections)
            self.driver.set_velocity(0.0, 0.0)
            return

        if no_entry and no_entry.confidence >= cfg.sign_min_conf:
            self._transition(NavigationState.STOPPED_AT_SIGN, "Acces interzis - opresc si astept", detections)
            self._stopped_until = now + cfg.stop_pause_s
            self.driver.set_velocity(0.0, 0.0)
            return

        if stop_sign and stop_sign.confidence >= cfg.sign_min_conf:
            sig = self._sig(stop_sign)
            if sig not in self._stop_sign_consumed:
                self._stop_sign_consumed.add(sig)
                self._transition(NavigationState.STOPPED_AT_SIGN,
                                 f"STOP detectat (conf={stop_sign.confidence:.2f})", detections)
                self._stopped_until = now + cfg.stop_pause_s
                self.driver.set_velocity(0.0, 0.0)
                return

        if yield_sign and yield_sign.confidence >= cfg.sign_min_conf:
            sig = self._sig(yield_sign)
            if sig not in self._stop_sign_consumed:
                self._stop_sign_consumed.add(sig)
                self._transition(NavigationState.STOPPED_AT_SIGN,
                                 f"CEDEAZA TRECEREA (conf={yield_sign.confidence:.2f})", detections)
                self._stopped_until = now + cfg.yield_pause_s
                self.driver.set_velocity(0.0, 0.0)
                return

        if yellow_light and yellow_light.confidence >= cfg.sign_min_conf:
            self.target_speed = self.cfg.v_slow
            if self.state != NavigationState.SLOW:
                self._transition(NavigationState.SLOW, "Galben - reduc viteza", detections)

        # ---- Mandatory direction signs: execute a turn maneuver ----
        mand_right = self._find(detections, "mandatory_right")
        mand_left = self._find(detections, "mandatory_left")
        if mand_right and mand_right.confidence >= cfg.sign_min_conf:
            sig = self._sig(mand_right)
            if sig not in self._mandatory_consumed:
                self._mandatory_consumed.add(sig)
                self._transition(NavigationState.TURNING_RIGHT, "Mandatory RIGHT - virez dreapta", detections)
                self._turn_until = now + cfg.turn_duration_s
                self.driver.set_velocity(cfg.turn_speed, -cfg.turn_speed)
                return
        if mand_left and mand_left.confidence >= cfg.sign_min_conf:
            sig = self._sig(mand_left)
            if sig not in self._mandatory_consumed:
                self._mandatory_consumed.add(sig)
                self._transition(NavigationState.TURNING_LEFT, "Mandatory LEFT - virez stanga", detections)
                self._turn_until = now + cfg.turn_duration_s
                self.driver.set_velocity(-cfg.turn_speed, cfg.turn_speed)
                return

        # ---- Default cruise + Braitenberg avoidance ----
        if front_dist < cfg.avoid_distance:
            self._transition(NavigationState.AVOIDING, f"Evitare obstacol fata={front_dist:.2f} m", detections)
        elif self.state == NavigationState.AVOIDING and front_dist > cfg.avoid_distance + 0.1:
            self._transition(NavigationState.CRUISE, "Drum liber - reiau cruise", detections)

        self.target_speed = min(self.target_speed, speed_target)
        v_left, v_right = self._compute_velocities(self.target_speed, left_dist, right_dist, front_dist)
        self.driver.set_velocity(v_left, v_right)

    # ------------------------------------------------------------------
    def _compute_velocities(self, base, left, right, front) -> Tuple[float, float]:
        cfg = self.cfg
        if self.state == NavigationState.EMERGENCY_STOP:
            return 0.0, 0.0
        if self.state == NavigationState.AVOIDING:
            # Braitenberg "fear": closer obstacle -> stronger turn away
            proximity_l = max(0.0, 1.0 - left)
            proximity_r = max(0.0, 1.0 - right)
            proximity_f = max(0.0, 1.0 - front)
            steer = cfg.braitenberg_gain * (proximity_l - proximity_r)
            forward = max(0.4, base - cfg.braitenberg_gain * 0.5 * proximity_f)
            v_left = forward + steer
            v_right = forward - steer
        else:
            v_left = v_right = base

        cap = cfg.v_max
        return float(max(-cap, min(cap, v_left))), float(max(-cap, min(cap, v_right)))

    def _min_distance(self, sonars, indices) -> float:
        best = 1.0
        for i in indices:
            if i < len(sonars):
                detected, d = sonars[i]
                if detected and d < best:
                    best = d
        return best

    def _find(self, detections: List[Detection], label: str) -> Detection | None:
        for d in detections:
            if d.label == label and d.confidence >= self.cfg.sign_min_conf:
                return d
        return None

    def _has_label(self, detections: List[Detection], label: str) -> bool:
        return self._find(detections, label) is not None

    def _sig(self, det: Detection) -> Tuple[int, int]:
        """Coarse fingerprint of a detection used to avoid double-firing stop signs."""
        x, y, _, _ = det.bbox
        return (x // 40, y // 40)

    def _transition(
        self, state: NavigationState, reason: str, detections: List[Detection]
    ) -> None:
        if state != self.state:
            self.state = state
            self._emit(reason, state, detections)

    def _emit(
        self,
        text: str,
        state: NavigationState,
        detections: List[Detection] | None = None,
    ) -> None:
        ev = NavigationEvent(
            timestamp=time.time(),
            text=text,
            state=state,
            detections=[d.label for d in (detections or [])],
        )
        self._events.append(ev)
        if self.on_event:
            try:
                self.on_event(ev)
            except Exception:
                pass

    @property
    def events(self) -> List[NavigationEvent]:
        return self._events


def _to_bgr(rgb: np.ndarray | None) -> np.ndarray | None:
    if rgb is None:
        return None
    import cv2
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
