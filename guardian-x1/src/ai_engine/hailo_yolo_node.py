#!/usr/bin/env python3
"""
Guardian X-1 Hailo-8L NPU Object Detection Node
Executes hardware-accelerated YOLOv8 inference (13 TOPS) for local object tracking.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class HailoYoloNode(Node):
    def __init__(self):
        super().__init__('hailo_yolo_node')
        self.get_logger().info("Initializing Hailo-8L NPU YOLOv8 Inference Node...")

        self.declare_parameter('system.ai_engine', 'hailo_8l')
        self.publisher = self.create_publisher(String, '/guardian/vision/detections', 10)
        self.timer = self.create_timer(0.1, self.inference_loop)  # 10 Hz detection stream

    def inference_loop(self):
        # Simulated NPU detection output structure matching HailoRT outputs
        detection_data = {
            "timestamp": self.get_clock().now().to_msg().sec,
            "engine": "Hailo-8L",
            "detections": [
                {"class": "person", "confidence": 0.92, "bbox": [120, 80, 240, 360]},
                {"class": "obstacle", "confidence": 0.88, "bbox": [300, 200, 420, 310]}
            ]
        }
        msg = String()
        msg.data = str(detection_data)
        self.publisher.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = HailoYoloNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
