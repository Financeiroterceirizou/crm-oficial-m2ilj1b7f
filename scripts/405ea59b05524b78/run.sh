#!/bin/bash
# Relatório mensal VISTORIAS licença EDJEL — 4 unidades + unificado (CC ADMINISTRATIVO).
# Gera para hoje e envia por e-mail (Resend) para vinicius@terceirizou.com.br.
cd "$(dirname "$0")/../.." || exit 1
HOJE=$(date +%F)
for UN in contagem_1 coronel_fabriciano ituiutaba_2 unai_2 unificado; do
  echo "=== EDJEL $UN ==="
  python3 scripts/relatorio_edjel/relatorio_edjel.py "$HOJE" "$UN" || echo "ERRO gerar $UN"
  python3 scripts/relatorio_edjel/enviar_edjel.py "$UN" || echo "ERRO enviar $UN"
done
echo "=== EDJEL fim ==="
