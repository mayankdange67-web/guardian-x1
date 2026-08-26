#!/usr/bin/env python3
"""
Guardian X-1 Web Telemetry Server
Serves local web application on port 8080 and handles WebSocket telemetry streams.
"""

import json
import asyncio
from flask import Flask, send_from_directory
import threading

app = Flask(__name__, static_folder='../../web_ui', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('../../web_ui', 'index.html')

@app.route('/api/status')
def status():
    return json.dumps({
        "system": "Guardian X-1",
        "version": "1.2.0",
        "status": "ONLINE",
        "port": 8080
    })

def run_flask():
    app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False)

if __name__ == '__main__':
    print("=== Launching Control Web Server on http://0.0.0.0:8080 ===")
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Keep process active
    try:
        while True:
            threading.Event().wait(1.0)
    except KeyboardInterrupt:
        print("\n[INFO] Control Web Server stopped.")
