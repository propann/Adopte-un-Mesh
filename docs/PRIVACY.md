# Vie privee

Adopte un Mesh est concu pour minimiser les donnees.

## Donnees collectees MVP

- pseudo public ;
- intention ;
- tags ;
- bio courte ;
- age optionnel ;
- identifiant public temporaire ;
- RSSI/SNR radio si fournis ;
- dernier signal vu ;
- reports et blocks.

## Donnees non collectees

- GPS exact ;
- document d'identite ;
- telephone ;
- adresse ;
- photo brute via LoRa ;
- paiement.

## Retention conseillee

| Donnee | Duree conseillee |
|---|---|
| beacon/profil temporaire | 30 min a 24 h |
| logs techniques | 7 a 30 jours |
| reports | plus long, acces admin uniquement |
| messages web futurs | parametrable, suppression possible |

## Suppression

Le MVP doit evoluer vers : export profil, purge profil, purge messages, purge reports non necessaires.
