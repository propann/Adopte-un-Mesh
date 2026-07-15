# Protocole radio AM1 / MM1

## Objectif

AM1 est un format texte tres court pour transporter des intentions sociales sur Meshtastic sans tuer le mesh.

MM1 est un format compatible prototypage, plus lisible pour les premiers essais de fiche profil.

La radio transporte l'etincelle. Elle ne transporte ni roman, ni photo HD, ni confession fiscale.

## Taille cible

- cible : moins de 120 caracteres ;
- maximum accepte API : 220 caracteres ;
- aucun secret ;
- aucune coordonnee GPS exacte ;
- aucune donnee de contact directe.

## Prefixes

Messages natifs produit :

```txt
AM1
```

Messages de prototypage fiche profil :

```txt
MM1|
```

## Types AM1

| Type | Sens |
|---|---|
| B | Beacon presence |
| L | Like / interet |
| M | Match |
| S | Signalement / safe |
| E | Evenement |
| I | Mini-image / avatar descriptor |

## Beacon AM1

```txt
AM1 B K7Q2 AD zLN 900 <3
```

| Champ | Sens |
|---|---|
| K7Q2 | ID public temporaire |
| AD | intentions : ami/date |
| zLN | zone Lyon Nord |
| 900 | TTL secondes |
| <3 | signature visuelle courte |

## Profil MM1 compatible

Format :

```txt
MM1|Pseudo|Genre/Recherche|Age|Hobbies|Bio courte
```

Exemple :

```txt
MM1|Enzo|M/F|49|Photo,LoRa,Hacking|Dispo cafe au soleil
```

Le Pi 5 parse ce message, ajoute `last_seen`, `rssi`, `snr` et `node_id` quand Meshtastic les fournit, puis fait un UPSERT dans SQLite.

Regles :

- age minimum : 18 ;
- pseudo max : 32 caracteres ;
- bio max : 160 caracteres ;
- 8 hobbies maximum ;
- pas de telephone, pas d'adresse, pas de GPS exact ;
- MM1 est accepte pour le labo, AM1 reste le protocole produit.

## Like

```txt
AM1 L K7Q2 M9AA S
```

S = soft.

## Match

```txt
AM1 M K7Q2 M9AA R4T8
```

## Safe / report

```txt
AM1 S K7Q2 M9AA spam
```

## Evenement

```txt
AM1 E K7Q2 LYON01 300 ♡
```

## Mini-image descriptor

```txt
AM1 I K7Q2 s=A7F2 h=♡ p=neon-zombie
```

Le serveur genere un avatar depuis `s`, `h` et `p`.

## Pourquoi le coeur

`<3` marche partout, meme sur les vieux terminaux. `♡` donne une signature plus forte sur les clients modernes.

Regle : si un affichage casse Unicode, fallback automatique vers `<3`.

## Interdits

- nom complet ;
- telephone ;
- adresse ;
- GPS exact ;
- photo brute ;
- document d'identite ;
- demande d'argent.

## Doctrine finale

`MM1` permet d'aller vite sur le terrain. `AM1` permet de durer. Le jour ou le reseau commence a ressembler a une parade de zombies bavards, on raccourcit tout.
