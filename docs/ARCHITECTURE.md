# Architecture - Adopte un Mesh

## Principe

Adopte un Mesh n'est pas Tinder sur LoRa. C'est une place de village locale :

- la radio signale une presence courte ;
- le Pi 5 heberge le site, l'API, la base, le broker MQTT et les logs ;
- le HDD garde les donnees persistantes ;
- la PWA donne le visage humain ;
- la moderation garde les zombies dehors.

## Flux general

```txt
Telephone / navigateur
        -> PWA http://adopte.mesh:8080
        -> API FastAPI :8000
        -> SQLite sur /srv/adopte-un-mesh/data
        -> Mosquitto local :1883
        -> radio-bridge
        -> radio Meshtastic USB
        -> Mesh EU_868 LongFast
```

## Services

| Service | Role |
|---|---|
| web | Interface mobile-first |
| api | Profils, likes, matches, reports, mesh inbound |
| mosquitto | Communication locale MQTT |
| radio-bridge | Lit les messages Meshtastic et les pousse vers l'API |
| HDD | Donnees, logs, sauvegardes |

## Stockage Pi 5 + HDD

Chemin standard : `/srv/adopte-un-mesh`.

Si un HDD est monte sur `/mnt/adopte-hdd`, le script `install_pi5.sh` bascule les donnees vers :

```txt
/mnt/adopte-hdd/adopte-un-mesh/
├── data
├── logs
├── mosquitto
└── backups
```

## Doctrine radio

- Region : EU_868.
- Preset : LongFast pour etre compatible avec le plus de monde.
- Canal public : rester compatible Meshtastic.
- Canal secondaire : ADOPT pour le projet.
- Pas de photo brute.
- Pas de GPS exact.
- Pas de donnees sensibles.

## Identite de communication

Le projet doit se reconnaitre meme dans un message minuscule :

```txt
AM1 B K7Q2 AD zLN 900 <3
AM1 B K7Q2 AD zLN 900 ♡
```

Le coeur `♡` ou `<3` devient la signature visuelle courte. C'est notre fanion dans le brouillard.
