#!/usr/bin/env python3
"""Leitura MCP googlesheets via JSON-RPC direto para o job 91e0856.
Lê as 3 planilhas vivas (FORMATTED_VALUE), salva artifacts completos em
tmp/polling/mcp_artifacts/ e grava os crus em tmp/polling/ na convenção do
cache (cora = header+dados sem aviso; jun/cad = header+dados). Retry em 429.
Adaptado de scripts/a5b0d6956d407911/fetch_mcp_live.py (2026-10-16).
"""
import json, os, time, urllib.request

BASE = '/home/ethos/.assistant/workspace'
ARTDIR = os.path.join(BASE, 'tmp/polling/mcp_artifacts')
TMP = os.path.join(BASE, 'tmp/polling')
os.makedirs(ARTDIR, exist_ok=True)
os.makedirs(TMP, exist_ok=True)

cfg = json.load(open('/home/ethos/.assistant/config.json'))
srv = cfg['tools']['mcp']['servers']['googlesheets']
URL = srv['url']
TOK = srv['headers']['Authorization'].split(' ', 1)[1]

READS = [
    ('cora_live.json', 'Principal!A1:N200',
     '1TYe2__HmgLUhqOoudmxm-I2fL94wKSJ8ThmXmbCUXfY'),
    ('jun_live.json', "'Leads Meta Ads - Jun.26'!A1:M200",
     '1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk'),
    ('cad_live.json', "'Leads Anúncios de Cadastro'!A1:M200",
     '1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk'),
]


def call(range_a1, ssid, tries=4):
    args = {'range': range_a1, 'spreadsheet_id': ssid,
            'value_render_option': 'FORMATTED_VALUE'}
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                       'params': {'name': 'GOOGLESHEETS_VALUES_GET',
                                  'arguments': args}}).encode()
    for attempt in range(1, tries + 1):
        req = urllib.request.Request(URL, data=body, method='POST', headers={
            'Authorization': 'Bearer ' + TOK,
            'Accept': 'application/json, text/event-stream',
            'Content-Type': 'application/json',
            'User-Agent': 'terceirizou-polling/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            print('  HTTP %s (tentativa %d)%s' % (
                e.code, attempt, ' - retry 65s' if attempt < tries else ' - esgotado'))
            if attempt < tries:
                time.sleep(65)
                continue
            raise
        payload = None
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            for dl in reversed([l[5:].strip() for l in raw.splitlines()
                                if l.startswith('data: ')]):
                try:
                    payload = json.loads(dl)
                    break
                except json.JSONDecodeError:
                    continue
        if payload is None:
            print('  resposta ilegivel - retry 65s')
            time.sleep(65)
            continue
        if payload.get('error'):
            print('  rpc error: %s - retry 65s' % str(payload['error'])[:120])
            time.sleep(65)
            continue
        result = payload.get('result', payload)
        content = result.get('content') if isinstance(result, dict) else None
        if not content:
            print('  sem content - retry 65s')
            time.sleep(65)
            continue
        inner = json.loads(content[0]['text'])
        if not inner.get('successfull', False):
            print('  tool erro: %s - retry 65s' % str(inner.get('error'))[:120])
            time.sleep(65)
            continue
        return inner
    raise SystemExit('fetch %s: esgotado apos %d tentativas' % (range_a1, tries))


for fname, rng, ssid in READS:
    print('lendo %s...' % fname)
    inner = call(rng, ssid)
    path = os.path.join(ARTDIR, fname)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(inner, f, ensure_ascii=False)
    vals = inner['data']['values']
    print('  OK (%d linhas brutas)' % len(vals))

cora = json.load(open(os.path.join(ARTDIR, 'cora_live.json'), encoding='utf-8'))
cv = cora['data']['values']
hi = next((i for i, r in enumerate(cv) if r and r[0] == 'data_envio'), None)
if hi is None:
    raise SystemExit('header data_envio nao encontrado na Cora ao vivo')
with open(os.path.join(TMP, 'cora.json'), 'w', encoding='utf-8') as f:
    json.dump({'values': cv[hi:]}, f, ensure_ascii=False)
print('cora.json: %d linhas (header + dados, sem aviso)' % (len(cv) - hi))

for art, out in [('jun_live.json', 'meta_ads_jun.json'),
                 ('cad_live.json', 'meta_ads_cadastro.json')]:
    d = json.load(open(os.path.join(ARTDIR, art), encoding='utf-8'))
    vals = d['data']['values']
    with open(os.path.join(TMP, out), 'w', encoding='utf-8') as f:
        json.dump({'values': vals}, f, ensure_ascii=False)
    print('%s: %d linhas (header + dados)' % (out, len(vals)))
# Marcador .mcp-fresh: NÃO é criado aqui. A correção de 23/10 (trap das
# 18:20) tira a marcação do fetch: o marker só é criado pelo script da rodada
# DEPOIS de conferir cache×live e validar_tmp passarem — se a Cora divergir
# (ex.: esvaziada), os crus ficam em tmp/polling SEM marker e o run.sh
# preserva o canônico. Sem isso, o fetch marcava antes da conferência e uma
# rodada seguinte processava a Cora vazia (estado cora 71→0 às 18:20).
print('fetch concluido (marker .mcp-fresh fica a cargo da rodada)')
