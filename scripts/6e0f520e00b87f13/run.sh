#!/usr/bin/env bash
# Cron 6e0f520e00b87f13 — REDE SOS SC NORTE: relatório SEMANAL (toda sexta, 09:00)
# Gera PDF + Excel (consolidado pago 01→sexta, a pagar até fim do mês, contas a pagar do mês seguinte)
# e envia por Resend para henrique@terceirizou.com.br (bcc financeiro@).
set -uo pipefail
cd "$(dirname "$0")/../.." || exit 1
python3 scripts/relatorio_rede_sos/semanal_rede_sos.py --enviar
