# Protocole radio AM1

## Objectif

AM1 est un format texte tres court pour transporter des intentions sociales sur Meshtastic sans tuer le mesh.

La radio transporte l'etincelle. Elle ne transporte ni roman, ni photo HD, ni confession fiscale.

## Taille cible

- cible : moins de 120 caracteres ;
- maximum accepte API : 200 caracteres ;
- aucun secret ;
- aucune coordonnee GPS exacte.

## Prefixe

Tous les messages commencent par :

```txt
AM1
```

## Types

| Type | Sens |
|---|---|
| B | Beacon presence |
| L | Like / interet |
| M | Match |
| S | Signalement / safe |
| E | Evenement |
| I | Mini-image / avatar descriptor |

## Beacon

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
