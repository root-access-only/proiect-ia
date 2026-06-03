"""Robot navigation package: CoppeliaSim driver + OpenCV vision."""
from .simulator import CoppeliaSimDriver, SimulatorError
from .vision import TrafficVision, Detection, LightState
from .controller import (
    NavigationController,
    NavigationConfig,
    NavigationState,
    NavigationEvent,
)

__all__ = [
    "CoppeliaSimDriver",
    "SimulatorError",
    "TrafficVision",
    "Detection",
    "LightState",
    "NavigationController",
    "NavigationConfig",
    "NavigationState",
    "NavigationEvent",
]
