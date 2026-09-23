#!/bin/bash
# Polling Google Sheets → CRM Terceirizou (F1-T05)
# Called by cron job. Agent fetches MCP data → saves to tmp/polling/ → this script transforms + processes.
#
# Flow:
#   1. Agent receives cron trigger
#   2. Agent fetches 3 Google Sheets via MCP (cora, meta_ads_jun, meta_ads_cadastro)
#   3. Agent saves raw data to tmp/polling/{source}.json
#   4. This script: transform.py → processar.py (stdin JSON → CRM upsert)
#   5. Agent reports results
#
set -euo pipefail

WORKSPACE="/home/ethos/.assistant/workspace"
TMP="$WORKSPACE/tmp/polling"
SCRIPTS="$WORKSPACE/scripts"
LOG="$TMP/polling.log"

mkdir -p "$TMP"

echo "[$(date -Iseconds)] Polling start" >> "$LOG"

# Estado e leads_input isolados por job: o cron a5b0 roda o MESMO transform.py
# em paralelo — sem isolamento, os dois escreviam o mesmo leads_input.json e
# um lia JSON pela metade (JSONDecodeError) ou processava lote do outro.
export ESTADO_PATH="$SCRIPTS/91e08561a5b65e5d/estado.json"
export LEADS_INPUT_PATH="$SCRIPTS/91e08561a5b65e5d/leads_input.json"

# Step 1: Transform raw MCP data → leads_input.json (isolado por job)
# GUARDA (2026-09-23): o cron pode disparar sem a etapa de leitura MCP
# (tmp/polling vazio). Rodar o transform com tmp vazio gravava leads_input.json
# como {} e DESTRUIA o canônico (56 KB → 2 bytes), forçando reconstrução manual.
# Se nenhum arquivo cru existe, aborta ANTES do transform (canônico preservado).
if ! ls "$TMP"/cora.json "$TMP"/meta_ads_jun.json "$TMP"/meta_ads_cadastro.json >/dev/null 2>&1; then
  echo "[$(date -Iseconds)] Polling SKIP: tmp/polling sem arquivos crus (cron sem leitura MCP); leads_input.json canônico preservado." >> "$LOG"
  echo '{"skipped": true, "motivo": "tmp/polling vazio - leads_input canônico preservado"}'
  exit 0
fi

python3 "$SCRIPTS/91e08561a5b65e5d/transform.py" 2>> "$LOG"

# Step 2: Process leads → upsert to CRM
# O log de ações permanece no caminho padrão (o resumo diário 95b7f382c0a1ba1d o lê).
RESULT=$(cat "$LEADS_INPUT_PATH" | python3 "$SCRIPTS/captacao_leads/processar.py" 2>> "$LOG")

echo "$RESULT" >> "$LOG"
echo "[$(date -Iseconds)] Polling done" >> "$LOG"

# Output result for agent to report
echo "$RESULT"
