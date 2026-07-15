from __future__ import annotations

import os
import time
from typing import Any

import requests

API_URL = os.getenv("API_URL", "http://api:8000")
SERIAL_PORT = os.getenv("MESHTASTIC_SERIAL_PORT", "/dev/ttyUSB0")
DRY_RUN = os.getenv("RADIO_DRY_RUN", "true").lower() == "true"
MAX_TEXT_LEN = int(os.getenv("RADIO_MAX_TEXT_LEN", "120"))


def post_inbound(payload: str, source: str = "radio") -> None:
    try:
        requests.post(
            f"{API_URL}/mesh/inbound",
            json={"payload": payload[:200], "source": source},
            timeout=5,
        )
    except Exception as exc:
        print(f"[radio-bridge] API unavailable, zombie probably chewing ethernet: {exc}", flush=True)


def run_dry() -> None:
    print("[radio-bridge] dry-run mode: fake mesh pulse every 60s", flush=True)
    while True:
        post_inbound("AM1 B DEMO AD zLN 900 <3", "dry-run")
        time.sleep(60)


def on_receive(packet: dict[str, Any], interface: Any) -> None:
    decoded = packet.get("decoded") or {}
    text = decoded.get("text")
    if not text:
        return
    text = str(text).strip()
    if len(text) > MAX_TEXT_LEN:
        print("[radio-bridge] refused long packet; love is brief on LoRa", flush=True)
        return
    if text.startswith("AM1"):
        post_inbound(text, "meshtastic")


def run_meshtastic() -> None:
    from pubsub import pub
    import meshtastic.serial_interface

    print(f"[radio-bridge] opening Meshtastic serial {SERIAL_PORT}", flush=True)
    interface = meshtastic.serial_interface.SerialInterface(SERIAL_PORT)
    pub.subscribe(on_receive, "meshtastic.receive")
    print("[radio-bridge] listening. If the dead knock, validate the payload.", flush=True)
    while True:
        time.sleep(5)


if __name__ == "__main__":
    if DRY_RUN:
        run_dry()
    else:
        run_meshtastic()
