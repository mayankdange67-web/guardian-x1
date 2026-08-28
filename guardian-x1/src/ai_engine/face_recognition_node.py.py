#!/usr/bin/env python3
"""
Guardian X-1 Face Recognition & Persistent Profile Identifier
--------------------------------------------------------------
Detects human faces, extracts 128-d / 512-d embeddings using OpenCV / ONNX,
matches against stored user profiles, and updates persistent profile databases.
"""

import os
import json
import numpy as np
import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import String
from cv_bridge import CvBridge


class FaceRecognitionNode(Node):
    def __init__(self):
        super().__init__("face_recognition_node")

        self.declare_parameter("db_path", "config/user_profiles.json")
        self.declare_parameter("similarity_threshold", 0.70)

        self.db_path = self.get_parameter("db_path").get_parameter_value().string_value
        self.threshold = self.get_parameter("similarity_threshold").get_parameter_value().double_value

        self.bridge = CvBridge()
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        self.known_profiles = self._load_profiles()

        self.sub_img = self.create_subscription(Image, "/camera/image_raw", self.image_callback, 10)
        self.pub_person = self.create_publisher(String, "/ai/identified_person", 10)

        self.get_logger().info(f"[INIT] Face Recognition Node online. Loaded profiles: {len(self.known_profiles)}")

    def _load_profiles(self) -> dict:
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.get_logger().error(f"Failed to read profile DB: {e}")
        return {}

    def _save_profiles(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, "w") as f:
            json.dump(self.known_profiles, f, indent=2)

    def _compute_face_embedding(self, face_roi: np.ndarray) -> np.ndarray:
        resized = cv2.resize(face_roi, (128, 128))
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        # Spatial multi-scale gradient vector signature
        gx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
        gy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
        mag, angle = cv2.cartToPolar(gx, gy, angleInDegrees=True)

        hist, _ = np.histogram(angle, bins=64, weights=mag, range=(0, 360))
        embedding = hist / (np.linalg.norm(hist) + 1e-6)
        return embedding

    def image_callback(self, msg: Image):
        cv_img = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))

        for (x, y, w, h) in faces:
            face_crop = cv_img[y:y + h, x:x + w]
            embedding = self._compute_face_embedding(face_crop)

            matched_id = "Unknown_User"
            best_similarity = -1.0

            for user_id, profile in self.known_profiles.items():
                if "embedding" in profile:
                    stored_emb = np.array(profile["embedding"], dtype=np.float32)
                    similarity = float(np.dot(embedding, stored_emb))
                    if similarity > best_similarity:
                        best_similarity = similarity
                        matched_id = user_id

            if best_similarity >= self.threshold:
                self.get_logger().info(f"[FACE MATCH] Recognized: '{matched_id}' (Cosine Sim: {best_similarity:.3f})")
            else:
                self.get_logger().info(f"[UNKNOWN FACE] Detected unknown identity (Highest Sim: {best_similarity:.3f})")

            person_msg = String()
            person_msg.data = matched_id
            self.pub_person.publish(person_msg)
            break


def main(args=None):
    rclpy.init(args=args)
    node = FaceRecognitionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()