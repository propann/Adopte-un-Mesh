# Mission Codex

Objectif : prendre cette base `main`, la tester sur Pi 5 et rendre le MVP utilisable en evenement local.

## Taches prioritaires

1. Lancer Docker en local et corriger tout build fail.
2. Tester API `/health`, `/api/active`, `/api/qr/site`.
3. Brancher une radio Meshtastic USB.
4. Passer `RADIO_DRY_RUN=false`.
5. Envoyer `MM1|Pseudo|M/F|49|Photo,LoRa|Cafe` depuis une radio.
6. Verifier creation/UPSERT du profil.
7. Ajouter bouton like et page matches.
8. Ajouter page admin reports.
9. Generer identicons SVG depuis `avatar_seed`.
10. Ajouter tests pytest.

## Contraintes

- Ne jamais commiter `.env`.
- Ne pas ajouter GPS exact.
- Ne pas envoyer de photo brute par LoRa.
- Garder `EU_868 + LONG_FAST` comme defaut France.
- Toute nouvelle commande Pi doit etre documentee dans `docs/OPERATIONS_RUNBOOK.md`.
