#!/usr/bin/env python3
"""Leitura MCP googlesheets via JSON-RPC direto (contorno de falha de transporte
e de payload grande em tool call). Lê as 3 planilhas vivas, salva os artifacts
completos em tmp/polling_a5b0/mcp_artifacts/ e monta o combinado jun+cad para
extract_live_jun_cad.py. Retry automático em 429 (quota por minuto).

Uso: python3 scripts/a5b0d6956d407911/fetch_mcp_live.py
"""
import json, os, time, urllib.request

BASE = '/home/ethos/.assistant/workspace'
ARTDIR = os.path.join(BASE, 'tmp/polling_a5b0/mcp_artifacts')
os.makedirs(ARTDIR, exist_ok=True)

cfg = json.load(open('/home/ethos/.assistant/config.json'))
srv = cfg['tools']['mcp']['servers']['googlesheets']
URL = srv['url']
TOK = srv['headers']['Authorization'].split(' ', 1)[1]

READS = [
    ('cora_live.json', 'GOOGLESHEETS_VALUES_GET', {
        'range': 'Principal!A1:N200',
        'spreadsheet_id': '1TYe2__HmgLUhqOoudmxm-I2fL94wKSJ8ThmXmbCUXfY',
        'value_render_option': 'FORMATTED_VALUE'}),
    ('jun_live.json', 'GOOGLESHEETS_VALUES_GET', {
        'range': "'Leads Meta Ads - Jun.26'!A1:M200",
        'spreadsheet_id': '1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk',
        'value_render_option': 'FORMATTED_VALUE'}),
    ('cad_live.json', 'GOOGLESHEETS_VALUES_GET', {
        'range': "'Leads Anúncios de Cadastro'!A1:M200",
        'spreadsheet_id': '1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk',
        'value_render_option': 'FORMATTED_VALUE'}),
]


def call(name, args, tries=4):
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                       'params': {'name': name, 'arguments': args}}).encode()
    for attempt in range(1, tries + 1):
        req = urllib.request.Request(URL, data=body, method='POST', headers={
            'Authorization': f'Bearer {TOK}',
            'Accept': 'application/json, text/event-stream',
            'Content-Type': 'application/json',
            'User-Agent': 'terceirizou-polling/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            print(f'  HTTP {e.code} (tentativa {attempt}) — retry em 65s' if attempt < tries else f'  HTTP {e.code} — esgotado')
            if attempt < tries:
                time.sleep(65)
                continue
            raise
        # resposta pode ser SSE (linhas data:) ou JSON puro
        payload = None
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            data_lines = [l[5:].strip() for l in raw.splitlines() if l.startswith('data: ')]
            for dl in reversed(data_lines):
                try:
                    payload = json.loads(dl)
                    break
                except json.JSONDecodeError:
                    continue
        if payload is None:
            print('  resposta ilegível — retry em 65s')
            time.sleep(65)
            continue
        if 'error' in payload and payload.get('error'):
            print(f'  rpc error: {str(payload["error"])[:120]} — retry em 65s')
            time.sleep(65)
            continue
        result = payload.get('result', payload)
        content = result.get('content') if isinstance(result, dict) else None
        if not content:
            print('  sem content — retry em 65s')
            time.sleep(65)
            continue
        inner = json.loads(content[0]['text'])
        if not inner.get('successfull', False):
            print(f'  tool erro: {str(inner.get("error"))[:120]} — retry em 65s')
            time.sleep(65)
            continue
        return inner
    raise SystemExit(f'fetch {name}: esgotado após {tries} tentativas')


for fname, tool, args in READS:
    print(f'lendo {fname}...')
    inner = call(tool, args)
    path = os.path.join(ARTDIR, fname)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(inner, f, ensure_ascii=False)
    n = len(inner.get('data', {}).get('values', []))
    print(f'  OK -> {path} ({n} linhas brutas)')

# combinado jun+cad no formato batch_get que extract_live_jun_cad.py espera
jun = json.load(open(os.path.join(ARTDIR, 'jun_live.json'), encoding='utf-8'))
cad = json.load(open(os.path.join(ARTDIR, 'cad_live.json'), encoding='utf-8'))
combined = {'data': {'valueRanges': [jun['data'], cad['data']]}}
with open(os.path.join(ARTDIR, 'jun_cad_live.json'), 'w', encoding='utf-8') as f:
    json.dump(combined, f, ensure_ascii=False)
print('combinado jun_cad_live.json OK')
