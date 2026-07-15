# Roadmap

## Phase 0 - Socle main

- API + PWA + Docker.
- Bridge Meshtastic USB.
- QR Wi-Fi/site/commandes.
- Docs securite et Pi 5.

## Phase 1 - Test Pi 5 reel

- Brancher radio USB.
- Verifier `/dev/ttyUSB0` ou `/dev/ttyACM0`.
- `RADIO_DRY_RUN=false`.
- Envoyer `MM1|...` depuis une radio.
- Verifier `/api/active`.

## Phase 2 - UX rencontre

- Bouton like dans interface.
- Page matches.
- Page reports/admin.
- Identicons SVG depuis avatar_seed.

## Phase 3 - Evenement

- QR evenement.
- Canal ADOPT prive avec PSK evenement.
- Badge local/verifie humainement.
- Purge auto fin d'evenement.

## Phase 4 - Durcissement

- Auth admin.
- MQTT ACL/password.
- Rate limit API + radio.
- Export/suppression profil.
- Sauvegarde chiffree.
