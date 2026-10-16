#!/bin/bash
# Relatório Gerencial Mensal TERCEIRIZOU — cron dia 05 09:00 (id 82b14458305f8f1f)
# Gera PDF+Excel do mês anterior (v4, API Controlle) e envia via Resend.
# Idempotente: enviar.py usa Idempotency-Key com mtime do PDF — mesma chave+payload
# devolve o mesmo id (sem duplicar); PDF regenerado = reenvio legítimo.
set -u
cd "$(dirname "$0")/../.."

MES_REF=$(python3 -c "from datetime import date, timedelta; print((date.today().replace(day=1)-timedelta(days=1)).strftime('%Y-%m'))")
PDF="artifacts/relatorio-terceirizou-${MES_REF}.pdf"
XLSX="artifacts/relatorio-terceirizou-${MES_REF}.xlsx"

# Gera só se faltar arquivo (re-run no mesmo dia não refaz)
if [ ! -f "$PDF" ] || [ ! -f "$XLSX" ]; then
  python3 scripts/relatorio_mensal_terceirizou_v4.py || exit 1
fi

python3 scripts/relatorio_mensal/enviar.py "$PDF"
