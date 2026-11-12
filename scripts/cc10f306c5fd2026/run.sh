#!/usr/bin/env bash
# Cron MENSAL CENTROVITA BRAÇO DO NORTE (unidade independente) — pacote gerencial
# Gera e envia: Relatório Gerencial (PDF + Excel) + Planilha de Indicadores do ano (PDF + Excel).
# Destino: vinicius@terceirizou.com.br · bcc financeiro@terceirizou.com.br
#
# Uso: [FORCE=1] [RETIFICAR=1] [DRY=1] ./run.sh [YYYY-MM-DD]   (default: hoje)
# Regras de segurança:
#   - guarda de competência: não regera nem reenvia o mesmo mês já entregue (FORCE=1 fura)
#   - o gerador TEM TRAVAS próprias: lista == balances em cada mês, fluxo fecha com a variação
#     do saldo e saldo do fluxo == balanceDone da licença — se abortar, não envia nada.
set -u
cd "$(dirname "$0")/../.." || exit 1

HOJE="${1:-$(date +%F)}"
DIA=$(python3 -c "import datetime; print(datetime.date.fromisoformat('$HOJE').strftime('%y%m%d'))")
ANO=$(python3 -c "import datetime; print(datetime.date.fromisoformat('$HOJE').year)")
DIR=scripts/relatorio_centrovita_bn
LOG=scripts/cc10f306c5fd2026/ultimo_run.log
REFARQ=scripts/cc10f306c5fd2026/.ultima_ref
STATEVI=scripts/cc10f306c5fd2026/.state_env
PDF="artifacts/${DIA}_Relatorio_Centrovita_BracoDoNorte.pdf"
XLSX="artifacts/${DIA}_Relatorio_Centrovita_BracoDoNorte.xlsx"
PDFI="artifacts/${DIA}_Indicadores_Centrovita_BN_${ANO}.pdf"
XLSXI="artifacts/${DIA}_Indicadores_Centrovita_BN_${ANO}.xlsx"

# competência = mês anterior fechado (calculado em python: neste pod o date -d é BusyBox)
REF=$(python3 -c "
import datetime
d = datetime.date.fromisoformat('$HOJE')
print((d.replace(day=1) - datetime.timedelta(days=1)).strftime('%Y-%m'))")

{
echo "=== run $(date -Iseconds) ref=$HOJE dia=$DIA competencia=$REF ano=$ANO ==="

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
  echo "--- relatório gerencial de $DIA já gerado, pulando geração ---"
else
  echo "--- gerar relatório gerencial ---"
  if python3 "$DIR/relatorio_centrovita_bn_caixa.py" "$HOJE"; then
    echo "gerencial OK"
  else
    echo "ERRO na geração do gerencial (travas? ver acima) — NADA será enviado."
    falhou=1
  fi
fi

if [ "$falhou" -eq 0 ] && { [ ! -s "$PDFI" ] || [ "${RETIFICAR:-0}" = "1" ]; }; then
  echo "--- gerar indicadores do ano ---"
  if python3 "$DIR/indicadores_centrovita_bn.py" "$ANO"; then
    echo "indicadores OK"
  else
    echo "AVISO: falha nos indicadores (ano $ANO) — o gerencial segue sozinho."
  fi
fi

if [ "$falhou" -ne 0 ] || [ ! -s "$PDF" ]; then
  echo "ABORTADO: sem pacote válido."
elif grep -qx "$DIA" "$STATEVI" 2>/dev/null && [ "${RETIFICAR:-0}" != "1" ]; then
  echo "--- envio de $DIA já concluído, pulando ---"
else
  echo "--- enviar ---"
  if HOJE="$HOJE" python3 "$DIR/enviar_gerencial_bn.py"; then
    echo "$DIA" >> "$STATEVI"
    echo "$REF $DIA" > "$REFARQ"
  else
    echo "ERRO no envio"
  fi
fi
echo "=== fim $(date -Iseconds) ==="
} >> "$LOG" 2>&1
tail -20 "$LOG"
