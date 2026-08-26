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
