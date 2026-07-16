#!/usr/bin/env bash
set -euo pipefail

if [[ ${EUID} -ne 0 ]]; then
  echo "Lance avec sudo: sudo ./scripts/setup_provisioning_station.sh"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_USER="${SUDO_USER:-$USER}"

apt update
apt install -y python3 python3-pip python3-venv pipx openssl qrencode sqlite3

sudo -u "$TARGET_USER" pipx ensurepath || true
sudo -u "$TARGET_USER" pipx install 'meshtastic[cli]' || sudo -u "$TARGET_USER" pipx upgrade 'meshtastic[cli]'

usermod -aG dialout,docker "$TARGET_USER"
chmod +x "$ROOT_DIR/scripts/provision_radio.py" "$ROOT_DIR/scripts/create_adopt_channel_key.sh"

if [[ ! -f "$ROOT_DIR/.env" ]]; then
  cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"
fi
chmod 600 "$ROOT_DIR/.env"

if ! grep -q '^PROFILE_TOKEN_PEPPER=.' "$ROOT_DIR/.env"; then
  PEPPER="$(openssl rand -hex 32)"
  sed -i "s/^PROFILE_TOKEN_PEPPER=.*/PROFILE_TOKEN_PEPPER=$PEPPER/" "$ROOT_DIR/.env"
fi

if ! grep -q '^ADMIN_TOKEN=.' "$ROOT_DIR/.env"; then
  ADMIN="$(openssl rand -hex 24)"
  sed -i "s/^ADMIN_TOKEN=.*/ADMIN_TOKEN=$ADMIN/" "$ROOT_DIR/.env"
fi

if ! grep -q '^ADOPT_CHANNEL_PSK=.' "$ROOT_DIR/.env"; then
  sudo -u "$TARGET_USER" ENV_FILE="$ROOT_DIR/.env" "$ROOT_DIR/scripts/create_adopt_channel_key.sh"
fi

cat <<EOF

[OK] Station d'enrolement preparee.

1. Redemarre la session ou le Pi pour appliquer le groupe dialout.
2. Branche une seule radio Meshtastic en USB.
3. Lance:

   cd $ROOT_DIR
   ./scripts/provision_radio.py

Le primaire public reste intact. Le canal secondaire ADOPT est configure localement.
EOF
