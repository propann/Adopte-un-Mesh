# Roadmap MVP

## Phase 0 - Fondation

- Repo propre.
- Docker Compose.
- API health.
- Site statique.
- Mosquitto local.
- Radio bridge dry-run.
- Documentation Pi 5 + HDD.

## Phase 1 - Banc Pi 5

- Brancher radio Meshtastic USB.
- Mettre `RADIO_DRY_RUN=false`.
- Recevoir `AM1 B` depuis une radio.
- Voir le paquet dans `/mesh/inbound`.
- Afficher les profils actifs.

## Phase 2 - Produit social minimum

- Like depuis l'interface.
- Match mutuel visible.
- Signalement admin.
- Blocage utilisateur.
- Avatar identicon depuis seed.
- Export/suppression profil.

## Phase 3 - Communication differenciante

- Pack de messages courts avec coeur `<3` ou `♡`.
- Mode evenement `Feu de camp`.
- QR code pour rejoindre le site local.
- Carte post-apo des signaux.
- Badges locaux manuels.

## Phase 4 - Durcissement

- Auth locale.
- ACL Mosquitto.
- Sauvegardes HDD.
- Journal d'audit.
- Rate limits radio/API.
- Tests automatises.

## Phase 5 - Lab mini-image

- Identicon SVG.
- Tiny image monochrome 32x32 en canal prive.
- Chunking avec reassemblage.
- Tests duty-cycle.
- Abandon si le mesh tousse trop.
