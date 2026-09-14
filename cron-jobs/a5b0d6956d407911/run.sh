#!/bin/bash
# Captação de Leads — run periódico (cron a5b0d6956d407911)
# O agente lê as planilhas via MCP e salva em $POLLING_TMP/{cora,meta_ads_jun,meta_ads_cadastro}.json.
# Este script transforma e processa com ESTADO e DIRETÓRIO DE POLLING PRÓPRIOS
# (não disputa estado nem arquivos com o 91e0856).
# NÃO usa build_input.py (dados hardcoded truncados divergiam da planilha ao vivo
# e brigavam com o pipeline live → CRM oscilando entre valores truncados e completos).
set -euo pipefail
cd /home/ethos/.assistant/workspace
export ESTADO_PATH="$PWD/scripts/a5b0d6956d407911/estado.json"
export LEADS_INPUT_PATH="$PWD/scripts/a5b0d6956d407911/leads_input.json"
# Diretório de polling PRÓPRIO deste job (fix 2026-09-14): o tmp/polling compartilhado
# brigava com o 91e0856 — rodadas simultâneas truncavam cora.json e apagavam os
# meta_ads_*.json do outro job (JSONDecodeError no transform).
export POLLING_TMP="$PWD/tmp/polling_a5b0"
mkdir -p "$POLLING_TMP"
python3 scripts/91e08561a5b65e5d/transform.py
cat "$LEADS_INPUT_PATH" | python3 scripts/captacao_leads/processar.py
