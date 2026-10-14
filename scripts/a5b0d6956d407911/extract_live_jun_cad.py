#!/usr/bin/env python3
"""Extrai as abas Jun/Cad do artifact de leitura MCP (googlesheets batch_get)
e grava tmp/polling_a5b0/{meta_ads_jun,meta_ads_cadastro}.json no formato cru
{"values": [...]}, preservando as strings FORMATTED_VALUE exatas.
Depois compara live x canônico (leads_input.json) campo a campo.

Fix NFC (2026-10-14): a leitura MCP traz strings NFD (Vinicius decomposto) e o
canônico está NFC — sem normalizar, cada rodada ao vivo diverge na linha 5 do
Cadastro (lead de teste) e o pipeline oscila. NFC deixa o pipeline idempotente.

Uso: python3 scripts/a5b0d6956d407911/extract_live_jun_cad.py <artifact.json>
"""
import json, sys, os, unicodedata

def nfc(v):
    return unicodedata.normalize('NFC', v) if isinstance(v, str) else v

BASE = '/home/ethos/.assistant/workspace'
ART = sys.argv[1]
OUT = os.environ.get('POLLING_TMP', os.path.join(BASE, 'tmp/polling_a5b0'))
CANON = os.path.join(BASE, 'scripts/a5b0d6956d407911/leads_input.json')

JUN_H = ['Data/Hora','Nome completo','Email','Telefone','segmento','cargo','gestao_financeira','problema','motivacao','anuncio','conjunto','campanha']
CAD_H = ['Data/Hora','Nome completo','Email','Telefone','cargo','funcionarios','faturamento','gestao_financeira','problema','interesse','investimento','motivacao','anuncio','conjunto','campanha']

d = json.load(open(ART, encoding='utf-8'))
data = d.get('data', d)
vrs = data['valueRanges']

def rows_to_dicts(rows, headers, drop_prestador=False, cad_norm=False):
    out = []
    for row in rows:
        if drop_prestador and len(row) > 12:
            row = row[:4] + row[5:]
        if cad_norm:
            row = row[:13] + [''] * max(0, 13 - len(row))
        out.append({h: (row[i] if i < len(row) else '') for i, h in enumerate(headers)})
    return out

li = json.load(open(CANON, encoding='utf-8'))
ok = True
for r in vrs:
    rng = r.get('range', '')
    if 'Jun.26' in rng:
        key, headers = 'meta_ads_jun', JUN_H
    elif 'Cadastro' in rng:
        key, headers = 'meta_ads_cadastro', CAD_H
    else:
        continue
    vals = r.get('values', [])
    # NFC nos strings (live NFD → canônico NFC; fix idempotência 2026-10-14)
    vals = [[nfc(c) for c in row] for row in vals]
    # grava cru EXATAMENTE como o MCP devolveu (com header, NFC)
    json.dump({'values': vals}, open(os.path.join(OUT, f'{key}.json'), 'w', encoding='utf-8'), ensure_ascii=False)
    # compara live x canônico (pula header)
    body = vals[1:] if vals and vals[0] and vals[0][0] == headers[0] else vals
    if key == 'meta_ads_jun':
        live = rows_to_dicts(body, headers, drop_prestador=len(vals[0]) > 12 if vals else False)
    else:
        live = rows_to_dicts(body, headers, cad_norm=True)
    canon = li[key]
    print(f'{key}: live {len(live)} linhas x canônico {len(canon)} linhas')
    if len(live) != len(canon):
        print(f'  DIVERGÊNCIA de contagem!')
        ok = False
    for i, (a, b) in enumerate(zip(live, canon)):
        diffs = {h: (a.get(h), b.get(h)) for h in headers if a.get(h) != b.get(h)}
        if diffs:
            ok = False
            print(f'  DIVERGÊNCIA linha {i+1} ({a.get("Data/Hora")}):')
            for h, (lv, cv) in diffs.items():
                print(f'    {h}: live={lv!r} canon={cv!r}')
print('RESULTADO:', 'OK (live == canônico)' if ok else 'DIVERGÊNCIA')
sys.exit(0 if ok else 1)
