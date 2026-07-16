# Adopte un Mesh

Rencontre locale, signal faible, intentions fortes.

**Doctrine : LoRa transporte l'etincelle, le Raspberry Pi 5 garde le feu.**

Adopte un Mesh est une plateforme locale de rencontre et de presence sociale autour de Meshtastic. Le projet utilise un Pi 5 avec HDD comme hub autonome : site web local, API, base SQLite persistante, radio-bridge USB, Mosquitto prive, portail Wi-Fi, station d'enrolement USB et outils de configuration QR.

> Ici, les zombies peuvent lire les panneaux. Pas les secrets.

## Lire d'abord

| Document | Role |
|---|---|
| `docs/GUIDE_COMPLET.md` | Manuel global projet |
| `docs/DOCKER_PI5.md` | Docker sur Raspberry Pi 5 + HDD |
| `docs/MESHTASTIC_BASELINE.md` | Reglages radio figes |
| `docs/RADIO_PROVISIONING_STATION.md` | Branchement USB, configuration CLI et profil unique par radio |
| `docs/RADIO_QR_SETUP.md` | QR et partage de configuration |
| `docs/SITE_BASELINE.md` | Base UX/fonctionnelle du site |
| `docs/SITE_AUDIT.md` | Audit et backlog du site |
| `docs/OPERATIONS_RUNBOOK.md` | Exploitation quotidienne |
| `docs/SECURITY.md` / `SECURITY.md` | Securite et signalement |
| `docs/PRIVACY.md` | Donnees, minimisation, retention |
| `docs/INCIDENT_RESPONSE.md` | Reponse aux incidents |

## Etat du depot

- API FastAPI + SQLite : profils, ingestion radio, likes, matches, reports, stats, admin local et blocage.
- PWA mobile-first : radar, QR, admin et actions profil.
- Radio bridge Python compatible Meshtastic USB.
- Station d'enrolement USB : une radio ID = un profil.
- Docker Compose dev + override Pi 5/HDD.
- Point d'acces Wi-Fi local via `hostapd` + `dnsmasq`.
- QR site, Wi-Fi, commandes CLI et QR natif Meshtastic.
- Documentation architecture, Docker, radio, securite et exploitation.

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

```bash
chmod +x scripts/*.sh
sudo HDD_MOUNT=/mnt/adopte-hdd ./scripts/install_pi5.sh
cp .env.example .env
./scripts/doctor.sh
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build
```

Stockage persistant :

```txt
/srv/adopte-un-mesh
/mnt/adopte-hdd/adopte-un-mesh
```

Voir `docs/DOCKER_PI5.md`, `docs/PI5_SERVER.md` et `docs/OPERATIONS_RUNBOOK.md`.

## Station USB d'enrolement

La station configure la radio et cree le compte lie a son vrai ID Meshtastic.

Installation :

```bash
sudo ./scripts/setup_provisioning_station.sh
sudo reboot
```

Enrolement :

```bash
./scripts/provision_radio.py
```

Le workflow :

```txt
radio branchee en USB
→ lecture node_id Meshtastic
→ configuration EU_868 / LONG_FAST / hop 3
→ primaire public conserve
→ canal secondaire ADOPT configure avec PSK privee
→ MQTT public coupe
→ profil cree ou mis a jour dans SQLite
→ token prive de gestion affiche une fois
→ QR natif Meshtastic affiche
```

Regle de base : **une radio ID = un profil**. Rebrancher la meme radio met a jour le meme compte. Voir `docs/RADIO_PROVISIONING_STATION.md`.

## Wi-Fi local / portail captif

```bash
sudo ADOPTE_AP_SSID="Adopte Un Mesh" \
  ADOPTE_WIFI_IFACE="wlan0" \
  ADOPTE_AP_ADDR="192.168.4.1" \
  ADOPTE_LOCAL_DOMAIN="adopteunmesh.local" \
  ./scripts/setup_wifi_ap.sh
```

Acces :

```txt
http://adopteunmesh.local
http://192.168.4.1
```

## Configuration radio ultra-compatible

```txt
Region: EU_868
Preset: LONG_FAST
Hop limit: 3
Primary: public/default conserve
Secondary #1: ADOPT
ADOPT PSK: privee, stockee uniquement dans .env
Position precision ADOPT: 0
MQTT public: off
```

Le primaire public reste intact pour capter les utilisateurs Meshtastic deja presents. Le canal secondaire `ADOPT` transporte les signaux rencontre.

## QR codes disponibles

Endpoints :

```txt
GET /api/qr/site
GET /api/qr/wifi
GET /api/radio/config
GET /api/radio/commands
GET /api/qr/radio-commands
```

Script QR :

```bash
./scripts/generate_radio_qr.sh
```

Pour le vrai QR natif des canaux :

```bash
meshtastic --port /dev/ttyACM0 --qr-all
```

Le QR contenant `ADOPT` est un secret local : ne pas le publier dans Git.

## Format profil radio

Prototype :

```txt
MM1|Pseudo|M/F|49|Photo,LoRa,Hacking|Dispo cafe au soleil
```

Produit :

```txt
AM1 B K7Q2 AD zLN 900 <3
AM1 I K7Q2 s=A7F2 h=♡ p=neon-zombie
```

Regle d'or : **pas de nom complet, pas de telephone, pas d'adresse, pas de GPS exact, pas de photo brute dans LoRa.**

## Structure

```txt
apps/api              API FastAPI + SQLite + QR + stats
apps/web              PWA statique
services/radio-bridge Bridge USB Meshtastic -> API
configs/mosquitto     Broker MQTT local
configs/nginx         Web + proxy API + captive portal
docker                Compose dev/Pi 5
docs                  Specifications et exploitation
scripts               Installation, provisioning USB, Wi-Fi, securite, QR, backup
```

## Securite

- une radio ID = un profil ;
- creation terrain via station USB de confiance ;
- PSK `ADOPT` generee localement ;
- token de gestion affiche une seule fois et stocke sous forme de hash ;
- secrets `.env` en permissions `600` ;
- MQTT public coupe ;
- GPS exact interdit ;
- blocage/report des le MVP ;
- profils avec TTL ;
- sauvegardes chiffrees recommandees ;
- runbook incident dans `docs/INCIDENT_RESPONSE.md`.

## Commandes de test

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/active
meshtastic --port /dev/ttyACM0 --info
sqlite3 /srv/adopte-un-mesh/data/adoptmesh.sqlite3 \
  'SELECT node_id, public_id, display_name FROM profiles;'
```

## Manifeste court

Adopte un Mesh n'est pas Tinder sur talkie-walkie. C'est un feu de camp numerique : la place publique Meshtastic reste ouverte, `ADOPT` devient la table de rencontre, le Pi garde les profils au chaud, et une radio ne peut pas se multiplier en douze clones sentimentaux.
