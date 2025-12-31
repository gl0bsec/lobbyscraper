#!/usr/bin/env python3
"""
Lightweight web server for EU Initiatives Archive frontend.
Serves the static frontend files and provides API endpoint for initiatives data.
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import sys


class InitiativesHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler for serving static files and API endpoints."""

    def __init__(self, *args, **kwargs):
        # Change to the web_frontend directory
        super().__init__(*args, directory=os.path.dirname(__file__), **kwargs)

    def end_headers(self):
        """Add no-cache headers for static files."""
        # Disable caching for development
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urlparse(self.path)

        # API endpoint for initiatives data
        if parsed_path.path == '/api/initiatives':
            self.serve_initiatives()
        else:
            # Serve static files
            super().do_GET()

    def serve_initiatives(self):
        """Serve the initiatives JSON data."""
        try:
            # Path to the all_initiatives.json file (one level up from web_frontend)
            json_path = os.path.join(os.path.dirname(__file__), '..', 'all_initiatives.json')

            if not os.path.exists(json_path):
                self.send_error(404, 'Initiatives data not found')
                return

            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            # Write the JSON data
            self.wfile.write(json.dumps(data).encode('utf-8'))

        except Exception as e:
            self.send_error(500, f'Error loading initiatives: {str(e)}')

    def log_message(self, format, *args):
        """Custom log message format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=8000):
    """Start the web server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, InitiativesHandler)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║        EU Initiatives Archive - Web Server Running          ║
╚══════════════════════════════════════════════════════════════╝

🌐 Server URL: http://localhost:{port}
📊 Serving initiatives data from: all_initiatives.json

Press Ctrl+C to stop the server
""")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        httpd.server_close()


if __name__ == '__main__':
    # Get port from command line argument or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
