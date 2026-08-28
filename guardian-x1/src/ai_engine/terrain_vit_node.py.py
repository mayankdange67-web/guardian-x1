#!/usr/bin/env python3
"""
Guardian X-1 Vision Transformer (ViT-Nano) Terrain Node
--------------------------------------------------------
Infers ground surface friction coefficients (\mu) and surface classification
from ground-facing vision patches using ONNX runtime.
"""

import os
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float32, String
from cv_bridge import CvBridge
import onnxruntime as ort


class TerrainViTNode(Node):
    def __init__(self):
        super().__init__("terrain_vit_node")

        self.declare_parameter("onnx_path", "models/onnx/terrain_vit_nano.onnx")
        onnx_path = self.get_parameter("onnx_path").get_parameter_value().string_value

        self.bridge = CvBridge()

        if os.path.exists(onnx_path):
            self.session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
            self.get_logger().info(f"[INIT] Terrain ViT-Nano ONNX loaded: {onnx_path}")
        else:
            self.session = None
            self.get_logger().warn(f"[WARN] ViT ONNX model missing at '{onnx_path}'")

        self.sub_img = self.create_subscription(Image, "/camera/downward/image_raw", self.image_callback, 10)
        self.pub_friction = self.create_publisher(Float32, "/ai/terrain_friction", 10)
        self.pub_surface = self.create_publisher(String, "/ai/surface_type", 10)

        self.classes = ["Asphalt", "Gravel", "Grass", "Mud"]

    def image_callback(self, msg: Image):
        if self.session is None:
            return

        cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding="rgb8")
        resized = cv2.resize(cv_img, (64, 64))

        input_tensor = resized.astype(np.float32) / 255.0
        input_tensor = np.transpose(input_tensor, (2, 0, 1))
        input_tensor = np.expand_dims(input_tensor, axis=0)

        friction_out, class_logits = self.session.run(None, {"terrain_patch": input_tensor})

        mu_val = float(friction_out[0, 0])
        surface_idx = int(np.argmax(class_logits[0]))
        surface_name = self.classes[surface_idx]

        f_msg = Float32()
        f_msg.data = mu_val
        self.pub_friction.publish(f_msg)

        s_msg = String()
        s_msg.data = surface_name
        self.pub_surface.publish(s_msg)


def main(args=None):
    rclpy.init(args=args)
    node = TerrainViTNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()