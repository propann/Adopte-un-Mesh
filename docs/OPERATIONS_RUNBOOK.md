# Runbook exploitation

## Demarrer

```bash
cp .env.example .env
./scripts/dev_up.sh
```

Sur Pi 5 :

```bash
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build
```

## Observer

```bash
docker compose -f docker/docker-compose.yml logs -f api web radio-bridge
./scripts/doctor.sh
```

## Tester ingestion radio sans radio

```bash
curl -X POST http://localhost:8000/mesh/inbound \
  -H 'Content-Type: application/json' \
  -d '{"payload":"MM1|Azoth|M/F|49|Photo,LoRa,Hacking|Cafe solaire","node_id":"!demo","rssi":-67,"snr":7.5}'
```

## Basculer en vraie radio

`.env` :

```txt
RADIO_DRY_RUN=false
MESHTASTIC_SERIAL_PORT=/dev/ttyUSB0
```

Puis :

```bash
docker compose -f docker/docker-compose.yml -f docker/compose.pi5.yml up -d --build radio-bridge
```

## Sauvegarder

```bash
./scripts/backup_hdd.sh
```

## Incident simple

1. couper le Wi-Fi ouvert ;
2. arreter radio-bridge ;
3. sauvegarder la DB ;
4. lire `docs/INCIDENT_RESPONSE.md` ;
5. purger les profils problematiques si necessaire.
