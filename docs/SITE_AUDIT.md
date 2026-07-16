# Audit du site — Adopte un Mesh

> Un bon site local ne doit pas juste etre joli. Il doit guider une personne qui n'a jamais vu Meshtastic, rassurer quelqu'un qui arrive dans le Wi-Fi du bunker, et donner a l'admin de quoi eteindre les zombies avant qu'ils ne trouvent le bouton envoyer.

## 1. Etat apres refonte

Le site contient maintenant :

- une navigation claire : Radar, Balise, Radio, Securite, Admin ;
- une hero page qui explique la promesse ;
- un statut API ;
- des statistiques rapides : profils actifs, total, reports, evenements mesh 24h ;
- un radar social en cartes ;
- une creation de profil local ;
- des QR site, Wi-Fi et commandes radio ;
- les commandes Meshtastic et la config radio figee ;
- un test d'injection de payload mesh ;
- des actions sur profil : interet, signaler, bloquer ;
- un panneau admin local pour reports, evenements et matches ;
- une charte securite visible.

## 2. Ce qui etait faible avant

| Zone | Probleme | Correction faite |
|---|---|---|
| Navigation | une seule page sans reperes | topbar + ancres |
| Statut | simple texte API | stats bunker + health |
| Radar | liste basique | cartes profil + fraicheur + RSSI/SNR |
| Actions | pas de like/report/block visibles | boutons par profil |
| Radio | QR presents mais peu expliques | bloc QR + commandes + config |
| Admin | absent cote UI | panneau admin local |
| Test terrain | seulement curl dans README | injection payload depuis le site |
| Ton produit | sympa mais discret | univers feu de camp/bunker/zombie plus lisible |

## 3. Parcours cible MVP

### Nouvel utilisateur

1. Se connecte au Wi-Fi `Adopte Un Mesh`.
2. Ouvre `http://adopteunmesh.local`.
3. Comprend en 10 secondes que le projet est local, temporaire et sobre.
4. Cree une balise web.
5. Voit son identifiant public local.
6. Consulte les signaux actifs.
7. Envoie un interet doux.
8. Peut signaler/bloquer.

### Utilisateur radio

1. Scanne le QR du site ou Wi-Fi.
2. Consulte les commandes radio.
3. Configure `EU_868`, `LONG_FAST`, hop 3.
4. Garde le canal primaire public.
5. Ajoute `ADOPT` en secondaire.
6. Envoie un message `AM1` ou `MM1` court.
7. Le Pi range le profil et l'affiche.

### Admin local

1. Ouvre le panneau admin.
2. Renseigne `ADMIN_TOKEN` si active.
3. Consulte reports, evenements mesh, matches.
4. Bloque les profils problematiques.
5. Verifie les logs Docker si besoin.

## 4. Ce qui manque encore pour un vrai MVP terrain

### Priorite A — indispensable

- Auth locale minimale : code de session, PIN evenement ou token court.
- Page admin plus structuree : filtres reports, bouton fermer report, bouton quarantaine node.
- Persistence cote navigateur : afficher clairement `Mon ID : XXXX` et bouton oublier mon profil.
- Gestion des erreurs UX : messages inline au lieu d'alert partout.
- Verification front des champs sensibles : telephone, adresse, GPS, liens suspects.
- Nettoyage automatique visible : afficher quand un profil expire.
- Vrai QR natif Meshtastic partage depuis l'app officielle documente avec captures plus tard.

### Priorite B — solide

- Page evenement : nom evenement, QR evenement, TTL plus court, canal event.
- Filtre radar : intention, fraicheur, zone, tags.
- Avatar identicon SVG genere depuis `avatar_seed`.
- Messagerie web locale apres match.
- Export/suppression profil depuis l'interface.
- Mode hors-ligne PWA avec manifest et service worker.
- Theme clair/sombre optionnel si usage plein soleil.

### Priorite C — futur propre

- Moderation humaine avec badges locaux.
- Table `events` dediee.
- Role organisateur.
- Ecran sante radio : port serie, dernier paquet, RSSI moyen.
- Graphiques simples pour le mesh local.
- Internationalisation FR/EN.

## 5. Regles UX a garder

- Moins de swipe, plus de contexte.
- Pas de mecanique casino.
- Les boutons dangereux doivent etre explicites.
- Les donnees radio doivent rester courtes.
- L'utilisateur doit comprendre que le Pi est local.
- L'utilisateur doit comprendre que LoRa n'est pas un coffre-fort.
- Le style post-apo doit rester chaleureux, pas anxiogene.

## 6. Definition de site propre v1

Le site sera considere propre v1 quand :

- il tourne sur telephone sans zoom horizontal ;
- le statut API et les stats sont visibles ;
- le radar affiche au moins les faux paquets dry-run ;
- un profil web peut etre cree ;
- un like fonctionne ;
- un report apparait dans admin ;
- un block retire le profil du radar ;
- les QR site/Wi-Fi/radio s'affichent ;
- l'utilisateur voit les regles securite avant d'agir ;
- l'admin sait quoi regarder en cas de probleme.

## 7. Phrase produit

Adopte un Mesh est un feu de camp numerique : les radios disent qui est la, le Pi garde la memoire, le site rend la rencontre lisible, et les zombies n'ont droit qu'a une visite guidee.
