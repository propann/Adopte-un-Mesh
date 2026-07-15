# Raspberry Pi 5 serveur

## Role

Le Pi 5 est le hub local : site, API, base, QR, Wi-Fi local, radio bridge et sauvegardes. Le HDD sert a sortir les donnees de la carte SD et a survivre aux coupures de courant mieux qu'un zombie sous cafeine.

## Materiel conseille

- Raspberry Pi 5.
- Alimentation officielle ou stable.
- SSD/NVMe/HDD monte sur `/mnt/adopte-hdd`.
- Radio Meshtastic en USB : T-Beam, T3-S3, Heltec, T-Deck en mode test.
- Antenne EU_868 correcte.

## Installation

```bash
sudo HDD_MOUNT=/mnt/adopte-hdd ./scripts/install_pi5.sh
cp .env.example .env
./scripts/doctor.sh
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build
```

## Passage en vraie radio

Trouver le port :

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

Editer `.env` :

```txt
RADIO_DRY_RUN=false
MESHTASTIC_SERIAL_PORT=/dev/ttyUSB0
```

Puis :

```bash
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build radio-bridge
```

## Portail Wi-Fi

```bash
sudo ./scripts/setup_wifi_ap.sh
```

## Durcissement

```bash
sudo ./scripts/harden_pi5.sh
```

## Sauvegarde

```bash
./scripts/backup_hdd.sh
```
