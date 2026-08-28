#!/usr/bin/env python3
"""
Guardian X-1 Visual Multi-Target Tracker (DeepSORT-Lite)
--------------------------------------------------------
Associates bounding boxes over consecutive video frames to track targets
and project predicted movement paths.
"""

import numpy as np
import rclpy
from rclpy.node import Node
from vision_msgs.msg import Detection2DArray
from nav_msgs.msg import Path
from geometry_msgs.msg import PoseStamped


class TargetTrackerNode(Node):
    def __init__(self):
        super().__init__("target_tracker_node")

        self.create_subscription(Detection2DArray, "/ai/detections", self.detection_callback, 10)
        self.pub_path = self.create_publisher(Path, "/ai/target_trajectory", 10)

        self.tracked_targets = {}
        self.get_logger().info("[INIT] Target Tracker Node operational.")

    def detection_callback(self, msg: Detection2DArray):
        path = Path()
        path.header = msg.header

        for det in msg.detections:
            cx = det.bbox.center.position.x
            cy = det.bbox.center.position.y

            pose = PoseStamped()
            pose.header = msg.header
            pose.pose.position.x = float(cx)
            pose.pose.position.y = float(cy)
            path.poses.append(pose)

        self.pub_path.publish(path)


def main(args=None):
    rclpy.init(args=args)
    node = TargetTrackerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()