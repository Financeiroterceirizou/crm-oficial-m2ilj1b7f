#!/bin/bash
# Captação de Leads — run periódico (cron a5b0d6956d407911)
# O agente lê as planilhas via MCP e salva em tmp/polling_a5b0/{cora,meta_ads_jun,meta_ads_cadastro}.json.
# Este script transforma e processa com ESTADO PRÓPRIO (não disputa estado com o 91e0856).
# NÃO usa mais build_input.py (dados hardcoded truncados divergiam da planilha ao vivo
# e brigavam com o pipeline live → CRM oscilando entre valores truncados e completos).
set -euo pipefail
cd /home/ethos/.assistant/workspace
export ESTADO_PATH="$PWD/scripts/a5b0d6956d407911/estado.json"
export LEADS_INPUT_PATH="$PWD/scripts/a5b0d6956d407911/leads_input.json"
# Diretório de polling PRÓPRIO deste job (o tmp/polling compartilhado brigava
# com o 91e0856: arquivos truncados e saves desaparecendo entre escritas).
export POLLING_TMP="$PWD/tmp/polling_a5b0"
mkdir -p "$POLLING_TMP"

# GUARDA (2026-09-23): se NENHUM arquivo cru existe no tmp (tmp é efêmero e o
# cron dispara sem a etapa de leitura MCP), abortar ANTES do transform — sem
# isso o transform grava leads_input.json vazio ({}) e destrói o canônico
# (fonte única do create_polling_files.py), como ocorreu em 23/09 13:00.
if ! ls "$POLLING_TMP"/cora.json "$POLLING_TMP"/meta_ads_jun.json "$POLLING_TMP"/meta_ads_cadastro.json >/dev/null 2>&1; then
  echo "tmp/polling_a5b0 sem arquivos crus — aguardando leitura MCP; leads_input canônico PRESERVADO."
  exit 0
fi

python3 scripts/91e08561a5b65e5d/transform.py
cat "$LEADS_INPUT_PATH" | python3 scripts/captacao_leads/processar.py
