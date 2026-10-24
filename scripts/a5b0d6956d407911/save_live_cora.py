#!/usr/bin/env python3
"""Extrai a aba Principal (Cora) do artifact de leitura MCP (googlesheets batch_get,
FORMATTED_VALUE) e grava tmp/polling_a5b0/cora.json no formato cru {"values": [...]},
preservando as strings FORMATTED_VALUE exatas. Depois compara live x canônico
(leads_input.json) campo a campo.

Uso: python3 scripts/a5b0d6956d407911/save_live_cora.py <artifact.json>
"""
import json, sys, os, unicodedata

def nfc(v):
    return unicodedata.normalize('NFC', v) if isinstance(v, str) else v

BASE = '/home/ethos/.assistant/workspace'
ART = sys.argv[1]
OUT = os.environ.get('POLLING_TMP', os.path.join(BASE, 'tmp/polling_a5b0'))
CANON = os.path.join(BASE, 'scripts/a5b0d6956d407911/leads_input.json')

CORA_H = ['data_envio','nome','cnpj_ou_cpf','tipo_empresa','email','telefone','servico_desejado','ramo_atividade','segmento','estado','cidade','preferencia_atendimento','status_atendimento','observação/comentários']

d = json.load(open(ART, encoding='utf-8'))
data = d.get('data', d)
if 'values' in data:
    vr = data  # resposta de VALUES_GET (objeto único)
else:
    vr = data['valueRanges'][0]
assert 'Principal' in vr.get('range', ''), f"range inesperado: {vr.get('range')}"
vals = vr.get('values', [])
vals = [[nfc(c) for c in row] for row in vals]

# QUARENTENA CORA (2026-10-23): live esvaziada pela Cora (só aviso + header + #N/A).
# NÃO sobrescrever tmp cora.json com a live vazia — manter o cache canônico no tmp
# para o run.sh abortar na quarentena (canônico 72 linhas) sem divergir.
dados_live = [r for r in vals if r and any(str(c).strip() for c in r[:12])]
if len(dados_live) < 50:
    import shutil
    shutil.copy(os.path.join(BASE, 'scripts/a5b0d6956d407911/cache/cora.json'),
                os.path.join(OUT, 'cora.json'))
    print(f'QUARENTENA CORA: live com {len(dados_live)} linhas de dados (<50; canônico 72) — tmp cora.json = cache canônico, rodada será abortada pelo guard.')
    sys.exit(1)

json.dump({'values': vals}, open(os.path.join(OUT, 'cora.json'), 'w', encoding='utf-8'), ensure_ascii=False)

# live como dicts: acha a linha do header 'data_envio' (linha 3 da planilha)
hdr_idx = next(i for i, row in enumerate(vals) if row and row[0] == 'data_envio')
live = [{h: (row[i] if i < len(row) else '') for i, h in enumerate(CORA_H)}
        for row in vals[hdr_idx + 1:]]

li = json.load(open(CANON, encoding='utf-8'))
canon = li['cora']
print(f'cora: live {len(live)} linhas x canônico {len(canon)} linhas')
ok = len(live) == len(canon)
if not ok:
    print('  DIVERGÊNCIA de contagem!')
for i, (a, b) in enumerate(zip(live, canon)):
    diffs = {h: (a.get(h), b.get(h)) for h in CORA_H if a.get(h) != b.get(h)}
    if diffs:
        ok = False
        print(f'  DIVERGÊNCIA linha {i+1} ({a.get("data_envio")}):')
        for h, (lv, cv) in diffs.items():
            print(f'    {h}: live={lv!r} canon={cv!r}')
print('RESULTADO:', 'OK (live == canônico)' if ok else 'DIVERGÊNCIA')
sys.exit(0 if ok else 1)
