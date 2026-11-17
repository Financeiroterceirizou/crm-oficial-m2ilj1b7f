#!/usr/bin/env bash
# Relatórios mensais FRATERNIDADE E HARMONIA — F e H (170068) + FILOSÓFICO (170069)
# Uso: [FORCE=1] ./run.sh [YYYY-MM-DD]   (default: hoje)
# Gera os 2 pacotes (PDF + Excel) e envia para financeirofeh@gmail.com
# Regras de segurança:
#   - resumível: pacote já gerado no dia é pulado; envio só com os 2 completos
#   - guarda de competência: não regera nem reenvia a mesma competência já entregue (FORCE=1 fura)
set -u
cd "$(dirname "$0")/../.." || exit 1
HOJE="${1:-$(date +%F)}"
# FIM_DATA=YYYY-MM-DD (ou 2o argumento) = rodada PARCIAL: fecha na data informada em vez do
# último dia do mês anterior. Serve para conferir o mês corrente no meio (ex.: 12/11/2026).
# Nesse modo a guarda de competência é ignorada de propósito e NÃO é gravada: a parcial não
# pode marcar a competência como entregue, senão o cron do dia 05 de dezembro seria pulado.
FIM_DATA="${FIM_DATA:-${2:-}}"
if [ -n "$FIM_DATA" ]; then HOJE="$FIM_DATA"; fi
DIA=$(python3 -c "import datetime; print(datetime.date.fromisoformat('$HOJE').strftime('%y%m%d'))")
DIR=scripts/relatorio_feh
LOG=$DIR/ultimo_run.log
STATEGER=$DIR/.state_ger
STATEEVI=$DIR/.state_env
REFARQ=$DIR/.ultima_ref

# competência entregue = mês anterior ao da data de referência
REF=$(python3 -c "
import datetime
d=datetime.date.fromisoformat('$HOJE')
print((d.replace(day=1)-datetime.timedelta(days=1)).strftime('%Y-%m'))")

{
echo "=== run $(date -Iseconds) ref=$HOJE dia=$DIA competencia=$REF ==="

# --- guarda de competência: antes de gerar qualquer coisa ---
if [ -n "$FIM_DATA" ]; then
  echo "MODO PARCIAL: recorte até $FIM_DATA — guarda de competência ignorada e não será gravada."
elif [ "${FORCE:-0}" != "1" ] && [ -s "$REFARQ" ]; then
  read -r REF_OLD DIA_OLD < "$REFARQ" || true
  if [ "${REF_OLD:-}" = "$REF" ]; then
    ATRAS=$(python3 -c "
import datetime
try:
    d0=datetime.datetime.strptime('${DIA_OLD:-0}','%y%m%d').date()
    d1=datetime.datetime.strptime('$DIA','%y%m%d').date()
    print((d1-d0).days)
except Exception:
    print(0)")
    if [ "${ATRAS:-0}" -ge 0 ]; then
      echo "PULADO: competência $REF já entregue em ${DIA_OLD} (há ${ATRAS}d) — nada gerado, nada enviado."
      echo "        (use FORCE=1 para reenviar de propósito)"
      echo "=== fim $(date -Iseconds) ==="
      exit 0
    fi
  fi
fi

# estado é por dia: virou o dia, zera
if [ "$(cat "$DIR/.state_dia" 2>/dev/null)" != "$DIA" ]; then
  rm -f "$STATEGER" "$STATEEVI"
  echo "$DIA" > "$DIR/.state_dia"
fi
touch "$STATEGER"

falhou=0
for P in feh filosofico; do
  if [ "$P" = "feh" ]; then ARQ="F_e_H"; else ARQ="Filosofico"; fi
  PDF="artifacts/${DIA}_Relatorio_Feh_${ARQ}.pdf"
  XLSX="artifacts/${DIA}_Relatorio_Feh_${ARQ}.xlsx"
  if grep -qx "$P" "$STATEGER" && [ -s "$PDF" ] && [ -s "$XLSX" ]; then
    echo "--- $P já gerado, pulando ---"
    continue
  fi
  echo "--- gerar $P ---"
  if FIM_DATA="$FIM_DATA" python3 $DIR/relatorio_feh.py "$HOJE" "$P"; then
    echo "$P" >> "$STATEGER"
  else
    echo "ERRO gerar $P"
    falhou=1
  fi
done

concluidos=$(sort -u "$STATEGER" | wc -l | tr -d ' ')
if [ "$concluidos" -lt 2 ] || [ "$falhou" -ne 0 ]; then
  echo "ABORTADO: só $concluidos/2 pacotes gerados — não envia nada nesta rodada."
elif grep -qx "$DIA" "$STATEEVI" 2>/dev/null; then
  echo "--- envio de $DIA já concluído, pulando ---"
else
  echo "--- enviar os 2 pacotes ---"
  if python3 $DIR/enviar_feh.py "$DIA" ambos; then
    echo "$DIA" >> "$STATEEVI"
    # parcial NÃO grava a competência: o fechamento do mês continua pendente para o cron
    [ -n "$FIM_DATA" ] || echo "$REF $DIA" > "$REFARQ"
  else
    echo "ERRO no envio"
  fi
fi
echo "=== fim $(date -Iseconds) ==="
} >> "$LOG" 2>&1
tail -40 "$LOG"
