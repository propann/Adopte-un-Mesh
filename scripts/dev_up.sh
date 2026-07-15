#!/usr/bin/env bash
set -euo pipefail
cp -n .env.example .env || true
docker compose -f docker/docker-compose.yml up --build
