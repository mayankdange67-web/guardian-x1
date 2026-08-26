"""
Guardian X-1 AI Engine Package.
Provides Hailo-8L NPU hardware-accelerated YOLO vision processing.
"""

from .hailo_yolo_node import HailoYoloNode

__all__ = ["HailoYoloNode"]
__version__ = "1.2.0"
