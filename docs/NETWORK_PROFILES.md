# Profils reseau Meshtastic

## Decision produit

Le profil principal pour la France est `GAULIX_ADOPT`.

Gaulix est une communaute nationale structuree qui harmonise les parametres Meshtastic et MeshCore. Son interet pour Adopte un Mesh est immediat : une radio nouvellement configuree rejoint un reseau francophone deja organise, puis utilise `ADOPT` comme canal secondaire rencontre.

## Contrainte importante

Une radio Meshtastic n'utilise qu'un seul ensemble de parametres LoRa a la fois : region, preset, frequence et slot. Tous les canaux logiques de la radio partagent ces parametres physiques.

Donc :

- `Fr_Balise` et `ADOPT` peuvent fonctionner ensemble sur une seule radio ;
- Gaulix et le LongFast mondial ne peuvent pas fonctionner simultanement sur une seule radio s'ils utilisent des presets ou frequences differents ;
- pour ecouter les deux mondes en meme temps, il faut deux radios.

## Profil GAULIX_ADOPT

```txt
Region: EU_868
Preset: LONG_MODERATE
Frequency override: 869.4625 MHz
Hop limit: 3
Primary channel: Fr_Balise
Primary PSK: AQ==
Secondary channel: ADOPT
Secondary PSK: privee, fournie par le Pi
Override duty cycle: false
```

Ce profil devient la valeur par defaut pour la France tant que les tests terrain autour de Lyon ne montrent pas un autre reseau local plus actif.

## Profil CLASSIC_LONGFAST_ADOPT

Profil de secours ou de voyage :

```txt
Region: EU_868
Preset: LONG_FAST
Frequency override: none
Hop limit: 3
Primary channel: LongFast/default
Primary PSK: AQ==
Secondary channel: ADOPT
Secondary PSK: privee
Override duty cycle: false
```

Attention : le canal `ADOPT` de ce profil ne communique pas avec `ADOPT` sur le profil Gaulix si le preset/frequence radio differents.

## Profils d'usage

### MOBILE

```txt
Role: CLIENT_MUTE en zone dense, sinon CLIENT
Rebroadcast: LOCAL_ONLY si supporte
NodeInfo interval: 14400 s
Position: off par defaut
Bluetooth: actif
Wi-Fi: off
MQTT: off
```

### FIXE

```txt
Role: CLIENT ou CLIENT_BASE selon emplacement
Rebroadcast: LOCAL_ONLY
NodeInfo interval: 14400 s
Position: manuelle et floutee, ou off
Bluetooth: selon besoin
Wi-Fi: off sauf gateway
MQTT: off
```

### GATEWAY

```txt
Role: CLIENT
USB permanent vers Pi
Position: off ou floutee
Wi-Fi/MQTT public: off
Broker local Pi: autorise
Radio bridge: actif
```

## Regle d'exploitation

Le profil reseau est choisi par le Pi lors de l'enrolement. L'utilisateur choisit uniquement son usage : mobile, fixe ou gateway. Les parametres critiques ne sont pas librement modifiables dans le formulaire public.
