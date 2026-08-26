"""
Guardian X-1 Smartwatch Interface Package.
Monitors wearer biometrics, heart rate telemetry, and emergency distress inputs.
"""

from .watch_node import WatchNode

__all__ = ["WatchNode"]
__version__ = "1.2.0"
