#!/usr/bin/env bash
set -euo pipefail

ok(){ printf '[OK] %s\n' "$1"; }
warn(){ printf '[WARN] %s\n' "$1"; }
fail(){ printf '[FAIL] %s\n' "$1"; exit 1; }

command -v docker >/dev/null && ok 'docker present' || fail 'docker absent'
docker compose version >/dev/null && ok 'docker compose present' || fail 'docker compose absent'
[ -f .env ] && ok '.env present' || warn '.env absent: cp .env.example .env'
[ -d /srv/adopte-un-mesh ] && ok '/srv/adopte-un-mesh present' || warn 'Pi data dir absent'
if ls /dev/ttyUSB* /dev/ttyACM* >/dev/null 2>&1; then ok 'radio serial candidate found'; else warn 'no /dev/ttyUSB* or /dev/ttyACM* found'; fi
curl -fsS http://localhost:8000/health >/dev/null 2>&1 && ok 'api reachable' || warn 'api not reachable yet'
curl -fsS http://localhost:8080/healthz >/dev/null 2>&1 && ok 'web reachable' || warn 'web not reachable yet'
printf 'Doctor fini. Si tout est vert, les zombies peuvent attendre.\n'
