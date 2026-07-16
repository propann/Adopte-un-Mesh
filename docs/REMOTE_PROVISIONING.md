# Enrolement distant depuis l'ordinateur de l'utilisateur

## Objectif

Le Raspberry Pi 5 reste chez l'operateur et heberge le site, l'API et les profils. Chaque utilisateur branche sa propre radio Meshtastic en USB sur son propre ordinateur, puis passe par le site Adopte un Mesh pour la configurer et creer son profil.

Le Pi ne voit jamais directement le port USB distant. La communication avec la radio doit donc etre executee sur l'ordinateur de l'utilisateur.

## Architecture cible

```txt
Navigateur utilisateur
  -> HTTPS vers le site du Pi 5
  -> creation d'une session d'enrolement courte
  -> choix du profil radio: mobile, fixe, gateway

Radio USB branchee au PC utilisateur
  -> mode A: agent local Adopte un Mesh (recommande)
  -> mode B: Web Serial dans Chrome/Edge (progressif)

Agent ou navigateur
  -> lit le vrai node_id Meshtastic
  -> recupere un bundle de configuration signe depuis le Pi
  -> applique la configuration localement
  -> renvoie node_id + resultat au Pi

Pi 5
  -> verifie le jeton d'enrolement
  -> cree ou met a jour le profil unique lie au node_id
  -> invalide le jeton
```

## Pourquoi un agent local

Un serveur distant ne peut pas ouvrir `/dev/ttyUSB0` sur l'ordinateur d'un utilisateur. L'agent local est le moyen le plus compatible pour Windows, Linux et macOS :

- il utilise le CLI Meshtastic officiel ;
- il peut detecter les ports serie ;
- il applique tous les reglages ;
- il produit un rapport lisible ;
- il fonctionne meme lorsque Web Serial n'est pas disponible.

Le site reste obligatoire : l'agent ne choisit pas librement les reglages. Il telecharge un bundle d'enrolement genere par le Pi.

## Mode Web Serial

Le navigateur peut parler au port serie local uniquement si :

- le navigateur supporte Web Serial, principalement Chrome/Edge desktop ;
- la page est servie en HTTPS ;
- l'utilisateur clique volontairement sur `Connecter ma radio` ;
- l'utilisateur choisit le port dans la boite de dialogue du navigateur.

Ce mode ne doit pas etre le seul chemin. Safari/iPhone et plusieurs navigateurs ne conviennent pas.

## Flux utilisateur

1. Ouvrir le site public HTTPS du Pi.
2. Creer ou modifier son profil minimal.
3. Choisir l'usage radio : `MOBILE`, `FIXE`, `GATEWAY`.
4. Le Pi cree un jeton d'enrolement valable 10 minutes.
5. Brancher la radio USB sur le PC.
6. Lancer l'agent local ou le mode Web Serial.
7. L'outil lit le `node_id`.
8. L'outil applique le profil reseau Gaulix + canal secondaire `ADOPT`.
9. Le Pi lie ce `node_id` au profil.
10. Une nouvelle tentative avec le meme `node_id` met a jour le profil existant, sans doublon.

## Regles de securite

- HTTPS obligatoire pour le site public.
- Jeton d'enrolement aleatoire, usage unique, expiration courte.
- Le bundle ne doit etre telecharge qu'une fois.
- La PSK `ADOPT` n'apparait jamais dans Git ni dans les logs.
- Le node_id est unique dans SQLite.
- Le token de gestion du profil est affiche une seule fois puis stocke hashe.
- L'agent affiche toutes les commandes avant application en mode audit.
- Une option `--dry-run` est obligatoire.
- Aucune administration distante de la radio n'est activee par defaut.

## Endpoints a implementer

```txt
POST /api/enrollments
GET  /api/enrollments/{token}/bundle
POST /api/enrollments/{token}/complete
POST /api/enrollments/{token}/fail
```

Le bundle contient :

```json
{
  "expires_at": 0,
  "profile_mode": "MOBILE",
  "radio_profile": "GAULIX_ADOPT",
  "settings": {
    "region": "EU_868",
    "modem_preset": "LONG_MODERATE",
    "frequency_override_mhz": 869.4625,
    "hop_limit": 3,
    "primary_channel": "Fr_Balise",
    "primary_psk": "AQ==",
    "secondary_channel": "ADOPT",
    "secondary_psk": "delivered-over-https",
    "position_precision": 0
  }
}
```

## Principe fondamental

Le site decide. L'ordinateur de l'utilisateur execute. Le Pi valide et garde le profil. La radio reste physiquement sous le controle de son proprietaire.
