#!/usr/bin/env python3
"""Valida tmp/polling (ou SPOT_DIR) contra o estado do 91e0856 — hash do DICT pós-transform."""
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
# NORMALIZA Cadastro como o transform.py (2026-10-14): o estado foi gerado com
# conjunto/campanha VAZIOS (13-col truncado), mas a leitura live A1:O200 traz 15
# colunas preenchidas → sem esse corte o validador acusa 27 misses falsos.
cad_raw = [r[:13] + [''] * max(0, 13 - len(r)) for r in cad_raw]
rows_cad = [{h: (row[i] if i < len(row) else '') for i, h in enumerate(CAD_H)} for row in cad_raw]

def chave(r):
    tel = normalizar_telefone(r.get('Telefone',''))
    em = normalizar_email(r.get('Email',''))
    cnpj = (r.get('cnpj_ou_cpf') or r.get('cnpj') or '').strip()
    return tel or em or cnpj

def hdict(r):
    return hashlib.sha256(json.dumps(r, ensure_ascii=False).encode('utf-8')).hexdigest()

ok = True
# Linhas estruturais que nunca existem no estado (aviso da Cora, linha vazia, headers)
def estrutural(r, name):
    first = (r.get('data_envio') or r.get('Data/Hora') or '')
    if first == 'data_envio' or first == 'Data/Hora':
        return True  # header
    if first == '' and not any(str(v).strip() for v in r.values() if v):
        return True  # linha vazia
    if str(first).startswith('Atenção:'):
        return True  # aviso da Cora
    return False

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
        elif estrutural(r, name):
            pass  # aviso/linha vazia/header — nunca devem casar (estrutural)
        else:
            miss += 1
            miss_list.append((chave(r), r.get('Data/Hora') or r.get('data_envio',''), (r.get('Nome completo') or r.get('nome',''))[:40]))
    print(f'{name}: {match} match / {miss} miss / {len(est_src)} chaves no estado')
    for m in miss_list:
        print('   MISS:', m)
        ok = False
print('RESULTADO:', 'OK' if ok else 'DIVERGÊNCIA')
sys.exit(0 if ok else 1)
