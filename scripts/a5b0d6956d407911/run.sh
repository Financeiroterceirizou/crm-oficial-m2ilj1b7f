#!/bin/bash
# Captação de Leads — run periódico (cron a5b0d6956d407911)
# O agente lê as planilhas via MCP e salva em tmp/polling/{cora,meta_ads_jun,meta_ads_cadastro}.json.
# Este script transforma e processa com ESTADO PRÓPRIO (não disputa estado com o 91e0856).
# NÃO usa mais build_input.py (dados hardcoded truncados divergiam da planilha ao vivo
# e brigavam com o pipeline live → CRM oscilando entre valores truncados e completos).
set -euo pipefail
cd /home/ethos/.assistant/workspace
python3 scripts/91e08561a5b65e5d/transform.py
export ESTADO_PATH="$PWD/scripts/a5b0d6956d407911/estado.json"
cat tmp/polling/leads_input.json | python3 scripts/captacao_leads/processar.py
