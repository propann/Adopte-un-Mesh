# Wi-Fi local et portail captif

Le Pi 5 peut devenir une bulle locale autonome : les utilisateurs se connectent au Wi-Fi `Adopte Un Mesh` puis ouvrent le site local.

## Commande

```bash
sudo ADOPTE_AP_SSID="Adopte Un Mesh" \
  ADOPTE_WIFI_IFACE="wlan0" \
  ADOPTE_AP_ADDR="192.168.4.1" \
  ADOPTE_LOCAL_DOMAIN="adopteunmesh.local" \
  ./scripts/setup_wifi_ap.sh
```

## Acces

```txt
http://adopteunmesh.local
http://192.168.4.1
```

## Captive portal

Le script configure des redirections pour Android, Apple et Windows : `/generate_204`, `/gen_204`, `/hotspot-detect.html`, `/ncsi.txt`, `/connecttest.txt`.

## Securite

Pour un evenement public court, Wi-Fi ouvert possible. Pour une installation durable : WPA2, mot de passe affiche sur place, admin separe, pare-feu actif.
