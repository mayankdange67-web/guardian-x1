"""
Guardian X-1 Smart Glasses Subsystem Package
-------------------------------------------
Provides ROS 2 nodes for waveguide AR optical HUD rendering and motorized
pop-up display deployment control.
"""

from .glasses_hud_node import GlassesHudNode
from .popup_display_node import PopupDisplayNode

__all__ = [
    "GlassesHudNode",
    "PopupDisplayNode",
]