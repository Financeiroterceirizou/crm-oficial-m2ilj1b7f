#!/usr/bin/env bash
# Cron MENSAL CENTROVITA TRINDADE — RELATÓRIO DE CAIXA
# Gera o pacote (PDF + Excel) e envia para vinicius@terceirizou.com.br.
# Destinos: vinicius@terceirizou.com.br + financeiroslcentrovitatrindade@gmail.com
#
# Uso: [FORCE=1] [RETIFICAR=1] [DRY=1] ./run.sh [YYYY-MM-DD]   (default: hoje)
# Regras de segurança:
#   - guarda de competência: não regera nem reenvia a mesma competência já entregue (FORCE=1 fura)
#   - resumível: geração e envio têm estado separado no dia
#   - o gerador TEM TRAVAS próprias: fluxo tem de fechar com a variação do saldo e a lista
#     tem de bater com o balances de cada centro de custo — se abortar, não envia nada.
set -u
cd "$(dirname "$0")/../.." || exit 1

HOJE="${1:-$(date +%F)}"
DIA=$(python3 -c "import datetime; print(datetime.date.fromisoformat('$HOJE').strftime('%y%m%d'))")
DIR=scripts/relatorio_centrovita_trindade
LOG=scripts/bef6dcfc68557d09/ultimo_run.log
REFARQ=scripts/bef6dcfc68557d09/.ultima_ref
STATEVI=scripts/bef6dcfc68557d09/.state_env
PDF="artifacts/${DIA}_Relatorio_Centrovita_Trindade.pdf"
XLSX="artifacts/${DIA}_Relatorio_Centrovita_Trindade.xlsx"

# competência = mês anterior fechado (calculado em python: neste pod o date -d é BusyBox)
REF=$(python3 -c "
import datetime
d = datetime.date.fromisoformat('$HOJE')
print((d.replace(day=1) - datetime.timedelta(days=1)).strftime('%Y-%m'))")

{
echo "=== run $(date -Iseconds) ref=$HOJE dia=$DIA competencia=$REF ==="

if [ "${DRY:-0}" = "1" ]; then
  echo "DRY=1: só diagnostico, nada e gerado nem enviado."
  echo "  competencia: $REF"
  echo "  guarda atual: $(cat "$REFARQ" 2>/dev/null || echo '(vazio)')"
  echo "  pacote de hoje: $(ls -la "$PDF" 2>/dev/null | awk '{print $5" bytes"}' || echo '(nao existe)')"
  echo "=== fim $(date -Iseconds) ==="
  exit 0
fi

if [ "${FORCE:-0}" != "1" ] && [ -s "$REFARQ" ]; then
  read -r REF_OLD DIA_OLD < "$REFARQ" || true
  if [ "${REF_OLD:-}" = "$REF" ] && [ "${RETIFICAR:-0}" != "1" ]; then
    echo "PULADO: competência $REF já entregue em ${DIA_OLD:-?} — nada gerado, nada enviado."
    echo "        (use FORCE=1 para regerar/reenviar de propósito)"
    echo "=== fim $(date -Iseconds) ==="
    exit 0
  fi
fi

falhou=0
if [ -s "$PDF" ] && [ -s "$XLSX" ] && [ "${RETIFICAR:-0}" != "1" ]; then
  echo "--- pacote de $DIA já gerado, pulando geração ---"
else
  echo "--- gerar ---"
  if python3 "$DIR/relatorio_centrovita_trindade.py" "$HOJE"; then
    echo "gerado OK"
  else
    echo "ERRO na geração (travas de consistência? ver acima) — NADA será enviado."
    falhou=1
  fi
fi

if [ "$falhou" -ne 0 ] || [ ! -s "$PDF" ]; then
  echo "ABORTADO: sem pacote válido."
elif grep -qx "$DIA" "$STATEVI" 2>/dev/null && [ "${RETIFICAR:-0}" != "1" ]; then
  echo "--- envio de $DIA já concluído, pulando ---"
else
  echo "--- enviar ---"
  if HOJE="$HOJE" python3 "$DIR/enviar_trindade.py"; then
    echo "$DIA" >> "$STATEVI"
    echo "$REF $DIA" > "$REFARQ"
  else
    echo "ERRO no envio"
  fi
fi
echo "=== fim $(date -Iseconds) ==="
} >> "$LOG" 2>&1
tail -25 "$LOG"
