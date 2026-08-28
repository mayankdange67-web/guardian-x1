#!/usr/bin/env python3
"""
Guardian X-1 Transparent OLED Telemetry HUD Node
------------------------------------------------
Interfaces with an SSD1309 1.51-inch transparent SPI/I2C OLED display (128x64 resolution).
Subscribes to system telemetry, active identity, kinetic state, and AI detection count,
rendering a high-contrast tactical HUD at 15 FPS.
"""

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from sensor_msgs.msg import BatteryState
from vision_msgs.msg import Detection2DArray

# PIL (Pillow) & Luma OLED libraries
from PIL import Image, ImageDraw, ImageFont

try:
    from luma.core.interface.serial import spi, i2c
    from luma.oled.device import ssd1309

    LUMA_AVAILABLE = True
except ImportError:
    LUMA_AVAILABLE = False


class OLEDDisplayNode(Node):
    def __init__(self):
        super().__init__("oled_display_node")

        # Configurable ROS 2 parameters
        self.declare_parameter("interface_type", "spi")  # "spi" or "i2c"
        self.declare_parameter("spi_port", 0)
        self.declare_parameter("spi_device", 0)
        self.declare_parameter("gpio_dc", 24)
        self.declare_parameter("gpio_rst", 25)
        self.declare_parameter("width", 128)
        self.declare_parameter("height", 64)

        interface_type = self.get_parameter("interface_type").get_parameter_value().string_value
        self.width = self.get_parameter("width").get_parameter_value().integer_value
        self.height = self.get_parameter("height").get_parameter_value().integer_value

        # Telemetry State Variables
        self.kinetic_mode = "ROVER"
        self.active_person = "UNKNOWN"
        self.battery_pct = 100.0
        self.battery_volt = 14.8
        self.target_count = 0
        self.npu_load = 0.0
        self.anim_frame = 0

        # Subscriptions
        self.create_subscription(String, "/guardian_x1/kinetic_mode", self.mode_callback, 10)
        self.create_subscription(String, "/ai/identified_person", self.person_callback, 10)
        self.create_subscription(BatteryState, "/guardian_x1/battery", self.battery_callback, 10)
        self.create_subscription(Detection2DArray, "/ai/detections", self.detections_callback, 10)
        self.create_subscription(Float32, "/guardian_x1/npu_utilization", self.npu_callback, 10)

        # Initialize SSD1309 Display Driver
        self.device = None
        if LUMA_AVAILABLE:
            try:
                if interface_type.lower() == "spi":
                    gpio_dc = self.get_parameter("gpio_dc").get_parameter_value().integer_value
                    gpio_rst = self.get_parameter("gpio_rst").get_parameter_value().integer_value
                    serial_bus = spi(port=0, device=0, gpio_DC=gpio_dc, gpio_RST=gpio_rst)
                else:
                    serial_bus = i2c(port=1, address=0x3C)

                self.device = ssd1309(serial_bus, width=self.width, height=self.height)
                self.get_logger().info("[INIT] Transparent SSD1309 OLED hardware connected.")
            except Exception as e:
                self.get_logger().warn(f"[WARN] Hardware OLED init failed ({e}). Operating in buffer-only mode.")
        else:
            self.get_logger().warn("[WARN] Luma.OLED library not found. Render buffer running headlessly.")

        # Default pixel font
        self.font_sm = ImageFont.load_default()

        # Render Loop at 15 Hz
        self.create_timer(1.0 / 15.0, self.render_hud_frame)

    # --- Subscriber Callbacks ---
    def mode_callback(self, msg: String):
        self.kinetic_mode = msg.data.upper()

    def person_callback(self, msg: String):
        self.active_person = msg.data.upper()

    def battery_callback(self, msg: BatteryState):
        self.battery_pct = msg.percentage if msg.percentage > 0 else 100.0
        self.battery_volt = msg.voltage

    def detections_callback(self, msg: Detection2DArray):
        self.target_count = len(msg.detections)

    def npu_callback(self, msg: Float32):
        self.npu_load = msg.data

    # --- Tactical HUD Renderer ---
    def render_hud_frame(self):
        self.anim_frame = (self.anim_frame + 1) % 360
        img = Image.new("1", (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)

        # 1. Outer Border & Framing Corners
        draw.rectangle([(0, 0), (self.width - 1, self.height - 1)], outline=1, fill=0)

        # Tactical Corner Markings
        draw.line([(0, 4), (0, 0), (4, 0)], fill=1, width=2)
        draw.line([(123, 0), (127, 0), (127, 4)], fill=1, width=2)
        draw.line([(0, 59), (0, 63), (4, 63)], fill=1, width=2)
        draw.line([(123, 63), (127, 63), (127, 59)], fill=1, width=2)

        # 2. Header Bar: System ID & Battery Indicator
        draw.line([(0, 12), (127, 12)], fill=1)
        draw.text((3, 1), "G-X1 TACTICAL", font=self.font_sm, fill=1)

        # Battery Indicator (Right Aligned)
        bat_str = f"{int(self.battery_pct)}%"
        draw.text((95, 1), bat_str, font=self.font_sm, fill=1)
        draw.rectangle([(118, 3), (125, 9)], outline=1)
        bat_fill_w = int(max(1, (self.battery_pct / 100.0) * 5))
        draw.rectangle([(119, 4), (119 + bat_fill_w, 8)], fill=1)

        # 3. Main Body Section: Kinetic Mode & Identity Lock
        draw.text((4, 16), f"MODE : {self.kinetic_mode}", font=self.font_sm, fill=1)

        # User Identification Lock
        user_disp = self.active_person if len(self.active_person) <= 10 else self.active_person[:8] + ".."
        draw.text((4, 27), f"USER : {user_disp}", font=self.font_sm, fill=1)

        # Target Counts & Load
        draw.text((4, 38), f"TGTS : {self.target_count}", font=self.font_sm, fill=1)
        draw.text((4, 49), f"NPU  : {int(self.npu_load)}%", font=self.font_sm, fill=1)

        # 4. Animated Reticle / Pulse Radar Indicator (Right Side)
        center_x, center_y = 104, 38
        radius = 14
        draw.ellipse([(center_x - radius, center_y - radius),
                      (center_x + radius, center_y + radius)], outline=1)

        # Sweeping Radar Vector Line
        rad_angle = math.radians(self.anim_frame * 6)
        end_x = center_x + int(radius * math.cos(rad_angle))
        end_y = center_y + int(radius * math.sin(rad_angle))
        draw.line([(center_x, center_y), (end_x, end_y)], fill=1)

        # Target Lock Pulsing Reticle inside Radar if Targets Found
        if self.target_count > 0:
            pulse_r = int((self.anim_frame % 10) / 2) + 2
            draw.ellipse([(center_x - pulse_r, center_y - pulse_r),
                          (center_x + pulse_r, center_y + pulse_r)], fill=1)

        # Push Frame Buffer to Hardware SSD1309 Display
        if self.device:
            try:
                self.device.display(img)
            except Exception as e:
                self.get_logger().error(f"OLED Refresh Failure: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = OLEDDisplayNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()