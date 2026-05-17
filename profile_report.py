from __future__ import annotations

import json
from datetime import datetime


def parse_profile_payload(raw_body: bytes) -> dict:
    payload = json.loads(raw_body.decode("utf-8"))
    return {
        "label": str(payload.get("label", "Input")).strip() or "Input",
        "value": str(payload.get("value", "")).strip(),
        "timestamp": str(payload.get("timestamp", "")).strip(),
        "page": str(payload.get("page", "")).strip(),
    }


def build_profile_report(payload: dict, client_ip: str = "") -> list[str]:
    received_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label = payload.get("label", "Input")
    value = payload.get("value", "")
    timestamp = payload.get("timestamp", "")
    page = payload.get("page", "")

    lines = ["", "=" * 56, f"Profile input received at: {received_at}"]
    if timestamp:
        lines.append(f"Browser timestamp:   {timestamp}")
    lines.append(f"Client IP:           {client_ip or '-'}")
    lines.append(f"{label}:".ljust(21) + f"{value or '-'}")
    if page:
        lines.append(f"Page URL:            {page}")
    lines.append("=" * 56)
    return lines
