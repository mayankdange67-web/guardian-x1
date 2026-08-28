#!/usr/bin/env python3
"""
Guardian X-1 Hailo-8L NPU Object Detection Node
-----------------------------------------------
Runs low-latency 8-bit quantized YOLOv8n inference on the Raspberry Pi 5 Hailo-8L NPU.
Outputs 2D bounding boxes and class predictions over ROS 2 topics.
"""

import os
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from vision_msgs.msg import (
    Detection2DArray,
    Detection2D,
    ObjectHypothesisWithPose,
    BoundingBox2D,
)
from cv_bridge import CvBridge

# Check Hailo PyHailo RT SDK availability
try:
    from hailo_platform import (
        HEF,
        VDevice,
        HailoStreamInterface,
        InferVStreams,
        ConfigureParams,
        InputVStreamParams,
        OutputVStreamParams,
    )

    HAILO_AVAILABLE = True
except ImportError:
    HAILO_AVAILABLE = False


class HailoYoloNode(Node):
    def __init__(self):
        super().__init__("hailo_yolo_node")

        self.declare_parameter("hef_path", "models/hailo/yolov8n_tactical.hef")
        self.declare_parameter("confidence_threshold", 0.45)
        self.declare_parameter("input_topic", "/camera/image_raw")
        self.declare_parameter("output_topic", "/ai/detections")

        self.hef_path = self.get_parameter("hef_path").get_parameter_value().string_value
        self.conf_thresh = self.get_parameter("confidence_threshold").get_parameter_value().double_value
        input_topic = self.get_parameter("input_topic").get_parameter_value().string_value
        output_topic = self.get_parameter("output_topic").get_parameter_value().string_value

        self.bridge = CvBridge()

        self.sub_img = self.create_subscription(Image, input_topic, self.image_callback, 10)
        self.pub_det = self.create_publisher(Detection2DArray, output_topic, 10)

        self.get_logger().info(f"[INIT] Hailo YOLOv8 Node initialized (Hailo-8L SDK Present: {HAILO_AVAILABLE})")

        if HAILO_AVAILABLE and os.path.exists(self.hef_path):
            self._init_hailo_device()
        else:
            self.get_logger().warn(
                f"[WARN] HEF path '{self.hef_path}' unavailable or SDK missing. Operating in bypass mode.")

    def _init_hailo_device(self):
        try:
            self.hef = HEF(self.hef_path)
            self.target = VDevice()
            self.configure_params = ConfigureParams.create_from_hef(
                hef=self.hef, interface=HailoStreamInterface.PCIe
            )
            self.network_group = self.target.configure(self.hef, self.configure_params)[0]
            self.input_vstream_params = InputVStreamParams.make(self.network_group)
            self.output_vstream_params = OutputVStreamParams.make(self.network_group)
            self.get_logger().info("[SUCCESS] Hailo-8L NPU Dataflow Pipeline Configured!")
        except Exception as e:
            self.get_logger().error(f"[FAIL] Hailo Initialization Error: {e}")

    def image_callback(self, msg: Image):
        cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        orig_h, orig_w = cv_img.shape[:2]
        resized = cv2.resize(cv_img, (640, 640))

        det_array = Detection2DArray()
        det_array.header = msg.header

        if HAILO_AVAILABLE and hasattr(self, "network_group"):
            input_data = {
                self.hef.get_input_vstream_infos()[0].name: np.expand_dims(resized, axis=0)
            }
            with InferVStreams(
                    self.network_group, self.input_vstream_params, self.output_vstream_params
            ) as infer_pipeline:
                results = infer_pipeline.infer(input_data)
                det_array = self._process_yolo_outputs(results, msg.header, orig_w, orig_h)

        self.pub_det.publish(det_array)

    def _process_yolo_outputs(self, raw_outputs, header, orig_w, orig_h) -> Detection2DArray:
        det_array = Detection2DArray()
        det_array.header = header

        for key, value in raw_outputs.items():
            preds = np.squeeze(value)
            if preds.ndim == 2:
                for det in preds:
                    score = float(det[4]) if len(det) > 4 else 0.0
                    if score >= self.conf_thresh:
                        d2d = Detection2D()
                        d2d.header = header

                        bbox = BoundingBox2D()
                        bbox.center.position.x = float(det[0] * orig_w / 640.0)
                        bbox.center.position.y = float(det[1] * orig_h / 640.0)
                        bbox.size_x = float(det[2] * orig_w / 640.0)
                        bbox.size_y = float(det[3] * orig_h / 640.0)
                        d2d.bbox = bbox

                        hyp = ObjectHypothesisWithPose()
                        hyp.hypothesis.class_id = str(int(det[5])) if len(det) > 5 else "0"
                        hyp.hypothesis.score = score
                        d2d.results.append(hyp)

                        det_array.detections.append(d2d)

        return det_array


def main(args=None):
    rclpy.init(args=args)
    node = HailoYoloNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()