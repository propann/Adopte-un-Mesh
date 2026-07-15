#!/usr/bin/env bash
set -euo pipefail

SSID="${ADOPTE_AP_SSID:-Adopte Un Mesh}"
PASSWORD="${ADOPTE_AP_PASSWORD:-}"
IFACE="${ADOPTE_WIFI_IFACE:-wlan0}"
ADDR="${ADOPTE_AP_ADDR:-192.168.4.1}"
DOMAIN="${ADOPTE_LOCAL_DOMAIN:-adopteunmesh.local}"
CIDR="${ADOPTE_AP_CIDR:-24}"

if [ "${EUID}" -ne 0 ]; then
  echo "Run with sudo. Le portail captif a besoin des clefs du bunker."
  exit 1
fi

apt-get update
apt-get install -y hostapd dnsmasq nginx-light
systemctl stop hostapd dnsmasq || true

cat >/etc/dhcpcd.conf.d/adopte-un-mesh.conf <<EOF
interface ${IFACE}
static ip_address=${ADDR}/${CIDR}
nohook wpa_supplicant
EOF

cat >/etc/hostapd/hostapd.conf <<EOF
country_code=FR
interface=${IFACE}
ssid=${SSID}
hw_mode=g
channel=6
ieee80211n=1
wmm_enabled=1
EOF

if [ -n "$PASSWORD" ]; then
cat >>/etc/hostapd/hostapd.conf <<EOF
wpa=2
wpa_passphrase=${PASSWORD}
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
EOF
fi

cat >/etc/dnsmasq.d/adopte-un-mesh.conf <<EOF
interface=${IFACE}
dhcp-range=192.168.4.20,192.168.4.220,255.255.255.0,12h
address=/#/${ADDR}
address=/${DOMAIN}/${ADDR}
EOF

cat >/etc/nginx/sites-available/adopte-captive <<EOF
server {
    listen 80 default_server;
    server_name _;
    location = /generate_204 { return 302 http://${DOMAIN}/; }
    location = /gen_204 { return 302 http://${DOMAIN}/; }
    location = /hotspot-detect.html { return 302 http://${DOMAIN}/; }
    location = /ncsi.txt { return 302 http://${DOMAIN}/; }
    location = /connecttest.txt { return 302 http://${DOMAIN}/; }
    location / { proxy_pass http://127.0.0.1:8080; proxy_set_header Host \$host; }
}
EOF
ln -sf /etc/nginx/sites-available/adopte-captive /etc/nginx/sites-enabled/adopte-captive
rm -f /etc/nginx/sites-enabled/default || true

systemctl unmask hostapd || true
systemctl enable hostapd dnsmasq nginx
systemctl restart dhcpcd || true
systemctl restart hostapd dnsmasq nginx

echo "Wi-Fi AP '${SSID}' actif sur ${ADDR}. Ouvre http://${DOMAIN}"
