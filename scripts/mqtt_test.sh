#!/usr/bin/env bash
set -euo pipefail
HOST="${MQTT_HOST:-localhost}"
TOPIC="${MQTT_ROOT_TOPIC:-adoptmesh}/beacon/in"
MSG="AM1 B TEST AD zLN 900 <3"

echo "Publication MQTT test vers $HOST / $TOPIC"
mosquitto_pub -h "$HOST" -t "$TOPIC" -m "$MSG"
echo "OK : $MSG"
