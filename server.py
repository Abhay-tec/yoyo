from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from location_report import build_location_report, parse_location_payload
from profile_report import build_profile_report, parse_profile_payload


HOST = "127.0.0.1"
PORT = 8000
BASE_DIR = Path(__file__).resolve().parent


class LocationDemoHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def do_POST(self) -> None:
        if self.path in {"/profile", "/api/profile"}:
            self.handle_profile_post()
            return

        if self.path not in {"/location", "/api/location"}:
            self.send_error(404, "File not found")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = parse_location_payload(raw_body)
        except (ValueError, KeyError, json.JSONDecodeError):
            self.send_error(400, "Invalid location payload")
            return

        client_ip = self.client_address[0] if self.client_address else ""
        for line in build_location_report(payload, client_ip):
            print(line)

        response = json.dumps({"ok": True}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def handle_profile_post(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = parse_profile_payload(raw_body)
        except (ValueError, KeyError, json.JSONDecodeError):
            self.send_error(400, "Invalid profile payload")
            return

        client_ip = self.client_address[0] if self.client_address else ""
        for line in build_profile_report(payload, client_ip):
            print(line)

        response = json.dumps({"ok": True}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format: str, *args) -> None:
        print(f"[http] {self.address_string()} - {format % args}")


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), LocationDemoHandler)
    print(f"Serving transparent location demo on http://{HOST}:{PORT}")
    print("Open /index.html, click Continue, and allow location.")
    print("Location details will be printed here in this terminal.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
