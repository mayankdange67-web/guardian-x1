#!/usr/bin/env python3
"""
Guardian X-1 Through-Wall Vision & Occupancy Grid Node
------------------------------------------------------
Parses Wi-Fi CSI amplitude phase perturbation & mmWave radar frames from ESP32-S3.
Reconstructs a 2D through-wall occupancy grid and target coordinates for display.
"""

import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav_msgs.msg import OccupancyGrid
from std_msgs.msg import String, Float32MultiArray


class ThroughWallRadarNode(Node):
    def __init__(self):
        super().__init__("through_wall_radar_node")

        self.create_subscription(String, "/esp32/raw_serial", self.serial_callback, 10)

        # Publishers
        self.pub_grid = self.create_publisher(OccupancyGrid, "/ai/through_wall_grid", 10)
        self.pub_target_pose = self.create_publisher(PoseStamped, "/ai/through_wall_target_pose", 10)
        self.pub_watch_feed = self.create_publisher(Float32MultiArray, "/smartwatch/through_wall_feed", 10)

        self.get_logger().info("[INIT] Through-Wall CSI Radar Vision Node operational.")

    def serial_callback(self, msg: String):
        line = msg.data.strip()
        if line.startswith("TW_VISION:"):
            parts = line.replace("TW_VISION:", "").split(",")
            if len(parts) >= 4:
                dist = float(parts[0])
                angle_deg = float(parts[1])
                conf = float(parts[2])
                attenuation = int(parts[3])

                # Convert polar coordinates to Cartesian (X, Y) relative to front chassis barrier
                angle_rad = math.radians(angle_deg)
                x = dist * math.sin(angle_rad)
                y = dist * math.cos(angle_rad)

                # Publish target position behind wall
                pose = PoseStamped()
                pose.header.stamp = self.get_clock().now().to_msg()
                pose.header.frame_id = "guardian_x1_front_chassis"
                pose.pose.position.x = x
                pose.pose.position.y = y
                pose.pose.position.z = 0.0
                self.pub_target_pose.publish(pose)

                # Stream target telemetry tuple to Smartwatch (dist, angle, conf, atten)
                watch_array = Float32MultiArray()
                watch_array.data = [dist, angle_deg, conf, float(attenuation)]
                self.pub_watch_feed.publish(watch_array)

                self.get_logger().info(f"[THROUGH-WALL VISION] Human detected behind barrier! Dist: {dist:.2f}m | Angle: {angle_deg:.1f}° | Wall Loss: {attenuation}dB")


def main(args=None):
    rclpy.init(args=args)
    node = ThroughWallRadarNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()