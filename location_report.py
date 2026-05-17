from __future__ import annotations

import json
from datetime import datetime
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


USER_AGENT = "TransparentLocationDemo/1.0"


def fetch_public_network_details() -> dict[str, str | bool]:
    request = Request(
        "https://ipwho.is/",
        headers={"User-Agent": USER_AGENT},
    )

    with urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))

    if not payload.get("success", False):
        raise ValueError(payload.get("message", "Public network lookup failed"))

    connection = payload.get("connection", {}) or {}
    timezone = payload.get("timezone", {})
    return {
        "ip": payload.get("ip", ""),
        "city": payload.get("city", ""),
        "region": payload.get("region", ""),
        "country": payload.get("country", ""),
        "country_code": payload.get("country_code", ""),
        "postal": payload.get("postal", ""),
        "timezone": timezone.get("id", "") if isinstance(timezone, dict) else "",
        "isp": connection.get("isp", ""),
        "org": connection.get("org", ""),
        "asn": connection.get("asn", ""),
        "domain": connection.get("domain", ""),
        "is_proxy": bool(connection.get("proxy", False)),
        "is_vpn": bool(connection.get("vpn", False)),
        "is_tor": bool(connection.get("tor", False)),
    }


def reverse_geocode(latitude: float, longitude: float) -> dict[str, str]:
    query = urlencode(
        {
            "format": "jsonv2",
            "lat": f"{latitude:.6f}",
            "lon": f"{longitude:.6f}",
            "addressdetails": 1,
        }
    )
    request = Request(
        f"https://nominatim.openstreetmap.org/reverse?{query}",
        headers={"User-Agent": USER_AGENT},
    )

    with urlopen(request, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))

    address = payload.get("address", {})
    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("hamlet")
        or address.get("municipality")
        or ""
    )
    return {
        "display_name": payload.get("display_name", ""),
        "city": city,
        "state": address.get("state", ""),
        "state_district": address.get("state_district", ""),
        "city_district": address.get("city_district", ""),
        "postcode": address.get("postcode", ""),
        "country": address.get("country", ""),
        "country_code": address.get("country_code", "").upper(),
        "road": address.get("road", ""),
        "house_number": address.get("house_number", ""),
        "suburb": address.get("suburb", ""),
        "county": address.get("county", ""),
        "neighbourhood": address.get("neighbourhood", ""),
    }


def parse_location_payload(raw_body: bytes) -> dict:
    payload = json.loads(raw_body.decode("utf-8"))
    payload["latitude"] = float(payload["latitude"])
    payload["longitude"] = float(payload["longitude"])
    payload["accuracy"] = float(payload.get("accuracy", 0))
    payload["timestamp"] = payload.get("timestamp", "")
    payload["network"] = payload.get("network", {}) or {}
    return payload


def build_location_report(payload: dict, client_ip: str = "") -> list[str]:
    latitude = float(payload["latitude"])
    longitude = float(payload["longitude"])
    accuracy = float(payload.get("accuracy", 0))
    timestamp = payload.get("timestamp", "")
    network = payload.get("network", {}) or {}

    received_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        address = reverse_geocode(latitude, longitude)
        geocode_error = ""
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        address = {}
        geocode_error = str(exc)

    try:
        public_network = fetch_public_network_details()
        public_network_error = ""
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        public_network = {}
        public_network_error = str(exc)

    lines = ["", "=" * 56, f"Location received at: {received_at}"]
    if timestamp:
        lines.append(f"Browser timestamp:   {timestamp}")
    lines.extend(
        [
            f"Client IP:           {client_ip or '-'}",
            f"Latitude:            {latitude:.6f}",
            f"Longitude:           {longitude:.6f}",
            f"Accuracy (meters):   {round(accuracy)}",
        ]
    )

    if address:
        lines.extend(
            [
                f"City:                {address.get('city', '-') or '-'}",
                f"State:               {address.get('state', '-') or '-'}",
                f"State District:      {address.get('state_district', '-') or '-'}",
                f"City District:       {address.get('city_district', '-') or '-'}",
                f"County:              {address.get('county', '-') or '-'}",
                f"Neighbourhood:       {address.get('neighbourhood', '-') or '-'}",
                f"Suburb:              {address.get('suburb', '-') or '-'}",
                f"Road:                {address.get('road', '-') or '-'}",
                f"House Number:        {address.get('house_number', '-') or '-'}",
                f"Postcode:            {address.get('postcode', '-') or '-'}",
                f"Country:             {address.get('country', '-') or '-'}",
                f"Country Code:        {address.get('country_code', '-') or '-'}",
                f"Full Address:        {address.get('display_name', '-') or '-'}",
            ]
        )
    else:
        lines.append("Address lookup:      Failed")
        if geocode_error:
            lines.append(f"Lookup error:        {geocode_error}")

    if network:
        connection = network.get("connection") or {}
        device = network.get("device") or {}
        screen = network.get("screen") or {}
        brands = device.get("userAgentBrands") or []
        brand_text = ", ".join(
            f"{item.get('brand', '?')} {item.get('version', '?')}"
            for item in brands
            if isinstance(item, dict)
        )
        languages = network.get("languages") or []

        lines.extend(
            [
                "Network Details:",
                f"User Agent:          {network.get('userAgent', '-') or '-'}",
                f"Platform:            {network.get('platform', '-') or '-'}",
                f"Language:            {network.get('language', '-') or '-'}",
                f"Languages:           {', '.join(languages) if languages else '-'}",
                f"Timezone:            {network.get('timezone', '-') or '-'}",
                f"Online:              {network.get('onLine', '-')}",
                f"Cookies Enabled:     {network.get('cookieEnabled', '-')}",
                f"CPU Cores:           {network.get('hardwareConcurrency', '-')}",
                f"Device Memory (GB):  {network.get('deviceMemory', '-')}",
                "Device Details:",
                f"Device Type:         {device.get('type', '-') or '-'}",
                f"Browser:             {device.get('browser', '-') or '-'}",
                f"Operating System:    {device.get('os', '-') or '-'}",
                f"Touch Points:        {device.get('touchPoints', '-')}",
                f"Vendor:              {device.get('vendor', '-') or '-'}",
                f"UA Mobile Flag:      {device.get('mobile', '-')}",
                f"UA Brands:           {brand_text or '-'}",
                f"Screen Size:         {screen.get('width', '-')} x {screen.get('height', '-')}",
                f"Available Screen:    {screen.get('availWidth', '-')} x {screen.get('availHeight', '-')}",
                f"Color Depth:         {screen.get('colorDepth', '-')}",
                f"Pixel Depth:         {screen.get('pixelDepth', '-')}",
                f"Device Pixel Ratio:  {screen.get('pixelRatio', '-')}",
                f"Connection Type:     {connection.get('type', '-') or '-'}",
                f"Effective Type:      {connection.get('effectiveType', '-') or '-'}",
                f"Downlink (Mbps):     {connection.get('downlink', '-')}",
                f"RTT (ms):            {connection.get('rtt', '-')}",
                f"Save-Data:           {connection.get('saveData', '-')}",
            ]
        )

    if public_network:
        lines.extend(
            [
                "Internet Provider Details:",
                f"Public IP:           {public_network.get('ip', '-') or '-'}",
                f"ISP Company:         {public_network.get('isp', '-') or '-'}",
                f"Organization:        {public_network.get('org', '-') or '-'}",
                f"ASN:                 {public_network.get('asn', '-') or '-'}",
                f"Provider Domain:     {public_network.get('domain', '-') or '-'}",
                f"Provider City:       {public_network.get('city', '-') or '-'}",
                f"Provider Region:     {public_network.get('region', '-') or '-'}",
                f"Provider Country:    {public_network.get('country', '-') or '-'}",
                f"Provider Postal:     {public_network.get('postal', '-') or '-'}",
                f"Provider Timezone:   {public_network.get('timezone', '-') or '-'}",
                f"Proxy Detected:      {public_network.get('is_proxy', '-')}",
                f"VPN Detected:        {public_network.get('is_vpn', '-')}",
                f"Tor Detected:        {public_network.get('is_tor', '-')}",
            ]
        )
    else:
        lines.append("Internet Provider:   Lookup failed")
        if public_network_error:
            lines.append(f"Provider Error:      {public_network_error}")

    if accuracy <= 20:
        lines.append("Accuracy Note:       Strong GPS/Wi-Fi level result")
    elif accuracy <= 100:
        lines.append("Accuracy Note:       Good approximate nearby result")
    else:
        lines.append("Accuracy Note:       Rough result, try outdoors or enable GPS/Wi-Fi")

    lines.append(f"Google Maps:         https://maps.google.com/?q={latitude:.6f},{longitude:.6f}")
    lines.append("=" * 56)
    return lines
