#!/usr/bin/env python3
"""Spot-check: valida cache x estado (mesma lógica do processar.py).

2026-10-07: lê o diretório da env var SPOT_DIR (default 'cache/') — permite
validar tmp/polling antes de rodar o pipeline:
  SPOT_DIR=/home/ethos/.assistant/workspace/tmp/polling python3 spotcheck_cache.py

Convenção dos arquivos: cora.json COM aviso+header (busca 'data_envio');
meta_ads_jun/cadastro SEM header (o spotcheck NÃO pula header das abas Meta).
"""
import json, os, re, hashlib, sys

os.chdir('/home/ethos/.assistant/workspace/scripts/91e08561a5b65e5d')

def normalizar_telefone(t):
    if not t: return ''
    d = re.sub(r'\D', '', str(t))
    if len(d) == 11 and d[0] == '0': d = d[1:]
    if len(d) == 10: d = '55' + d
    elif len(d) == 11: d = '55' + d
    return d

def normalizar_email(e):
    return (e or '').strip().lower()

def hash_linha(vals):
    return hashlib.sha256(json.dumps(vals, ensure_ascii=False).encode('utf-8')).hexdigest()

HEADERS = {
    'cora': ['data_envio','nome','cnpj_ou_cpf','tipo_empresa','email','telefone','servico_desejado','ramo_atividade','segmento','estado','cidade','preferencia_atendimento','status_atendimento','observação/comentários'],
    'meta_ads_jun': ['Data/Hora','Nome completo','Email','Telefone','segmento','cargo','gestao_financeira','problema','motivacao','anuncio','conjunto','campanha'],
    'meta_ads_cadastro': ['Data/Hora','Nome completo','Email','Telefone','cargo','funcionarios','faturamento','gestao_financeira','problema','interesse','investimento','motivacao','anuncio','conjunto','campanha'],
}

est = json.load(open('estado.json'))
ok_total = True
for src, headers in HEADERS.items():
    with open(os.environ.get('SPOT_DIR', 'cache') + '/' + src + '.json') as fh:
        raw = json.load(fh).get('values', [])
    if src == 'cora':
        idx = next(i for i, r in enumerate(raw) if r and r[0] == 'data_envio')
        raw = raw[idx+1:]
    elif src == 'meta_ads_jun' and raw and len(raw[0]) > 12:
        raw = [r[:4] + r[5:] for r in raw]
    rows = []
    for row in raw:
        obj = {}
        for i, h in enumerate(headers):
            obj[h] = row[i] if i < len(row) else ''
        rows.append(obj)
    match = miss = 0
    misses = []
    for idx, r in enumerate(rows):
        tel = normalizar_telefone(r.get('telefone') or r.get('Telefone'))
        em = normalizar_email(r.get('email') or r.get('Email'))
        chave = tel or em
        if not chave:
            print(src, 'linha', idx, 'SEM CHAVE:', repr(r.get('Data/Hora') or r.get('data_envio')), repr(r.get('Nome completo') or r.get('nome')), 'email=', repr(r.get('Email') or r.get('email')), 'tel=', repr(r.get('Telefone') or r.get('telefone')))
            h = hash_linha(r)
            hits = [k for k, v in est[src].items() if (isinstance(v, str) and v == h) or (isinstance(v, list) and h in v)]
            print('   hash no estado sob:', hits)
            continue
        h = hash_linha(r)
        v = est.get(src, {}).get(chave)
        found = (isinstance(v, str) and v == h) or (isinstance(v, list) and h in v)
        if found:
            match += 1
        else:
            miss += 1
            if len(misses) < 3:
                misses.append((chave, r.get('Data/Hora') or r.get('data_envio'), r.get('Nome completo') or r.get('nome')))
    print(src + ':', match, 'match /', miss, 'miss', misses if misses else '')
    if miss: ok_total = False
print('VALIDAÇÃO FINAL:', 'OK' if ok_total else 'DIVERGÊNCIA')
