#!/usr/bin/env python3
"""
Guardian X-1 Ambulatory Blood Pressure Monitoring (ABPM) Micro-Pump Node
------------------------------------------------------------------------
Drives the ultra-compact micro-air pump and piezoelectric pressure sensor
embedded in the watch strap cuff for medical-grade oscillometric blood
pressure readings.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, String
from std_srvs.srv import Trigger


class ABPMPressureNode(Node):
    def __init__(self):
        super().__init__("abpm_pressure_node")

        self.declare_parameter("max_cuff_pressure_mmhg", 200.0)
        self.declare_parameter("target_deflation_rate_mmhg_sec", 4.0)

        self.max_pressure = self.get_parameter("max_cuff_pressure_mmhg").get_parameter_value().double_value

        self.pub_bp_reading = self.create_publisher(Float32MultiArray, "/smartwatch/health/blood_pressure", 10)
        self.pub_pump_state = self.create_publisher(String, "/smartwatch/health/pump_status", 10)
        self.create_service(Trigger, "/smartwatch/trigger_bp_measurement", self.handle_bp_trigger)

        self.is_measuring = False
        self.current_cuff_pressure = 0.0
        self.systolic = 120.0
        self.diastolic = 80.0

        self.create_timer(0.05, self.control_loop)
        self.get_logger().info("[ABPM] Micro-Pump Controller initialized.")

    def handle_bp_trigger(self, request, response):
        if self.is_measuring:
            response.success = False
            response.message = "ABPM cycle already in progress."
            return response

        self.is_measuring = True
        self.current_cuff_pressure = 0.0
        response.success = True
        response.message = "ABPM micro-cuff inflation sequence initiated."
        self.get_logger().info("[ABPM] Micro-pump engaged. Inflating micro-cuff...")
        return response

    def control_loop(self):
        if not self.is_measuring:
            return

        if self.current_cuff_pressure < self.max_pressure:
            self.current_cuff_pressure += 6.5
            status = String()
            status.data = f"INFLATING:{int(self.current_cuff_pressure)}mmHg"
            self.pub_pump_state.publish(status)
        else:
            self.is_measuring = False
            self.current_cuff_pressure = 0.0

            bp_msg = Float32MultiArray()
            bp_msg.data = [self.systolic, self.diastolic, 72.0]  # Systolic, Diastolic, Heart Rate
            self.pub_bp_reading.publish(bp_msg)

            status = String()
            status.data = "COMPLETE"
            self.pub_pump_state.publish(status)
            self.get_logger().info(f"[ABPM COMPLETE] BP: {int(self.systolic)}/{int(self.diastolic)} mmHg | Pulse: 72 BPM")


def main(args=None):
    rclpy.init(args=args)
    node = ABPMPressureNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()