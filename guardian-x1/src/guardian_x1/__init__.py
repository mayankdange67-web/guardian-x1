"""
Guardian X-1 Core Subsystems Package.
Manages central state machine, telemetry, communication bridges, and drive control.
"""

from .state_machine import StateMachine
from .rover_controller import RoverController
from .flight_bridge import FlightBridge
from .cellular_manager import CellularManager
from .web_server import WebServer

__all__ = [
    "StateMachine",
    "RoverController",
    "FlightBridge",
    "CellularManager",
    "WebServer",
]
__version__ = "1.2.0"
