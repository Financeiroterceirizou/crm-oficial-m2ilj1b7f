#!/usr/bin/env python3
"""Valida tmp/polling (ou SPOT_DIR) contra o estado do 91e0856 — hash do DICT pós-transform.

ESTADO_PATH (2026-10-09): permite validar o tmp de QUALQUER job contra o SEU estado
(ex.: SPOT_DIR=tmp/polling_a5b0 ESTADO_PATH=scripts/a5b0d6956d407911/estado.json).
Antes o estado do 91e0856 era fixo — validar o tmp do a5b0 gerava MISS falso nas
linhas que existem só no estado do a5b0 (ex.: linhas de teste F1-T04 da Jun).
"""
import json, re, hashlib, os, sys

BASE = '/home/ethos/.assistant/workspace'
SRC_DIR = os.environ.get('SPOT_DIR', os.path.join(BASE, 'tmp/polling'))
est = json.load(open(os.environ.get('ESTADO_PATH', os.path.join(BASE, 'scripts/91e08561a5b65e5d/estado.json'))))

def normalizar_telefone(t):
    if not t: return ''
    d = re.sub(r'\D', '', str(t))
    if len(d) == 11 and d[0] == '0': d = d[1:]
    if len(d) == 10: d = '55' + d
    elif len(d) == 11: d = '55' + d
    return d

def normalizar_email(e):
    return (e or '').strip().lower()

CORA_H = ['data_envio','nome','cnpj_ou_cpf','tipo_empresa','email','telefone','servico_desejado','ramo_atividade','segmento','estado','cidade','preferencia_atendimento','status_atendimento','observação/comentários']
JUN_H = ['Data/Hora','Nome completo','Email','Telefone','segmento','cargo','gestao_financeira','problema','motivacao','anuncio','conjunto','campanha']
CAD_H = ['Data/Hora','Nome completo','Email','Telefone','cargo','funcionarios','faturamento','gestao_financeira','problema','interesse','investimento','motivacao','anuncio','conjunto','campanha']

cora_raw = json.load(open(os.path.join(SRC_DIR, 'cora.json')))['values']
rows_cora = [{h: (row[i] if i < len(row) else '') for i, h in enumerate(CORA_H)} for row in cora_raw]

jun_raw = json.load(open(os.path.join(SRC_DIR, 'meta_ads_jun.json')))['values']
rows_jun = []
for row in jun_raw:
    if len(row) > 12:
        row = row[:4] + row[5:]
    rows_jun.append({h: (row[i] if i < len(row) else '') for i, h in enumerate(JUN_H)})

cad_raw = json.load(open(os.path.join(SRC_DIR, 'meta_ads_cadastro.json')))['values']
rows_cad = [{h: (row[i] if i < len(row) else '') for i, h in enumerate(CAD_H)} for row in cad_raw]

def chave(r):
    tel = normalizar_telefone(r.get('Telefone',''))
    em = normalizar_email(r.get('Email',''))
    cnpj = (r.get('cnpj_ou_cpf') or r.get('cnpj') or '').strip()
    return tel or em or cnpj

def hdict(r):
    return hashlib.sha256(json.dumps(r, ensure_ascii=False).encode('utf-8')).hexdigest()

ok = True
for name, rows in [('cora', rows_cora), ('meta_ads_jun', rows_jun), ('meta_ads_cadastro', rows_cad)]:
    est_src = est.get(name, {})
    all_hashes = set()
    for k, v in est_src.items():
        hs = v if isinstance(v, list) else [v]
        for h in hs: all_hashes.add(h)
    match = miss = 0
    miss_list = []
    for r in rows:
        h = hdict(r)
        if h in all_hashes: match += 1
        else:
            miss += 1
            miss_list.append((chave(r), r.get('Data/Hora') or r.get('data_envio',''), (r.get('Nome completo') or r.get('nome',''))[:40]))
    print(f'{name}: {match} match / {miss} miss / {len(est_src)} chaves no estado')
    for m in miss_list:
        print('   MISS:', m)
    if miss > 0: ok = False

if not ok:
    print('RESULTADO: DIVERGÊNCIA')
    sys.exit(1)
print('RESULTADO: OK')
