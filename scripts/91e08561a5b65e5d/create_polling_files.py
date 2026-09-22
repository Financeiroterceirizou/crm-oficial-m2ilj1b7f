#!/usr/bin/env python3
"""Regenera tmp/polling/{cora,meta_ads_jun,meta_ads_cadastro}.json no formato
canônico (MCP FORMATTED_VALUE: {"values": [...]}) a partir do leads_input.json
canônico do job a5b0 (scripts/a5b0d6956d407911/leads_input.json) — fonte única
mantida em sincronia com as planilhas.

Histórico (2026-09-17): este script tinha os dados hardcoded e ficou DESATUALIZADO
(faltavam 8 linhas Cora 24/08–02/09 e 4 linhas Jun 26/08–13/09) → rodadas com ele
produziam 34 ignorados em vez de 38 e não viam linhas novas. Agora deriva do
input canônico do a5b0, que é mantido atualizado.

FIX 2026-09-19: gerar a aba Jun SEMPRE no formato CRU de 13 colunas (com a
coluna "É prestador de serviços?" no índice 4). Antes gerava 12 colunas
pós-transform; quando uma linha nova chega da leitura ao vivo com 13, o
transform.py mapeava por índice e DESLOCAVA tudo (segmento='sim', cargo
recebendo segmento, anuncio recebendo motivacao) — mesmo padrão do incidente
de 17/09. O descarte da coluna extra é condicional no transform.py (>12 col).

Run: python3 scripts/91e08561a5b65e5d/create_polling_files.py
"""
import json, os

WORKSPACE = "/home/ethos/.assistant/workspace"
TMP = os.path.join(WORKSPACE, "tmp", "polling")
CANONICO = os.path.join(WORKSPACE, "scripts", "a5b0d6956d407911", "leads_input.json")

# Headers no formato CRU da planilha (o transform.py aplica o descarte da
# coluna "É prestador de serviços?" (índice 4) condicionalmente — só se o
# header tiver >12 colunas).
HEADERS = {
    'cora': ['data_envio','nome','cnpj_ou_cpf','tipo_empresa','email','telefone',
             'servico_desejado','ramo_atividade','segmento','estado','cidade',
             'preferencia_atendimento','status_atendimento','observação/comentários'],
    'meta_ads_jun': ['Data/Hora','Nome completo','Email','Telefone','É prestador de serviços?',
                     'Qual o segmento de atuação da empresa?','Qual seu cargo na empresa?',
                     'Quem faz a gestão financeira hoje?','Qual o maior problema na gestão financeira?',
                     'O que te motivou a buscar a terceirização financeira agora','Nome do Anúncio',
                     'Conjunto de Anúncio','Campanha'],
    'meta_ads_cadastro': ['Data/Hora','Nome completo','Email','Telefone','cargo','funcionarios',
                          'faturamento','gestao_financeira','problema','interesse','investimento',
                          'motivacao','anuncio','conjunto','campanha'],
}

os.makedirs(TMP, exist_ok=True)
with open(CANONICO, encoding='utf-8') as f:
    canon = json.load(f)

for fonte, headers in HEADERS.items():
    rows = canon.get(fonte, [])
    if fonte == 'meta_ads_jun':
        # Linhas canônicas (12 chaves) → 13 colunas cruas com '' no índice 4
        values = [headers]
        for r in rows:
            v = [r.get(h, '') for h in ['Data/Hora','Nome completo','Email','Telefone']]
            v.append(r.get('É prestador de serviços?', ''))  # coluna extra, índice 4
            v += [r.get(h, '') for h in ['segmento','cargo','gestao_financeira','problema',
                                          'motivacao','anuncio','conjunto','campanha']]
            values.append(v)
    else:
        values = [headers] + [[r.get(h, '') for h in headers] for r in rows]
    with open(os.path.join(TMP, f'{fonte}.json'), 'w', encoding='utf-8') as f:
        json.dump({"values": values}, f, ensure_ascii=False)
    print(f'{fonte}.json: {len(values)} rows')
print('OK — tmp/polling regenerado do canônico a5b0 (Jun 13 colunas cruas)')
