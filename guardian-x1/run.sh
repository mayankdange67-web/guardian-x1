#!/usr/bin/env bash
set -e

echo "=== Launching Guardian X-1 System Ecosystem (v1.2.0 - eSIM Enabled) ==="

# Check and start Ollama local server if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "[LAUNCH] Starting Ollama local server..."
    ollama serve &
    sleep 3
fi

# Start Cellular / eSIM Manager for wide-area LTE telemetry failover
echo "[LAUNCH] Starting Cellular / eSIM Manager..."
python3 src/guardian_x1/cellular_manager.py &

# Start Smartwatch Ecosystem Node
echo "[LAUNCH] Starting Smartwatch Ecosystem Node..."
python3 src/smartwatch/watch_node.py &

# Start Control Web Server on port 8080
echo "[LAUNCH] Starting Control Web Server on port 8080..."
python3 src/guardian_x1/web_server.py &

# Start Master Robotics Core (State Machine) in foreground
echo "[LAUNCH] Starting Master Robotics Core..."
python3 src/guardian_x1/state_machine.py
