#!/usr/bin/env python3
"""
Guardian X-1 Web Telemetry Server
Serves local web application on port 8080 and handles HTTP/WebSocket API requests.
"""

import json
import threading
from flask import Flask, send_from_directory

class WebServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        self.app = Flask(__name__, static_folder='../../web_ui', static_url_path='')
        self._setup_routes()
        self._thread = None

    def _setup_routes(self):
        @self.app.route('/')
        def index():
            return send_from_directory('../../web_ui', 'index.html')

        @self.app.route('/api/status')
        def status():
            return json.dumps({
                "system": "Guardian X-1",
                "version": "1.2.0",
                "status": "ONLINE",
                "port": self.port
            })

    def start(self):
        """Starts the Flask Web Server in a background thread."""
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print(f"[WEB SERVER] Running on http://{self.host}:{self.port}")

    def _run(self):
        self.app.run(host=self.host, port=self.port, debug=False, use_reloader=False)

if __name__ == '__main__':
    server = WebServer()
    server.start()
    try:
        while True:
            threading.Event().wait(1.0)
    except KeyboardInterrupt:
        print("\n[INFO] Web server stopped.")
