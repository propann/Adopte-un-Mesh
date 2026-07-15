#!/usr/bin/env bash
set -euo pipefail

HDD_MOUNT="${HDD_MOUNT:-/mnt/adopte-hdd}"
ROOT_DIR="/srv/adopte-un-mesh"

if [ "${EUID}" -ne 0 ]; then
  echo "Run with sudo. The bunker needs keys to the basement."
  exit 1
fi

apt-get update
apt-get install -y ca-certificates curl git sqlite3 python3 python3-pip ufw qrencode hostapd dnsmasq nginx-light

if ! command -v docker >/dev/null 2>&1; then
  curl -fsSL https://get.docker.com | sh
fi

mkdir -p "$ROOT_DIR/data" "$ROOT_DIR/backups" "$ROOT_DIR/mosquitto/config" "$ROOT_DIR/mosquitto/data" "$ROOT_DIR/mosquitto/log"

if mountpoint -q "$HDD_MOUNT"; then
  mkdir -p "$HDD_MOUNT/adopte-un-mesh"
  rsync -a "$ROOT_DIR/" "$HDD_MOUNT/adopte-un-mesh/" || true
  echo "HDD detected at $HDD_MOUNT"
else
  echo "WARN: $HDD_MOUNT is not mounted. Continuing on SD/NVMe root."
fi

usermod -aG docker,dialout "${SUDO_USER:-pi}" || true
cp configs/mosquitto/mosquitto.conf "$ROOT_DIR/mosquitto/config/mosquitto.conf"
chmod -R 750 "$ROOT_DIR"

echo "Pi 5 pret. Redemarre la session pour les groupes docker/dialout. Les zombies n'aiment pas les permissions propres."
