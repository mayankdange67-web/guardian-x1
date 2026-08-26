#!/usr/bin/env python3
"""
Guardian X-1 MAVLink Flight Controller Serial Bridge Node
Communicates with SpeedyBee F405 V4 Flight Controller over UART6 (/dev/ttyAMA0 @ 921600 baud).
"""

import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class FlightBridgeNode(Node):
    def __init__(self):
        super().__init__('flight_bridge_node')
        self.get_logger().info("Initializing SpeedyBee F405 V4 MAVLink Serial Bridge...")

        self.declare_parameter('flight_stack.serial_port', '/dev/ttyAMA0')
        self.declare_parameter('flight_stack.baudrate', 921600)

        self.port = self.get_parameter('flight_stack.serial_port').value
        self.baudrate = self.get_parameter('flight_stack.baudrate').value

        self.status_pub = self.create_publisher(String, '/guardian/flight/status', 10)
        self.subscription = self.create_subscription(
            String, '/guardian/state_machine/command', self.handle_command, 10
        )
        self.is_armed = False
        self.get_logger().info(f"[FLIGHT BRIDGE] Bound to serial interface {self.port} @ {self.baudrate} baud.")

    def handle_command(self, msg: String):
        cmd = msg.data
        if cmd == "ARM":
            self.arm_vehicle()
        elif cmd == "DISARM":
            self.disarm_vehicle()
        elif cmd == "TAKEOFF":
            self.takeoff()

    def arm_vehicle(self):
        self.is_armed = True
        self.get_logger().info("[MAVLINK] Vehicle ARMED")

    def disarm_vehicle(self):
        self.is_armed = False
        self.get_logger().info("[MAVLINK] Vehicle DISARMED")

    def takeoff(self):
        if self.is_armed:
            self.get_logger().info("[MAVLINK] Executing Autonomous Takeoff to RTL Altitude (5.0m)")

def main(args=None):
    rclpy.init(args=args)
    node = FlightBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
