"""
Guardian X-1 Display Subsystem Package
--------------------------------------
Drives the front-mounted 1.51-inch 128x64 transparent OLED (SSD1309) HUD display,
rendering real-time telemetry, NPU metrics, facial recognition locks, and kinetic mode status.
"""

from .oled_display_node import OLEDDisplayNode

__all__ = ["OLEDDisplayNode"]