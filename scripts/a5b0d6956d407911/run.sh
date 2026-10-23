#!/bin/bash
# Captação de Leads — run periódico (cron a5b0d6956d407911)
# O agente lê as planilhas via MCP e salva em tmp/polling/{cora,meta_ads_jun,meta_ads_cadastro}.json.
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

# GUARDA FRESH (2026-10-08 20:30): mesmo vetor do 91e0856 — arquivos crus
# gravados no tmp sem leitura MCP verificada (escrita externa corrompida
# recontaminou o canônico e gerou 1 update errado no CRM em 19:59). Só roda
# se o agente marcou tmp/polling_a5b0/.mcp-fresh na rodada.
if [ ! -f "$POLLING_TMP/.mcp-fresh" ]; then
  echo "tmp/polling_a5b0 sem marcador .mcp-fresh (escrita externa suspeita) — leads_input canônico PRESERVADO."
  rm -f "$POLLING_TMP"/cora.json "$POLLING_TMP"/meta_ads_jun.json "$POLLING_TMP"/meta_ads_cadastro.json
  exit 0
fi
rm -f "$POLLING_TMP/.mcp-fresh"

# QUARENTENA CORA (2026-10-23 20:00): a Cora esvaziou a planilha live (colunas A-L
# sem dados; só restaram status_atendimento em M/N em 6 linhas). Rodar o transform
# com a Cora vazia ZERA o estado cora e sobrescreve o canônico (ocorreu 18:20 e
# 20:00). Abortar enquanto a Cora live tiver menos de 50 linhas de dados (canônico
# tem 72). Só a decisão do Vinícius (ou planilha nova da Cora) libera.
if ! CORA_JSON="$POLLING_TMP/cora.json" python3 - <<'EOF'
import json, os, sys
d = json.load(open(os.environ['CORA_JSON']))
rows = d.get('values', d) if isinstance(d, dict) else d
dados = [r for r in rows if r and any(str(c).strip() for c in r[:12])]
if len(dados) < 50:
    print(f"QUARENTENA CORA: live com {len(dados)} linhas de dados (<50; canônico 72) — rodada abortada, canônico PRESERVADO.")
    sys.exit(1)
EOF
then
  echo "Abortado pela quarentena da Cora."
  exit 1
fi

python3 scripts/91e08561a5b65e5d/transform.py
cat "$LEADS_INPUT_PATH" | python3 scripts/captacao_leads/processar.py
