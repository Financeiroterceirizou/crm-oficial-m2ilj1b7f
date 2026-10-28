#!/bin/bash
# AUTOMAÇÃO ÚNICA — Meta Ads → Planilha espelho → CRM Terceirizou
# Decisão do champion 28/10/2026: uma rodada por dia às 18h; Cora fora do escopo.
#
# Roda o script direto (sem agent_turn no caminho crítico): se o LLM estiver
# sem crédito, a sincronização continua acontecendo.
set -uo pipefail

WORKSPACE="/home/ethos/.assistant/workspace"
cd "$WORKSPACE" || exit 1

python3 scripts/sync_meta_diario/sync_meta_diario.py
RC=$?

# Relatório para o resumo da rodada
if [ -f scripts/sync_meta_diario/ultima_rodada.json ]; then
  echo "--- relatorio ---"
  cat scripts/sync_meta_diario/ultima_rodada.json
fi

exit $RC
