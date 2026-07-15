# Securite technique

## Menaces principales

| Risque | Reponse MVP |
|---|---|
| Harcelement | block/report immediat |
| Stalking | pas de GPS exact, position precision 0 par defaut |
| Spam LoRa | messages courts, prefixe filtre, longueur max |
| Fuite de secret | `.env` ignore, pas de PSK dans Git |
| MQTT expose | broker local, ACL a activer en prod |
| Perte de HDD | backups SQLite |

## Donnees interdites par radio

- nom complet ;
- telephone ;
- adresse ;
- coordonnees GPS exactes ;
- photo brute ;
- document d'identite ;
- demande d'argent.

## Politique PSK

- Primary public : default uniquement pour compatibilite.
- Secondary `ADOPT` : `psk random` pour les tests prives/evenements.
- Ne jamais publier une PSK privee dans GitHub.

## Logs

Les logs doivent aider a diagnostiquer sans exposer les personnes. Conserver peu, anonymiser, purger regulierement.

## Mesures Pi 5

- `ufw` actif ;
- `fail2ban` actif si SSH expose ;
- pas d'admin sur Wi-Fi public ouvert ;
- sauvegardes hors appareil ;
- mise a jour systeme ;
- mots de passe uniques.
