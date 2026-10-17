#!/usr/bin/env bash
# Sobe o backend e um túnel HTTPS do Cloudflare e mostra a URL para colar no console da Alexa.
#   ./skill/subir.sh
# A URL do túnel rápido muda a cada execução: atualize o endpoint no console sempre que rodar.
set -euo pipefail

cd "$(dirname "$0")/.."
PORTA="${PORTA:-8000}"
LOG_TUNEL="$(mktemp)"
CLOUDFLARED="$(command -v cloudflared || echo "$HOME/.local/bin/cloudflared")"

.venv/bin/uvicorn backend.app:app --port "$PORTA" &
SERVIDOR=$!
"$CLOUDFLARED" tunnel --no-autoupdate --url "http://localhost:$PORTA" >"$LOG_TUNEL" 2>&1 &
TUNEL=$!
trap 'kill $SERVIDOR $TUNEL 2>/dev/null; rm -f "$LOG_TUNEL"' EXIT

URL=""
for _ in $(seq 1 40); do
  URL="$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' "$LOG_TUNEL" | head -1 || true)"
  [ -n "$URL" ] && break
  sleep 1
done
[ -z "$URL" ] && { echo "O túnel não subiu. Log em $LOG_TUNEL"; exit 1; }

echo
echo "Endpoint para o console da Alexa:  $URL/alexa"
echo "Ctrl+C para parar."
echo
wait "$SERVIDOR"
