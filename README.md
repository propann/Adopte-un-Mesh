# Adopte un Mesh

Rencontre locale, signal faible, intentions fortes.

**Doctrine : LoRa transporte l'etincelle, le Raspberry Pi 5 garde le feu.**

Adopte un Mesh est une plateforme locale de rencontre et de presence sociale autour de Meshtastic. Le projet utilise un Pi 5 avec HDD comme hub autonome : site web, API, base SQLite persistante, radio passerelle USB, MQTT prive, portail Wi-Fi, station d'enrolement et outils de configuration radio.

> Ici, les zombies peuvent lire les panneaux. Pas les secrets.

## Lire d'abord

| Document | Role |
|---|---|
| `docs/GUIDE_COMPLET.md` | Manuel global projet |
| `docs/DEPLOYMENT_READINESS.md` | Etat reel avant deploiement et checklist Go/No-Go |
| `docs/COOLIFY_MULTI_SERVER.md` | Coolify central sur un autre serveur + Pi 5 distant |
| `docs/DOCKER_PI5.md` | Docker sur Raspberry Pi 5 + HDD |
| `docs/MESHTASTIC_BASELINE.md` | Reglages radio et profils reseau |
| `docs/RADIO_PROVISIONING_STATION.md` | Configuration CLI et profil unique par radio |
| `docs/REMOTE_PROVISIONING.md` | Enrolement depuis l'ordinateur de l'utilisateur |
| `docs/POSITION_PRIVACY.md` | Position floutee et interdiction du GPS exact public |
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
- Radio passerelle Meshtastic USB permanente sur le Pi.
- Bridge USB vers API et MQTT prive.
- Emission MQTT vers LoRa desactivee par defaut et limitee au canal `ADOPT`.
- Station d'enrolement : une radio ID = un profil.
- Docker Compose dev, Pi 5 et Coolify distant.
- Stockage persistant HDD.
- Documentation architecture, deploiement, radio, securite et exploitation.

## Niveau de maturite

Le projet est pret pour :

```txt
LABORATOIRE / PILOTE FERME
```

Il n'est pas encore recommande pour une ouverture publique sans surveillance. Voir `docs/DEPLOYMENT_READINESS.md`.

## Demarrage rapide dev

```bash
cp .env.example .env
./scripts/dev_up.sh
```

Acces :

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

## Deploiement avec Coolify sur un autre serveur

Une instance Coolify externe peut gerer le Pi 5 par SSH.

Dans Coolify :

1. ajouter le Pi comme serveur distant ;
2. valider Docker et SSH ;
3. connecter ce depot GitHub ;
4. choisir :

```txt
docker/compose.coolify.pi5.yml
```

5. affecter le domaine uniquement au service `web`, port interne `80` ;
6. ajouter les secrets dans l'interface Coolify ;
7. verifier le montage HDD et la radio USB directement sur le Pi.

Le domaine doit pointer vers le Pi, son tunnel ou son reverse proxy. Le serveur Coolify principal ne transporte pas automatiquement le trafic.

Voir `docs/COOLIFY_MULTI_SERVER.md`.

## Radio passerelle permanente du Pi

Architecture :

```txt
Radio Meshtastic USB
        |
        v
radio-bridge
  |           |
  v           v
API         Mosquitto prive
  |           |
  v           v
SQLite      automations internes
```

MQTT :

```txt
adopte/mesh/inbound
adopte/mesh/status
adopte/mesh/outbound/adopt
```

Le flux sortant vers LoRa reste coupe par defaut :

```dotenv
MQTT_ALLOW_OUTBOUND=false
```

Le port MQTT `1883` ne doit pas etre expose sur Internet.

## Station d'enrolement

La station configure la radio et cree le compte lie a son vrai ID Meshtastic.

```bash
sudo ./scripts/setup_provisioning_station.sh
sudo reboot
./scripts/provision_radio.py
```

Regle : **une radio ID = un profil**. Rebrancher la meme radio met a jour le meme compte.

## Configuration radio

Principes fixes :

```txt
Region legale EU_868
Profil reseau public choisi selon la zone
Canal primaire communautaire conserve
Canal secondaire #1 ADOPT
PSK ADOPT privee
Position floutee ou coupee
MQTT public desactive
```

Une radio utilise une seule couche radio physique a la fois. Les canaux primaire et secondaire doivent donc partager la meme region, le meme preset et la meme frequence physique.

## Position

Valeurs publiques autorisees :

```txt
0  : aucune position
12 : zone large
13 : ville / secteur
15 : quartier large avec avertissement
32 : position exacte interdite dans l'enrolement public
```

Voir `docs/POSITION_PRIVACY.md`.

## QR radio

```bash
./scripts/generate_radio_qr.sh
meshtastic --port /dev/ttyACM0 --qr-all
```

Le QR contenant la PSK `ADOPT` est un secret local : ne pas le publier dans Git.

## Format radio

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

## Securite minimale

- une radio ID = un profil ;
- PSK `ADOPT` generee localement ;
- token de gestion stocke sous forme de hash ;
- secrets hors Git ;
- MQTT prive et non expose ;
- emission LoRa par MQTT coupee au premier deploiement ;
- GPS exact interdit ;
- blocage/report des le MVP ;
- profils avec TTL ;
- admin protegee par token ;
- sauvegarde HDD et sauvegarde hors site a tester.

## Tests essentiels

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/stats
curl http://localhost:8000/api/active
meshtastic --port /dev/ttyACM0 --info
mosquitto_sub -h 127.0.0.1 -t 'adopte/mesh/#' -v
```

## Manifeste court

Adopte un Mesh n'est pas Tinder sur talkie-walkie. C'est un feu de camp numerique : la place publique Meshtastic reste ouverte, `ADOPT` devient la table de rencontre, le Pi garde les profils au chaud, et le MQTT reste derriere la porte blindee.
