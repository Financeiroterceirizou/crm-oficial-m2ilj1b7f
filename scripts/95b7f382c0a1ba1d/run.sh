#!/usr/bin/env bash
# Resumo diário da Captação de Leads — gera HTML e envia por e-mail (Resend).
# Desde 21/09 o envio é via API Resend (MCP gmail sem conta conectada no canal
# do cron — bloqueio de plataforma; ver MEMORY.md). Chave LOCAL em resend_key.txt.
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
cd "$AQUI"

python3 gerar_resumo.py
python3 enviar_email.py
