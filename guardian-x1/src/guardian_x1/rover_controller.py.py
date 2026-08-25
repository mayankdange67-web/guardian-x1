#!/usr/bin/env python3
"""
Guardian X-1 Drone Flight Autonomous Controller
Handles multirotor flight control, altitude hold, PID positioning, vector navigation, and safe landing.
"""
import logging
import math
import time
import yaml
from typing import Dict

logging.basicConfig(level=logging.INFO, format="[DRONE_CTRL] %(asctime)s - %(message)s")


class DroneController:
    def __init__(self, config_path: str = "config/control_params.yaml"):
        with open(config_path, 'r') as f:
            cfg = yaml.safe_load(f)
        self.drone_cfg = cfg.get('drone_flight', {})
        self.max_alt = self.drone_cfg.get('max_altitude_m', 15.0)
        self.max_speed = self.drone_cfg.get('max_horizontal_speed_mps', 3.0)
        self.pid_gains = self.drone_cfg.get('pid_gains', {'kp': 1.2, 'ki': 0.05, 'kd': 0.3})

        # Flight state variables
        self.armed = False
        self.current_alt = 0.0
        self.target_alt = 0.0
        self.pos_x = 0.0
        self.pos_y = 0.0
        self.flight_mode = "DISARMED"  # DISARMED, ARMED, TAKEOFF, POSHOLD, LANDING, RTL

    def arm_motors(self) -> bool:
        self.armed = True
        self.flight_mode = "ARMED"
        logging.info("Drone quadrotor motors ARMED. Props spinning at idle RPM.")
        return True

    def disarm_motors(self) -> bool:
        self.armed = False
        self.flight_mode = "DISARMED"
        self.target_alt = 0.0
        logging.warning("Drone quadrotor motors DISARMED.")
        return True

    def takeoff(self, target_altitude: float) -> bool:
        if not self.armed:
            self.arm_motors()

        alt = min(target_altitude, self.max_alt)
        self.target_alt = alt
        self.flight_mode = "TAKEOFF"
        logging.info(f"Initiating autonomous quadrotor takeoff to target altitude: {alt}m")

        # Altitude climb sequence
        while self.current_alt < self.target_alt:
            self.current_alt += 0.5
            time.sleep(0.1)
            logging.info(f"Climbing... Current Altitude: {self.current_alt:.1f}m")

        self.flight_mode = "POSHOLD"
        logging.info(f"Target altitude {self.target_alt}m reached. Position hold active.")
        return True

    def land(self) -> bool:
        logging.info("Initiating autonomous precision landing sequence...")
        self.flight_mode = "LANDING"

        while self.current_alt > 0.1:
            self.current_alt -= 0.3
            time.sleep(0.1)
            logging.info(f"Descending... Current Altitude: {max(0.0, self.current_alt):.1f}m")

        self.current_alt = 0.0
        self.disarm_motors()
        logging.info("Touchdown confirmed. Quadrotor disarmed.")
        return True

    def navigate_vector(self, dx: float, dy: float, dz: float = 0.0):
        if not self.armed:
            logging.error("Cannot execute vector movement: Drone is disarmed.")
            return

        dist = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
        duration = dist / self.max_speed

        self.pos_x += dx
        self.pos_y += dy
        self.target_alt = max(0.5, min(self.target_alt + dz, self.max_alt))
        self.current_alt = self.target_alt

        logging.info(
            f"Navigating Drone Vector -> ΔX: {dx}m, ΔY: {dy}m, Target Alt: {self.target_alt}m (Est: {duration:.1f}s)")
        self.flight_mode = "POSHOLD"

    def return_to_launch(self):
        logging.warning("Return-to-Launch (RTL) triggered!")
        self.flight_mode = "RTL"
        self.navigate_vector(-self.pos_x, -self.pos_y)
        self.land()

    def get_telemetry(self) -> Dict:
        return {
            "armed": self.armed,
            "flight_mode": self.flight_mode,
            "altitude_m": round(self.current_alt, 2),
            "position": {"x": round(self.pos_x, 2), "y": round(self.pos_y, 2)},
            "battery_v": 15.8,
            "satellites": 14
        }