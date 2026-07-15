# Adopte un Mesh

Rencontre locale, signal faible, intentions fortes.

**Doctrine : LoRa transporte l'etincelle, le Raspberry Pi 5 garde le feu.**

Adopte un Mesh est une plateforme locale de rencontre et de presence sociale autour de Meshtastic. Le projet utilise un Pi 5 avec HDD comme hub autonome : site web local, API, base SQLite persistante, radio-bridge USB, Mosquitto prive, portail Wi-Fi et outils de configuration QR.

> Ici, les zombies peuvent lire les panneaux. Pas les secrets.

## Lire d'abord

La documentation de reference est maintenant organisee comme un vrai manuel de bunker :

| Document | Role |
|---|---|
| `docs/GUIDE_COMPLET.md` | Manuel global projet : architecture, Docker, radio, site, securite, roadmap |
| `docs/DOCKER_PI5.md` | Deploiement Docker sur Raspberry Pi 5 + HDD |
| `docs/MESHTASTIC_BASELINE.md` | Reglages radio figes et ultra-compatibles |
| `docs/SITE_BASELINE.md` | Base UX/fonctionnelle du site local |
| `docs/RADIO_QR_SETUP.md` | QR, commandes CLI, partage de configuration radio |
| `docs/PI5_SERVER.md` | Preparation serveur Pi 5 |
| `docs/OPERATIONS_RUNBOOK.md` | Exploitation quotidienne et pannes |
| `docs/SECURITY.md` / `SECURITY.md` | Securite projet et procedure de signalement |
| `docs/PRIVACY.md` | Donnees, minimisation, retention |
| `docs/INCIDENT_RESPONSE.md` | Que faire en cas d'abus, fuite, spam ou incident |

## Etat du depot

Cette branche `main` contient maintenant la fondation MVP directement exploitable :

- API FastAPI + SQLite avec profils, ingestion radio, likes, matches, reports et blocage.
- PWA mobile-first avec interface post-apocalyptique et coeur radio.
- Radio bridge Python compatible Meshtastic USB, avec mode dry-run.
- Docker Compose dev + override Pi 5/HDD.
- Point d'acces Wi-Fi local via `hostapd` + `dnsmasq`.
- Generation de QR codes : URL locale, Wi-Fi, fiche radio et commandes CLI Meshtastic.
- Documentation architecture, Docker Pi, securite, privacy, protocole radio, Pi 5, QR, site et runbook.

## Demarrage rapide dev

```bash
cp .env.example .env
./scripts/dev_up.sh
```

Puis ouvrir :

- site : http://localhost:8080
- API : http://localhost:8000/health
- API via nginx : http://localhost:8080/api/health
- Mosquitto : localhost:1883

Arret :

```bash
./scripts/dev_down.sh
```

## Installation Pi 5 + HDD

Prerequis conseille : Raspberry Pi OS Lite 64-bit, Pi 5, stockage SSD/NVMe ou HDD monte, radio Meshtastic en USB.

```bash
chmod +x scripts/*.sh
sudo HDD_MOUNT=/mnt/adopte-hdd ./scripts/install_pi5.sh
cp .env.example .env
./scripts/doctor.sh
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build
```

Par defaut, les donnees persistantes sont preparees sous :

```txt
/srv/adopte-un-mesh
/mnt/adopte-hdd/adopte-un-mesh
```

Voir `docs/DOCKER_PI5.md`, `docs/PI5_SERVER.md` et `docs/OPERATIONS_RUNBOOK.md`.

## Wi-Fi local / portail captif

Le Pi peut creer une bulle Wi-Fi autonome :

```bash
sudo ADOPTE_AP_SSID="Adopte Un Mesh" \
  ADOPTE_WIFI_IFACE="wlan0" \
  ADOPTE_AP_ADDR="192.168.4.1" \
  ADOPTE_LOCAL_DOMAIN="adopteunmesh.local" \
  ./scripts/setup_wifi_ap.sh
```

Les utilisateurs se connectent au Wi-Fi `Adopte Un Mesh`, puis ouvrent :

```txt
http://adopteunmesh.local
http://192.168.4.1
```

## Configuration radio ultra-compatible

La cible terrain par defaut est volontairement simple :

```txt
Region: EU_868
Preset: LONG_FAST
Hop limit: 3
Primary: LongFast/default public
Secondary: ADOPT
Position precision: 0 ou floutee
MQTT public: off par defaut
```

Meshtastic impose que les appareils partagent region + preset LoRa pour communiquer pleinement ; les canaux sont indexes de 0 a 7 ; les noms de canaux et PSK doivent correspondre pour lire les messages. Voir `docs/MESHTASTIC_BASELINE.md` et `docs/RADIO_QR_SETUP.md`.

Commandes radio de base :

```bash
meshtastic --set lora.region EU_868 --set lora.modem_preset LONG_FAST --set lora.hop_limit 3
meshtastic --ch-set psk default --ch-index 0
meshtastic --ch-set module_settings.position_precision 0 --ch-index 0
meshtastic --ch-set name ADOPT --ch-set psk random --ch-index 1
meshtastic --qr-all
meshtastic --info
```

## QR codes disponibles

Endpoints :

```txt
GET /api/qr/site
GET /api/qr/wifi
GET /api/radio/config
GET /api/radio/commands
GET /api/qr/radio-commands
```

Script CLI :

```bash
./scripts/generate_radio_qr.sh
```

Le QR radio du projet ne remplace pas le QR natif Meshtastic. Pour les canaux Meshtastic, la methode la plus sure reste de generer/partager le QR depuis l'application officielle ou via `meshtastic --qr-all` une fois la radio configuree.

## Format profil radio

Format terrain accepte pour prototype :

```txt
MM1|Pseudo|M/F|49|Photo,LoRa,Hacking|Dispo cafe au soleil
```

Format produit recommande :

```txt
AM1 B K7Q2 AD zLN 900 <3
AM1 I K7Q2 s=A7F2 h=♡ p=neon-zombie
```

Regle d'or : **pas de nom complet, pas de telephone, pas d'adresse, pas de GPS exact, pas de photo brute dans LoRa.**

## Base du site

Le site est une PWA locale, pas une app native au MVP. Voir `docs/SITE_BASELINE.md`.

Pages cibles :

- accueil / statut bunker ;
- creation profil temporaire ;
- radar social ;
- QR site/Wi-Fi/radio ;
- securite : block/report/charte ;
- admin MVP : reports, logs, etat radio.

## Structure

```txt
apps/api              API FastAPI + SQLite + QR
apps/web              PWA statique
services/radio-bridge Bridge USB Meshtastic -> API
configs/mosquitto     Broker MQTT local
configs/nginx         Web + proxy API + captive portal
docker                Compose dev/Pi 5
docs                  Specifications et exploitation
scripts               Installation, Wi-Fi AP, securite, QR, backup
```

## Securite

- pas de secret commite ;
- PSK privee generee localement ;
- MQTT local prive par defaut ;
- GPS exact interdit ;
- blocage/report des le MVP ;
- profils temporaires avec TTL ;
- durcissement Pi dans `scripts/harden_pi5.sh` ;
- runbook incident dans `docs/INCIDENT_RESPONSE.md`.

## Commandes de test

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/active
curl -X POST http://localhost:8000/mesh/inbound \
  -H 'Content-Type: application/json' \
  -d '{"payload":"MM1|Azoth|M/F|49|Photo,LoRa,Hacking|Cafe solaire et zombies polis","node_id":"!demo","rssi":-67,"snr":7.5}'
```

## Manifeste court

Adopte un Mesh n'est pas Tinder sur talkie-walkie. C'est un feu de camp numerique : on signale une presence, on protege les personnes, on laisse le Pi organiser le village, et on laisse LoRa respirer.
