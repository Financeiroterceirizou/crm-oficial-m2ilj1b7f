#!/usr/bin/env bash
# Resumo diário da Captação de Leads — gera HTML com dashboard e envia por e-mail.
# Canal de envio: Resend API (domínio próprio terceirizou.com.br).
# O MCP gmail NÃO funciona aqui: sem conta conectada no canal do cron (bloqueio de plataforma,
# recorrente desde 02/09) e sem acesso a MCP dentro do shell — por isso o Resend é primário.
set -euo pipefail
AQUI="$(cd "$(dirname "$0")" && pwd)"
cd "$AQUI"

DATA=$(date +%d/%m/%Y)
python3 gerar_resumo.py
python3 enviar_email.py resumo_diario.html "$DATA"
