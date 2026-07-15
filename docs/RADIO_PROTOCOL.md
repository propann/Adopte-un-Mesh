# Protocole radio

## Prefixes acceptes

| Prefixe | Usage |
|---|---|
| `AM1` | protocole produit Adopte un Mesh |
| `MM1|` | format prototype MeshMeet compatible humain |

## AM1 beacon

```txt
AM1 B K7Q2 AD zLN 900 <3
```

- `B` beacon profil ;
- `K7Q2` ID public temporaire ;
- `AD` intention ;
- `zLN` zone floutee ;
- `900` TTL ;
- `<3` signature compatible vieux clients.

## AM1 avatar descriptor

```txt
AM1 I K7Q2 s=A7F2 h=♡ p=neon-zombie
```

Le serveur reconstruit un avatar depuis seed + coeur + palette. Pas de photo brute.

## MM1 prototype

```txt
MM1|Pseudo|M/F|49|Photo,LoRa,Hacking|Dispo cafe au soleil
```

Accepte par le bridge pour tester vite. A ne pas utiliser sur canal public avec des donnees sensibles.

## Contraintes

- cible : 120 caracteres ;
- maximum API : 220 caracteres ;
- pas de secrets ;
- pas de GPS exact ;
- TTL court ;
- rate limit a renforcer en phase 2.
