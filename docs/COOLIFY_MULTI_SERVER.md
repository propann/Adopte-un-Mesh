# Coolify multi-serveurs — Pi 5 distant

## Verdict

Oui : une instance Coolify installee sur un autre serveur peut gerer le Raspberry Pi 5 comme serveur distant.

Coolify se connecte au Pi en SSH, deploie les conteneurs dessus, surveille leur etat et peut relancer/redeployer les ressources. Le serveur principal Coolify ne transporte pas automatiquement le trafic du site : le domaine doit pointer vers le Pi, son tunnel, ou un reverse proxy qui atteint le Pi.

## Architecture retenue

```txt
[Serveur A]
Coolify UI + orchestration
        |
        | SSH
        v
[Pi 5 chez Azoth]
Docker + HDD + radio USB
  - web
  - api
  - mosquitto prive
  - radio-bridge
```

## Conditions

- Raspberry Pi OS Lite 64-bit ou autre Linux ARM64 supporte ;
- SSH joignable depuis le serveur Coolify ;
- authentification SSH par cle ;
- Docker Engine 24+ ;
- utilisateur de deploiement autorise a utiliser Docker ;
- acces au groupe `dialout` pour la radio USB ;
- HDD monte avant tout deploiement ;
- chemins `/srv/adopte-un-mesh/*` crees ;
- architecture ARM64 prise en compte pour les builds.

## Ajouter le Pi dans Coolify

1. Dans Coolify : `Servers` puis `Add`.
2. Ajouter l'adresse IP ou le nom DNS du Pi.
3. Ajouter la cle SSH generee par Coolify dans `~/.ssh/authorized_keys` du compte cible.
4. Valider le serveur.
5. Verifier Docker et l'espace disque.
6. Creer un projet/environnement `adopte-un-mesh`.
7. Ajouter le depot GitHub.
8. Choisir le fichier Compose :

```txt
docker/compose.coolify.pi5.yml
```

9. Ajouter les variables d'environnement dans Coolify, jamais dans Git.
10. Assigner le domaine uniquement au service `web`, port interne `80`.

## Reseau et domaine

Le trafic public doit arriver sur le Pi, pas sur le serveur Coolify principal.

Solutions possibles :

- redirection NAT/port 443 vers le Pi ;
- adresse IPv6 publique ;
- Cloudflare Tunnel installe sur le Pi ;
- VPN/Tailscale + reverse proxy externe ;
- site public sur VPS et API/radio locale sur Pi, architecture plus complexe pour plus tard.

Pour le premier deploiement, le plus simple est un tunnel HTTPS vers le service web du Pi.

## Radio USB dans Coolify

Le conteneur `radio-bridge` doit recevoir le device reel :

```dotenv
MESHTASTIC_SERIAL_PORT=/dev/ttyUSB0
```

ou :

```dotenv
MESHTASTIC_SERIAL_PORT=/dev/ttyACM0
```

Verifier sur le Pi :

```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
id
```

Le compte et Docker doivent avoir acces au groupe `dialout`.

## Stockage persistant

Les donnees ne doivent pas rester dans un volume ephemere Coolify.

```txt
/srv/adopte-un-mesh/data
/srv/adopte-un-mesh/backups
/srv/adopte-un-mesh/mosquitto/data
/srv/adopte-un-mesh/mosquitto/log
```

Ces chemins peuvent etre des dossiers reels du HDD ou des liens vers `/mnt/adopte-hdd/adopte-un-mesh`.

## Builds ARM64

Le Pi est ARM64. Pour eviter les problemes :

- utiliser des images multi-architecture ;
- construire directement sur le Pi au debut ;
- ne pas utiliser un build server AMD64 pour produire une image ARM64 sans build multi-arch ;
- si plusieurs serveurs deploient la meme app, utiliser des architectures compatibles ou un registre multi-arch.

## Ce que Coolify gere

- clone Git ;
- build et redeploiement ;
- variables d'environnement ;
- logs conteneurs ;
- health checks ;
- proxy HTTPS ;
- redemarrage des services.

## Ce que Coolify ne regle pas seul

- montage du HDD ;
- droits USB/dialout ;
- configuration radio Meshtastic ;
- NAT de la box ;
- antenne et couverture RF ;
- sauvegarde hors site ;
- moderation des utilisateurs.

## Regle de production

Le service `web` est le seul service expose publiquement. L'API reste joignable via Nginx, Mosquitto reste interne, et le port serie reste uniquement monte dans `radio-bridge`.
