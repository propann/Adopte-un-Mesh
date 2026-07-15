# Architecture

## Vision

Adopte un Mesh est une architecture locale-first : les radios Meshtastic transportent seulement des signaux courts, le Pi 5 stocke, organise et sert l'interface.

```txt
Radio Meshtastic mobile
  -> LoRa EU_868 LongFast
  -> Radio passerelle USB
  -> radio-bridge Python
  -> FastAPI
  -> SQLite sur HDD
  -> Nginx/PWA
  -> telephone connecte au Wi-Fi local
```

## Services

| Service | Role |
|---|---|
| web | interface statique mobile-first |
| api | profils, ingestion radio, QR, securite MVP |
| radio-bridge | ecoute Meshtastic USB et pousse vers API |
| mosquitto | bus local optionnel |
| nginx | web, proxy API, captive portal |

## Donnees persistantes

- `/srv/adopte-un-mesh/data/adoptmesh.sqlite3`
- `/srv/adopte-un-mesh/backups`
- `/srv/adopte-un-mesh/mosquitto/*`

## Pourquoi SQLite

MVP simple, robuste, backup facile, parfait pour un Pi 5. PostgreSQL viendra seulement quand le village deviendra une ville.

## Pourquoi pas de photo LoRa

LoRa est lent et partage l'air avec tout le monde. On transporte une graine d'avatar, pas une photo. Le zombie peut garder son selfie en local.
