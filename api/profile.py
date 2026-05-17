from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler

from profile_report import build_profile_report, parse_profile_payload


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = parse_profile_payload(raw_body)
        except (ValueError, KeyError, json.JSONDecodeError):
            self._send_json(400, {"ok": False, "error": "Invalid profile payload"})
            return

        forwarded_for = self.headers.get("x-forwarded-for", "")
        client_ip = forwarded_for.split(",")[0].strip() if forwarded_for else ""

        for line in build_profile_report(payload, client_ip):
            print(line)

        self._send_json(200, {"ok": True})

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)
