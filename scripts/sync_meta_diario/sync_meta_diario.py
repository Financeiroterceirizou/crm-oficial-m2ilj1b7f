#!/usr/bin/env python3
"""AUTOMAÇÃO ÚNICA — Meta Ads → Planilha espelho → CRM Terceirizou.

Decisão do champion em 28/10/2026:
  - O Make alimenta a planilha espelho do Meta Ads; ela é a fonte.
  - A automação roda UMA vez por dia, às 18h.
  - Cora NÃO participa desta automação.

Por que não usa o LLM no caminho crítico:
  Os jobs antigos (91e0856 / a5b0) dependiam de um agent_turn do cron para ler
  a planilha via MCP — e morreram em 28/10 com "insufficient_balance" (429).
  Aqui a leitura é JSON-RPC direto no MCP googlesheets, feita pelo próprio
  script: se o LLM estiver sem crédito, a automação continua rodando.

Fluxo:
  1. lê as 2 abas vivas da planilha espelho (Jun.26 e Anúncios de Cadastro)
  2. transforma para o contrato canônico do processar.py
  3. processar.py faz dedup (telefone → email) e upsert no CRM via API REST
  4. grava relatório da rodada + exit code (0 ok, 1 falha) para o cron alarmar

Uso:  python3 sync_meta_diario.py [--dry-run]
"""
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta

BASE = '/home/ethos/.assistant/workspace'
AQUI = os.path.dirname(os.path.abspath(__file__))
TMP = os.path.join(BASE, 'tmp', 'sync_meta')
ESTADO_PATH = os.path.join(AQUI, 'estado.json')
REPORT_PATH = os.path.join(AQUI, 'ultima_rodada.json')
LOG_PATH = os.path.join(AQUI, 'sync.log')

SSID_META = '1GiZZjYkBNz_i6r_0cg2D9N6FulB4rJftFctzh4WxeEk'  # propriedade Terceirizou
ABAS = [
    ('meta_ads_jun', "'Leads Meta Ads - Jun.26'!A1:M200"),
    ('meta_ads_cadastro', "'Leads Anúncios de Cadastro'!A1:M200"),
]

BRT = timezone(timedelta(hours=-3))


def log(msg):
    linha = f"[{datetime.now(BRT).strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(linha)
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(linha + '\n')


# ---------------------------------------------------------------- leitura MCP
def _mcp_call(range_a1, tries=4):
    """Lê uma faixa da planilha via JSON-RPC direto no MCP googlesheets.

    Mesmo mecanismo validado em scripts/91e08561a5b65e5d/fetch_mcp_live_91e.py.
    Retry em 429 (cota do Google) com espera de 65s.
    """
    cfg = json.load(open('/home/ethos/.assistant/config.json'))
    srv = cfg['tools']['mcp']['servers']['googlesheets']
    url = srv['url']
    tok = srv['headers']['Authorization'].split(' ', 1)[1]
    args = {'range': range_a1, 'spreadsheet_id': SSID_META,
            'value_render_option': 'FORMATTED_VALUE'}
    body = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                       'params': {'name': 'GOOGLESHEETS_VALUES_GET',
                                  'arguments': args}}).encode()
    for tentativa in range(1, tries + 1):
        req = urllib.request.Request(url, data=body, method='POST', headers={
            'Authorization': 'Bearer ' + tok,
            'Accept': 'application/json, text/event-stream',
            'Content-Type': 'application/json',
            'User-Agent': 'terceirizou-sync-meta-diario/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                raw = r.read().decode('utf-8')
        except urllib.error.HTTPError as e:
            log(f'  HTTP {e.code} na leitura (tentativa {tentativa}/{tries})')
            if tentativa < tries:
                time.sleep(65)
                continue
            raise
        except (urllib.error.URLError, OSError) as e:
            log(f'  erro de rede {e} (tentativa {tentativa}/{tries})')
            if tentativa < tries:
                time.sleep(10 * tentativa)
                continue
            raise

        payload = None
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            for dl in reversed([l[5:].strip() for l in raw.splitlines()
                                if l.startswith('data: ')]):
                try:
                    payload = json.loads(dl)
                    break
                except json.JSONDecodeError:
                    continue
        if payload is None:
            log('  resposta ilegível — retry')
            time.sleep(30)
            continue
        if payload.get('error'):
            log(f"  rpc error: {str(payload['error'])[:120]} — retry")
            time.sleep(30)
            continue

        result = payload.get('result', payload)
        content = result.get('content') if isinstance(result, dict) else None
        if not content:
            log('  sem content — retry')
            time.sleep(30)
            continue
        inner = json.loads(content[0]['text'])
        if not inner.get('successfull', False):
            # 429 de cota do Sheets vem aqui dentro (successfull=false)
            log(f"  tool erro: {str(inner.get('error'))[:130]} — retry")
            if tentativa < tries:
                time.sleep(65)
                continue
            raise RuntimeError('leitura da planilha falhou')
        return inner
    raise RuntimeError('leitura da planilha esgotou as tentativas')


def ler_abas():
    """Retorna {nome_fonte: {'values': [...]}} no contrato do transform."""
    os.makedirs(TMP, exist_ok=True)
    crus = {}
    for nome, faixa in ABAS:
        log(f'lendo {nome}...')
        inner = _mcp_call(faixa)
        vals = inner['data']['values']
        crus[nome] = {'values': vals}
        with open(os.path.join(TMP, f'{nome}.json'), 'w', encoding='utf-8') as f:
            json.dump(crus[nome], f, ensure_ascii=False)
        log(f'  {nome}: {len(vals)} linhas brutas')
    return crus


# ------------------------------------------------------------------ transform
def transformar(crus):
    """Aplica o transform.py canônico (mesmo contrato de hash do estado.json)."""
    env = dict(os.environ)
    env['POLLING_TMP'] = TMP
    env['LEADS_INPUT_PATH'] = os.path.join(TMP, 'leads_input.json')
    r = subprocess.run(
        [sys.executable, os.path.join(BASE, 'scripts', '91e08561a5b65e5d', 'transform.py')],
        capture_output=True, text=True, env=env, timeout=180)
    if r.returncode != 0:
        log(f'transform FALHOU: {r.stderr[-500:]}')
        raise RuntimeError('transform falhou')
    return env['LEADS_INPUT_PATH']


# ------------------------------------------------------------------ processar
def processar(leads_input_path, dry_run=False):
    """Upsert no CRM via processar.py canônico."""
    env = dict(os.environ)
    env['ESTADO_PATH'] = ESTADO_PATH
    env['LEADS_INPUT_PATH'] = leads_input_path
    with open(leads_input_path, encoding='utf-8') as f:
        dados = f.read()
    r = subprocess.run(
        [sys.executable, os.path.join(BASE, 'scripts', 'captacao_leads', 'processar.py')],
        input=dados, capture_output=True, text=True, env=env, timeout=900)
    if r.returncode != 0:
        log(f'processar FALHOU: {r.stderr[-500:]}')
        raise RuntimeError('processar falhou')
    try:
        return json.loads(r.stdout.strip())
    except json.JSONDecodeError:
        log(f'processar saída inesperada: {r.stdout[-300:]}')
        raise RuntimeError('saída do processar ilegível')


# --------------------------------------------------------------------- guarda
def guarda_sanidade(crus):
    """Aborta se a planilha parecer vazia/quebrada — evita zerar o estado.

    Regra: cada aba precisa ter header + pelo menos 1 linha de dados. Se uma
    aba vier vazia, é falha do Make/planilha, não ausência de leads.
    """
    for nome, d in crus.items():
        vals = d.get('values') or []
        dados = [r for r in vals[1:] if r and any(str(c).strip() for c in r)]
        if len(dados) == 0:
            raise RuntimeError(
                f'{nome}: planilha sem linhas de dados (header={len(vals)} linha(s)) — '
                f'rodada abortada para não zerar o estado. Verificar se o Make parou de gravar.')
        log(f'  sanidade {nome}: {len(dados)} linhas de dados')


# ------------------------------------------------------------------------ main
def main():
    dry = '--dry-run' in sys.argv
    inicio = datetime.now(BRT)
    log('=' * 70)
    log(f'rodada iniciada{" (DRY-RUN)" if dry else ""}')

    relatorio = {'inicio': inicio.isoformat(), 'dry_run': dry}
    try:
        crus = ler_abas()
        guarda_sanidade(crus)
        leads_input = transformar(crus)
        if dry:
            with open(leads_input, encoding='utf-8') as f:
                d = json.load(f)
            relatorio['preview'] = {k: len(v) for k, v in d.items() if isinstance(v, list)}
            log(f"DRY-RUN: {relatorio['preview']}")
            relatorio['status'] = 'dry_run_ok'
            return 0

        resultado = processar(leads_input)
        relatorio['resultado'] = resultado
        criados = resultado.get('criados', resultado.get('total_criados', 0))
        atualizados = resultado.get('atualizados', resultado.get('total_atualizados', 0))
        ignorados = resultado.get('ignorados', resultado.get('total_ignorados', 0))
        log(f'resultado: criados={criados} atualizados={atualizados} ignorados={ignorados}')
        relatorio['status'] = 'ok'
        return 0
    except Exception as e:
        relatorio['status'] = 'falha'
        relatorio['erro'] = str(e)
        log(f'FALHA: {e}')
        return 1
    finally:
        fim = datetime.now(BRT)
        relatorio['fim'] = fim.isoformat()
        relatorio['duracao_s'] = round((fim - inicio).total_seconds(), 1)
        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, ensure_ascii=False, indent=1)
        log(f"rodada encerrada: {relatorio.get('status')} em {relatorio['duracao_s']}s")
        log('=' * 70)


if __name__ == '__main__':
    sys.exit(main())
