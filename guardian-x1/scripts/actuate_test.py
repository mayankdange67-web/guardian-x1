#!/usr/bin/env python3
"""
Guardian X-1 Actuator & Drivetrain Verification Script
Tests TB6612FNG motor driver channels and payload servo PWM on Raspberry Pi 5.
Reads GPIO parameters directly from config/control_params.yaml.
"""

import os
import sys
import time
import yaml

try:
    import gpiod
    from gpiod.line import Direction, Value
except ImportError:
    print("[ERROR] 'gpiod' library not found. Install via 'pip install gpiod' or apt.")
    sys.exit(1)


def load_params():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'control_params.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            params = yaml.safe_load(f)
            return params.get('pins', {})
    print("[WARN] config/control_params.yaml not found. Using fallback GPIO pin defaults.")
    return {
        'gpio_chip': '/dev/gpiochip4',
        'motor_left_dir': 17,
        'motor_left_pwm': 12,
        'motor_right_dir': 27,
        'motor_right_pwm': 13,
        'payload_servo_pwm': 18
    }


def main():
    print("=== Guardian X-1 Drivetrain & Actuator Test ===")
    pins = load_params()
    chip_path = pins.get('gpio_chip', '/dev/gpiochip4')
    
    left_dir_pin = pins.get('motor_left_dir', 17)
    left_pwm_pin = pins.get('motor_left_pwm', 12)
    right_dir_pin = pins.get('motor_right_dir', 27)
    right_pwm_pin = pins.get('motor_right_pwm', 13)
    servo_pin = pins.get('payload_servo_pwm', 18)

    print(f"[CONFIG] Target GPIO Chip: {chip_path}")
    print(f"[CONFIG] Left Motor  -> DIR: GPIO {left_dir_pin}, PWM: GPIO {left_pwm_pin}")
    print(f"[CONFIG] Right Motor -> DIR: GPIO {right_dir_pin}, PWM: GPIO {right_pwm_pin}")
    print(f"[CONFIG] Servo PWM   -> GPIO {servo_pin}")

    try:
        chip = gpiod.Chip(chip_path)
    except Exception as e:
        print(f"[ERROR] Failed to open GPIO chip '{chip_path}': {e}")
        sys.exit(1)

    # Request GPIO output lines
    line_offsets = [left_dir_pin, left_pwm_pin, right_dir_pin, right_pwm_pin, servo_pin]
    line_settings = {offset: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE) for offset in line_offsets}
    
    try:
        request = chip.request_lines(consumer="gx1_actuate_test", config=line_settings)
    except Exception as e:
        print(f"[ERROR] Failed to request GPIO lines: {e}")
        sys.exit(1)

    try:
        # Test 1: Left Motor Forward
        print("\n[TEST 1/5] Running Left Motor FORWARD (1.5s)...")
        request.set_value(left_dir_pin, Value.ACTIVE)
        request.set_value(left_pwm_pin, Value.ACTIVE)
        time.sleep(1.5)
        request.set_value(left_pwm_pin, Value.INACTIVE)
        time.sleep(0.5)

        # Test 2: Right Motor Forward
        print("[TEST 2/5] Running Right Motor FORWARD (1.5s)...")
        request.set_value(right_dir_pin, Value.ACTIVE)
        request.set_value(right_pwm_pin, Value.ACTIVE)
        time.sleep(1.5)
        request.set_value(right_pwm_pin, Value.INACTIVE)
        time.sleep(0.5)

        # Test 3: Reverse Both Motors
        print("[TEST 3/5] Running Both Motors REVERSE (1.5s)...")
        request.set_value(left_dir_pin, Value.INACTIVE)
        request.set_value(right_dir_pin, Value.INACTIVE)
        request.set_value(left_pwm_pin, Value.ACTIVE)
        request.set_value(right_pwm_pin, Value.ACTIVE)
        time.sleep(1.5)
        request.set_value(left_pwm_pin, Value.INACTIVE)
        request.set_value(right_pwm_pin, Value.INACTIVE)
        time.sleep(0.5)

        # Test 4: Payload Servo Pulse
        print("[TEST 4/5] Pulsing Payload Servo Release Trigger...")
        for _ in range(50):
            request.set_value(servo_pin, Value.ACTIVE)
            time.sleep(0.0015)  # ~1.5ms pulse
            request.set_value(servo_pin, Value.INACTIVE)
            time.sleep(0.0185)

        # Test 5: All Stop
        print("[TEST 5/5] Disabling all actuator lines...")
        for offset in line_offsets:
            request.set_value(offset, Value.INACTIVE)
        
        print("\n[SUCCESS] All actuator and motor driver tests passed!")

    except KeyboardInterrupt:
        print("\n[WARN] Test aborted by user.")
    finally:
        request.release()
        chip.close()


if __name__ == '__main__':
    main()
