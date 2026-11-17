#!/usr/bin/env bash
# Relatório Gerencial CENTROVITA (Mauro Ramos + Barra da Lagoa) — REGIME DE CAIXA
# Gera pacote único PDF + Excel: comparativo, mês anterior, despesas em aberto,
# previsão do mês corrente, fluxo 13m realizado e projeção 12m — por centro de custo
# e consolidado. Usa scripts/relatorio_centrovita_mr_caixa/relatorio_centrovita_caixa.py.
# Uso: ./run.sh [YYYY-MM-DD]      (default: hoje)
set -u
cd "$(dirname "$0")/../.." || exit 1
HOJE="${1:-$(date +%F)}"
exec python3 scripts/relatorio_centrovita_mr_caixa/relatorio_centrovita_caixa.py "$HOJE"
