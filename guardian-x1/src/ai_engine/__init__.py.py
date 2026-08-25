"""
AI Engine module for Guardian X-1 ecosystem.
Provides Hailo-8L NPU acceleration, object detection, and target tracking pipelines.
"""

from .inference_node import VisionAIEngine

__all__ = ["VisionAIEngine"]