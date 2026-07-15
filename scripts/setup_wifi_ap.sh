#!/usr/bin/env bash
set -euo pipefail

SSID="${ADOPTE_AP_SSID:-Adopte Un Mesh}"
WIFI_IFACE="${ADOPTE_WIFI_IFACE:-wlan0}"
AP_ADDR="${ADOPTE_AP_ADDR:-192.168.4.1}"
DHCP_START="${ADOPTE_DHCP_START:-192.168.4.20}"
DHCP_END="${ADOPTE_DHCP_END:-192.168.4.180}"
COUNTRY="${ADOPTE_WIFI_COUNTRY:-FR}"
DOMAIN="${ADOPTE_LOCAL_DOMAIN:-adopteunmesh.local}"

if [[ $EUID -ne 0 ]]; then
  echo "[ap] lance ce script avec sudo. Meme les zombies respectent systemd."
  exit 1
fi

apt-get update
apt-get install -y hostapd dnsmasq nginx-light
systemctl stop hostapd || true
systemctl stop dnsmasq || true
systemctl unmask hostapd || true

cat >/etc/hostapd/hostapd.conf <<EOF
country_code=${COUNTRY}
interface=${WIFI_IFACE}
driver=nl80211
ssid=${SSID}
hw_mode=g
channel=6
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
# Reseau ouvert volontairement pour evenement/local. Pour prod longue duree, activer WPA2.
EOF

cat >/etc/dnsmasq.d/adopte-un-mesh.conf <<EOF
interface=${WIFI_IFACE}
bind-interfaces
domain-needed
bogus-priv
dhcp-range=${DHCP_START},${DHCP_END},255.255.255.0,12h
dhcp-option=3,${AP_ADDR}
dhcp-option=6,${AP_ADDR}
address=/#/${AP_ADDR}
EOF

cat >/etc/systemd/network/10-adopte-ap.network <<EOF
[Match]
Name=${WIFI_IFACE}

[Network]
Address=${AP_ADDR}/24
IPForward=yes
EOF

cat >/etc/hostapd/hostapd.default <<EOF
DAEMON_CONF="/etc/hostapd/hostapd.conf"
EOF

# Captive portal helper for Android/iOS/Windows checks. They hit weird URLs; we answer politely.
cat >/etc/nginx/sites-available/adopte-captive <<EOF
server {
    listen 80 default_server;
    server_name _;

    location /generate_204 { return 302 http://${DOMAIN}/; }
    location /gen_204 { return 302 http://${DOMAIN}/; }
    location /hotspot-detect.html { return 302 http://${DOMAIN}/; }
    location /ncsi.txt { return 302 http://${DOMAIN}/; }
    location /connecttest.txt { return 302 http://${DOMAIN}/; }

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF
ln -sf /etc/nginx/sites-available/adopte-captive /etc/nginx/sites-enabled/adopte-captive
rm -f /etc/nginx/sites-enabled/default || true

systemctl enable systemd-networkd
systemctl restart systemd-networkd
systemctl enable hostapd dnsmasq nginx
systemctl restart hostapd dnsmasq nginx

echo "[ap] Wi-Fi '${SSID}' pret sur ${AP_ADDR}. Domaine piege a zombies: ${DOMAIN}"
