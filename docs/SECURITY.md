# Securite et vie privee

## Regles du MVP

- Service reserve aux majeurs.
- Pas de GPS exact.
- Pas de nom complet sur LoRa.
- Pas de telephone sur LoRa.
- Pas de photo brute sur LoRa.
- Pas de paiement.
- Pas de verification biometrie maison.
- Blocage et signalement disponibles des le MVP.

## Donnees radio

Les messages AM1 sont consideres publics ou semi-publics. Meme si un canal est chiffre, on ne met rien de sensible dedans.

## Donnees serveur

SQLite MVP sur HDD local. Acces au Pi limite au LAN au debut.

## MQTT

Mosquitto est en anonymous local pour le MVP dev. Avant exposition reseau :

- password_file ;
- acl_file ;
- TLS ;
- pas de wildcard large pour clients externes.

## Anti-abus

- TTL presence.
- Rate limit beacon.
- Quarantaine profil/node.
- Liste reports admin.
- Logs anonymises.

## Rendez-vous humains

L'interface doit rappeler : lieu public, prévenir un proche, pas d'argent, pas de document d'identite, pas de pression.

Le mesh connecte. Il ne garantit pas que l'humain en face n'est pas un gobelin avec du parfum.
