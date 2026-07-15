# Baseline Meshtastic — reglages figes

Ce document definit la configuration radio de reference pour Adopte un Mesh. Le but est d'etre ultra-compatible avec le reseau Meshtastic existant tout en ayant un canal secondaire propre au projet.

## 1. Doctrine

Adopte un Mesh ne fork pas Meshtastic au MVP.

On utilise :

- firmware Meshtastic officiel ;
- app officielle ou CLI officielle ;
- region legale locale ;
- preset commun ;
- canal primaire compatible ;
- canal secondaire `ADOPT` pour les signaux projet ;
- messages courts `AM1` ou `MM1`.

Le custom firmware viendra seulement quand le produit sera deja vivant. D'abord la route, ensuite le bolide.

## 2. Configuration France/Europe

```txt
Region: EU_868
Modem preset: LONG_FAST
Use preset: true
Hop limit: 3
Transmit power: 0 / legal default
Override duty cycle: false
Primary channel: LongFast/default public
Primary PSK: default
Secondary channel: ADOPT
Secondary PSK: random/private
Position precision: 0 by default
MQTT public: disabled by default
```

## 3. Pourquoi ces choix

### EU_868

La region `EU_868` correspond a l'Union Europeenne 868 MHz. Elle applique une limite duty cycle de 10%. Le firmware Meshtastic stoppe les emissions si la limite est atteinte. Donc : beacons lents, messages courts, pas de spam romantique.

### LONG_FAST

`LONG_FAST` est le preset par defaut. C'est le meilleur compromis de depart entre portee et vitesse. Il est aussi celui qui donne le plus de chances de rejoindre un reseau local existant.

### Hop limit 3

Meshtastic indique que le hop limit par defaut est 3 et qu'il convient a la plupart des cas. On garde 3 pour eviter de transformer chaque like en expedition interdepartementale.

### Canal primaire public

Le canal primaire sert aux emissions automatiques comme position/telemetrie. Pour maximiser la compatibilite, on garde le primaire public/default ou equivalent local, puis on ajoute `ADOPT` en secondaire.

### Canal secondaire ADOPT

`ADOPT` porte les signaux projet :

- presence courte ;
- mini profil ;
- coeur ;
- event ;
- safe/report ;
- tests controles.

La PSK doit etre aleatoire et partagee via QR Meshtastic officiel ou canal de confiance.

## 4. Commandes CLI de reference

Detecter la radio :

```bash
meshtastic --info
```

Configurer LoRa :

```bash
meshtastic --set lora.region EU_868 --set lora.modem_preset LONG_FAST --set lora.hop_limit 3
meshtastic --set lora.tx_power 0
meshtastic --set lora.override_duty_cycle false
```

Configurer canal primaire :

```bash
meshtastic --ch-set psk default --ch-index 0
meshtastic --ch-set module_settings.position_precision 0 --ch-index 0
```

Ajouter/configurer canal ADOPT :

```bash
meshtastic --ch-set name ADOPT --ch-set psk random --ch-index 1
meshtastic --ch-set module_settings.position_precision 0 --ch-index 1
meshtastic --ch-set uplink_enabled false --ch-index 1
meshtastic --ch-set downlink_enabled false --ch-index 1
```

Generer QR natif Meshtastic :

```bash
meshtastic --qr
meshtastic --qr-all
```

Exporter/verifier :

```bash
meshtastic --info
meshtastic --nodes
```

## 5. Roles radio recommandes

| Usage | Role conseille | Notes |
|---|---|---|
| Utilisateur mobile | `CLIENT` ou `CLIENT_MUTE` | `CLIENT_MUTE` en zone dense |
| Gateway Pi 5 USB | `CLIENT` | simple, stable |
| Node fixe haut place | `CLIENT_BASE` | si vraiment utile |
| Routeur pur | eviter au MVP | uniquement si site radio excellent |

Ne pas mettre tout le monde en router. Un mauvais router, c'est un zombie avec megaphone dans un tunnel.

## 6. Messages radio projet

### Beacon AM1

```txt
AM1 B K7Q2 AD zLN 900 <3
```

### Profil prototype MM1

```txt
MM1|Pseudo|M/F|49|Photo,LoRa,Hacking|Dispo cafe au soleil
```

### Mini avatar descriptor

```txt
AM1 I K7Q2 s=A7F2 h=♡ p=neon-zombie
```

## 7. Frequnce d'emission conseillee

| Message | Cadence max |
|---|---|
| Presence normale | 10-15 min |
| Presence evenement | 3-5 min |
| Like | action utilisateur uniquement |
| Match | notification unique |
| Safe/report | action utilisateur uniquement |
| Mini avatar | a l'inscription puis rare |

## 8. Position et vie privee

Par defaut :

```bash
meshtastic --ch-set module_settings.position_precision 0 --ch-index 0
meshtastic --ch-set module_settings.position_precision 0 --ch-index 1
```

Si evenement ou cartographie floutee : choisir une precision faible, par exemple autour de plusieurs km. Ne jamais utiliser precision complete pour de la rencontre publique.

## 9. MQTT

Pour le produit :

```txt
MQTT public Meshtastic: off
Mosquitto local Pi: yes
Uplink/downlink public: off
JSON MQTT: debug seulement
```

Raison : le MQTT public Meshtastic a des restrictions et une politique zero-hop ; il n'est pas le bus produit d'Adopte un Mesh. Le Pi 5 utilise son broker local comme outil interne.

## 10. QR et partage de config

Trois niveaux :

1. QR Wi-Fi : connecter au Pi ;
2. QR site : ouvrir la PWA ;
3. QR Meshtastic natif : partager les canaux et reglages radio.

Le QR natif Meshtastic doit venir de :

```bash
meshtastic --qr-all
```

ou de l'application officielle.

## 11. Matos cible

| Materiel | Role ideal |
|---|---|
| LilyGO T-Beam | node mobile/gateway test |
| LilyGO T3-S3 | gateway USB Pi 5 |
| LilyGO T-Deck / T-Deck Plus | terminal terrain graphique |
| Heltec LoRa V3/V4 | node simple / test |
| RAK nRF52 | node basse conso |

## 12. Interdits MVP

- fork firmware ;
- photo brute sur LoRa ;
- GPS exact ;
- PSK dans Git ;
- beacon < 3 minutes ;
- MQTT public comme dependance ;
- custom frequency ;
- override duty cycle.

## 13. Sources officielles a verifier avant changement

- LoRa Configuration : https://meshtastic.org/docs/configuration/radio/lora/
- Channel Configuration : https://meshtastic.org/docs/configuration/radio/channels/
- Python CLI : https://meshtastic.org/docs/software/python/cli/
- MQTT : https://meshtastic.org/docs/software/integrations/mqtt/
