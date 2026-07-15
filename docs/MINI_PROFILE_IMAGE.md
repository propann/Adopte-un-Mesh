# Mini image de profil

## Decision MVP

Pas de photo brute par LoRa. On transmet un descripteur court :

```txt
AM1 I K7Q2 s=A7F2 h=♡ p=neon-zombie
```

## Pourquoi

LoRa est partage, lent et limite. Une photo tue le reseau. Une graine d'avatar donne une identite visuelle sans transporter d'image.

## Strategie

1. `s` : seed courte ;
2. `h` : coeur/symbole ;
3. `p` : palette ;
4. le site genere un identicon local.

## Option labo

Chunk image uniquement en reseau prive/evenement, rate-limit strict, jamais sur canal public.
