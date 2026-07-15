# Adopte un Mesh

Rencontre locale, signal faible, intentions fortes.

Adopte un Mesh est une plateforme de rencontre locale autour de Meshtastic, d'un Raspberry Pi 5, d'un HDD persistant et d'une interface web mobile-first.

La doctrine est simple : **LoRa transporte l'etincelle, le Pi 5 garde le feu**.

## Ce que contient ce bootstrap

- API FastAPI minimale avec SQLite.
- PWA statique mobile-first.
- Docker Compose pour Pi 5.
- Mosquitto local pour les integrations MQTT.
- Radio bridge Python pour parler a une radio Meshtastic en USB.
- Ingestion de profils radio `AM1` et `MM1|...`.
- Portail Wi-Fi local via `hostapd`, `dnsmasq` et Nginx.
- Documentation serveur Pi, securite, protocole radio, mini-image de profil et Wi-Fi captif.
- Scripts d'installation, diagnostic et test terrain.

## Demarrage rapide developpement

```bash
cp .env.example .env
docker compose -f docker/docker-compose.yml up --build
```

Puis ouvrir :

- Site : http://localhost:8080
- API : http://localhost:8000/health
- Mosquitto : localhost:1883

## Demarrage Pi 5

```bash
chmod +x scripts/*.sh
./scripts/install_pi5.sh
./scripts/doctor.sh
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build
```

## Mode Wi-Fi local / portail captif

Le Pi 5 peut devenir un point d'acces local autonome :

```bash
sudo ADOPTE_AP_SSID="Adopte Un Mesh" \
  ADOPTE_WIFI_IFACE="wlan0" \
  ADOPTE_AP_ADDR="192.168.4.1" \
  ADOPTE_LOCAL_DOMAIN="adopteunmesh.local" \
  ./scripts/setup_wifi_ap.sh
```

Ensuite, les utilisateurs se connectent au Wi-Fi `Adopte Un Mesh` et ouvrent :

```txt
http://adopteunmesh.local
```

ou :

```txt
http://192.168.4.1
```

Voir `docs/WIFI_AP_CAPTIVE_PORTAL.md`.

## Format profil radio compatible

Format compact terrain :

```txt
MM1|Pseudo|M/F|49|Photo,LoRa,Hacking|Dispo cafe au soleil
```

Le Pi parse ce message, recupere le RSSI/SNR si Meshtastic les fournit, et fait un UPSERT dans SQLite. Les endpoints utiles :

```txt
GET /api/profiles
GET /api/active
POST /mesh/inbound
```

`MM1` est accepte pour prototypage, mais la doctrine produit reste : peu de donnees, TTL court, pas de GPS exact, pas de numero de telephone par LoRa.

## Mini image de profil par mesh

On ne transporte pas une vraie photo par LoRa au MVP. Meshtastic garde environ 200 octets utiles par payload applicatif, donc une image classique ferait exploser le reseau.

La strategie retenue :

1. **Avatar seed** : un identicon genere depuis une graine courte.
2. **Descriptor mesh** : un message `AM1 I ...` de moins de 120 caracteres.
3. **Tiny chunks experimentaux** : uniquement en reseau prive/evenement, rate-limites, jamais sur le canal public.

Voir `docs/MINI_PROFILE_IMAGE.md`.

## Structure

```txt
apps/api              API FastAPI + SQLite
apps/web              PWA statique
services/radio-bridge Bridge USB Meshtastic -> API
configs/mosquitto     Broker MQTT local
docker                Compose dev/Pi 5
docs                  Specifications projet
scripts               Installation, Wi-Fi AP et diagnostic
```

## Regles d'or

- Pas de GPS exact.
- Pas de nom complet par LoRa.
- Pas de telephone par LoRa.
- Pas de photo brute par LoRa.
- TTL court pour presence et beacons.
- Blocage et signalement des le MVP.
- Broker MQTT local prive, pas de dependance au MQTT public.

## Etat

Bootstrap MVP : pret pour tests locaux et premier banc Pi 5 + radio Meshtastic USB.
