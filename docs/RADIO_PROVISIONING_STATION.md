# Station USB d'enrolement radio

> Une radio, un profil. Le primaire public reste vivant. Le canal `ADOPT` ouvre la porte du bunker.

## Objectif

La station d'enrolement tourne sur le Raspberry Pi 5 ou sur une machine Linux de confiance. On branche une radio Meshtastic en USB, puis l'outil :

1. detecte le port serie ;
2. lit le veritable ID Meshtastic de la radio ;
3. applique la baseline `EU_868` + `LONG_FAST` + hop 3 ;
4. ne modifie pas le canal primaire public ;
5. configure le canal secondaire index 1 nomme `ADOPT` ;
6. applique la PSK privee stockee dans `.env` ;
7. coupe uplink/downlink MQTT sur `ADOPT` ;
8. desactive MQTT public ;
9. configure le nom et le role du node ;
10. cree ou met a jour un seul profil SQLite lie au `node_id` ;
11. affiche le QR natif Meshtastic des canaux ;
12. genere un token de gestion du profil affiche une seule fois.

## Principe d'identite

```txt
node_id Meshtastic unique
        |
        v
profil unique dans SQLite
```

La base cree un index unique partiel sur `profiles.node_id`.

- premiere connexion : creation du profil ;
- radio deja connue : mise a jour du meme profil ;
- impossible de creer deux profils avec le meme ID radio ;
- le public ID peut rester stable meme si le pseudo change.

Ce mecanisme limite les doublons, mais ne transforme pas l'ID Meshtastic en preuve cryptographique absolue. L'enrolement doit donc se faire physiquement sur une station de confiance, avec la radio branchee en USB.

## Installation de la station

```bash
cd Adopte-un-Mesh
sudo ./scripts/setup_provisioning_station.sh
sudo reboot
```

Le script installe :

- Python 3 ;
- `pipx` ;
- le CLI officiel `meshtastic` ;
- `openssl` ;
- `qrencode` ;
- `sqlite3` ;
- les droits `dialout` pour acceder au port serie.

Il genere aussi localement :

- `ADMIN_TOKEN` ;
- `PROFILE_TOKEN_PEPPER` ;
- `ADOPT_CHANNEL_PSK`.

Ces valeurs restent dans `.env`, avec permissions `600`.

## Enrolement interactif

Brancher une seule radio puis lancer :

```bash
./scripts/provision_radio.py
```

Le programme demande :

- pseudo public ;
- age ;
- genre/recherche ;
- intention ;
- tags ;
- bio courte ;
- zone floutee ;
- signature visuelle ;
- role radio.

Roles conseilles :

| Usage | Role |
|---|---|
| radio utilisateur mobile | `CLIENT_MUTE` en zone dense, sinon `CLIENT` |
| terminal T-Deck | `CLIENT` |
| passerelle Pi bien placee | `CLIENT_BASE` ou `CLIENT` |

Exemple non interactif :

```bash
./scripts/provision_radio.py \
  --port /dev/ttyACM0 \
  --pseudo Azoth \
  --age 49 \
  --recherche M/F \
  --intent date \
  --tags photo,lora,balade \
  --bio "Cafe solaire et zombies polis" \
  --zone lyon-nord \
  --heart '♡' \
  --role CLIENT
```

## Configuration appliquee

La station applique seulement les parametres communs necessaires :

```txt
Region          EU_868
Preset          LONG_FAST
Hop limit       3
Primary         conserve tel quel
Secondary #1    ADOPT
ADOPT PSK       cle privee locale
Position ADOPT  precision 0
MQTT ADOPT      uplink/downlink off
MQTT module     off
```

### Pourquoi ne pas reecrire le primaire

Le primaire public/default est ce qui donne le plus de chances de rester compatible avec les utilisateurs Meshtastic deja presents localement. La station ne le renomme pas et ne change pas sa PSK.

Cette regle est volontaire :

```txt
canal 0 = place publique Meshtastic
canal 1 = espace rencontre ADOPT
```

Les radios doivent avoir la meme region et le meme preset pour se voir au niveau radio. Pour lire le canal `ADOPT`, elles doivent aussi partager son nom et sa PSK.

## QR natif Meshtastic

A la fin, la station lance :

```bash
meshtastic --port /dev/ttyACM0 --qr-all
```

Ce QR doit etre traite comme un secret s'il contient le canal `ADOPT` prive. Ne pas le publier dans le depot ni sur un site public.

## Stockage du profil

Par defaut :

```txt
/srv/adopte-un-mesh/data/adoptmesh.sqlite3
```

Le chemin peut etre change avec :

```dotenv
HOST_DATABASE_PATH=/autre/chemin/adoptmesh.sqlite3
```

Le profil est cree avec :

- `node_id` unique ;
- `public_id` stable ;
- `avatar_seed` derive du node ID ;
- token de gestion stocke uniquement sous forme de hash ;
- date d'enrolement ;
- TTL du profil ;
- donnees minimales.

## Token de gestion

Le token est affiche une seule fois apres l'enrolement.

Il doit servir ensuite a :

- modifier le profil ;
- renouveler son TTL ;
- supprimer le profil ;
- revoquer le compte.

Le serveur ne stocke que son hash avec un pepper local.

## Procedure terrain

1. Verifier que la radio est bien le bon appareil.
2. Brancher une seule radio.
3. Lancer l'enrolement.
4. Noter le node ID et le public ID.
5. Donner le token de gestion a l'utilisateur, sur papier ou QR local temporaire.
6. Scanner le QR natif Meshtastic sur le telephone de l'utilisateur si necessaire.
7. Tester un message sur le primaire public.
8. Tester un message court sur `ADOPT`.
9. Verifier l'apparition du profil sur le site.
10. Debrancher la radio avant la suivante.

## Limites et securite

- La station doit etre administree par une personne de confiance.
- Ne jamais exposer le port serie a un navigateur public.
- Ne jamais afficher la PSK `ADOPT` dans les logs du site.
- Le QR des canaux doit etre temporaire et local.
- Le profil ne doit contenir ni adresse, ni telephone, ni GPS exact.
- Une sauvegarde chiffree de la base est recommandee.
- En cas de radio volee, l'admin doit bloquer le profil et faire tourner la PSK si la menace est serieuse.

## Test rapide

```bash
meshtastic --port /dev/ttyACM0 --info
./scripts/provision_radio.py --port /dev/ttyACM0
sqlite3 /srv/adopte-un-mesh/data/adoptmesh.sqlite3 \
  'SELECT node_id, public_id, display_name FROM profiles;'
```

Le resultat attendu : une seule ligne par `node_id`. Meme radio, meme profil. Le clone zombie reste dehors.
