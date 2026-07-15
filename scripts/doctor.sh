#!/usr/bin/env bash
set -euo pipefail

ok() { echo "OK   $*"; }
fail() { echo "FAIL $*"; exit 1; }
warn() { echo "WARN $*"; }

command -v docker >/dev/null && ok "docker present" || fail "docker absent"
docker compose version >/dev/null && ok "docker compose present" || fail "docker compose absent"

[ -f .env ] && ok ".env present" || warn ".env absent, copier .env.example"
[ -d /srv/adopte-un-mesh ] && ok "/srv/adopte-un-mesh present" || warn "stockage serveur absent"
[ -e "${MESHTASTIC_SERIAL_PORT:-/dev/ttyUSB0}" ] && ok "radio vue sur ${MESHTASTIC_SERIAL_PORT:-/dev/ttyUSB0}" || warn "radio non vue, le coeur LoRa dort peut-etre"

curl -fsS http://localhost:8000/health >/tmp/adopt_health.json && ok "api health OK" || warn "api non joignable"
curl -fsS http://localhost:8080/healthz >/dev/null && ok "web health OK" || warn "web non joignable"

if command -v mosquitto_pub >/dev/null; then
  mosquitto_pub -h localhost -t adoptmesh/admin/status -m "doctor ping" && ok "mqtt publish OK" || warn "mqtt publish KO"
else
  warn "mosquitto-clients absent"
fi

echo "Diagnostic termine. Si tout est OK, les zombies restent dehors."
