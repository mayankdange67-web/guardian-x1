/**
 * Guardian X-1 Ecosystem Control Panel Client
 * Manages WebSocket connection, live status updates, and user commands.
 */

const WS_URL = `ws://${window.location.hostname}:8080/ws/ecosystem`;
let socket = null;

// DOM Elements
const modeBadge = document.getElementById('mode-badge');
const batteryBadge = document.getElementById('battery-badge');
const linkBadge = document.getElementById('link-badge');

const cellularState = document.getElementById('cellular-state');
const cellularApn = document.getElementById('cellular-apn');
const cellularRssi = document.getElementById('cellular-rssi');
const cellularBroker = document.getElementById('cellular-broker');

const obstacleDist = document.getElementById('obstacle-dist');
const wearerHr = document.getElementById('wearer-hr');
const consoleLogs = document.getElementById('console-logs');

function initWebSocket() {
  logConsole("Connecting to WebSocket endpoint...", "info");
  
  socket = new WebSocket(WS_URL);

  socket.onopen = function() {
    linkBadge.innerText = "LINK: MESH ACTIVE";
    linkBadge.style.color = "var(--accent-green)";
    logConsole("WebSocket connection established.", "info");
  };

  socket.onmessage = function(event) {
    try {
      const data = JSON.parse(event.data);
      handleTelemetryUpdate(data);
    } catch (e) {
      console.error("Failed to parse incoming WebSocket message:", e);
    }
  };

  socket.onerror = function(error) {
    linkBadge.innerText = "LINK: ERROR";
    linkBadge.style.color = "var(--accent-red)";
    logConsole("WebSocket link error occurred.", "error");
  };

  socket.onclose = function() {
    linkBadge.innerText = "LINK: RECONNECTING";
    linkBadge.style.color = "var(--accent-orange)";
    logConsole("WebSocket link closed. Retrying in 3s...", "warn");
    setTimeout(initWebSocket, 3000);
  };
}

function handleTelemetryUpdate(data) {
  // 1. Update State Machine Metrics
  if (data.mode) {
    modeBadge.innerText = `MODE: ${data.mode}`;
  }
  if (data.battery_v) {
    batteryBadge.innerText = `BATTERY: ${data.battery_v.toFixed(1)} V`;
  }
  if (data.min_obstacle_cm !== undefined) {
    obstacleDist.innerText = `${data.min_obstacle_cm.toFixed(1)} cm`;
  }

  // 2. Update Cellular / eSIM Data
  if (data.cellular) {
    cellularState.innerText = data.cellular.status || "UNKNOWN";
    cellularState.style.color = (data.cellular.status === "CONNECTED") ? "var(--accent-green)" : "var(--accent-red)";
    if (data.cellular.apn) cellularApn.innerText = data.cellular.apn;
    if (data.cellular.rssi_dbm) cellularRssi.innerText = `${data.cellular.rssi_dbm} dBm`;
    if (data.cellular.broker) cellularBroker.innerText = data.cellular.broker;
  }

  // 3. Update Wearer Smartwatch Data
  if (data.heartrate) {
    wearerHr.innerText = `${data.heartrate} BPM`;
  }
}

function sendCommand(cmdName) {
  if (socket && socket.readyState === WebSocket.OPEN) {
    const payload = JSON.stringify({
      type: "command",
      auth_token: "gx1-secure-mesh-2026",
      command: cmdName,
      timestamp: Date.now()
    });
    socket.send(payload);
    logConsole(`Sent command: ${cmdName}`, "info");
  } else {
    logConsole(`Cannot send '${cmdName}' - WebSocket disconnected.`, "error");
  }
}

function logConsole(message, type = "info") {
  if (!consoleLogs) return;
  const timeStr = new Date().toLocaleTimeString();
  const logDiv = document.createElement('div');
  logDiv.className = `log-entry ${type}`;
  logDiv.innerText = `[${timeStr}] ${message}`;
  consoleLogs.appendChild(logDiv);
  consoleLogs.scrollTop = consoleLogs.scrollHeight;
}

// Initialize connection on load
window.addEventListener('load', initWebSocket);
