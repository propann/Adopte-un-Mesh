# Compatibilite materiel

## Cible MVP

| Role | Materiel conseille |
|---|---|
| Gateway Pi 5 USB | LilyGO T3-S3, T-Beam, Heltec ESP32 LoRa |
| Terminal terrain | T-Deck / T-Deck Plus |
| Node mobile basse conso | nRF52 / RAK / T-Echo |
| Relais fixe | ESP32 ou nRF52 avec bonne antenne |

## Regles

- Firmware Meshtastic officiel en priorite.
- Region `EU_868` en France.
- Preset `LONG_FAST` pour compatibilite generale.
- Pas de firmware custom au MVP.
- Pas de MeshCore dans le reseau produit Meshtastic : test labo seulement.

## Port USB

Le bridge cherche un port declare dans `.env` :

```txt
MESHTASTIC_SERIAL_PORT=/dev/ttyUSB0
```

Verifier :

```bash
ls /dev/ttyUSB* /dev/ttyACM*
```

## T-Deck

Excellent terminal graphique. Utiliser firmware officiel recent avec Meshtastic UI/BaseUI quand disponible. Pour Adopte, le T-Deck sert surtout de terminal terrain, pas de serveur.
