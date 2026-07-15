# Wi-Fi local et portail captif

Objectif : le Raspberry Pi 5 devient une bulle locale autonome. Les personnes proches se connectent au Wi-Fi `Adopte Un Mesh`, ouvrent n'importe quelle page, et tombent sur le site.

> Le mesh capte les signaux. Le Pi 5 tient la taverne. Les zombies restent dehors, sauf s'ils acceptent la charte.

## Architecture

```txt
Telephone utilisateur
  -> Wi-Fi local `Adopte Un Mesh`
  -> Pi 5 `192.168.4.1`
  -> Nginx local
  -> Web `localhost:8080`
  -> API `/api/*`
  -> SQLite sur HDD
```

## Services Linux

- `hostapd` : cree le point d'acces Wi-Fi.
- `dnsmasq` : DHCP + DNS menteur proprement assumé.
- `nginx-light` : capture les URLs de detection portail et redirige vers le site.
- `docker compose` : lance web, API, Mosquitto, radio-bridge.

## Commande

```bash
sudo ADOPTE_AP_SSID="Adopte Un Mesh" \
  ADOPTE_WIFI_IFACE="wlan0" \
  ADOPTE_AP_ADDR="192.168.4.1" \
  ADOPTE_LOCAL_DOMAIN="adopteunmesh.local" \
  ./scripts/setup_wifi_ap.sh
```

Puis lancer la stack :

```bash
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build
```

## Redirection DNS

Le script configure `dnsmasq` avec :

```txt
address=/#/192.168.4.1
```

Donc `http://play.me`, `http://adopteunmesh.local`, `http://zombie.love` ou n'importe quel domaine pointe vers le Pi.

## Captive portal

Le script repond aux URLs de detection courantes :

- Android : `/generate_204`, `/gen_204`
- Apple : `/hotspot-detect.html`
- Windows : `/ncsi.txt`, `/connecttest.txt`

Ces routes redirigent vers `http://adopteunmesh.local/`.

## Securite

Le reseau est ouvert par defaut pour un evenement ou un test rapide. Pour une installation longue duree, preferer :

- WPA2 avec mot de passe affiche localement ;
- admin sur autre interface ou VLAN ;
- pas d'exposition Internet directe ;
- pare-feu `ufw` ou `nftables` ;
- sauvegarde chiffree du HDD.

## Limite importante

Le portail captif ne remplace pas une vraie application. Certains telephones ouvrent une mini-fenetre captive limitee. Pour un usage confortable, l'utilisateur doit ouvrir son navigateur et aller sur :

```txt
http://adopteunmesh.local
```

ou directement :

```txt
http://192.168.4.1
```
