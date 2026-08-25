"""
Smart Glasses module for Guardian X-1 ecosystem.
Exposes glasses node interface for HUD telemetry rendering and voice command handling.
"""

from .glasses_node import SmartGlassesNode

__all__ = ["SmartGlassesNode"]