#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
KEY="$(openssl rand -base64 32 | tr -d '\n')"

if [[ ! -f "$ENV_FILE" ]]; then
  cp "$ROOT_DIR/.env.example" "$ENV_FILE"
fi

python3 - "$ENV_FILE" "$KEY" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
key = sys.argv[2]
lines = path.read_text(encoding="utf-8").splitlines()
out = []
replaced = False
for line in lines:
    if line.startswith("ADOPT_CHANNEL_PSK="):
        out.append(f"ADOPT_CHANNEL_PSK={key}")
        replaced = True
    else:
        out.append(line)
if not replaced:
    out.append(f"ADOPT_CHANNEL_PSK={key}")
path.write_text("\n".join(out) + "\n", encoding="utf-8")
PY

chmod 600 "$ENV_FILE"
echo "[OK] Cle ADOPT generee et stockee dans $ENV_FILE"
echo "[INFO] Ne jamais committer cette cle. Les zombies ont deja assez de privileges."
