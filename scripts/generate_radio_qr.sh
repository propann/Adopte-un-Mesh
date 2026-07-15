#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${OUT_DIR:-qr-out}"
SITE_URL="${APP_PUBLIC_BASE_URL:-http://adopteunmesh.local}"
SSID="${ADOPTE_AP_SSID:-Adopte Un Mesh}"
PASSWORD="${ADOPTE_AP_PASSWORD:-}"
REGION="${MESHTASTIC_REGION:-EU_868}"
PRESET="${MESHTASTIC_MODEM_PRESET:-LONG_FAST}"
HOPS="${MESHTASTIC_HOP_LIMIT:-3}"
PRIMARY="${MESHTASTIC_PRIMARY_CHANNEL:-LongFast}"
SECONDARY="${MESHTASTIC_SECONDARY_CHANNEL:-ADOPT}"
PRECISION="${MESHTASTIC_POSITION_PRECISION:-0}"

command -v qrencode >/dev/null || { echo 'Install qrencode: sudo apt install qrencode'; exit 1; }
mkdir -p "$OUT_DIR"

if [ -n "$PASSWORD" ]; then
  WIFI="WIFI:T:WPA;S:${SSID};P:${PASSWORD};;"
else
  WIFI="WIFI:T:nopass;S:${SSID};;"
fi

COMMANDS=$(cat <<EOF
meshtastic --set lora.region ${REGION} --set lora.modem_preset ${PRESET} --set lora.hop_limit ${HOPS}
meshtastic --ch-set name ${PRIMARY} --ch-set psk default --ch-index 0
meshtastic --ch-set module_settings.position_precision ${PRECISION} --ch-index 0
meshtastic --ch-set name ${SECONDARY} --ch-set psk random --ch-index 1
meshtastic --info
EOF
)

printf '%s' "$SITE_URL" | qrencode -o "$OUT_DIR/site.png"
printf '%s' "$WIFI" | qrencode -o "$OUT_DIR/wifi.png"
printf '%s' "$COMMANDS" | qrencode -o "$OUT_DIR/radio-commands.png"
printf '%s\n' "$COMMANDS" > "$OUT_DIR/radio-commands.txt"

echo "QR generes dans $OUT_DIR : site.png, wifi.png, radio-commands.png"
