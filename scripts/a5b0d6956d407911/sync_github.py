#!/usr/bin/env python3
"""Sincroniza arquivos do job a5b0 com o GitHub via JSON-RPC direto no MCP.
Mesmo mecanismo do sync_github.py do 91e0856 (commit de arquivo do disco =
SEMPRE JSON-RPC direto lendo do disco; push_files via tool call trunca)."""
import json, urllib.request, sys, os

CFG = '/home/ethos/.assistant/config.json'
cfg = json.load(open(CFG))
srv = cfg['tools']['mcp']['servers']['github']
URL, HDRS = srv['url'], dict(srv.get('headers', {}))
HDRS.update({'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'})

OWNER, REPO, BRANCH = 'Financeiroterceirizou', 'crm-oficial-m2ilj1b7f', 'main'
BASE = '/home/ethos/.assistant/workspace/scripts/a5b0d6956d407911'
PREFIX = 'scripts/a5b0d6956d407911'
FILES = ['leads_input.json', 'estado.json', 'fetch_mcp_live.py', 'sync_github.py',
         'cache/cora.json', 'cache/meta_ads_jun.json', 'cache/meta_ads_cadastro.json']

_id = [0]

def rpc(name, args):
    _id[0] += 1
    body = json.dumps({'jsonrpc': '2.0', 'id': _id[0], 'method': 'tools/call',
                       'params': {'name': name, 'arguments': args}}).encode()
    req = urllib.request.Request(URL, data=body, headers=HDRS)
    raw = urllib.request.urlopen(req, timeout=180).read().decode()
    parts = [l[6:] for l in raw.split('\n') if l.startswith('data: ')]
    if not parts:
        raise RuntimeError('sem data SSE: ' + raw[:300])
    payload = None
    for cand in parts:
        try:
            payload = json.loads(cand)
            break
        except Exception:
            continue
    if payload is None:
        raise RuntimeError('SSE não parseável: ' + raw[:300])
    if payload.get('error'):
        raise RuntimeError('RPC error: ' + json.dumps(payload['error'])[:300])
    return payload['result']

def github_text(path):
    try:
        r = rpc('get_file_contents', {'owner': OWNER, 'repo': REPO, 'path': f'{PREFIX}/{path}'})
        content = r['content']
        if len(content) < 2 or content[1].get('type') != 'resource':
            return None, False
        return content[1]['resource']['text'], True
    except RuntimeError as e:
        if 'Not Found' in str(e) or '404' in str(e):
            return None, False
        raise

def main():
    changed, ok_files = [], []
    for f in FILES:
        local = open(os.path.join(BASE, f), encoding='utf-8').read()
        gh, exists = github_text(f)
        if not exists or gh != local:
            changed.append((f, local, 'nova' if not exists else 'divergente'))
        else:
            ok_files.append(f)
    print('iguais:', ', '.join(ok_files) or '-')
    if not changed:
        print('NADA A COMMITAR — GitHub já sincronizado')
        return
    for f, _, motivo in changed:
        print(f'divergente ({motivo}): {f}')
    msg = 'Polling a5b0: fetch_mcp_live.py (leitura JSON-RPC GOOGLESHEETS_VALUES_GET) + leads_input/estado (2026-10-16 00:15)'
    r = rpc('push_files', {'owner': OWNER, 'repo': REPO, 'branch': BRANCH, 'message': msg,
                           'files': [{'path': f'{PREFIX}/{f}', 'content': c}
                                     for f, c, _ in changed]})
    summary = r['content'][0]['text'] if isinstance(r.get('content'), list) else json.dumps(r)[:200]
    print('push:', summary[:200])
    falhas = []
    for f, local, _ in changed:
        gh, exists = github_text(f)
        if not exists or gh != local:
            falhas.append(f)
    if falhas:
        print('VERIFICAÇÃO FALHOU:', falhas); sys.exit(1)
    print(f'VERIFICAÇÃO OK: {len(changed)} arquivo(s) byte a byte no GitHub')

if __name__ == '__main__':
    main()
