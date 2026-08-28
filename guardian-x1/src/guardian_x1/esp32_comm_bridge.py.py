#!/usr/bin/env python3
"""
Guardian X-1 ESP32-S3 High-Speed Serial Bridge Node
---------------------------------------------------
Parses high-speed UART packets (921600 Baud) from the ESP32-S3 co-processor,
translating raw encoder velocities, IMU angles, and battery levels into ROS 2 topics.
"""

import serial
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu, JointState, BatteryState
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool


class ESP32CommBridgeNode(Node):
    def __init__(self):
        super().__init__("esp32_comm_bridge")

        self.declare_parameter("port", "/dev/ttyAMA0")
        self.declare_parameter("baudrate", 921600)

        port = self.get_parameter("port").get_parameter_value().string_value
        baudrate = self.get_parameter("baudrate").get_parameter_value().integer_value

        try:
            self.serial_conn = serial.Serial(port, baudrate, timeout=0.01)
            self.get_logger().info(f"[INIT] Serial bridge connected to {port} @ {baudrate} baud.")
        except Exception as e:
            self.serial_conn = None
            self.get_logger().error(f"[FAIL] Could not open serial port {port}: {e}")

        # Publishers
        self.pub_imu = self.create_publisher(Imu, "/guardian_x1/imu", 10)
        self.pub_joints = self.create_publisher(JointState, "/guardian_x1/joint_states", 10)
        self.pub_battery = self.create_publisher(BatteryState, "/guardian_x1/battery", 10)

        # Subscriber for motor actuator commands
        self.create_subscription(Twist, "/guardian_x1/cmd_vel", self.cmd_callback, 10)
        self.create_subscription(Bool, "/guardian_x1/emergency_stop", self.estop_callback, 10)

        # Polling Timer (100 Hz)
        self.create_timer(0.01, self.read_serial_loop)

    def cmd_callback(self, msg: Twist):
        if self.serial_conn and self.serial_conn.is_open:
            packet = f"CMD:{msg.linear.x:.2f},{msg.angular.z:.2f}\n"
            try:
                self.serial_conn.write(packet.encode("utf-8"))
            except Exception as e:
                self.get_logger().error(f"Serial write error: {e}")

    def estop_callback(self, msg: Bool):
        if msg.data and self.serial_conn and self.serial_conn.is_open:
            try:
                self.serial_conn.write(b"ESTOP:1\n")
            except Exception as e:
                self.get_logger().error(f"E-Stop write error: {e}")

    def read_serial_loop(self):
        if not self.serial_conn or not self.serial_conn.is_open:
            return

        try:
            line = self.serial_conn.readline().decode("utf-8", errors="ignore").strip()
            if line.startswith("IMU:"):
                parts = line.replace("IMU:", "").split(",")
                if len(parts) >= 3:
                    imu_msg = Imu()
                    imu_msg.header.stamp = self.get_clock().now().to_msg()
                    imu_msg.header.frame_id = "imu_link"
                    imu_msg.angular_velocity.x = float(parts[0])
                    imu_msg.angular_velocity.y = float(parts[1])
                    imu_msg.angular_velocity.z = float(parts[2])
                    self.pub_imu.publish(imu_msg)

            elif line.startswith("BAT:"):
                parts = line.replace("BAT:", "").split(",")
                if len(parts) >= 2:
                    bat_msg = BatteryState()
                    bat_msg.voltage = float(parts[0])
                    bat_msg.percentage = float(parts[1])
                    self.pub_battery.publish(bat_msg)
        except Exception as e:
            pass


def main(args=None):
    rclpy.init(args=args)
    node = ESP32CommBridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()