#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captação de Leads — sincronização planilhas Google Sheets → CRM Terceirizou.

Pipeline:
  1. O agente (ETHOS) lê as planilhas via MCP e salva em tmp/polling/{fonte}.json.
  2. transform.py converte para {fonte: [ {coluna: valor}, ... ]} (leads_input.json).
  3. Este script recebe o JSON em stdin e faz upsert no CRM (PocketBase/Skip):
     - dedup por e-mail > telefone > dedup_key
     - idempotência por hash da linha (estado por job via ESTADO_PATH)

Estado (ESTADO_PATH, default scripts/captacao_leads/estado.json):
  { fonte: { chave_dedup: [hash_linha, ...] } }
  - LISTA de hashes por chave: várias linhas da planilha podem compartilhar a
    mesma chave (ex.: colisão Cora Isamara×Sperka). Guardar um hash só causava
    ping-pong infinito de updates.

Lições embutidas (não remover sem ler o changelog):
  - PocketBase rejeita '!=' em filtros (400) — busca sem filtro e filtra em Python.
  - updateRule leads: responsavel = @request.auth.id || admin → lead com
    responsavel='-' só é atualizável por token admin (404 caso contrário).
  - Linha SEM nome: create falha 400 (validation_required) para sempre e update
    nunca dispara → descartar e registrar no estado (linhas de teste F1-T04 da
    aba Jun vêm com colunas deslocadas → telefone vira '104').
  - Linha criptografada da Cora (nome+email cript, sem telefone): descartar e
    registrar no estado.
"""
import json
import os
import re
import sys
import hashlib
import urllib.request
import urllib.error
import datetime
import random

BASE = 'https://crm-oficial-65bb8.shrd00.internal.goskip.dev'
ESTADO = os.environ.get('ESTADO_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'estado.json'))
LOG = os.environ.get('LOG_PATH', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log_acoes.jsonl'))

_ADMIN_EMAIL = 'vinicius@terceirizou.com.br'
_ADMIN_SENHA = 'Terceirizou@2026'
_TOKEN = None


def _token():
    global _TOKEN
    if _TOKEN: return _TOKEN
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crm_token.txt')
    if os.path.exists(path):
        _TOKEN = open(path).read().strip()
    return _TOKEN


def renovar_token():
    """Re-autentica como admin e salva o token novo (acionada em 401/403)."""
    global _TOKEN
    req = urllib.request.Request(
        BASE + '/api/collections/users/auth-with-password',
        data=json.dumps({'identity': _ADMIN_EMAIL, 'password': _ADMIN_SENHA}).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'},
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    _TOKEN = data['token']
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crm_token.txt'), 'w') as f:
        f.write(_TOKEN)
    return _TOKEN


def api(method, path, data=None):
    """Chamada à API do CRM. Em 401/403 renova o token e tenta mais uma vez."""
    headers = {
        'Authorization': 'Bearer ' + (_token() or ''),
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
    }
    req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8') if data is not None else None, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', 'replace')
        if e.code in (401, 403):
            try:
                renovar_token()
                headers['Authorization'] = 'Bearer ' + _TOKEN
                req = urllib.request.Request(BASE + path, data=json.dumps(data).encode('utf-8') if data is not None else None, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=40) as resp2:
                    return resp2.status, json.loads(resp2.read().decode('utf-8'))
            except Exception:
                pass
        return e.code, body


SPREADSHEETS = [
    {
        'nome': 'cora',
        'canal': 'banco_cora',
        'planilha': '1TYe2__aZ0Y-x9LbUevJ8gYEMvGZtOWZE',
        'aba': 'Principal',
        'header_row': 3,
        'colunas': {
            'data_envio': 'data_envio', 'nome': 'nome', 'cnpj_ou_cpf': 'cnpj_ou_cpf',
            'tipo_empresa': 'tipo_empresa', 'email': 'email', 'telefone': 'telefone',
            'servico_desejado': 'servico_desejado', 'ramo_atividade': 'ramo_atividade',
            'segmento': 'segmento', 'estado': 'estado', 'cidade': 'cidade',
            'preferencia_atendimento': 'preferencia_atendimento',
            'status_atendimento': 'status_atendimento',
            'observação/comentários': 'observacao',
        },
    },
    {
        'nome': 'meta_ads_jun',
        'canal': 'meta',
        'planilha': '1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk',
        'aba': 'Leads Meta Ads - Jun.26',
        'header_row': 1,
        'colunas': {
            'Data/Hora': 'data_hora', 'Nome completo': 'nome', 'Email': 'email',
            'Telefone': 'telefone', 'segmento': 'segmento', 'cargo': 'cargo',
            'gestao_financeira': 'gestao_financeira', 'problema': 'problema',
            'motivacao': 'motivacao', 'anuncio': 'anuncio', 'conjunto': 'conjunto',
            'campanha': 'campanha',
        },
    },
    {
        'nome': 'meta_ads_cadastro',
        'canal': 'meta',
        'planilha': '1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk',
        'aba': 'Leads Anúncios de Cadastro',
        'header_row': 1,
        'colunas': {
            'Data/Hora': 'data_hora', 'Nome completo': 'nome', 'Email': 'email',
            'Telefone': 'telefone', 'cargo': 'cargo', 'funcionarios': 'funcionarios',
            'faturamento': 'faturamento', 'gestao_financeira': 'gestao_financeira',
            'problema': 'problema', 'interesse': 'interesse',
            'investimento': 'investimento', 'motivacao': 'motivacao',
            'anuncio': 'anuncio', 'conjunto': 'conjunto', 'campanha': 'campanha',
        },
    },
]


def normalizar_telefone(t):
    if not t: return ''
    d = re.sub(r'\D', '', str(t))
    if len(d) == 11 and d[0] == '0': d = d[1:]
    if len(d) == 10: d = '55' + d
    elif len(d) == 11: d = '55' + d
    return d


def normalizar_email(e):
    return (e or '').strip().lower()


def limpar_cnpj(c):
    if not c: return ''
    return re.sub(r'\D', '', str(c))


def parece_criptografado(s):
    """Detecta valores criptografados da Cora (base64 com '=', '+', '/' e poucas letras)."""
    if not s: return False
    s = str(s).strip()
    if len(s) < 16: return False
    especiais = sum(1 for ch in s if ch in '+=/')
    letras = sum(1 for ch in s if ch.isalpha())
    return especiais >= 1 and letras / max(len(s), 1) > 0.5


def gerar_dedup_key(tel, em, cnpj):
    if em: return 'email:' + em
    if tel: return 'tel:' + tel
    if cnpj: return 'cnpj:' + cnpj
    return ''


def gerar_lead_id():
    return format(random.getrandbits(32), '08x')


def hash_linha(vals):
    return hashlib.sha256(json.dumps(vals, ensure_ascii=False).encode('utf-8')).hexdigest()


def carregar_estado():
    if os.path.exists(ESTADO):
        try:
            return json.load(open(ESTADO, encoding='utf-8'))
        except Exception:
            return {}
    return {}


def salvar_estado(est):
    json.dump(est, open(ESTADO, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)


def registrar_acao(acao):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'ts': datetime.datetime.now().isoformat(), **acao}, ensure_ascii=False) + '\n')


def mapear_respostas(linha, fonte):
    """Campos extras da planilha → JSON 'respostas' do lead (chaves canônicas)."""
    respostas = {}
    for col, chave in fonte['colunas'].items():
        if chave in ('nome', 'email', 'telefone', 'data_hora', 'anuncio', 'conjunto', 'campanha', 'cnpj_ou_cpf'):
            continue
        v = linha.get(col)
        if v not in (None, ''):
            respostas[chave] = str(v)
    return respostas


def mapear_origem(fonte):
    """Mapeia o canal da fonte para o valor do select 'origem' do CRM."""
    mapa = {'banco_cora': 'cora', 'meta': 'meta_ads'}
    return mapa.get(fonte['canal'], 'manual')


def processar_linhas(fonte, linhas, estado_atual):
    """linhas: lista de dicts (coluna -> valor). Retorna (criados, atualizados, ignorados, estado_novo)."""
    est = estado_atual.get(fonte['nome'], {})
    criados = []
    atualizados = []
    ignorados = []
    estado_novo = {}

    # Carrega leads existentes do CRM (para dedup)
    st, dados = api('GET', '/api/collections/leads/records?perPage=300')
    if st != 200:
        raise RuntimeError(f'Falha ao buscar leads: {st} {dados}')
    leads_existentes = dados['items']
    por_telefone = {}
    por_email = {}
    por_dedup = {}
    for l in leads_existentes:
        tel = normalizar_telefone(l.get('telefone'))
        if tel: por_telefone[tel] = l
        em = normalizar_email(l.get('email'))
        if em: por_email[em] = l
        dk = l.get('dedup_key', '')
        if dk: por_dedup[dk] = l

    for i, linha in enumerate(linhas):
        # Chave de dedup da planilha: telefone (ou email se telefone vazio)
        tel = normalizar_telefone(linha.get('telefone') or linha.get('Telefone'))
        em = normalizar_email(linha.get('email') or linha.get('Email'))
        cnpj = limpar_cnpj(linha.get('cnpj_ou_cpf') or '')
        chave = tel or em or cnpj
        if not chave:
            ignorados.append({'linha': i + fonte['header_row'] + 1, 'motivo': 'sem identificador'})
            continue

        # Cora criptografado: se nome E email são criptografados E não há telefone, pula
        # (CNPJ é legítimo — não descarta linhas com CNPJ válido)
        nome_raw = str(linha.get('nome') or linha.get('Nome completo') or '').strip()
        email_raw = str(linha.get('email') or linha.get('Email') or '').strip()
        if parece_criptografado(nome_raw) and parece_criptografado(email_raw) and not tel:
            ignorados.append({'linha': i + fonte['header_row'] + 1, 'motivo': 'dados criptografados'})
            # registra o hash para não re-avaliar a linha a cada rodada
            h = hash_linha(linha)
            base = estado_novo.get(chave) or est.get(chave)
            hashes_chave = [base] if isinstance(base, str) else (list(base) if base else [])
            estado_novo[chave] = sorted(set(hashes_chave + [h]))
            continue

        # Linha sem nome útil: o CRM exige 'nome' no create (validation_required) e
        # o update nunca dispara (nome vazio não gera upd). Sem esse descarte, a
        # linha tenta CREATE a cada rodada e falha 400 para sempre (ex.: linhas de
        # teste F1-T04 na aba Jun com colunas deslocadas → telefone vira '104').
        if not nome_raw:
            ignorados.append({'linha': i + fonte['header_row'] + 1, 'motivo': 'sem nome (create sempre falharia)'})
            h = hash_linha(linha)
            base = estado_novo.get(chave) or est.get(chave)
            hashes_chave = [base] if isinstance(base, str) else (list(base) if base else [])
            estado_novo[chave] = sorted(set(hashes_chave + [h]))
            continue

        h = hash_linha(linha)
        # já processada e inalterada?
        # est[chave] pode ser string (hash único, legado) ou lista de hashes —
        # várias linhas da planilha podem compartilhar a mesma chave de dedup
        # (ex.: colisão Cora Isamara×Sperka, mesmo telefone/e-mail). Sem lista,
        # só o hash da ÚLTIMA linha fica no estado e a primeira linha é
        # re-processada em TODA rodada (ping-pong infinito de updates).
        # Base de hashes: prioriza o ACUMULADO desta rodada (estado_novo) —
        # sem isso, a 2ª linha com a mesma chave na mesma passada sobrescreve
        # o hash da 1ª e sobra 1 update por rodada para sempre.
        base = estado_novo.get(chave)
        if base is None:
            base = est.get(chave)
        if isinstance(base, str):
            hashes_chave = [base]
        elif base is None:
            hashes_chave = []
        else:
            hashes_chave = list(base)
        if h in hashes_chave:
            estado_novo[chave] = sorted(set(hashes_chave + [h]))
            continue

        # procura lead existente (dedup por email > telefone > dedup_key)
        lead = por_email.get(em) if em else None
        if not lead and tel:
            lead = por_telefone.get(tel)
        if not lead:
            dk = gerar_dedup_key(tel, em, cnpj)
            if dk:
                lead = por_dedup.get(dk)

        nome_lead = (linha.get('nome') or linha.get('Nome completo') or '').strip()[:200]
        origem = mapear_origem(fonte)
        dedup_key = gerar_dedup_key(tel, em, cnpj)
        respostas = mapear_respostas(linha, fonte)
        campanha = (linha.get('campanha') or linha.get('Campanha') or '').strip()[:200]
        anuncio = (linha.get('anuncio') or linha.get('Nome do Anúncio') or '').strip()[:200]

        if lead:
            # ATUALIZA apenas campos relevantes (não sobrescreve config do CRM)
            upd = {}
            if nome_lead and nome_lead != (lead.get('nome') or ''):
                upd['nome'] = nome_lead
            if tel and tel != (lead.get('telefone') or ''):
                upd['telefone'] = tel
            if em and em != (lead.get('email') or ''):
                upd['email'] = em
            if campanha and campanha != (lead.get('campanha') or ''):
                upd['campanha'] = campanha
            if anuncio and anuncio != (lead.get('anuncio_criativo') or ''):
                upd['anuncio_criativo'] = anuncio
            if respostas:
                # Merge com respostas existentes
                existing = lead.get('respostas') or {}
                if isinstance(existing, str):
                    try: existing = json.loads(existing)
                    except: existing = {}
                merged = {**existing, **respostas}
                if merged != existing:
                    upd['respostas'] = merged
            if upd:
                st2, r2 = api('PATCH', f'/api/collections/leads/records/{lead["id"]}', upd)
                if st2 in (200, 201):
                    atualizados.append({'id': lead['id'], 'campos': list(upd.keys())})
                    registrar_acao({'fonte': fonte['nome'], 'acao': 'update', 'lead_id': lead['id'], 'campos': list(upd.keys()), 'telefone': tel})
                    estado_novo[chave] = sorted(set(hashes_chave + [h]))
                else:
                    ignorados.append({'linha': i, 'motivo': f'update falhou {st2}'})
            else:
                estado_novo[chave] = sorted(set(hashes_chave + [h]))
        else:
            # CRIA — campos obrigatórios do schema atual
            payload = {
                'lead_id': gerar_lead_id(),
                'opportunity_id': '-',
                'nome': nome_lead,
                'telefone': tel or (linha.get('telefone') or ''),
                'origem': origem,
                'estagio': 'capturado',
                'responsavel': '-',
                'dedup_key': dedup_key,
            }
            if em: payload['email'] = em
            if campanha: payload['campanha'] = campanha
            if anuncio: payload['anuncio_criativo'] = anuncio
            if respostas: payload['respostas'] = respostas

            st2, r2 = api('POST', '/api/collections/leads/records', payload)
            if st2 in (200, 201):
                criados.append({'id': r2['id'], 'nome': payload['nome']})
                registrar_acao({'fonte': fonte['nome'], 'acao': 'create', 'lead_id': r2['id'], 'nome': payload['nome'], 'telefone': tel})
                estado_novo[chave] = sorted(set(hashes_chave + [h]))
            else:
                ignorados.append({'linha': i, 'motivo': f'create falhou {st2}: {str(r2)[:100]}'})

    estado_atual[fonte['nome']] = estado_novo
    return criados, atualizados, ignorados, estado_atual


def main():
    # O agente externo (MCP) fornece as linhas de cada planilha; aqui processa JSON em stdin
    # formato: {"cora": [ {coluna: valor}, ... ], "meta_ads_jun": [...], "meta_ads_cadastro": [...]}
    dados_entrada = json.load(sys.stdin)
    estado = carregar_estado()
    resumo = {'criados': [], 'atualizados': [], 'ignorados': 0}
    for fonte in SPREADSHEETS:
        linhas = dados_entrada.get(fonte['nome'], [])
        if not linhas:
            continue
        criados, atualizados, ignorados, estado = processar_linhas(fonte, linhas, estado)
        resumo['criados'].extend(criados)
        resumo['atualizados'].extend(atualizados)
        resumo['ignorados'] += len(ignorados)
    salvar_estado(estado)
    print(json.dumps(resumo, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
