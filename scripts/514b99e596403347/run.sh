#!/bin/bash
# RELATÓRIO MENSAL SÃO LOURENÇO (L & R) VISTORIA — mensal, dia 04 14:00
# (1) gera PDF+Excel do mês anterior (relatórios 1 e 2 em competência)
# (2) envia para vinicius@terceirizou.com.br via Resend
# Guarda de competência: já enviado o mesmo mês de referência -> não reenvia.
#   FORCE=1 fura sem marcar; RETIFICAR=1 reenvia marcando [RETIFICAÇÃO].
set -u
cd "$(dirname "$0")/../.." || exit 1
DIR="scripts/514b99e596403347"
LOG="$DIR/ultimo_run.log"
mkdir -p "$DIR"

REF=$(python3 - <<'PY'
from datetime import date
d = date.today().replace(day=1)
p = d.replace(year=d.year-1, month=12) if d.month == 1 else d.replace(month=d.month-1)
print(p.strftime("%Y-%m"))
PY
)

ULT=$(cat "$DIR/.ultima_ref" 2>/dev/null || true)
if [ "$ULT" = "$REF" ] && [ "${FORCE:-0}" != "1" ] && [ "${RETIFICAR:-0}" != "1" ]; then
  echo "SKIP: competência $REF já enviada (ver $DIR/enviados.json). Use FORCE=1 ou RETIFICAR=1 para reenviar."
  exit 0
fi

echo "=== run $(date '+%F %T') ref=$REF retif=${RETIFICAR:-0} ===" >> "$LOG"
python3 scripts/relatorio_sao_lorenco/relatorio_sao_lorenco.py >> "$LOG" 2>&1
G=$?
python3 scripts/relatorio_sao_lorenco/enviar_sao_lorenco.py >> "$LOG" 2>&1
E=$?
echo "=== fim gerar=$G enviar=$E ===" >> "$LOG"

if [ "$G" = "0" ] && [ "$E" = "0" ]; then
  echo "$REF" > "$DIR/.ultima_ref"
  python3 - "$REF" "${RETIFICAR:-0}" <<'PY'
import json, os, sys
from datetime import datetime
ref, retif = sys.argv[1], sys.argv[2]
p = "scripts/514b99e596403347/enviados.json"
d = json.load(open(p)) if os.path.exists(p) else {}
d.setdefault(ref, []).append({"enviado_em": datetime.now().strftime("%Y-%m-%d %H:%M"),
                              "retificacao": retif == "1"})
json.dump(d, open(p, "w"), indent=1, ensure_ascii=False)
PY
fi

tail -20 "$LOG"
