# Mini image de profil par mesh

## Verdict

Oui, on peut faire quelque chose qui ressemble a une image de profil par mesh.

Non, on ne doit pas envoyer une vraie photo brute par LoRa au MVP.

LoRa est une allumette, pas un camion de demenagement.

## Strategie retenue MVP

### 1. Avatar descriptor

On envoie une graine courte et une signature graphique :

```txt
AM1 I K7Q2 s=A7F2 h=♡ p=neon-zombie
```

Le site reconstruit un avatar localement :

- fond genere depuis `s` ;
- symbole `h` ;
- palette `p` ;
- motif identicon cote web.

Avantage :

- moins de 80 caracteres ;
- fiable ;
- joli ;
- compatible mesh ;
- pas de photo sensible.

## Strategie experimentale : tiny chunks

A tester seulement en canal prive evenement.

Format :

```txt
AM1 C K7Q2 img=A1 n=01/12 data=BASE64...
```

Problemes :

- beaucoup de paquets ;
- pertes probables ;
- duty cycle ;
- pollution du mesh ;
- abus facile.

Decision : **interdit sur canal public**.

## Idee visuelle differenciante

Au lieu d'une photo : une carte de signal.

Exemple :

```txt
♡ K7Q2
photo · balade · cafe
zone: lyon-nord
signal: vivant
```

Le profil devient un blason radio, pas une vitrine Instagram.

## Phase future

- generer identicon SVG cote web ;
- stocker vrais avatars sur Pi 5 uniquement ;
- echanger par QR code local pendant evenement ;
- compression monochrome 32x32 reservee aux labs.

## Regle zombie

Si ton image demande plus de dix paquets LoRa, ce n'est plus un avatar : c'est un cadavre reseau qui marche encore.
