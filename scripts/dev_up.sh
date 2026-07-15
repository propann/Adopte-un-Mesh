#!/usr/bin/env bash
set -euo pipefail
docker compose -f docker/docker-compose.yml up -d --build
printf 'Bunker demarre: http://localhost:8080\n'
