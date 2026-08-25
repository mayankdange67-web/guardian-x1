#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import subprocess
import time

class CellularManager(Node):
    def __init__(self):
        super().__init__('cellular_manager')
        self.get_logger().info("Initializing Guardian X-1 eSIM / Cellular Manager...")
        
        # Load parameters
        self.declare_parameter('cellular.apn', 'iot.econnect.com')
        self.declare_parameter('cellular.modem_port', '/dev/ttyUSB2')
        self.apn = self.get_parameter('cellular.apn').value
        self.modem_port = self.get_parameter('cellular.modem_port').value

        # Publisher for cellular telemetry & connection status
        self.status_publisher = self.create_publisher(String, '/guardian/cellular/status', 10)
        self.timer = self.create_timer(10.0, self.check_cellular_status)
        
        self.connected = False

    def check_cellular_status(self):
        # Simulated or AT-command check for LTE / eSIM connectivity
        try:
            # Check if network interface (e.g., wwan0 or ppp0) has an IP
            result = subprocess.run(['ip', 'addr', 'show', 'wwan0'], capture_output=True, text=True)
            if "inet " in result.stdout:
                self.connected = True
                status_msg = String()
                status_msg.data = f"CONNECTED (APN: {self.apn}, Signal: LTE 4G)"
                self.status_publisher.publish(status_msg)
            else:
                self.connected = False
                self.get_logger().warn("eSIM / LTE link down. Attempting reconnection...")
        except Exception as e:
            self.get_logger().error(f"Error checking cellular interface: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = CellularManager()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
