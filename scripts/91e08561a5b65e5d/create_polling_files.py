#!/usr/bin/env python3
"""Regenera tmp/polling/{cora,meta_ads_jun,meta_ads_cadastro}.json no formato
canônico (MCP FORMATTED_VALUE: {"values": [...]}) a partir do leads_input.json
canônico do job a5b0 (scripts/a5b0d6956d407911/leads_input.json) — fonte única
mantida em sincronia com as planilhas.

Histórico (2026-09-17): este script tinha os dados hardcoded e ficou DESATUALIZADO
(faltavam 8 linhas Cora 24/08–02/09 e 4 linhas Jun 26/08–13/09) → rodadas com ele
produziam 34 ignorados em vez de 38 e não viam linhas novas. Agora deriva do
input canônico do a5b0, que é mantido atualizado.

Run: python3 scripts/91e08561a5b65e5d/create_polling_files.py
"""
import json, os

WORKSPACE = "/home/ethos/.assistant/workspace"
TMP = os.path.join(WORKSPACE, "tmp", "polling")
CANONICO = os.path.join(WORKSPACE, "scripts", "a5b0d6956d407911", "leads_input.json")

# Headers na ordem do transform.py (pós-descarte da coluna "É prestador de serviços?")
HEADERS = {
    'cora': ['data_envio','nome','cnpj_ou_cpf','tipo_empresa','email','telefone',
             'servico_desejado','ramo_atividade','segmento','estado','cidade',
             'preferencia_atendimento','status_atendimento','observação/comentários'],
    'meta_ads_jun': ['Data/Hora','Nome completo','Email','Telefone','segmento','cargo',
                     'gestao_financeira','problema','motivacao','anuncio','conjunto','campanha'],
    'meta_ads_cadastro': ['Data/Hora','Nome completo','Email','Telefone','cargo','funcionarios',
                          'faturamento','gestao_financeira','problema','interesse','investimento',
                          'motivacao','anuncio','conjunto','campanha'],
}

os.makedirs(TMP, exist_ok=True)
with open(CANONICO, encoding='utf-8') as f:
    canon = json.load(f)

for fonte, headers in HEADERS.items():
    rows = canon.get(fonte, [])
    values = [headers] + [[r.get(h, '') for h in headers] for r in rows]
    with open(os.path.join(TMP, f'{fonte}.json'), 'w', encoding='utf-8') as f:
        json.dump({"values": values}, f, ensure_ascii=False)
    print(f'{fonte}.json: {len(values)} rows')
print('OK — tmp/polling regenerado do canônico a5b0')
