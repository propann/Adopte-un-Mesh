# QR et configuration radio Meshtastic

Objectif : rendre la configuration terrain simple, sans casser la compatibilite avec le reseau Meshtastic existant.

## Doctrine ultra-compatible

- Region France/Europe : `EU_868`.
- Preset le plus compatible : `LONG_FAST`.
- Hop limit : `3`.
- Canal primaire : garder le canal public/default pour voir le plus de monde.
- Canal secondaire : `ADOPT` pour les signaux courts du projet.
- Position precision : `0` si on ne veut jamais envoyer la position, ou precision floutee si usage evenement.
- MQTT public : off par defaut.

## Commandes CLI recommandees

```bash
meshtastic --set lora.region EU_868 --set lora.modem_preset LONG_FAST --set lora.hop_limit 3
meshtastic --ch-set name LongFast --ch-set psk default --ch-index 0
meshtastic --ch-set module_settings.position_precision 0 --ch-index 0
meshtastic --ch-set name ADOPT --ch-set psk random --ch-index 1
meshtastic --info
```

Important : la commande `psk random` genere une cle privee. Il faut sauvegarder le resultat de `meshtastic --info` et le partager uniquement aux personnes autorisees.

## QR codes fournis par le projet

L'API expose :

```txt
/api/qr/site
/api/qr/wifi
/api/qr/radio-commands
```

Le script :

```bash
./scripts/generate_radio_qr.sh
```

genere :

```txt
qr-out/site.png
qr-out/wifi.png
qr-out/radio-commands.png
qr-out/radio-commands.txt
```

## Limite volontaire

Le projet ne pretend pas fabriquer un QR natif Meshtastic universel pour toutes les apps. Les apps Meshtastic changent et gerent les QR de canaux avec leurs propres formats internes. Pour un QR de canal natif, la methode la plus fiable reste :

1. configurer la radio dans l'app officielle ;
2. utiliser le partage/QR de canal officiel ;
3. scanner ce QR avec les autres clients.

Notre QR reste volontairement compatible : Wi-Fi standard, URL standard, texte de commandes standard.

## Rappels Meshtastic

- Les appareils doivent avoir la meme region et le meme modem preset pour communiquer pleinement.
- Les canaux vont de 0 a 7.
- Les noms de canaux et PSK doivent correspondre pour lire les messages.
- En Europe, respecter le duty cycle. Pas de spam amoureux : le coeur bat lentement.
