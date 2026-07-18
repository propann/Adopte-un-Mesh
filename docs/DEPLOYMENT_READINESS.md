# Etat de preparation au deploiement

## Verdict actuel

Le projet est pret pour un **premier deploiement de laboratoire sur Pi 5**, mais pas encore pour une ouverture publique sans surveillance.

## Pret maintenant

- depot structure ;
- Docker Compose dev ;
- Compose Pi 5/Coolify ;
- API FastAPI ;
- site mobile-first ;
- SQLite persistante sur HDD ;
- Mosquitto prive ;
- radio-bridge USB ;
- publication radio vers MQTT ;
- emission MQTT vers LoRa desactivee par defaut ;
- profils, likes, matches, reports, blocage ;
- QR site/Wi-Fi/config ;
- documentation Pi, radio, securite et exploitation ;
- health checks API et web.

## A verifier sur le vrai Pi

### Systeme

```bash
uname -m
cat /etc/os-release
docker version
docker compose version
df -h
lsblk -f
```

Attendu : ARM64/aarch64, OS 64-bit, Docker 24+, HDD monte et suffisamment libre.

### Dossiers

```bash
sudo mkdir -p \
  /srv/adopte-un-mesh/data \
  /srv/adopte-un-mesh/backups \
  /srv/adopte-un-mesh/mosquitto/data \
  /srv/adopte-un-mesh/mosquitto/log
```

### Radio

```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
meshtastic --port /dev/ttyUSB0 --info
```

Adapter le port si la radio utilise `/dev/ttyACM0`.

### Variables obligatoires

- `ADMIN_TOKEN` fort ;
- `PROFILE_TOKEN_PEPPER` fort ;
- `ADOPT_CHANNEL_PSK` generee localement ;
- `RADIO_DRY_RUN=false` ;
- `MESHTASTIC_SERIAL_PORT` correct ;
- `CORS_ORIGINS` limite au domaine reel ;
- `APP_PUBLIC_BASE_URL` en HTTPS ;
- `MQTT_ALLOW_OUTBOUND=false` au premier deploiement.

## Test avant ouverture

1. Deployer sans radio en `RADIO_DRY_RUN=true`.
2. Verifier :

```bash
curl -f https://DOMAINE/api/health
curl -f https://DOMAINE/api/stats
```

3. Creer un profil de test.
4. Verifier le radar.
5. Faire un report et verifier l'admin.
6. Brancher la radio.
7. Passer `RADIO_DRY_RUN=false`.
8. Verifier les logs `radio-bridge`.
9. Publier un paquet AM1 depuis une seconde radio.
10. Verifier API, SQLite et MQTT.

## MQTT de laboratoire

Ecouter :

```bash
mosquitto_sub -h 127.0.0.1 -t 'adopte/mesh/#' -v
```

Le topic attendu pour les receptions est :

```txt
adopte/mesh/inbound
```

L'emission vers LoRa reste coupee tant que :

```dotenv
MQTT_ALLOW_OUTBOUND=false
```

## Bloquants avant ouverture publique

- authentification utilisateur complete encore minimale ;
- modification/suppression de profil par token a terminer ;
- fermeture et traitement des reports dans l'admin ;
- rate limiting API ;
- protection CSRF/session si cookies ;
- validation plus forte des textes sensibles ;
- vraie politique de retention automatisee ;
- sauvegarde hors site testee ;
- HTTPS obligatoire ;
- test de charge et de coupure electrique ;
- test physique de la radio et du canal ADOPT ;
- validation communautaire de la baseline reseau choisie.

## Niveau de deploiement conseille

### Maintenant

`LAB` : toi, quelques radios, utilisateurs connus.

### Apres tests terrain

`PILOTE FERME` : petit groupe invite, moderation manuelle.

### Plus tard

`PUBLIC` : seulement apres auth, rate limit, sauvegardes, suppression utilisateur et moderation abouties.

## Go / No-Go

### GO laboratoire

- Pi stable ;
- HDD monte ;
- HTTPS ou acces local prive ;
- secrets definis ;
- MQTT non expose ;
- outbound LoRa coupe ;
- admin accessible seulement a toi.

### NO-GO public

- port 1883 ouvert Internet ;
- API 8000 exposee directement ;
- CORS `*` ;
- token admin vide ;
- GPS exact ;
- radio en mode router sans etude RF ;
- sauvegarde inexistante ;
- profils sans moyen de suppression.
