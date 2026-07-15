# Base du site — PWA Adopte un Mesh

Ce document definit la base produit du site local. Il sert de reference UX, fonctionnelle et technique pour eviter que le projet derive en usine a gaz sentimentale avec des zombies dans les formulaires.

## 1. Role du site

Le site n'est pas Meshtastic. Le site est la couche humaine au-dessus du mesh.

Il doit :

- afficher les profils captes localement ;
- permettre de creer un profil web temporaire ;
- afficher les QR utiles ;
- expliquer comment rejoindre le canal ADOPT ;
- montrer les signaux recents ;
- permettre blocage et signalement ;
- servir de portail evenement ;
- fonctionner sur telephone sans app native.

## 2. Principes UX

1. Mobile-first.
2. Peu de boutons.
3. Texte court.
4. Pas de swipe infini.
5. Pas de dopamine casino.
6. Statut reseau visible.
7. Securite accessible en un clic.
8. Ton post-apo doux : coeur, radio, bunker, zombie, mais lisible.

Phrase produit :

```txt
Je suis la, pas loin, disponible pour parler, sans livrer mon adresse au brouillard.
```

## 3. Pages MVP

### Accueil

Contenu :

- logo/sigil coeur `♡` ou `<3` ;
- phrase : `LoRa transporte l'etincelle. Le Pi 5 garde le feu.` ;
- statut API ;
- bouton creer profil ;
- bouton radar social ;
- bouton QR.

### Profil local

Champs :

- pseudo court ;
- age optionnel, 18+ seulement ;
- intention : ami/date/balade/photo/event ;
- tags ;
- bio courte ;
- coeur/avatar ;
- duree de visibilite.

Regles :

- pas de nom complet ;
- pas de numero de telephone ;
- pas d'adresse ;
- bio 160 caracteres max ;
- profil temporaire.

### Radar social

Affiche :

- profils actifs ;
- fraicheur : vert < 10 min, orange < 30 min, gris au-dela ;
- RSSI/SNR si disponible ;
- zone large ;
- tags ;
- bouton like ;
- bouton report ;
- bouton block.

### QR

Affiche :

- QR site ;
- QR Wi-Fi ;
- QR commandes radio ;
- lien vers doc radio ;
- rappel : pour un vrai QR Meshtastic natif, utiliser l'application officielle ou `meshtastic --qr-all`.

### Securite

Affiche :

- charte rapide ;
- blocage ;
- signalement ;
- conseils rendez-vous public ;
- rappel : pas de transfert d'argent ;
- rappel : ne pas partager coordonnees exactes.

### Admin MVP

Affiche :

- reports ouverts ;
- derniers mesh_events ;
- etat radio bridge ;
- nombre profils actifs ;
- logs courts ;
- bouton quarantaine future.

## 4. API cible du site

Endpoints existants/importants :

```txt
GET  /api/health
GET  /api/profiles
GET  /api/active
POST /profiles
POST /mesh/inbound
GET  /api/radio/config
GET  /api/radio/commands
GET  /api/qr/site
GET  /api/qr/wifi
GET  /api/qr/radio-commands
```

A ajouter ensuite :

```txt
POST /api/profiles/{id}/like
POST /api/profiles/{id}/block
POST /api/profiles/{id}/report
GET  /api/admin/reports
GET  /api/admin/mesh-events
POST /api/admin/quarantine/{node_id}
```

## 5. Composants UI

### Carte profil

```txt
[♡] Pseudo · age optionnel
intention · zone · tags
bio courte
fraicheur: vert/orange/gris
RSSI/SNR si disponible
[like] [report] [block]
```

### Carte radio

```txt
Region: EU_868
Preset: LONG_FAST
Canal principal: public/default
Canal ADOPT: secondaire
QR natif: meshtastic --qr-all
```

### Carte bunker

```txt
API: OK
Radio bridge: dry-run / real
MQTT: local
HDD: mounted
Dernier signal: 12:42
Zombies: contenus
```

## 6. Style visuel

Palette actuelle :

- fond noir bleute ;
- rose/rouge coeur ;
- vert signal ;
- orange alerte ;
- gris poussiere radio.

Mots-clefs :

```txt
bunker social
feu de camp numerique
coeur radio
signal faible, intention forte
zombies contenus
pirate radio propre
```

## 7. Donnees affichees et donnees cachees

Afficher :

- pseudo ;
- age optionnel ;
- intention ;
- tags ;
- bio courte ;
- zone large ;
- fraicheur ;
- RSSI/SNR technique ;
- contact_hint mesh.

Ne pas afficher publiquement :

- IP ;
- logs bruts complets ;
- node_id complet si pas utile ;
- reports detailles ;
- cle PSK ;
- chemin base de donnees ;
- secrets `.env`.

## 8. Accessibilite

- contrastes forts ;
- boutons larges ;
- pas d'information uniquement par couleur ;
- texte court ;
- compatible petit ecran ;
- fallback coeur `<3` si Unicode casse.

## 9. Definition du MVP accepte

Le site est acceptable quand :

1. il s'ouvre sur mobile ;
2. `/api/health` repond ;
3. il affiche les profils dry-run ;
4. il affiche les profils `MM1` entrants ;
5. il affiche les QR ;
6. il explique comment configurer les radios ;
7. il montre clairement les regles de securite ;
8. il ne demande pas de donnees sensibles.

## 10. Futures pages

- Evenements locaux ;
- badges verifies localement ;
- conversations web apres match ;
- admin moderation avancee ;
- export/suppression profil ;
- mode installation festival/atelier ;
- generation d'avatars SVG depuis `avatar_seed`.

## 11. Phrase UX de garde-fou

Si une fonctionnalite demande beaucoup de LoRa, elle doit probablement etre cote web.

Si une fonctionnalite demande une donnee sensible, elle doit probablement etre supprimee.

Si un zombie comprend le bouton sans manger le Pi, l'UX est bonne.
