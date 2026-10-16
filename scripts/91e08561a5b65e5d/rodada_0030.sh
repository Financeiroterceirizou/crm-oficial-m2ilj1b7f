#!/bin/bash
# Rodada completa 91e0856 (protocolo .mcp-fresh) em UM único exec call
# (contorno da falha de transporte: 1ª exec da sessão executa tudo).
cd /home/ethos/.assistant/workspace || exit 1
echo "=== fetch MCP live (JSON-RPC direto) ==="
python3 scripts/91e08561a5b65e5d/fetch_mcp_live_91e.py || exit 1
echo "=== validar_tmp (live vs estado) ==="
SPOT_DIR=tmp/polling ESTADO_PATH="$PWD/scripts/91e08561a5b65e5d/estado.json" python3 scripts/91e08561a5b65e5d/validar_tmp.py
V=$?
echo "=== validar exit: $V ==="
if [ $V -ne 0 ]; then
  rm -f tmp/polling/.mcp-fresh
  echo "ABORTAR: validar falhou - crus ficam em tmp/polling SEM marker para investigação"
  exit 1
fi
touch tmp/polling/.mcp-fresh
echo "=== run 1 ==="
bash scripts/91e08561a5b65e5d/run.sh
touch tmp/polling/.mcp-fresh
echo "=== run 2 ==="
bash scripts/91e08561a5b65e5d/run.sh
echo "=== estado ==="
python3 -c "import json; e=json.load(open('scripts/91e08561a5b65e5d/estado.json')); print({k:len(v) for k,v in e.items()})"
echo "=== fim ==="
