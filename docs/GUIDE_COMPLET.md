# Guide complet — Adopte un Mesh

> LoRa transporte l'etincelle. Le Raspberry Pi 5 garde le feu. Le site sert le cafe, et les zombies signent la charte avant d'entrer.

Ce guide est le document pivot du depot. Il explique quoi construire, comment le deployer sur Raspberry Pi 5 avec HDD, quels reglages Meshtastic figer, quelle base de site garder, et quelles limites respecter pour que le projet reste compatible, securise et viable sur le terrain.

## 1. Objectif produit

Adopte un Mesh est un systeme local de rencontre, presence et evenements base sur :

- des radios Meshtastic simples ;
- un Raspberry Pi 5 comme hub local ;
- un HDD/SSD pour les donnees persistantes ;
- une PWA locale accessible en Wi-Fi ;
- un radio-bridge USB qui ecoute les messages courts ;
- une base SQLite pour profils temporaires, reports, matches et logs techniques ;
- des QR codes pour simplifier l'acces au site, au Wi-Fi et aux commandes radio.

La promesse n'est pas de refaire Tinder dans LoRa. La promesse est plus maligne :

```txt
radio = presence courte
pi 5  = memoire locale
web   = profil confortable
admin = securite et moderation
```

## 2. Architecture cible

```txt
[Radio utilisateur / T-Deck / T-Beam]
        |
        | LoRa EU_868 / LongFast / messages courts AM1-MM1
        v
[Radio passerelle Meshtastic USB]
        |
        | USB serie /dev/ttyUSB0 ou /dev/ttyACM0
        v
[Raspberry Pi 5 + HDD]
        |-- radio-bridge Python
        |-- API FastAPI
        |-- SQLite persistante
        |-- PWA Nginx
        |-- Mosquitto local prive
        |-- portail Wi-Fi hostapd + dnsmasq
        |-- QR site / Wi-Fi / commandes radio
```

## 3. Regles d'or

1. Pas de GPS exact.
2. Pas de telephone par LoRa.
3. Pas de nom complet par LoRa.
4. Pas de photo brute par LoRa.
5. Pas de cle PSK reelle dans Git.
6. Pas de dependance au MQTT public pour le produit.
7. Pas de beacon bavard : LoRa est une bougie, pas un projecteur de stade.
8. Blocage et signalement visibles des le MVP.
9. Les profils radio expirent automatiquement.
10. Le Pi 5 reste le cerveau ; les radios restent compatibles Meshtastic.

## 4. Socle Pi 5

Voir aussi :

- `docs/PI5_SERVER.md`
- `docs/DOCKER_PI5.md`
- `docs/OPERATIONS_RUNBOOK.md`
- `docs/WIFI_AP_CAPTIVE_PORTAL.md`

Installation de base :

```bash
sudo apt update
sudo apt install -y git docker.io docker-compose-plugin python3 python3-pip hostapd dnsmasq nginx-light qrencode mosquitto-clients
sudo usermod -aG docker,dialout $USER
```

Preparation depot :

```bash
git clone https://github.com/propann/Adopte-un-Mesh.git
cd Adopte-un-Mesh
chmod +x scripts/*.sh
cp .env.example .env
```

Preparation HDD :

```bash
sudo HDD_MOUNT=/mnt/adopte-hdd ./scripts/install_pi5.sh
```

Demarrage :

```bash
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build
```

Verification :

```bash
./scripts/doctor.sh
curl http://localhost:8000/health
curl http://localhost:8080/api/health
```

## 5. Docker sur Pi 5

Les services Docker sont :

| Service | Role | Port |
|---|---|---|
| `api` | FastAPI + SQLite | 8000 interne/externe dev |
| `web` | Nginx + PWA + proxy `/api` | 8080 dev, 80 via AP/Nginx selon setup |
| `mosquitto` | MQTT local prive | 1883 |
| `radio-bridge` | USB Meshtastic -> API | pas de port public |

En mode Pi 5, les donnees API vont dans `/srv/adopte-un-mesh/data`, et le HDD peut porter `/mnt/adopte-hdd/adopte-un-mesh` via lien symbolique ou montage dedie.

Commandes utiles :

```bash
# lancer
./scripts/dev_up.sh

# arreter
./scripts/dev_down.sh

# logs
cd docker
docker compose logs -f api web radio-bridge mosquitto

# rebuild propre
docker compose down
docker compose up -d --build
```

## 6. Baseline Meshtastic figee

Voir aussi :

- `docs/MESHTASTIC_BASELINE.md`
- `docs/RADIO_QR_SETUP.md`
- `docs/RADIO_PROTOCOL.md`

Reglages par defaut France/Europe :

```txt
Region: EU_868
Preset: LONG_FAST
Hop limit: 3
TX power: 0 / legal default
Primary channel: LongFast/default public
Secondary channel: ADOPT
Secondary PSK: random / privee / jamais commitee
Position precision primary: 0 ou floutee selon evenement
MQTT public: off par defaut
Radio role mobile: CLIENT_MUTE ou CLIENT
Radio role passerelle fixe: CLIENT ou CLIENT_BASE
```

Commandes CLI de base :

```bash
meshtastic --set lora.region EU_868 --set lora.modem_preset LONG_FAST --set lora.hop_limit 3
meshtastic --ch-set psk default --ch-index 0
meshtastic --ch-set module_settings.position_precision 0 --ch-index 0
meshtastic --ch-set name ADOPT --ch-set psk random --ch-index 1
meshtastic --qr-all
meshtastic --info
```

Important : `meshtastic --qr-all` genere un QR/URL de canaux natif Meshtastic depuis la radio. C'est la methode la plus compatible pour partager une config entre radios. Les QR du site aident les humains ; le QR natif Meshtastic aide les radios.

## 7. Protocole radio projet

Deux formats sont acceptes au MVP :

### AM1 — format produit court

```txt
AM1 B K7Q2 AD zLN 900 <3
```

- `AM1` : protocole Adopte Mesh v1 ;
- `B` : beacon/profil minimal ;
- `K7Q2` : ID temporaire ;
- `AD` : intentions ;
- `zLN` : zone large ;
- `900` : TTL secondes ;
- `<3` ou `♡` : signature visuelle.

### MM1 — format prototype lisible

```txt
MM1|Pseudo|M/F|49|Photo,LoRa,Hacking|Dispo cafe au soleil
```

`MM1` est pratique pour tester, mais plus bavard. En public, preferer `AM1`.

## 8. Base du site

Voir aussi : `docs/SITE_BASELINE.md`.

Pages MVP :

1. Accueil / statut bunker.
2. Creation profil local.
3. Radar social : profils actifs.
4. QR : site, Wi-Fi, commandes radio.
5. Securite : blocage, signalement, charte.
6. Admin simple : reports, dernieres trames, etat radio.

Style : sombre, lisible, mobile-first, coeur radio, humour post-apo. Pas de swipe casino. L'interface doit etre une taverne de survivants propres, pas une machine a dopamine sous neon malade.

## 9. Donnees SQLite MVP

Tables principales :

- `profiles`
- `likes`
- `matches`
- `reports`
- `blocks`
- `mesh_events`

Regles :

- `last_seen` pilote l'affichage actif ;
- `active_until` expire les profils ;
- `rssi` et `snr` servent d'indicateurs techniques, pas de localisation exacte ;
- les reports restent admin ;
- les logs techniques doivent rester limites en duree.

## 10. QR codes

QR fournis par l'API :

```txt
/api/qr/site
/api/qr/wifi
/api/qr/radio-commands
/api/radio/config
/api/radio/commands
```

Script :

```bash
./scripts/generate_radio_qr.sh
```

Politique :

- QR Wi-Fi : standard Android/iOS ;
- QR site : URL locale ;
- QR commandes : lisible par humain ;
- QR Meshtastic natif : genere par `meshtastic --qr` ou `meshtastic --qr-all` depuis la radio configuree.

## 11. Securite

Voir :

- `SECURITY.md`
- `docs/SECURITY.md`
- `docs/PRIVACY.md`
- `docs/INCIDENT_RESPONSE.md`

Principes :

- reseau Wi-Fi ouvert uniquement en demo/evenement court ;
- Wi-Fi WPA2 recommande en installation longue ;
- pas d'administration exposee sur le Wi-Fi public ;
- sauvegardes regulieres ;
- logs anonymises ;
- moderation humaine pour reports ;
- PSK privees hors Git ;
- pas de piece d'identite en MVP ;
- pas de paiement ;
- pas de message sensible en clair.

## 12. Roadmap courte

Phase 1 : socle fonctionnel

- Docker demarre sur Pi 5 ;
- radio-bridge dry-run OK ;
- API health OK ;
- QR site/Wi-Fi OK ;
- profils `MM1` visibles.

Phase 2 : radio reelle

- connecter T-Beam/T3-S3/Heltec en USB ;
- `RADIO_DRY_RUN=false` ;
- recevoir un `AM1` ;
- recevoir un `MM1` ;
- stocker RSSI/SNR.

Phase 3 : site vivant

- page admin ;
- reports/blocages visibles ;
- bouton like ;
- matches ;
- avatars identicon par seed.

Phase 4 : evenement

- QR natif de canal ADOPT ;
- mode evenement ;
- profils temporaires ;
- charte publique ;
- moderation locale.

## 13. Test terrain minimal

1. Pi 5 allume.
2. HDD monte.
3. Docker OK.
4. PWA visible depuis telephone.
5. Radio USB visible dans `/dev/ttyUSB0` ou `/dev/ttyACM0`.
6. Radio reglee `EU_868` + `LONG_FAST`.
7. Canal ADOPT secondaire cree.
8. Envoi depuis une radio :

```txt
AM1 B TEST AD zLN 900 <3
```

9. Le profil apparait dans le site.
10. Le zombie est contenu.

## 14. Sources techniques a surveiller

- Documentation Meshtastic LoRa : https://meshtastic.org/docs/configuration/radio/lora/
- Documentation Meshtastic Channels : https://meshtastic.org/docs/configuration/radio/channels/
- Documentation CLI Meshtastic : https://meshtastic.org/docs/software/python/cli/
- Documentation MQTT Meshtastic : https://meshtastic.org/docs/software/integrations/mqtt/

Quand Meshtastic change, ce guide doit etre relu avant de modifier les commandes radio.
