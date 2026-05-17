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
        "snapshot": payload.get("snapshot", {}) or {},
    }


def build_profile_report(payload: dict, client_ip: str = "") -> list[str]:
    received_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    label = payload.get("label", "Input")
    value = payload.get("value", "")
    timestamp = payload.get("timestamp", "")
    page = payload.get("page", "")
    snapshot = payload.get("snapshot", {}) or {}

    lines = ["", "=" * 56, f"Profile input received at: {received_at}"]
    if timestamp:
        lines.append(f"Browser timestamp:   {timestamp}")
    lines.append(f"Client IP:           {client_ip or '-'}")
    lines.append(f"{label}:".ljust(21) + f"{value or '-'}")
    if page:
        lines.append(f"Page URL:            {page}")
    if snapshot:
        connection = snapshot.get("connection") or {}
        device = snapshot.get("device") or {}
        screen = snapshot.get("screen") or {}
        battery = snapshot.get("battery") or {}
        languages = snapshot.get("languages") or []
        brands = device.get("userAgentBrands") or []
        brand_text = ", ".join(
            f"{item.get('brand', '?')} {item.get('version', '?')}"
            for item in brands
            if isinstance(item, dict)
        )
        lines.extend(
            [
                "Snapshot Details:",
                f"User Agent:          {snapshot.get('userAgent', '-') or '-'}",
                f"Platform:            {snapshot.get('platform', '-') or '-'}",
                f"Language:            {snapshot.get('language', '-') or '-'}",
                f"Languages:           {', '.join(languages) if languages else '-'}",
                f"Timezone:            {snapshot.get('timezone', '-') or '-'}",
                f"Online:              {snapshot.get('onLine', '-')}",
                f"Device Type:         {device.get('type', '-') or '-'}",
                f"Browser:             {device.get('browser', '-') or '-'}",
                f"Operating System:    {device.get('os', '-') or '-'}",
                f"Vendor:              {device.get('vendor', '-') or '-'}",
                f"UA Brands:           {brand_text or '-'}",
                f"Screen Size:         {screen.get('width', '-')} x {screen.get('height', '-')}",
                f"Connection Type:     {connection.get('type', '-') or '-'}",
                f"Effective Type:      {connection.get('effectiveType', '-') or '-'}",
                f"Downlink (Mbps):     {connection.get('downlink', '-')}",
                f"RTT (ms):            {connection.get('rtt', '-')}",
                f"Battery Level:       {battery.get('level', '-')}",
                f"Battery Charging:    {battery.get('charging', '-')}",
                f"Battery Save Mode:   {battery.get('saveMode', '-')}",
            ]
        )
    lines.append("=" * 56)
    return lines
