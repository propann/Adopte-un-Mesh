#!/usr/bin/env bash
set -euo pipefail

if [ "${EUID}" -ne 0 ]; then echo 'Run with sudo'; exit 1; fi
apt-get update
apt-get install -y ufw fail2ban unattended-upgrades
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'ssh'
ufw allow 80/tcp comment 'local web/captive portal'
ufw allow 8080/tcp comment 'adopte web dev'
ufw allow 1883/tcp comment 'mqtt local only - restrict if exposed'
ufw --force enable
systemctl enable --now fail2ban unattended-upgrades
find /srv/adopte-un-mesh -type d -exec chmod 750 {} \; 2>/dev/null || true
find /srv/adopte-un-mesh -type f -exec chmod 640 {} \; 2>/dev/null || true
echo 'Pi durci. Le zombie peut toquer, pas rentrer.'
