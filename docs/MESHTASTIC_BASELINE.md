# Baseline Meshtastic — reglages figes

Ce document definit la configuration radio de reference pour Adopte un Mesh en France.

## 1. Decision

Le profil par defaut est maintenant :

```txt
GAULIX_ADOPT
```

La radio rejoint le reseau communautaire francophone Gaulix sur son canal primaire, puis ajoute `ADOPT` comme canal secondaire dedie a la rencontre.

Adopte un Mesh ne fork pas Meshtastic au MVP. On utilise le firmware officiel, l'app officielle, le Web Client officiel ou le CLI officiel.

## 2. Configuration France principale

```txt
Region: EU_868
Modem preset: LONG_MODERATE
Frequency override: 869.4625 MHz
Hop limit: 3
Transmit power: 0 / legal default
Override duty cycle: false
Primary channel: Fr_Balise
Primary PSK: AQ==
Secondary channel: ADOPT
Secondary PSK: privee, generee et distribuee par le Pi
Position precision: 0 par defaut
MQTT public: desactive par defaut
```

## 3. Pourquoi Gaulix

Gaulix cherche a harmoniser les reglages des communautes francaises. L'objectif produit est qu'une personne qui vient de configurer sa radio puisse voir un reseau existant tout de suite, puis disposer de notre canal `ADOPT` sur la meme couche radio.

Le profil exact doit rester modifiable cote administration, car la densite RF reelle depend toujours de la zone. Un test terrain Lyon/Neyron doit confirmer la reception locale.

## 4. Contrainte physique

Une radio Meshtastic n'utilise qu'un seul preset et une seule frequence a la fois. Les canaux 0 a 7 sont logiques et partagent la meme couche LoRa.

Donc :

```txt
Fr_Balise + ADOPT sur profil Gaulix = oui
LongFast mondial + ADOPT LongFast = oui
Gaulix + LongFast mondial en simultane sur une seule radio = non
```

Pour ecouter Gaulix et LongFast en parallele, utiliser deux radios.

## 5. Profil de secours

Le profil `CLASSIC_LONGFAST_ADOPT` reste disponible pour les zones ou LongFast est reellement plus actif :

```txt
Region: EU_868
Preset: LONG_FAST
Frequency override: none
Hop limit: 3
Primary: LongFast/default
Primary PSK: AQ==
Secondary: ADOPT
Secondary PSK: privee
```

Ne pas melanger les QR des deux profils : un canal `ADOPT` sur Gaulix ne communique pas avec un canal `ADOPT` sur LongFast si la couche radio differe.

## 6. Profils d'usage

| Usage | Role conseille | Comportement |
|---|---|---|
| Mobile zone dense | `CLIENT_MUTE` | ne relaie pas inutilement |
| Mobile zone peu dense | `CLIENT` | usage normal |
| Fixe maison | `CLIENT` | stable, faible bavardage |
| Fixe point haut valide | `CLIENT_BASE` | seulement apres test terrain |
| Gateway Pi 5 | `CLIENT` | USB permanent, MQTT local uniquement |

Ne pas mettre tout le monde en router. Un mauvais router, c'est un zombie avec megaphone dans un tunnel.

## 7. Reglages de sobriete

```txt
NodeInfo interval: 14400 s minimum
Position: off par defaut
Position fixe: manuelle et floutee si necessaire
Smart position mobile: seulement si consentement explicite
MQTT public: off
Override duty cycle: false
```

## 8. Canal ADOPT

`ADOPT` transporte uniquement :

- presence courte ;
- mini profil ;
- coeur ;
- event ;
- safe/report ;
- signaux de match tres courts.

La PSK reste hors Git. Elle est fournie dans un bundle d'enrolement court via HTTPS.

## 9. Messages projet

```txt
AM1 B K7Q2 AD zLN 900 <3
AM1 I K7Q2 s=A7F2 h=♡ p=neon-zombie
```

Le format `MM1|...` reste reserve aux prototypes et tests locaux.

## 10. Cadence

| Message | Cadence max |
|---|---|
| Presence normale | 10-15 min |
| Presence evenement | 3-5 min |
| Like | action utilisateur uniquement |
| Match | notification unique |
| Safe/report | action utilisateur uniquement |
| Avatar | inscription puis rare |

## 11. Enrolement distant

Le Pi 5 heberge le site et decide du profil. La radio est branchee sur l'ordinateur de l'utilisateur.

Deux modes sont prevus :

1. agent local utilisant le CLI Meshtastic, recommande ;
2. Web Serial Chrome/Edge desktop, en mode progressif.

Voir `docs/REMOTE_PROVISIONING.md`.

## 12. QR

Le QR natif Meshtastic doit etre genere apres application de la configuration :

```bash
meshtastic --qr
meshtastic --qr-all
```

La PSK `ADOPT` pouvant etre incluse, ce QR doit etre traite comme un secret de groupe.

## 13. Interdits MVP

- fork firmware ;
- photo brute sur LoRa ;
- GPS exact ;
- PSK dans Git ;
- beacon agressif ;
- override duty cycle ;
- administration radio distante ouverte ;
- modification libre des parametres critiques par un utilisateur public.

## 14. Sources a verifier avant changement

- Documentation Meshtastic LoRa et canaux ;
- CLI Meshtastic ;
- documentation Gaulix actuelle ;
- carte et tests terrain autour de la zone de deploiement.
