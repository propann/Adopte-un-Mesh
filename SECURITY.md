# Security Policy

Adopte un Mesh manipule des signaux sociaux locaux. Meme si le projet est fun, les risques sont reels : harcelement, localisation, spam, faux profils, fuite de messages.

## Regles non negociables

- Pas de GPS exact.
- Pas de nom complet, telephone, adresse ou document d'identite dans LoRa.
- Pas de photo brute dans LoRa.
- Pas de secret dans Git.
- Pas de dependance au MQTT public pour le produit.
- Profils temporaires et TTL courts.
- Blocage et signalement actifs des le MVP.

## Reporter une faille

Ouvrir une issue GitHub si la faille ne contient pas de secret. Pour une faille sensible, contacter le mainteneur hors canal public et ne pas publier de preuve exploitable.

## Surface sensible

- Pi 5 expose en Wi-Fi local.
- API locale FastAPI.
- Mosquitto local.
- Radio Meshtastic USB.
- Base SQLite sur HDD.
- QR codes de configuration.

## Durcissement minimum Pi 5

```bash
sudo ./scripts/harden_pi5.sh
```

En production longue duree : WPA2 sur le Wi-Fi, MQTT avec mot de passe/ACL, admin separe, sauvegardes chiffrees, mises a jour regulieres.
