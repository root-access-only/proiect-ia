"""Thin wrapper around the CoppeliaSim ZMQ remote API.

The wrapper hides the boilerplate of handle lookup, vision-sensor decoding and
graceful shutdown so the controller code stays focused on AI logic. All public
methods are *safe* - they catch the underlying RemoteAPI exceptions and raise a
single :class:`SimulatorError` instead.
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterable, List, Tuple

import numpy as np


class SimulatorError(RuntimeError):
    """Raised when communication with CoppeliaSim fails."""


@dataclass
class RobotHandles:
    """Bundle of CoppeliaSim handles for a Pioneer P3-DX."""

    robot: int
    left_motor: int
    right_motor: int
    vision_sensor: int
    sonars: List[int]


class CoppeliaSimDriver:
    """High-level CoppeliaSim client tailored to the lab scene.

    The class works with the standard CoppeliaSim scene that contains a Pioneer
    P3-DX named ``/PioneerP3DX`` and an optional vision sensor mounted on it
    (default path ``/PioneerP3DX/visionSensor``). If the vision sensor is at a
    different path (e.g. a child of the camera plate), pass its path in.
    """

    def __init__(
        self,
        robot_path: str = "/PioneerP3DX",
        left_motor_path: str = "/PioneerP3DX/leftMotor",
        right_motor_path: str = "/PioneerP3DX/rightMotor",
        vision_path: str = "/PioneerP3DX/visionSensor",
        sonar_count: int = 16,
        host: str = "localhost",
        port: int = 23000,
    ):
        try:
            from coppeliasim_zmqremoteapi_client import RemoteAPIClient
        except ImportError as exc:
            raise SimulatorError(
                "coppeliasim-zmqremoteapi-client is not installed. "
                "Run: pip install coppeliasim-zmqremoteapi-client"
            ) from exc

        try:
            self._client = RemoteAPIClient(host=host, port=port)
            self.sim = self._client.require("sim")
        except Exception as exc:
            raise SimulatorError(
                f"Could not connect to CoppeliaSim at {host}:{port}. "
                "Is the simulator open with the scene loaded?"
            ) from exc

        self.handles = RobotHandles(
            robot=self._get(robot_path),
            left_motor=self._get(left_motor_path),
            right_motor=self._get(right_motor_path),
            vision_sensor=self._try_get(vision_path),
            sonars=[
                self._try_get(f"{robot_path}/ultrasonicSensor[{i}]")
                for i in range(sonar_count)
            ],
        )
        self.handles.sonars = [h for h in self.handles.sonars if h is not None]

    # ------------------------------------------------------------------
    # Handle lookup
    # ------------------------------------------------------------------
    def _get(self, path: str) -> int:
        try:
            return self.sim.getObject(path)
        except Exception as exc:
            raise SimulatorError(f"Object not found: {path!r}") from exc

    def _try_get(self, path: str) -> int | None:
        try:
            return self.sim.getObject(path)
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Simulation lifecycle
    # ------------------------------------------------------------------
    def start(self) -> None:
        try:
            self.sim.startSimulation()
            time.sleep(0.3)
        except Exception as exc:
            raise SimulatorError("Failed to start simulation") from exc

    def stop(self) -> None:
        try:
            self.set_velocity(0.0, 0.0)
            self.sim.stopSimulation()
        except Exception:
            pass

    @contextmanager
    def session(self):
        """Context manager that guarantees ``stop()`` on exit."""
        self.start()
        try:
            yield self
        finally:
            self.stop()

    # ------------------------------------------------------------------
    # Sensors / actuators
    # ------------------------------------------------------------------
    def set_velocity(self, v_left: float, v_right: float) -> None:
        """Set motor target velocities in rad/s."""
        try:
            self.sim.setJointTargetVelocity(self.handles.left_motor, float(v_left))
            self.sim.setJointTargetVelocity(self.handles.right_motor, float(v_right))
        except Exception as exc:
            raise SimulatorError("Failed to set motor velocity") from exc

    def get_position(self) -> Tuple[float, float, float]:
        """Return (x, y, z) of the robot in world coordinates."""
        try:
            pos = self.sim.getObjectPosition(self.handles.robot, self.sim.handle_world)
            return float(pos[0]), float(pos[1]), float(pos[2])
        except Exception as exc:
            raise SimulatorError("Failed to read robot position") from exc

    def get_yaw(self) -> float:
        """Return robot yaw (heading) in radians, in world frame."""
        try:
            euler = self.sim.getObjectOrientation(self.handles.robot, self.sim.handle_world)
            return float(euler[2])
        except Exception as exc:
            raise SimulatorError("Failed to read robot orientation") from exc

    def read_sonars(self) -> List[Tuple[bool, float]]:
        """Return ``(detected, distance_m)`` for every ultrasonic sensor."""
        out: List[Tuple[bool, float]] = []
        for h in self.handles.sonars:
            try:
                result, distance, *_ = self.sim.readProximitySensor(h)
                out.append((bool(result), float(distance) if result else 1.0))
            except Exception:
                out.append((False, 1.0))
        return out

    def grab_image(self) -> np.ndarray | None:
        """Capture an RGB frame from the on-board vision sensor.

        Returns:
            ``HxWx3`` ``uint8`` NumPy array in RGB order, or ``None`` if the
            vision sensor is not present in the scene.
        """
        if self.handles.vision_sensor is None:
            return None
        try:
            img, resolution = self.sim.getVisionSensorImg(self.handles.vision_sensor)
            w, h = int(resolution[0]), int(resolution[1])
            arr = np.frombuffer(img, dtype=np.uint8).reshape(h, w, 3)
            return np.flipud(arr).copy()
        except Exception:
            return None
