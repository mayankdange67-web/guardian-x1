# Guardian X-1 System Wiring & Pinout Guide

This document outlines power distribution, signal routing, GPIO mapping, and peripheral communication buses across the platform.

---

## Power Distribution Architecture

```text
               ┌────────────────────────┐
               │ 4S 2200mAh LiPo (14.8V)│
               └───────────┬────────────┘
                           │ XT60
                           ▼
             ┌─────────────────────────────┐
             │ SpeedyBee 55A BLHeli_S ESC  │
             └──────┬───────────────┬──────┘
                    │ VBAT          │ VBAT
                    ▼               ▼
           [4x EMAX Motors]   [5V / 5A Heavy-Duty UBEC]
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
             [Raspberry Pi 5] [TB6612FNG]    [RPLIDAR A1M8]
             (5V / 5A Pin 2,4)(VCC 5V)       (5V VCC)


Raspberry Pi 5 GPIO & Bus InterconnectsFunctionPin NameBoard PinTarget DeviceDevice Pin / PortNotes5V Power5V0Pin 2, 4UBEC Output5V PositiveMain system power inputGroundGNDPin 6, 9, 14Common GroundGNDSystem ground referenceRover Motor L DIRGPIO 17Pin 11TB6612FNG DriverAIN1Left drive directionRover Motor L PWMGPIO 12Pin 32TB6612FNG DriverPWMALeft drive speed controlRover Motor R DIRGPIO 27Pin 13TB6612FNG DriverBIN1Right drive directionRover Motor R PWMGPIO 13Pin 33TB6612FNG DriverPWMBRight drive speed controlPayload Servo PWMGPIO 18Pin 12Servo SignalPWM InDrop mechanism controlMAVLink UART TXGPIO 14 (TXD0)Pin 8SpeedyBee F405 V4RX6 (UART6)Flight control telemetryMAVLink UART RXGPIO 15 (RXD0)Pin 10SpeedyBee F405 V4TX6 (UART6)Flight control commandsGPIO Chip/dev/gpiochip4-Pi 5 RP1 Controller-Libgpiod driver target

Peripheral Bus AssignmentsPeripheralBus / InterfacePort IdentifierBaud / SpeedPower SourceHailo-8L NPUPCIe Gen 2/3 (x1)M.2 Key M HAT5.0 GbpsPCIe Bus (3.3V)RPLIDAR A1M8USB Serial/dev/ttyUSB0115200 baudPi 5 USB (5V)Arducam ToFUSB Serial / CSI/dev/ttyUSB1USB 2.0 HighPi 5 USB (5V)LTE / eSIM ModemUSB Serial UART/dev/ttyUSB2115200 baudPi 5 USB (5V)IMX219 RGB CameraCSI 2-LaneCam/Disp 0 PortMIPI CSI-2Pi 5 CSI PortSpeedyBee F405MAVLink Serial/dev/ttyAMA0921600 baud

Hardware Safety & Fusing
Main Fuse: 60A inline mini-ANL fuse on positive battery lead.

Logic Fuse: 5A fast-acting PTC self-resetting fuse on 5V UBEC output.

Capacitance: 1000µF 35V Low-ESR electrolytic capacitor soldered directly across main ESC XT60 pads to suppress inductive motor voltage spikes.
