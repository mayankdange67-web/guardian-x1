"""
Guardian X-1 Core Vehicle Subsystem Package
-------------------------------------------
Manages ESP32-S3 serial bridging, predictive cellular link selection, differential rover control,
physics-informed flight stabilization, central safety state machine arbitration, and WebSockets telemetry.
"""

from .cellular_manager import CellularManagerNode
from .esp32_comm_bridge import ESP32CommBridgeNode
from .flight_bridge import FlightBridgeNode
from .rover_controller import RoverControllerNode
from .state_machine import StateMachineNode
from .web_server import WebServerNode

__all__ = [
    "CellularManagerNode",
    "ESP32CommBridgeNode",
    "FlightBridgeNode",
    "RoverControllerNode",
    "StateMachineNode",
    "WebServerNode",
]