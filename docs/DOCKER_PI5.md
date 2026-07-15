# Docker sur Raspberry Pi 5 + HDD

Ce document fige la maniere de lancer Adopte un Mesh sur Raspberry Pi 5. Le but : un serveur local solide, redemarrable, sauvegardable, avec un HDD/SSD pour ne pas transformer la carte SD en biscotte carbonisee.

## 1. Architecture Docker

```txt
Pi 5
├── docker compose
│   ├── api            FastAPI + SQLite
│   ├── web            Nginx + PWA + proxy /api
│   ├── mosquitto      broker MQTT local prive
│   └── radio-bridge   Meshtastic USB -> API
├── /srv/adopte-un-mesh
│   ├── data           base SQLite
│   ├── backups        sauvegardes
│   ├── logs           logs applicatifs si besoin
│   └── mosquitto      data/log/config broker
└── /mnt/adopte-hdd/adopte-un-mesh
    └── stockage persistant conseille
```

## 2. Prerequis systeme

OS conseille : Raspberry Pi OS Lite 64-bit.

```bash
sudo apt update
sudo apt install -y \
  git curl jq sqlite3 \
  docker.io docker-compose-plugin \
  python3 python3-pip \
  hostapd dnsmasq nginx-light \
  qrencode mosquitto-clients

sudo usermod -aG docker,dialout $USER
```

Redemarrer la session apres ajout aux groupes :

```bash
sudo reboot
```

## 3. Preparation du depot

```bash
git clone https://github.com/propann/Adopte-un-Mesh.git
cd Adopte-un-Mesh
chmod +x scripts/*.sh
cp .env.example .env
```

## 4. Variables importantes `.env`

```dotenv
DATABASE_PATH=/data/adopte-un-mesh.sqlite3
PUBLIC_BASE_URL=http://adopteunmesh.local
ADOPTE_AP_SSID=Adopte Un Mesh
ADOPTE_AP_PASSWORD=
ADOPT_DEFAULT_ZONE=local
ADOPT_PROFILE_TTL_SECONDS=86400
ADOPT_ACTIVE_WINDOW_SECONDS=1800
RADIO_DRY_RUN=true
MESHTASTIC_SERIAL_PORT=/dev/ttyUSB0
RADIO_MAX_TEXT_LEN=160
MESHTASTIC_REGION=EU_868
MESHTASTIC_MODEM_PRESET=LONG_FAST
MESHTASTIC_HOP_LIMIT=3
MESHTASTIC_PRIMARY_CHANNEL=LongFast
MESHTASTIC_SECONDARY_CHANNEL=ADOPT
MESHTASTIC_POSITION_PRECISION=0
```

En test sans radio : `RADIO_DRY_RUN=true`.

Avec radio reelle :

```dotenv
RADIO_DRY_RUN=false
MESHTASTIC_SERIAL_PORT=/dev/ttyUSB0
```

ou :

```dotenv
MESHTASTIC_SERIAL_PORT=/dev/ttyACM0
```

## 5. Preparation HDD

Monter le HDD/SSD sur `/mnt/adopte-hdd`, puis lancer :

```bash
sudo HDD_MOUNT=/mnt/adopte-hdd ./scripts/install_pi5.sh
```

Le script prepare :

```txt
/srv/adopte-un-mesh/data
/srv/adopte-un-mesh/backups
/srv/adopte-un-mesh/logs
/srv/adopte-un-mesh/mosquitto
/mnt/adopte-hdd/adopte-un-mesh
```

## 6. Lancement compose

Depuis la racine du depot :

```bash
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build
```

Verifier :

```bash
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml ps
curl http://localhost:8000/health
curl http://localhost:8080/api/health
```

## 7. Logs utiles

```bash
cd docker
docker compose logs -f api
docker compose logs -f web
docker compose logs -f radio-bridge
docker compose logs -f mosquitto
```

Tout ensemble :

```bash
docker compose logs -f
```

## 8. Rebuild propre

```bash
cd docker
docker compose down
docker compose build --no-cache
docker compose up -d
```

Avec override Pi :

```bash
docker compose -f docker-compose.yml -f compose.pi5.yml down
docker compose -f docker-compose.yml -f compose.pi5.yml up -d --build
```

## 9. Radio USB dans Docker

Le service `radio-bridge` monte les ports :

```yaml
devices:
  - "/dev/ttyUSB0:/dev/ttyUSB0"
  - "/dev/ttyACM0:/dev/ttyACM0"
```

Pour detecter la radio :

```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
meshtastic --info
```

Si permission refusee :

```bash
sudo usermod -aG dialout $USER
sudo reboot
```

## 10. Sauvegarde

Script :

```bash
./scripts/backup_hdd.sh
```

Principe :

- sauvegarder SQLite ;
- sauvegarder `.env` separement et prudemment ;
- ne jamais commiter les sauvegardes ;
- tester la restauration, sinon ce n'est pas une sauvegarde, c'est une priere.

## 11. Durcissement minimal

```bash
sudo ./scripts/harden_pi5.sh
```

A faire aussi manuellement :

- mot de passe systeme fort ;
- SSH par cle ;
- firewall local ;
- admin non expose sur Wi-Fi public ;
- Wi-Fi ouvert seulement en evenement court ;
- WPA2 pour installation longue ;
- mise a jour regulieres.

## 12. Ports

| Port | Service | Public ? |
|---|---|---|
| 80 | portail local selon setup Wi-Fi/Nginx | oui local |
| 8080 | PWA dev Docker | local |
| 8000 | API dev | local/dev |
| 1883 | Mosquitto | local seulement |

En installation propre, exposer surtout le site via Nginx. L'API doit etre accessible via `/api`, pas ouverte au monde comme un buffet pour zombies.

## 13. Checklist de demarrage terrain

```bash
mount | grep adopte
./scripts/doctor.sh
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml ps
curl http://localhost:8080/api/health
curl http://localhost:8080/api/radio/config
```

Puis depuis un telephone :

```txt
http://adopteunmesh.local
http://192.168.4.1
```

## 14. Pannes communes

| Symptome | Cause probable | Correction |
|---|---|---|
| API hors ligne | conteneur api crash | `docker compose logs api` |
| Radio non detectee | mauvais port serie | tester `/dev/ttyUSB0` puis `/dev/ttyACM0` |
| Permission radio | user pas dans dialout | `sudo usermod -aG dialout $USER` |
| Site OK mais API KO | proxy Nginx | verifier `configs/nginx/default.conf` |
| Donnees perdues | volume non persistant | verifier override `compose.pi5.yml` |
| MQTT inutilement public | port expose hors LAN | firewall + pas de NAT routeur |
