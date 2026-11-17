#!/usr/bin/env bash
# Cron "DREs Gerenciais UNILAGES por CC" (job 16c262aa2551ff3d) — dia 04 às 14:00.
# Gera 7 pacotes (PDF+Excel) — GERAL + 6 CCs — da DRE Gerencial da UNILAGES do mês
# anterior fechado, consolida em 1 Excel e envia 1 e-mail com os 7 PDFs + o Excel
# para henrique@terceirizou.com.br (Resend, from financeiro@).
#
# Esteira real: scripts/relatorio_unilages_v2/dre_unilages_cc.py
#                         /consolida_dre_cc.py  /enviar_dre_cc.py
#
# Guarda de envio: um mês de referência sai UMA vez (scripts/16c262aa2551ff3d/guard.py).
# Motivo: o fechamento do mês anterior ainda corre nos primeiros dias do mês; uma
# segunda rodada reenviaria o MESMO mês com números diferentes.
set -u
cd /home/ethos/.assistant/workspace || exit 1

STATE_DIR="scripts/16c262aa2551ff3d"
LOG="$STATE_DIR/ultima_rodada.log"
mkdir -p "$STATE_DIR" tmp

DIA=$(date +%y%m%d)
REF=$(python3 -c "from datetime import date,timedelta; d=date.today().replace(day=1)-timedelta(days=1); print(f'{d.year}-{d.month:02d}')")
REF_CURTA=$(python3 -c "from datetime import date,timedelta; d=date.today().replace(day=1)-timedelta(days=1); print(f'{d.year}{d.month:02d}')")
MES_REF="$REF-01"   # o gerador espera o PRIMEIRO DIA do mês de referência
CCS="geral correia_pinto curitibanos lages_bm_adm otacilio_costa sao_joaquim urubici"
# tag usada no nome do arquivo por dre_unilages_cc.py (só o geral é capitalizado)
tag_de() { [ "$1" = "geral" ] && echo "Geral" || echo "$1"; }

echo "=== $(date '+%Y-%m-%d %H:%M:%S') rodada DRE Unilages por CC — ref $REF ===" | tee "$LOG"

# ---------- 1. geração dos 7 pacotes ----------
falhou=""
for cc in $CCS; do
  ok=0
  TAG=$(tag_de "$cc")
  for tent in 1 2 3; do
    python3 scripts/relatorio_unilages_v2/dre_unilages_cc.py "$(date +%F)" "$MES_REF" "$cc" \
        > "tmp/unilages_dre_${cc}.log" 2>&1
    rc=$?
    if [ $rc -eq 0 ] && [ -s "artifacts/${DIA}_DRE_Unilages_${TAG}_${REF_CURTA}.pdf" ] \
                    && [ -s "artifacts/${DIA}_DRE_Unilages_${TAG}_${REF_CURTA}.xlsx" ]; then ok=1; break; fi
    echo "--- $cc tentativa $tent falhou (rc=$rc)" | tee -a "$LOG"
    tail -3 "tmp/unilages_dre_${cc}.log" | tee -a "$LOG"
    [ $tent -lt 3 ] && sleep 60
  done
  if [ $ok -ne 1 ]; then falhou="$falhou $cc"; fi
done

if [ -n "$falhou" ]; then
  echo "RESULTADO: FALHA na geração de:$falhou" | tee -a "$LOG"
  exit 1
fi
echo "gerados os 7 pacotes (PDF+Excel)" | tee -a "$LOG"

# ---------- 2. Excel consolidado ----------
if ! python3 scripts/relatorio_unilages_v2/consolida_dre_cc.py "$REF_CURTA" > tmp/unilages_consolida.log 2>&1; then
  echo "RESULTADO: FALHA ao consolidar o Excel" | tee -a "$LOG"
  tail -5 tmp/unilages_consolida.log | tee -a "$LOG"
  exit 1
fi
tail -1 tmp/unilages_consolida.log | tee -a "$LOG"

# ---------- 3. resumo numérico (para a guarda e para o relato) ----------
RESUMO=$(python3 - "$DIA" "$REF_CURTA" <<'PY'
import os, re, subprocess, sys
dia, ref = sys.argv[1], sys.argv[2]
ccs = ["Geral", "correia_pinto", "curitibanos", "lages_bm_adm", "otacilio_costa", "sao_joaquim", "urubici"]
partes = []
for cc in ccs:
    p = f"artifacts/{dia}_DRE_Unilages_{cc}_{ref}.pdf"
    txt = subprocess.run(["pdftotext", "-layout", p, "-"], capture_output=True, text=True).stdout
    def pega(rot):
        m = re.search(rot + r"\s+([\d.]+)\s+(-?R\$ [\d.,]+)", txt)
        return m.group(2).replace("R$ ", "").strip().replace(".", "").replace(",", ".") if m else "?"
    partes.append(f"{cc}: rec={pega('Total de Receitas')} desp={pega('Total de Despesas')} res={pega('Resultado do mês')}")
print(" | ".join(partes))
PY
)
echo "$RESUMO" > "$STATE_DIR/ultimo_resumo.txt"
echo "resumo: $RESUMO" | tee -a "$LOG"

# ---------- 4. guarda de envio ----------
python3 "$STATE_DIR/guard.py" check "$REF" | tee -a "$LOG"
ja_env="${PIPESTATUS[0]}"
if [ "$ja_env" -eq 3 ]; then
  python3 "$STATE_DIR/guard.py" diff "$REF" "$RESUMO" | tee -a "$LOG"
  echo "RESULTADO: SEM ENVIO — $REF já enviado antes; arquivos regenerados em artifacts/ para conferência" | tee -a "$LOG"
  exit 0
fi

# ---------- 5. envio (1 e-mail: 7 PDFs + Excel consolidado) ----------
envio=$(python3 scripts/relatorio_unilages_v2/enviar_dre_cc.py "$REF_CURTA" 2>&1)
rc_env=$?
echo "$envio" | tee -a "$LOG"
if [ $rc_env -ne 0 ]; then
  echo "RESULTADO: gerou os arquivos mas o ENVIO falhou (rc=$rc_env)" | tee -a "$LOG"
  exit 2
fi

ID=$(echo "$envio" | sed -n 's/.*resend id \([0-9a-f-]*\).*/\1/p')
python3 "$STATE_DIR/guard.py" record "$REF" "DRE_Unilages_por_CC_${REF_CURTA}" "${ID:-?}" "$RESUMO" | tee -a "$LOG"

echo "RESULTADO: OK — 7 PDFs + Excel consolidado enviados (ref $REF, resend ${ID:-?})" | tee -a "$LOG"
