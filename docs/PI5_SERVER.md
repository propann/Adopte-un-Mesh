# Serveur Raspberry Pi 5 + HDD

## Mission du Pi 5

Le Pi 5 est le coeur chaud du projet :

- heberger le site local ;
- exposer l'API ;
- garder la base SQLite ;
- gerer Mosquitto ;
- brancher une radio Meshtastic en USB ;
- stocker logs et sauvegardes sur HDD ;
- servir de point d'entree pour les evenements.

## Materiel conseille

- Raspberry Pi 5.
- Alimentation officielle ou stable.
- HDD/SSD USB ou NVMe via boitier/HAT.
- Radio Meshtastic USB : T3-S3, T-Beam, Heltec ou equivalent.
- Antenne correcte EU_868.
- Option : petit UPS ou batterie pour evenement.

## Preparation HDD

Exemple avec un disque vu comme `/dev/sda1` :

```bash
sudo mkdir -p /mnt/adopte-hdd
sudo blkid
sudo nano /etc/fstab
```

Ajouter une ligne adaptee avec l'UUID :

```txt
UUID=XXXX-XXXX /mnt/adopte-hdd ext4 defaults,noatime 0 2
```

Puis :

```bash
sudo mount -a
mountpoint /mnt/adopte-hdd
```

## Installation

```bash
git clone https://github.com/propann/Adopte-un-Mesh.git
cd Adopte-un-Mesh
chmod +x scripts/*.sh
HDD_MOUNT=/mnt/adopte-hdd ./scripts/install_pi5.sh
./scripts/doctor.sh
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build
```

## Ports

| Port | Service |
|---|---|
| 8080 | Site Adopte un Mesh |
| 8000 | API FastAPI |
| 1883 | MQTT local |

## Radio USB

Verifier le port :

```bash
ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
```

Dans `.env` :

```txt
MESHTASTIC_SERIAL_PORT=/dev/ttyUSB0
RADIO_DRY_RUN=false
```

## Mode bunker local

Au debut, ne pas exposer le Pi sur Internet. Le site peut vivre en LAN/hotspot local.

Quand le projet est stable : reverse proxy HTTPS, ACL MQTT, sauvegardes chiffrees, admin token fort.
