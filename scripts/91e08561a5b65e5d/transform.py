#!/usr/bin/env python3
"""Transform raw MCP Google Sheets data into processar.py input format.

Reads JSON files from tmp/polling/ (saved by the agent from MCP calls),
transforms them into the format expected by processar.py, and writes to
leads_input.json (default tmp/polling/leads_input.json, isolável por job
via env var LEADS_INPUT_PATH).

Usage: python3 transform.py
"""
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.dirname(os.path.dirname(AQUI))
CAPTACAO = os.path.join(WORKSPACE, 'scripts', 'captacao_leads')
TMP = os.path.join(WORKSPACE, 'tmp', 'polling')

# Headers expected by processar.py for each source
HEADERS = {
    'cora': [
        'data_envio', 'nome', 'cnpj_ou_cpf', 'tipo_empresa', 'email', 'telefone',
        'servico_desejado', 'ramo_atividade', 'segmento', 'estado', 'cidade',
        'preferencia_atendimento', 'status_atendimento', 'observação/comentários'
    ],
    # Chaves CANÔNICAS esperadas pelo processar.py (mesmas do converter.py).
    # A aba Jun tem a coluna extra "É prestador de serviços?" (índice 4) que é
    # descartada antes do mapeamento (ver main()).
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
        
        # MCP format: {"values": [[row1], [row2], ...]}
        # Tolerante: alguns saves do agente gravam a lista crua (sem wrapper
        # {"values": ...}). Aceitar ambos os formatos (fix 2026-09-11).
        if isinstance(data, dict):
            raw_values = data.get('values', [])
        elif isinstance(data, list):
            raw_values = data
        else:
            print(f'  WARN: formato inesperado em {filepath}, pulando {source_name}', file=sys.stderr)
            continue
        
        # Skip header row if first row matches headers (meta sheets include header)
        if raw_values and raw_values[0][0] == headers[0]:
            raw_values = raw_values[1:]
        
        # Cora sheet has a warning text row and empty row before the actual header
        # Skip these until we find the actual header row
        if source_name == 'cora' and raw_values:
            # Find the actual header row (starts with 'data_envio')
            header_idx = None
            for idx, row in enumerate(raw_values):
                if row and row[0] == 'data_envio':
                    header_idx = idx
                    break
            if header_idx is not None:
                raw_values = raw_values[header_idx + 1:]  # Skip header and everything before it

        # Jun tem a coluna extra "É prestador de serviços?" (índice 4) que NÃO
        # entra no dict (processar.py não a usa) — descarta antes de transformar
        if source_name == 'meta_ads_jun':
            raw_values = [r[:4] + r[5:] for r in raw_values]

        # Transform to list-of-dicts
        rows = transform_rows(raw_values, headers)
        output[source_name] = rows
        print(f'  {source_name}: {len(rows)} rows', file=sys.stderr)
    
    # Write output for processar.py
    # Caminho isolável por job via LEADS_INPUT_PATH (evita corrida quando dois
    # crons transformam em paralelo — mesmo arquivo sendo escrito por ambos).
    out_path = os.environ.get('LEADS_INPUT_PATH', os.path.join(TMP, 'leads_input.json'))
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False)
    
    print(f'  Total: {sum(len(v) for v in output.values())} rows → {out_path}', file=sys.stderr)
    return output


if __name__ == '__main__':
    main()
