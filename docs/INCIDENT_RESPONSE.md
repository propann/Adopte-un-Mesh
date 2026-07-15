# Reponse incident

## Incidents possibles

- spam radio ;
- harcelement ;
- profil mineur ;
- fuite de PSK ;
- Wi-Fi public abuse ;
- base corrompue ;
- radio passerelle compromise.

## Procedure rapide

```bash
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml stop radio-bridge
./scripts/backup_hdd.sh
```

Puis :

1. noter heure, symptome, node_id si disponible ;
2. bloquer/proteger les personnes ;
3. couper le canal ADOPT si PSK fuitee ;
4. regenerer une PSK `ADOPT` ;
5. publier un nouveau QR officiel evenement ;
6. conserver les reports utiles, purger le reste.

## Si harcelement

- bloquer le profil cible ;
- garder le report ;
- ne pas afficher publiquement les details ;
- si evenement physique : intervention humaine, pas juste techno.

## Si PSK fuitee

Une PSK fuitee est morte. On ne la soigne pas, on l'enterre.
