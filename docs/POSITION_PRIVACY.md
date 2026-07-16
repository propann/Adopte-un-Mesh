# Politique de position et de vie privee

> On peut chercher des gens sans publier leur porte d'entree. Le GPS doit aider a comprendre une zone, jamais a designer une maison.

## 1. Regle produit

Adopte un Mesh n'autorise jamais la position exacte dans le parcours public d'enrolement.

La position Meshtastic est geree par canal. Le site et l'agent local appliquent une precision choisie, mais uniquement parmi des niveaux approuves.

## 2. Niveaux autorises

| Mode produit | Bits Meshtastic | Precision approximative | Usage |
|---|---:|---:|---|
| `off` | 0 | aucune position transmise | utilisateur tres prudent, profil web uniquement |
| `region` | 12 | environ 5,8 km | grande zone rurale ou evenement large |
| `city` | 13 | environ 2,9 km | valeur par defaut recommandee |
| `district` | 15 | environ 729 m | option avancee avec avertissement |

Le mode `city` est le compromis par defaut : assez flou pour ne pas designer une adresse, assez utile pour comprendre qu'une personne est dans la meme zone generale.

## 3. Modes interdits dans l'enrolement public

Les valeurs suivantes ne sont pas proposees dans l'interface publique :

- 16 bits ou plus ;
- 32 bits, precision complete ;
- coordonnees manuelles exactes ;
- position fixe exacte d'un domicile ;
- activation silencieuse du GPS ;
- partage automatique de vitesse, cap ou altitude personnelle.

Un eventuel mode precis futur devra etre :

1. reserve a une operation admin ;
2. temporaire ;
3. justifie par un usage clair ;
4. confirme deux fois ;
5. accompagne d'une date d'expiration ;
6. journalise sans stocker inutilement les coordonnees.

## 4. Application sur les canaux

Par defaut :

```txt
Canal public principal : city / 13 bits
Canal ADOPT secondaire : city / 13 bits
```

Une installation peut choisir :

```txt
Canal public principal : region / 12 bits
Canal ADOPT secondaire : off / 0 bit
```

Ce second profil est recommande pour les personnes qui veulent rester visibles sur le reseau public general sans transmettre de position dans le canal rencontre.

## 5. GPS local et diffusion radio

Deux notions doivent rester separees :

- le GPS de la radio peut etre utilise localement par l'appareil ;
- `position_precision` determine ce qui est effectivement transmis sur un canal.

Mettre `position_precision=0` empeche l'envoi de position sur ce canal. Cela ne doit pas etre presente comme une promesse de securite absolue pour toutes les autres fonctions de l'appareil : la configuration complete doit toujours etre verifiee apres provisioning.

## 6. Interface du site

Le formulaire d'enrolement affiche :

```txt
Aucune position
Zone large (~6 km)
Ville / secteur (~3 km) — recommande
Quartier large (~700 m) — avance
```

Le formulaire n'affiche jamais :

```txt
Position exacte
Maison
Adresse
Coordonnees GPS
```

Pour `district`, l'utilisateur doit cocher :

> Je comprends que cette precision peut aider a deduire ma zone de vie si je diffuse souvent depuis le meme endroit.

## 7. Protection contre les mauvaises utilisations

Le serveur doit :

- refuser les valeurs hors liste ;
- refuser 32 bits dans l'API publique ;
- refuser latitude/longitude dans les profils ;
- filtrer les bios contenant des coordonnees evidentes ;
- ne pas afficher de carte precise ;
- ne pas conserver d'historique de mouvement ;
- ne garder que la derniere zone floutee si le produit en a besoin ;
- limiter la frequence des beacons.

## 8. Valeurs d'environnement

```dotenv
ADOPT_POSITION_MODE=city
MESHTASTIC_PRIMARY_POSITION_PRECISION=13
MESHTASTIC_ADOPT_POSITION_PRECISION=13
ADOPT_ALLOW_PRECISE_POSITION=false
```

`ADOPT_ALLOW_PRECISE_POSITION` reste `false` en production normale.

## 9. Commandes CLI de reference

Exemple mode `city` :

```bash
meshtastic --ch-set module_settings.position_precision 13 --ch-index 0
meshtastic --ch-set module_settings.position_precision 13 --ch-index 1
```

Exemple canal ADOPT sans position :

```bash
meshtastic --ch-set module_settings.position_precision 0 --ch-index 1
```

## 10. Decision finale

La precision complete n'est pas une fonctionnalite sociale. C'est une information sensible.

Adopte un Mesh choisit donc :

```txt
flou par defaut
choix limite
aucun historique
jamais exact en public
```

Le coeur peut battre fort. La carte, elle, reste myope.
