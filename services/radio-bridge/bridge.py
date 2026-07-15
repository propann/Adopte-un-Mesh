from __future__ import annotations

import os
import time
from typing import Any

import requests

API_URL = os.getenv("API_URL", "http://api:8000")
SERIAL_PORT = os.getenv("MESHTASTIC_SERIAL_PORT", "/dev/ttyUSB0")
DRY_RUN = os.getenv("RADIO_DRY_RUN", "true").lower() == "true"
MAX_TEXT_LEN = int(os.getenv("RADIO_MAX_TEXT_LEN", "160"))

SUPPORTED_PREFIXES = ("AM1", "MM1|")


def post_inbound(
    payload: str,
    source: str = "radio",
    node_id: str | None = None,
    rssi: int | None = None,
    snr: float | None = None,
) -> None:
    try:
        requests.post(
            f"{API_URL}/mesh/inbound",
            json={
                "payload": payload[:220],
                "source": source,
                "node_id": node_id,
                "rssi": rssi,
                "snr": snr,
            },
            timeout=5,
        )
    except Exception as exc:
        print(f"[radio-bridge] API unavailable, zombie probably chewing ethernet: {exc}", flush=True)


def run_dry() -> None:
    print("[radio-bridge] dry-run mode: fake mesh pulse every 60s", flush=True)
    demo_messages = [
        "AM1 B DEMO AD zLN 900 <3",
        "MM1|Azoth|M/F|49|Photo,LoRa,Hacking|Dispo cafe au soleil, zombies tenus en laisse",
    ]
    index = 0
    while True:
        post_inbound(demo_messages[index % len(demo_messages)], "dry-run", node_id=f"!dry{index:04x}", rssi=-67, snr=7.5)
        index += 1
        time.sleep(60)


def packet_node_id(packet: dict[str, Any]) -> str | None:
    return packet.get("fromId") or packet.get("from") or packet.get("from_id")


def packet_rssi(packet: dict[str, Any]) -> int | None:
    value = packet.get("rxRssi") or packet.get("rssi")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def packet_snr(packet: dict[str, Any]) -> float | None:
    value = packet.get("rxSnr") or packet.get("snr")
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def on_receive(packet: dict[str, Any], interface: Any) -> None:
    decoded = packet.get("decoded") or {}
    text = decoded.get("text")
    if not text:
        return
    text = str(text).strip()
    if len(text) > MAX_TEXT_LEN:
        print("[radio-bridge] refused long packet; love is brief on LoRa", flush=True)
        return
    if text.startswith(SUPPORTED_PREFIXES):
        post_inbound(
            text,
            "meshtastic",
            node_id=packet_node_id(packet),
            rssi=packet_rssi(packet),
            snr=packet_snr(packet),
        )


def run_meshtastic() -> None:
    from pubsub import pub
    import meshtastic.serial_interface

    print(f"[radio-bridge] opening Meshtastic serial {SERIAL_PORT}", flush=True)
    meshtastic.serial_interface.SerialInterface(SERIAL_PORT)
    pub.subscribe(on_receive, "meshtastic.receive")
    print("[radio-bridge] listening. If the dead knock, validate the payload.", flush=True)
    while True:
        time.sleep(5)


if __name__ == "__main__":
    if DRY_RUN:
        run_dry()
    else:
        run_meshtastic()
