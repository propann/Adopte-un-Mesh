from __future__ import annotations

import json
import os
import time
from typing import Any

import paho.mqtt.client as mqtt
import requests

API_URL = os.getenv("API_URL", "http://api:8000")
SERIAL_PORT = os.getenv("MESHTASTIC_SERIAL_PORT", "/dev/ttyUSB0")
DRY_RUN = os.getenv("RADIO_DRY_RUN", "true").lower() == "true"
MAX_TEXT_LEN = int(os.getenv("RADIO_MAX_TEXT_LEN", "160"))
SUPPORTED_PREFIXES = ("AM1", "MM1|")
ADOPT_CHANNEL_INDEX = int(os.getenv("MESHTASTIC_ADOPT_CHANNEL_INDEX", "1"))

MQTT_HOST = os.getenv("MQTT_HOST", "mosquitto")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_USERNAME = os.getenv("MQTT_USERNAME", "")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD", "")
MQTT_INBOUND_TOPIC = os.getenv("MQTT_INBOUND_TOPIC", "adopte/mesh/inbound")
MQTT_OUTBOUND_TOPIC = os.getenv("MQTT_OUTBOUND_TOPIC", "adopte/mesh/outbound/adopt")
MQTT_STATUS_TOPIC = os.getenv("MQTT_STATUS_TOPIC", "adopte/mesh/status")
MQTT_ALLOW_OUTBOUND = os.getenv("MQTT_ALLOW_OUTBOUND", "false").lower() == "true"

mesh_interface: Any | None = None
mqtt_client: mqtt.Client | None = None


def post_inbound(payload: str, source: str = "radio", node_id: str | None = None, rssi: int | None = None, snr: float | None = None) -> None:
    try:
        requests.post(
            f"{API_URL}/mesh/inbound",
            json={"payload": payload[:220], "source": source, "node_id": node_id, "rssi": rssi, "snr": snr},
            timeout=5,
        ).raise_for_status()
    except Exception as exc:
        print(f"[radio-bridge] API unavailable, zombie probably chewing ethernet: {exc}", flush=True)


def publish_mqtt(event: dict[str, Any]) -> None:
    if mqtt_client is None:
        return
    try:
        mqtt_client.publish(MQTT_INBOUND_TOPIC, json.dumps(event, ensure_ascii=False), qos=0, retain=False)
    except Exception as exc:
        print(f"[radio-bridge] MQTT publish failed: {exc}", flush=True)


def run_dry() -> None:
    print("[radio-bridge] dry-run mode: fake mesh pulse every 60s", flush=True)
    demo_messages = [
        "AM1 B DEMO AD zLN 900 <3",
        "MM1|Azoth|M/F|49|Photo,LoRa,Hacking|Dispo cafe au soleil, zombies tenus en laisse",
    ]
    index = 0
    while True:
        payload = demo_messages[index % len(demo_messages)]
        event = {"payload": payload, "source": "dry-run", "node_id": f"!dry{index:04x}", "rssi": -67, "snr": 7.5}
        post_inbound(**event)
        publish_mqtt(event)
        index += 1
        time.sleep(60)


def packet_node_id(packet: dict[str, Any]) -> str | None:
    for key in ("fromId", "from_id", "from"):
        value = packet.get(key)
        if value is not None:
            return str(value)
    return None


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


def packet_channel(packet: dict[str, Any]) -> int | None:
    value = packet.get("channel")
    try:
        return int(value) if value is not None else None
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

    event = {
        "payload": text,
        "source": "meshtastic",
        "node_id": packet_node_id(packet),
        "rssi": packet_rssi(packet),
        "snr": packet_snr(packet),
        "channel": packet_channel(packet),
        "received_at": int(time.time()),
    }
    publish_mqtt(event)

    if text.startswith(SUPPORTED_PREFIXES):
        post_inbound(text, "meshtastic", event["node_id"], event["rssi"], event["snr"])


def on_mqtt_connect(client: mqtt.Client, userdata: Any, flags: Any, reason_code: Any, properties: Any = None) -> None:
    print(f"[radio-bridge] MQTT connected: {reason_code}", flush=True)
    client.publish(MQTT_STATUS_TOPIC, "online", qos=1, retain=True)
    if MQTT_ALLOW_OUTBOUND:
        client.subscribe(MQTT_OUTBOUND_TOPIC, qos=1)
        print(f"[radio-bridge] outbound enabled on {MQTT_OUTBOUND_TOPIC}", flush=True)
    else:
        print("[radio-bridge] outbound disabled; Pi is listening only", flush=True)


def on_mqtt_message(client: mqtt.Client, userdata: Any, message: mqtt.MQTTMessage) -> None:
    if not MQTT_ALLOW_OUTBOUND or mesh_interface is None:
        return
    try:
        text = message.payload.decode("utf-8").strip()
    except UnicodeDecodeError:
        print("[radio-bridge] refused non-UTF8 MQTT payload", flush=True)
        return
    if not text.startswith(SUPPORTED_PREFIXES):
        print("[radio-bridge] refused outbound payload outside AM1/MM1", flush=True)
        return
    if len(text) > MAX_TEXT_LEN:
        print("[radio-bridge] refused outbound payload too long", flush=True)
        return
    try:
        mesh_interface.sendText(text, channelIndex=ADOPT_CHANNEL_INDEX)
        print(f"[radio-bridge] sent to ADOPT channel {ADOPT_CHANNEL_INDEX}: {text}", flush=True)
    except Exception as exc:
        print(f"[radio-bridge] LoRa outbound failed: {exc}", flush=True)


def connect_mqtt() -> mqtt.Client:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="adopte-radio-bridge")
    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.will_set(MQTT_STATUS_TOPIC, "offline", qos=1, retain=True)
    client.on_connect = on_mqtt_connect
    client.on_message = on_mqtt_message
    client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
    client.loop_start()
    return client


def run_meshtastic() -> None:
    global mesh_interface, mqtt_client

    from pubsub import pub
    import meshtastic.serial_interface

    mqtt_client = connect_mqtt()
    print(f"[radio-bridge] opening Meshtastic serial {SERIAL_PORT}", flush=True)
    mesh_interface = meshtastic.serial_interface.SerialInterface(SERIAL_PORT)
    pub.subscribe(on_receive, "meshtastic.receive")
    print("[radio-bridge] listening. Public mesh is observed; only ADOPT may be emitted by MQTT.", flush=True)
    while True:
        time.sleep(5)


if __name__ == "__main__":
    if DRY_RUN:
        mqtt_client = connect_mqtt()
        run_dry()
    else:
        run_meshtastic()
