#!/usr/bin/env python3
"""
serve.py: Local Analytical Serving Layer for Amman Shadow Economy Dashboard
---------------------------------------------------------------------------
Lightweight HTTP server serving the MapLibre 3D/2D analytical dashboard
and the geospatial API data files (/server/data/).

Usage:
    python3 serve.py [port]
    (Default port: 3000)
"""

import os
import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = Path(__file__).resolve().parent.parent  # /dashboard
SERVER_DATA_DIR = BASE_DIR / "server" / "data"
PUBLIC_DIR = BASE_DIR / "public"

class DashboardRequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Route requests starting with /server/data/ to the data directory
        if path.startswith("/server/data/"):
            rel = path.replace("/server/data/", "")
            return str(SERVER_DATA_DIR / rel)
        elif path == "/" or path == "":
            return str(PUBLIC_DIR / "index.html")
        else:
            return str(PUBLIC_DIR / path.lstrip("/"))

    def end_headers(self):
        # Enable CORS for local cross-origin file inspection
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

def run_server(port=3000):
    server_address = ("", port)
    try:
        httpd = HTTPServer(server_address, DashboardRequestHandler)
        print("=" * 70)
        print("AMMAN SHADOW ECONOMY ANALYTICAL SERVING LAYER ACTIVE")
        print("=" * 70)
        print(f"[*] Dashboard URL:       http://localhost:{port}")
        print(f"[*] Public Assets:       {PUBLIC_DIR}")
        print(f"[*] Serving Data Directory: {SERVER_DATA_DIR}")
        print("Press Ctrl+C to stop the local server.")
        print("=" * 70)
        httpd.serve_forever()
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"[!] Port {port} in use, attempting port {port + 1}...")
            run_server(port + 1)
        else:
            raise e

if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    run_server(port_arg)
