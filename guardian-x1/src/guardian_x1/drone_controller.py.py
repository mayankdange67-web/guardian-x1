#!/usr/bin/env python3
import logging, time
logging.basicConfig(level=logging.INFO, format="[DRONE] %(message)s")
class DroneController:
    def __init__(self):
        self.armed = False
        self.current_alt = 0.0
    def takeoff(self, target_altitude: float):
        self.armed = True
        self.current_alt = target_altitude
        logging.info(f"Autonomous takeoff to {target_altitude}m")
    def land(self):
        self.current_alt = 0.0
        self.armed = False
        logging.info("Autonomous landing executed.")
    def disarm_motors(self):
        self.armed = False
        logging.info("Motors disarmed.")
        