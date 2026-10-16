#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Captação de Leads — monitora duas planilhas do Google Sheets e sincroniza com o CRM Terceirizou.

Fontes:
  - Cora:        https://docs.google.com/spreadsheets/d/1TYe2__HmgLUhqOoudmxm-I2fL94wKSJ8ThmXmbCUXfY
  - Meta Ads:    https://docs.google.com/spreadsheets/d/1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk  (PROPRIEDADE TERCEIRIZOU, desde 2026-08-31)

Regras:
  - Processa somente linhas NOVAS ou ALTERADAS desde a última verificação (por data/hora ou estado local).
  - Dedup: se o lead já existe no CRM (telefone/e-mail/CNPJ), atualiza; senão cria.
  - Preserva regras do CRM: hooks de score/trava rodam no create; canal_origem por fonte.
  - Log das ações em JSON para o resumo diário.

Uso: python3 processar.py
"""
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
import datetime
import hashlib
import re

# ---------- Config ----------
BASE = os.environ.get("CRM_BASE_URL", "https://crm-oficial-65bb8.shrd00.internal.goskip.dev")
AQUI = os.path.dirname(os.path.abspath(__file__))
TOKEN = open(os.path.join(AQUI, 'crm_token.txt')).read().strip()

# Credenciais de automação (usuário do CRM) — usadas para renovar o token quando expirar
_ADMIN_EMAIL = "vinicius@terceirizou.com.br"
_ADMIN_SENHA = "Terceirizou@2026"

# User-Agent de navegador — obrigatório: sem ele o Cloudflare bloqueia com "error code: 1010"
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'}

def renovar_token():
    """Re-autentica e salva novo token (JWT de auth expira ~5 dias)."""
    global TOKEN
    try:
        req = urllib.request.Request(
            BASE + '/api/collections/users/auth-with-password',
            data=json.dumps({'identity': _ADMIN_EMAIL, 'password': _ADMIN_SENHA}).encode('utf-8'),
            headers={'Content-Type': 'application/json', **UA},
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=40) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        TOKEN = data['token']
        with open(os.path.join(AQUI, 'crm_token.txt'), 'w', encoding='utf-8') as f:
            f.write(TOKEN)
        print('  [token] renovado e salvo', file=sys.stderr)
    except Exception as e:
        print(f'  [token] falha ao renovar: {e}', file=sys.stderr)
# Estado e log podem ser isolados por job via env var (evita briga entre o
# polling 91e08561a5b65e5d e o job antigo a5b0d6956d407911, que compartilhavam
# o mesmo arquivo e se invalidavam mutuamente a cada ciclo).
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


def api(method, path, data=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode('utf-8') if data is not None else None,
        headers={'Content-Type': 'application/json',
                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
                 'Authorization': 'Bearer ' + TOKEN},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        # Token expirado/inválido: renova uma vez e tenta de novo
        if e.code in (401, 403):
            renovar_token()
            req2 = urllib.request.Request(
                BASE + path,
                data=json.dumps(data).encode('utf-8') if data is not None else None,
                headers={'Content-Type': 'application/json',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
                         'Authorization': 'Bearer ' + TOKEN},
                method=method,
            )
            try:
                with urllib.request.urlopen(req2, timeout=40) as resp2:
                    return resp2.status, json.loads(resp2.read().decode('utf-8'))
            except urllib.error.HTTPError as e2:
                return e2.code, e2.read().decode('utf-8')[:300]
        return e.code, e.read().decode('utf-8')[:300]


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
    if len(s) < 20: return False
    letras = sum(1 for ch in s if ch.isalpha())
    especiais = sum(1 for ch in s if ch in '=+/')
    # base64 típico: muitos não-alfanuméricos e proporção baixa de letras
    if especiais > 0 and (letras / len(s)) < 0.75:
        return True
    # string longa sem espaços, só base64-ish
    if len(s) > 30 and ' ' not in s and sum(1 for ch in s if ch.isalnum() or ch in '=+/') == len(s):
        return True
    # base64 clássico: comprimento múltiplo de 4, termina em '=' (padding), só charset base64
    if ' ' not in s and len(s) % 4 == 0 and s.endswith('=') and \
       sum(1 for ch in s if ch.isalnum() or ch in '=+/') == len(s):
        return True
    # Célula Cora truncada (2026-09-24): re-criptografia da Cora truncou um e-mail
    # cifrado para 24 chars terminando em '=' — caiu no dedup como e-mail "real"
    # e criou lead duplicado. Regra: e-mail com padding base64 mas SEM '@' é
    # criptografado, independente de tamanho (e-mail real sempre tem @).
    if s.endswith('=') and '@' not in s and \
       sum(1 for ch in s if ch.isalnum() or ch in '=+/') == len(s):
        return True
    return False


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
    with open(LOG_DIARIO, 'a', encoding='utf-8') as f:
        f.write(json.dumps({'ts': datetime.datetime.now().isoformat(), **acao}, ensure_ascii=False) + '\n')


# ---------- Leitura das planilhas via Google Sheets (MCP) ----------
# Esta função é chamada externamente: o agente lê as planilhas via MCP googlesheets e
# entrega as linhas como JSON. Aqui implementamos o processamento puro (testável).
def gerar_lead_id():
    """Gera um lead_id curto único (8 chars hex)."""
    import uuid
    return uuid.uuid4().hex[:8]


def gerar_dedup_key(tel, em, cnpj):
    """Gera chave de dedup a partir dos identificadores disponíveis."""
    if em: return f'email:{em}'
    if tel: return f'tel:{tel}'
    if cnpj: return f'cnpj:{cnpj}'
    return ''


def mapear_respostas(linha, fonte):
    """Extrai respostas do formulário como JSON para o campo 'respostas' do CRM."""
    respostas = {}
    if fonte['nome'] == 'meta_ads_jun':
        # Colunas extras do Meta Jun que vão para respostas
        for campo_src, campo_dst in [
            ('segmento', 'segmento'),
            ('cargo', 'cargo'),
            ('gestao_financeira', 'gestao_financeira'),
            ('problema', 'problema'),
            ('motivacao', 'motivacao'),
        ]:
            val = linha.get(campo_src, '')
            if val and str(val).strip():
                respostas[campo_dst] = str(val).strip()
    elif fonte['nome'] == 'meta_ads_cadastro':
        for campo_src, campo_dst in [
            ('cargo', 'cargo'),
            ('funcionarios', 'funcionarios'),
            ('faturamento', 'faturamento'),
            ('gestao_financeira', 'gestao_financeira'),
            ('problema', 'problema'),
            ('interesse', 'interesse'),
            ('investimento', 'investimento'),
            ('motivacao', 'motivacao'),
        ]:
            val = linha.get(campo_src, '')
            if val and str(val).strip():
                respostas[campo_dst] = str(val).strip()
    elif fonte['nome'] == 'cora':
        for campo_src, campo_dst in [
            ('servico_desejado', 'servico_desejado'),
            ('ramo_atividade', 'ramo_atividade'),
            ('segmento', 'segmento'),
            ('preferencia_atendimento', 'preferencia_atendimento'),
            ('status_atendimento', 'status_atendimento'),
            ('observação/comentários', 'observacao'),
        ]:
            val = linha.get(campo_src, '')
            if val and str(val).strip() and str(val).strip() != '-':
                respostas[campo_dst] = str(val).strip()
    return respostas if respostas else None


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

    # Carrega leads existentes do CRM (para dedup) — com paginação
    # (perPage=300 fixo deixava de enxergar leads além do primeiro lote; com
    # >300 registros o dedup falhava e lead existente era re-criado)
    leads_existentes = []
    page = 1
    while True:
        st, dados = api('GET', f'/api/collections/leads/records?perPage=200&page={page}')
        if st != 200:
            raise RuntimeError(f'Falha ao buscar leads (página {page}): {st} {dados}')
        leads_existentes.extend(dados['items'])
        if page * 200 >= dados.get('totalItems', 0) or not dados['items']:
            break
        page += 1
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
