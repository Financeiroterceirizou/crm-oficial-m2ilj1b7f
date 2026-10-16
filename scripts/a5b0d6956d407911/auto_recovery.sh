#!/bin/bash
# Recuperação autônoma 18:20 — sonda o CRM a cada 60s; quando voltar, roda o pipeline (2 rodadas).
cd /home/ethos/.assistant/workspace
LOG=scripts/a5b0d6956d407911/recuperacao_1820.log
: > "$LOG"
for i in $(seq 1 12); do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 -X POST https://crm-oficial-65bb8.shrd00.internal.goskip.dev/api/collections/users/auth-with-password -H 'Content-Type: application/json' -d '{}' || echo 000)
  echo "$(date +%H:%M:%S) probe $i: $code" >> "$LOG"
  if [ "$code" != "503" ] && [ "$code" != "000" ]; then
    echo "CRM voltou — rodando pipeline" >> "$LOG"
    cp scripts/91e08561a5b65e5d/cache/cora.json scripts/91e08561a5b65e5d/cache/meta_ads_jun.json scripts/91e08561a5b65e5d/cache/meta_ads_cadastro.json tmp/polling_a5b0/
    touch tmp/polling_a5b0/.mcp-fresh
    echo "=== RODADA 1 ===" >> "$LOG"
    bash scripts/a5b0d6956d407911/run.sh >> "$LOG" 2>&1 || true
    cp scripts/91e08561a5b65e5d/cache/cora.json scripts/91e08561a5b65e5d/cache/meta_ads_jun.json scripts/91e08561a5b65e5d/cache/meta_ads_cadastro.json tmp/polling_a5b0/
    touch tmp/polling_a5b0/.mcp-fresh
    echo "=== RODADA 2 ===" >> "$LOG"
    bash scripts/a5b0d6956d407911/run.sh >> "$LOG" 2>&1 || true
    echo "FIM" >> "$LOG"
    exit 0
  fi
  sleep 60
done
echo "CRM NAO VOLTOU EM 12 MIN" >> "$LOG"
