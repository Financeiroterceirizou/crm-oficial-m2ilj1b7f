#!/bin/bash
# Rodada de polling a5b0 — protocolo .mcp-fresh completo em UMA execução
# (contorno da anomalia de transporte: escritas em tmp/polling_a5b0 somem entre
# chamadas exec na mesma sessão — executar tudo em um único script bash).
# Base: rodada_1320.sh, sem o append hardcoded no execucoes.log (o log recebe
# a linha com os números REAIS após a rodada, via append_file do agente).
set -uo pipefail
cd /home/ethos/.assistant/workspace

echo "=== RODADA a5b0 $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "--- 1) fetch MCP live (JSON-RPC direto) ---"
python3 scripts/a5b0d6956d407911/fetch_mcp_live.py || { echo "FETCH FALHOU"; exit 1; }

echo "--- 2) extract/save live (comparação live x canônico) ---"
python3 scripts/a5b0d6956d407911/save_live_cora.py tmp/polling_a5b0/mcp_artifacts/cora_live.json || { echo "CORA DIVERGE"; exit 1; }
python3 scripts/a5b0d6956d407911/extract_live_jun_cad.py tmp/polling_a5b0/mcp_artifacts/jun_cad_live.json || { echo "JUN/CAD DIVERGE"; exit 1; }

echo "--- 3) validar_tmp (91e0856, com fix 13-col) ---"
SPOT_DIR="$PWD/tmp/polling_a5b0" ESTADO_PATH="$PWD/scripts/a5b0d6956d407911/estado.json" \
  python3 scripts/91e08561a5b65e5d/validar_tmp.py || { echo "VALIDAR_TMP FALHOU"; exit 1; }

echo "--- 4) touch .mcp-fresh + run.sh rodada 1 ---"
touch tmp/polling_a5b0/.mcp-fresh
bash scripts/a5b0d6956d407911/run.sh 2>&1 | tail -5

echo "--- 5) touch .mcp-fresh + run.sh rodada 2 ---"
touch tmp/polling_a5b0/.mcp-fresh
bash scripts/a5b0d6956d407911/run.sh 2>&1 | tail -5

echo "--- 6) estado final ---"
python3 - <<'EOF'
import json
est = json.load(open('scripts/a5b0d6956d407911/estado.json'))
for k in ('cora','meta_ads_jun','meta_ads_cadastro'):
    src = est.get(k, {})
    n = sum(len(v) if isinstance(v, list) else 1 for v in src.values())
    print(f'{k}: {n} hashes em {len(src)} chaves')
EOF

echo "FIM OK"