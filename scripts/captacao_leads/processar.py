#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Polling planilhas Google Sheets -> CRM Terceirizou (PocketBase/Skip).

Lê JSON em stdin no formato:
  {"cora": [ {coluna: valor}, ... ], "meta_ads_jun": [...], "meta_ads_cadastro": [...]}

- Dedup: se o lead já existe no CRM (telefone/e-mail/CNPJ), atualiza; senão cria.
- Estado (hash por linha processada) em ESTADO_PATH (env var) para permitir
  instâncias paralelas com estados isolados.
- Token JWT renovado automaticamente em 401/403 (renovar_token).
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error
import hashlib
from datetime import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
ESTADO = os.environ.get('ESTADO_PATH', os.path.join(AQUI, 'estado.json'))
LOG_DIARIO = os.environ.get('LOG_DIARIO_PATH', os.path.join(AQUI, 'log_acoes.jsonl'))

SPREADSHEETS = [
    {
        'nome': 'cora',
        'id': '1TYe2__HmgLUhqOoudmxm-I2fL94wKSJ8ThmXmbCUXfY',
        'aba': 'Principal',
        'header_row': 4,          # linha do cabeçalho (dados começam na 5)
        'canal': 'banco_cora',
        'colunas': ['data_envio', 'nome', 'cnpj_ou_cpf', 'tipo_empresa', 'email', 'telefone',
                    'servico_desejado', 'ramo_atividade', 'segmento', 'estado', 'cidade',
                    'preferencia_atendimento', 'status_atendimento', 'observação/comentários'],
    },
    {
        'nome': 'meta_ads_jun',
        'id': '1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk',   # NOVA (propriedade Terceirizou)
        'aba': 'Leads Meta Ads - Jun.26',
        'header_row': 1,
        'canal': 'meta',
        'colunas': ['Data/Hora', 'Nome completo', 'Email', 'Telefone', 'segmento', 'cargo',
                    'gestao_financeira', 'problema', 'motivacao', 'anuncio', 'conjunto', 'campanha'],
        'mapeamento': {
            'Data/Hora': 'Data/Hora',
            'nome': 'Nome completo',
            'email': 'Email',
            'telefone': 'Telefone',
            'segmento': 'Qual o segmento de atuação da empresa?',
            'cargo': 'Qual seu cargo na empresa?',
            'gestao_financeira': 'Quem faz a gestão financeira hoje?',
            'problema': 'Qual o maior problema na gestão financeira?',
            'motivacao': 'O que te motivou a buscar a terceirização financeira agora',
            'anuncio': 'Nome do Anúncio',
            'conjunto': 'Conjunto de Anúncio',
            'campanha': 'Campanha',
        },
    },
    {
        'nome': 'meta_ads_cadastro',
        'id': '1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk',   # NOVA (propriedade Terceirizou)
        'aba': 'Leads Anúncios de Cadastro',
        'header_row': 1,
        'canal': 'meta',
        'colunas': ['Data/Hora', 'Nome completo', 'Email', 'Telefone', 'cargo', 'funcionarios',
                    'faturamento', 'gestao_financeira', 'problema', 'interesse', 'investimento',
                    'motivacao', 'anuncio', 'conjunto', 'campanha'],
        'mapeamento': {
            'Data/Hora': 'Data/Hora',
            'nome': 'Nome completo',
            'email': 'Email',
            'telefone': 'Telefone',
            'cargo': 'Qual é o seu cargo na empresa?',
            'funcionarios': 'Quantos funcionários a empresa possui hoje?',
            'faturamento': 'Qual é o faturamento médio mensal da empresa?',
            'gestao_financeira': 'Hoje, como é feita a gestão financeira da empresa?',
            'problema': 'Qual é o MAIOR problema financeiro da sua empresa hoje?',
            'interesse': 'Você tem interesse em contratar uma empresa para cuidar da gestão financeira do seu negócio?',
            'investimento': 'Se fizer sentido, você estaria disposto a investir mensalmente para ter uma gestão financeira profissional?',
            'motivacao': 'O que te motivou a buscar terceirização financeira agora?',
            'anuncio': 'Nome do Anúncio',
            'conjunto': 'Conjunto de Anúncio',
            'campanha': 'Campanha',
        },
    },
]

BASE = 'https://crm-oficial-65bb8.shrd00.internal.goskip.dev'
TOKEN_PATH = os.path.join(AQUI, 'crm_token.txt')

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}


def api(metodo, rota, payload=None):
    """Chamada à API do CRM (PocketBase). Renova token em 401/403 e tenta de novo."""
    token = ler_token()
    st, resp = _req(metodo, rota, payload, token)
    if st in (401, 403):
        renovar_token()
        token = ler_token()
        st, resp = _req(metodo, rota, payload, token)
    return st, resp


def _req(metodo, rota, payload, token):
    url = BASE + rota
    data = json.dumps(payload).encode('utf-8') if payload is not None else None
    req = urllib.request.Request(url, data=data, method=metodo)
    req.add_header('Authorization', 'Bearer ' + token)
    req.add_header('Content-Type', 'application/json')
    for k, v in UA.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode('utf-8'))
        except Exception:
            body = {}
        return e.code, body


def ler_token():
    with open(TOKEN_PATH) as f:
        return f.read().strip()


def renovar_token():
    """Re-autentica como vinicius@terceirizou.com.br e salva o novo JWT."""
    email = 'vinicius@terceirizou.com.br'
    senha = 'Terceirizou@2026'
    st, resp = _req('POST', '/api/collections/users/auth-with-password',
                    {'identity': email, 'password': senha}, '')
    if st == 200 and resp.get('token'):
        with open(TOKEN_PATH, 'w') as f:
            f.write(resp['token'])
        return True
    raise RuntimeError(f'Falha ao renovar token: {st} {str(resp)[:200]}')


def normalizar_telefone(t):
    """Normaliza telefone para formato internacional sem símbolos (55DDNNNNNNNNN)."""
    if not t:
        return ''
    digits = re.sub(r'\D', '', str(t))
    if not digits:
        return ''
    if not digits.startswith('55'):
        digits = '55' + digits
    return digits


def normalizar_email(e):
    if not e:
        return ''
    return str(e).strip().lower()


def limpar_cnpj(c):
    if not c:
        return ''
    return re.sub(r'\D', '', str(c))


def gerar_dedup_key(tel, em, cnpj):
    """Chave de dedup: email > telefone > cnpj (mesma convenção do webhook)."""
    if em:
        return 'email:' + em
    if tel:
        return 'tel:' + tel
    if cnpj:
        return 'cnpj:' + cnpj
    return ''


def gerar_lead_id():
    return 'lead_' + hashlib.sha1(str(datetime.utcnow().timestamp()).encode()).hexdigest()[:12]


def hash_linha(vals):
    return hashlib.sha256(json.dumps(vals, ensure_ascii=False, sort_keys=True).encode('utf-8')).hexdigest()


def carregar_estado():
    if os.path.exists(ESTADO):
        with open(ESTADO) as f:
            return json.load(f)
    return {}


def salvar_estado(estado):
    with open(ESTADO, 'w') as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def registrar_acao(acao):
    acao['ts'] = datetime.now().isoformat()
    with open(LOG_DIARIO, 'a') as f:
        f.write(json.dumps(acao, ensure_ascii=False) + '\n')


def mapear_respostas(linha, fonte):
    """Extrai campos de respostas do formulário para o JSON 'respostas' do lead."""
    resp = {}
    mapa = fonte.get('mapeamento') or {}
    for chave, coluna in mapa.items():
        if chave in ('Data/Hora', 'nome', 'email', 'telefone', 'anuncio', 'conjunto', 'campanha'):
            continue
        val = str(linha.get(coluna) or '').strip()
        if val and val != '-':
            resp[chave] = val
    # Cora: colunas canônicas direto
    if fonte['nome'] == 'cora':
        for chave in ('servico_desejado', 'ramo_atividade', 'segmento', 'estado', 'cidade', 'preferencia_atendimento'):
            val = str(linha.get(chave) or '').strip()
            if val and val != '-':
                resp[chave] = val
    return resp


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
            continue

        h = hash_linha(linha)
        # já processada e inalterada?
        # est[chave] pode ser string (hash único, legado) ou lista de hashes —
        # várias linhas da planilha podem compartilhar a mesma chave de dedup
        # (ex.: colisão Cora Isamara×Sperka, mesmo telefone/e-mail). Sem lista,
        # só o hash da ÚLTIMA linha fica no estado e a primeira linha é
        # re-processada em TODA rodada (ping-pong infinito de updates).
        hashes_chave = est.get(chave)
        if isinstance(hashes_chave, str):
            hashes_chave = [hashes_chave]
        elif hashes_chave is None:
            hashes_chave = []
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


def parece_criptografado(texto):
    """Detecta nome/e-mail anonimizado pela Cora (ex.: '***' ou base64-ish)."""
    if not texto:
        return False
    t = str(texto)
    if '***' in t or '•••' in t:
        return True
    # heurística: sequência longa sem vogais/espacos (hash)
    if re.fullmatch(r'[A-Za-z0-9+/=]{24,}', t.replace(' ', '')):
        return True
    return False


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
