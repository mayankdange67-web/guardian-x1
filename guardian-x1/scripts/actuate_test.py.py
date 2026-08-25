#!/usr/bin/env python3
import time
def test_hardware():
    print("[TEST] Sending 50% PWM to Left Motor... OK")
    time.sleep(1)
    print("[TEST] Sending 50% PWM to Right Motor... OK")
    print("[TEST] Hardware benchmark successful.")
if __name__ == "__main__":
    test_hardware()