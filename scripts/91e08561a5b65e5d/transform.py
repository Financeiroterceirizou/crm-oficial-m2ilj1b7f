#!/usr/bin/env python3
"""Transform raw MCP Google Sheets data into processar.py input format.

CONTRATO CRÍTICO (2026-09-14): os arquivos tmp/polling/{fonte}.json DEVEM conter
os valores das células EXATAMENTE como o values_get FORMATTED_VALUE retorna —
datas 'YYYY-MM-DD HH:MM' na Cora e 'DD/MM/YYYY HH:MM' nas abas Meta; números
como string (CPF com zero à esquerda, telefone com vírgulas, como exibido).
O processar.py deduplica por hash_linha(dict) e os hashes do estado.json foram
gerados NESSE formato. Se esta etapa receber valores crus (serial numérico do
Google, ints), TODO hash muda → o pipeline re-processa todas as linhas
(re-sync em massa de updates no CRM). Validado por hash-match contra o estado
real (Sperka/Isamara/Fabiana) em 2026-09-14.

Fluxo: agente lê as planilhas via MCP googlesheets (FORMATTED_VALUE) e salva em
tmp/polling/{cora,meta_ads_jun,meta_ads_cadastro}.json → este transform mapeia
os headers canônicos → processar.py faz dedup + upsert no CRM (via LEADS_INPUT_PATH).
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(os.path.dirname(AQUI))
TMP = os.path.join(WORKSPACE, 'tmp', 'polling')

# Headers canônicos esperados pelo processar.py (mesmos do converter.py).
HEADERS = {
    'cora': [
        'data_envio', 'nome', 'cnpj_ou_cpf', 'tipo_empresa', 'email', 'telefone',
        'servico_desejado', 'ramo_atividade', 'segmento', 'estado', 'cidade',
        'preferencia_atendimento', 'status_atendimento', 'observação/comentários'
    ],
    # A aba Jun tem a coluna extra "É prestador de serviços?" (índice 4), descartada.
    'meta_ads_jun': [
        'Data/Hora', 'Nome completo', 'Email', 'Telefone',
        'segmento', 'cargo', 'gestao_financeira', 'problema', 'motivacao',
        'anuncio', 'conjunto', 'campanha'
    ],
    'meta_ads_cadastro': [
        'Data/Hora', 'Nome completo', 'Email', 'Telefone',
        'cargo', 'funcionarios', 'faturamento', 'gestao_financeira', 'problema',
        'interesse', 'investimento', 'motivacao', 'anuncio', 'conjunto', 'campanha'
    ],
}


def transform_rows(raw_values, headers):
    """Convert list-of-lists (from MCP) to list-of-dicts (for processar.py)."""
    result = []
    for row in raw_values:
        obj = {}
        for i, h in enumerate(headers):
            val = row[i] if i < len(row) else ''
            obj[h] = val
        result.append(obj)
    return result


def main():
    output = {}
    for source_name, headers in HEADERS.items():
        filepath = os.path.join(TMP, f'{source_name}.json')
        if not os.path.exists(filepath):
            print(f'  WARN: {filepath} not found, skipping {source_name}', file=sys.stderr)
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # MCP format: {"values": [[row1], [row2], ...]} — tolera lista crua.
        if isinstance(data, dict):
            raw_values = data.get('values', [])
        elif isinstance(data, list):
            raw_values = data
        else:
            print(f'  WARN: formato inesperado em {filepath}, pulando {source_name}', file=sys.stderr)
            continue

        # Pula linha de cabeçalho se presente
        if raw_values and raw_values[0][0] == headers[0]:
            raw_values = raw_values[1:]

        # Cora: pula linhas de aviso/colunas extras até achar o header real
        if source_name == 'cora':
            header_idx = None
            for idx, row in enumerate(raw_values):
                if row and row[0] == 'data_envio':
                    header_idx = idx
                    break
            if header_idx is not None:
                raw_values = raw_values[header_idx + 1:]

        # Jun: descarta a coluna extra "É prestador de serviços?" (índice 4)
        if source_name == 'meta_ads_jun':
            raw_values = [r[:4] + r[5:] for r in raw_values]

        output[source_name] = transform_rows(raw_values, headers)

        # GUARDA (2026-09-14): data em formato numérico = leitura UNFORMATTED_VALUE
        # (serial do Google). Nesse formato os hashes NÃO batem com o estado.json
        # → processar.py re-processaria TODAS as linhas (re-sync em massa).
        # Aborta (exit 1) antes de gravar o input; o run.sh (set -euo pipefail)
        # interrompe antes do processar.py. Agente deve re-ler as planilhas com
        # value_render_option=FORMATTED_VALUE e salvar tmp/polling/*.json de novo.
        col_data = 'data_envio' if source_name == 'cora' else 'Data/Hora'
        suspeitas = [r.get(col_data) for r in output[source_name]
                     if isinstance(r.get(col_data), (int, float))
                     or str(r.get(col_data)).replace('.', '', 1).isdigit()]
        if suspeitas:
            print(f'  ERRO CRÍTICO: {source_name} tem {len(suspeitas)} valores de data em '
                  f'formato numérico (serial UNFORMATTED). Re-ler com value_render_option='
                  f'FORMATTED_VALUE e salvar tmp/polling/{source_name}.json. Abortando.',
                  file=sys.stderr)
            sys.exit(1)

        print(f'  {source_name}: {len(output[source_name])} rows', file=sys.stderr)

    # Caminho isolável por job via LEADS_INPUT_PATH (evita corrida entre crons)
    out_path = os.environ.get('LEADS_INPUT_PATH', os.path.join(TMP, 'leads_input.json'))
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)

    print(f'  Total: {sum(len(v) for v in output.values())} rows → {out_path}', file=sys.stderr)


if __name__ == '__main__':
    main()
