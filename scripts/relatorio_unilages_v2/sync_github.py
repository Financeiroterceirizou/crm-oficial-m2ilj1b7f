#!/usr/bin/env python3
"""Commit dos scripts UNILAGES (DRE por CC, indicadores, semanal) no GitHub.
JSON-RPC direto no server MCP, lendo os arquivos DO DISCO (nunca conteúdo inline).
Regra inegociável: todo processo executado vira commit no repo do projeto.
Verificação byte a byte obrigatória ao final.
"""
import json
import os
import urllib.request

CFG = '/home/ethos/.assistant/config.json'
cfg = json.load(open(CFG))
srv = cfg['tools']['mcp']['servers']['github']
URL, HDRS = srv['url'], dict(srv.get('headers', {}))
HDRS.update({'Content-Type': 'application/json', 'Accept': 'application/json, text/event-stream'})

OWNER, REPO, BRANCH = 'Financeiroterceirizou', 'crm-oficial-m2ilj1b7f', 'main'
RAIZ = '/home/ethos/.assistant/workspace'

# caminhos relativos à raiz do workspace (só código; NUNCA .controlle_token / .resend_key)
ARQUIVOS = [
    'scripts/relatorio_unilages_v2/dre_unilages_cc.py',
    'scripts/relatorio_unilages_v2/consolida_dre_cc.py',
    'scripts/relatorio_unilages_v2/enviar_dre_cc.py',
    'scripts/relatorio_unilages_v2/consolida_retro.py',
    'scripts/relatorio_unilages_v2/enviar_retro.py',
    'scripts/relatorio_unilages_v2/sync_github.py',
    'scripts/16c262aa2551ff3d/run.sh',
    'scripts/16c262aa2551ff3d/guard.py',
]
MSG = 'DRE Unilages por CC: automação mensal dia 04 (wrapper + guarda de competência + consolidador + envio único)'

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
        r = rpc('get_file_contents', {'owner': OWNER, 'repo': REPO, 'path': path})
        content = r['content']
        if len(content) < 2 or content[1].get('type') != 'resource':
            return None, False
        return content[1]['resource']['text'], True
    except Exception:
        return None, False


def main():
    pend = []
    for rel in ARQUIVOS:
        local = open(os.path.join(RAIZ, rel), encoding='utf-8').read()
        remoto, existe = github_text(rel)
        if existe and remoto == local:
            print(f'igual, skip: {rel}')
            continue
        pend.append({'path': rel, 'content': local})
        print(f'commit: {rel} ({len(local)} bytes)')

    if not pend:
        print('nada a commitar')
        return 0

    r = rpc('push_files', {'owner': OWNER, 'repo': REPO, 'branch': BRANCH,
                           'files': pend, 'message': MSG})
    print('push_files ok:', json.dumps(r)[:200])

    ok = True
    for rel in ARQUIVOS:
        local = open(os.path.join(RAIZ, rel), encoding='utf-8').read()
        remoto, existe = github_text(rel)
        if not existe or remoto != local:
            print(f'DIVERGE: {rel}')
            ok = False
        else:
            print(f'verificado byte a byte: {rel}')
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
