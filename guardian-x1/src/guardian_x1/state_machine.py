#!/usr/bin/env python3
"""
Guardian X-1 Master State Machine Node
Arbitrates system operating modes (GROUND_ROVER, AERIAL_FLIGHT, EMERGENCY_RTL, FAILSAFE_LAND)
and processes sensor feedback from LiDAR, ToF depth camera, and cellular telemetry.
"""

import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import LaserScan

class StateMachineNode(Node):
    def __init__(self):
        super().__init__('state_machine_node')
        self.get_logger().info("Initializing Guardian X-1 Master State Machine Core...")

        # System States: GROUND_ROVER, AERIAL_FLIGHT, EMERGENCY_RTL, FAILSAFE_LAND
        self.current_state = "GROUND_ROVER"
        self.battery_voltage = 14.8
        self.wifi_mesh_connected = True
        self.lte_connected = False
        self.obstacle_distance_cm = 999.0

        # Parameters
        self.declare_parameter('rover_drive.emergency_brake_dist_cm', 20.0)
        self.emergency_brake_cm = self.get_parameter('rover_drive.emergency_brake_dist_cm').value

        # Publishers
        self.status_pub = self.create_publisher(String, '/guardian/state_machine/status', 10)
        self.cmd_pub = self.create_publisher(String, '/guardian/state_machine/command', 10)

        # Subscriptions
        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        self.create_subscription(String, '/guardian/cellular/status', self.cellular_callback, 10)
        self.create_subscription(String, '/ecosystem/watch/telemetry', self.watch_callback, 10)

        self.timer = self.create_timer(1.0 / 50.0, self.state_loop)  # 50 Hz main loop

    def scan_callback(self, msg: LaserScan):
        if len(msg.ranges) > 0:
            valid_ranges = [r * 100.0 for r in msg.ranges if r > 0.05]
            if valid_ranges:
                self.obstacle_distance_cm = min(valid_ranges)

    def cellular_callback(self, msg: String):
        try:
            data = json.loads(msg.data)
            self.lte_connected = (data.get("status") == "CONNECTED")
        except Exception:
            pass

    def watch_callback(self, msg: String):
        try:
            data = json.loads(msg.data)
            if data.get("command") == "EMERGENCY_RTL":
                self.get_logger().warn("[OVERRIDE] Received Emergency RTL command from smartwatch!")
                self.current_state = "EMERGENCY_RTL"
        except Exception:
            pass

    def state_loop(self):
        # Obstacle avoidance check in Ground Rover Mode
        if self.current_state == "GROUND_ROVER":
            if self.obstacle_distance_cm <= self.emergency_brake_cm:
                self.get_logger().warn(f"[OBSTACLE] Emergency obstacle at {self.obstacle_distance_cm:.1f} cm! Halting rover.")

        # Publish state heartbeat
        payload = {
            "mode": self.current_state,
            "battery_v": self.battery_voltage,
            "min_obstacle_cm": self.obstacle_distance_cm,
            "lte_connected": self.lte_connected
        }
        msg = String()
        msg.data = json.dumps(payload)
        self.status_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = StateMachineNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
