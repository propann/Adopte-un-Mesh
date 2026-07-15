# Mission Codex - prochaine passe

## Objectif

Transformer ce bootstrap en MVP testable sur Raspberry Pi 5 + HDD + radio Meshtastic USB.

## Taches prioritaires

1. Lancer `docker compose -f docker/docker-compose.yml up --build`.
2. Corriger les erreurs de build.
3. Ajouter tests API : health, creation profil, active profiles, like mutuel, report.
4. Ajouter identicon SVG cote web depuis `avatar_seed`.
5. Ajouter bouton like dans la PWA.
6. Ajouter page admin reports.
7. Connecter radio-bridge a Meshtastic reel via `/dev/ttyUSB0`.
8. Ajouter endpoint `/mesh/outbound` pour envoyer un message AM1.
9. Ajouter rate-limit API simple.
10. Ajouter sauvegarde HDD `scripts/backup.sh`.

## Contraintes

- Ne pas envoyer de photo brute par LoRa.
- Ne pas changer le primary Meshtastic public par defaut.
- Garder ADOPT en canal secondaire.
- Ne pas mettre de secret dans le depot.
- Garder le ton post-apocalyptique propre.

## Commit conseille

```txt
feat: harden pi5 mvp and radio bridge
```
