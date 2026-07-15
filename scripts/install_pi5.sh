#!/usr/bin/env bash
set -euo pipefail

APP_ROOT="/srv/adopte-un-mesh"
HDD_MOUNT="${HDD_MOUNT:-/mnt/adopte-hdd}"

say() { echo "[adopte-mesh] $*"; }

say "Installation Pi 5 - le bunker se reveille."

sudo apt-get update
sudo apt-get install -y ca-certificates curl git docker.io docker-compose-plugin mosquitto-clients python3 python3-venv jq
sudo systemctl enable --now docker

say "Creation des dossiers persistants sur HDD ou stockage serveur."
sudo mkdir -p "$APP_ROOT"/{data,logs,mosquitto/config,mosquitto/data,mosquitto/log,backups}

if mountpoint -q "$HDD_MOUNT"; then
  say "HDD detecte sur $HDD_MOUNT : preparation des liens persistants."
  sudo mkdir -p "$HDD_MOUNT/adopte-un-mesh"/{data,logs,mosquitto,backups}
  sudo rsync -a "$APP_ROOT/" "$HDD_MOUNT/adopte-un-mesh/" || true
  sudo rm -rf "$APP_ROOT"
  sudo ln -s "$HDD_MOUNT/adopte-un-mesh" "$APP_ROOT"
else
  say "Aucun HDD monte sur $HDD_MOUNT. On utilise $APP_ROOT. Le zombie du stockage repassera plus tard."
fi

if [ ! -f .env ]; then
  cp .env.example .env
  say ".env cree depuis .env.example : pense a changer ADMIN_TOKEN."
fi

say "Copie Mosquitto config vers stockage persistant."
sudo cp configs/mosquitto/mosquitto.conf "$APP_ROOT/mosquitto/config/mosquitto.conf"

say "OK. Lance ensuite :"
echo "docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build"
