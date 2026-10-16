#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Resumo diário da automação Captação de Leads — gera o corpo do e-mail com:
   - ações das últimas 24h (criações/atualizações por fonte)
   - dashboard do CRM (leads ativos, clientes, MRR, funil)
Envia para contato@terceirizou.com.br via Gmail (MCP gmail_send_email).
"""
import json
import os
import datetime

AQUI = os.path.dirname(os.path.abspath(__file__))
LOG_DIARIO = os.path.join(AQUI, 'log_acoes.jsonl')

FONTES = {'cora': 'Banco Cora', 'meta_ads_jun': 'Meta Ads (Jun/26)', 'meta_ads_cadastro': 'Meta Ads (Cadastro)'}


def ler_acoes_24h():
    """Lê o log e retorna ações das últimas 24h."""
    agora = datetime.datetime.now()
    limite = agora - datetime.timedelta(hours=24)
    acoes = []
    if os.path.exists(LOG_DIARIO):
        with open(LOG_DIARIO, encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                if not linha: continue
                try:
                    a = json.loads(linha)
                    ts = datetime.datetime.fromisoformat(a['ts'])
                    if ts >= limite:
                        acoes.append(a)
                except Exception:
                    continue
    return acoes


def resumo_dashboard():
    """Retorna métricas do CRM (leads ativos, clientes, MRR) — será preenchido pelo agente no envio."""
    return {
        'leads_ativos': None,   # preenchido na hora do envio via API
        'clientes_ativos': None,
        'mrr': None,
        'leads_no_mes': None,
        'em_reuniao': None,
        'em_proposta': None,
    }


def montar_html(acoes, dashboard):
    total_criados = sum(1 for a in acoes if a['acao'] == 'create')
    total_atualizados = sum(1 for a in acoes if a['acao'] == 'update')
    por_fonte = {}
    for a in acoes:
        if a['acao'] not in ('create', 'update'):
            continue  # ações internas (ex.: hash-registrado) não entram no resumo
        fn = FONTES.get(a['fonte'], a['fonte'])
        por_fonte.setdefault(fn, {'create': 0, 'update': 0})
        por_fonte[fn][a['acao']] += 1

    linhas_acoes = ''
    for fn, v in por_fonte.items():
        linhas_acoes += (
            f'<tr><td>{fn}</td><td>{v.get("create", 0)}</td><td>{v.get("update", 0)}</td></tr>'
        )
    if not linhas_acoes:
        linhas_acoes = '<tr><td colspan="3" style="text-align:center;color:#888;">Nenhuma ação nas últimas 24h</td></tr>'

    return f"""<html><body style="font-family:Arial,sans-serif;background:#f8fafc;padding:24px;">
  <div style="max-width:640px;margin:auto;background:#fff;border-radius:12px;border:1px solid #e2e8f0;padding:24px;">
    <h2 style="margin:0;color:#0f172a;">📊 Resumo Diário — Captação de Leads</h2>
    <p style="color:#64748b;margin:4px 0 20px;">{datetime.datetime.now().strftime('%d/%m/%Y %H:%M')} · últimas 24h</p>

    <h3 style="color:#0f172a;margin-bottom:8px;">Ações nas últimas 24h</h3>
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
      <thead><tr style="background:#f1f5f9;">
        <th style="padding:8px;text-align:left;">Fonte</th>
        <th style="padding:8px;">Criados</th>
        <th style="padding:8px;">Atualizados</th>
      </tr></thead>
      <tbody>{linhas_acoes}</tbody>
    </table>
    <p style="font-size:13px;color:#475569;margin-top:8px;"><strong>Total:</strong> {total_criados} criados · {total_atualizados} atualizados</p>

    <h3 style="color:#0f172a;margin:24px 0 8px;">Dashboard do CRM</h3>
    <table style="width:100%;border-collapse:collapse;font-size:14px;">
      <thead><tr style="background:#f1f5f9;">
        <th style="padding:8px;text-align:left;">Indicador</th>
        <th style="padding:8px;text-align:right;">Valor</th>
      </tr></thead>
      <tbody>
        <tr><td style="padding:8px;">Leads ativos</td><td style="padding:8px;text-align:right;">{dashboard.get('leads_ativos', '—')}</td></tr>
        <tr><td style="padding:8px;">Leads no mês</td><td style="padding:8px;text-align:right;">{dashboard.get('leads_no_mes', '—')}</td></tr>
        <tr><td style="padding:8px;">Em reunião</td><td style="padding:8px;text-align:right;">{dashboard.get('em_reuniao', '—')}</td></tr>
        <tr><td style="padding:8px;">Em proposta</td><td style="padding:8px;text-align:right;">{dashboard.get('em_proposta', '—')}</td></tr>
        <tr><td style="padding:8px;">Clientes ativos</td><td style="padding:8px;text-align:right;">{dashboard.get('clientes_ativos', '—')}</td></tr>
        <tr><td style="padding:8px;">MRR (R$)</td><td style="padding:8px;text-align:right;">{dashboard.get('mrr', '—')}</td></tr>
      </tbody>
    </table>
    <p style="color:#94a3b8;font-size:12px;margin-top:20px;">Automação Captação de Leads · Terceirizou CRM</p>
  </div>
</body></html>"""


def main():
    acoes = ler_acoes_24h()
    dashboard = resumo_dashboard()
    html = montar_html(acoes, dashboard)
    # O envio do e-mail é feito pelo agente (MCP gmail_send_email), que preenche o dashboard
    # via API do CRM antes de enviar. Este script gera o corpo; o orquestrador envia.
    print(json.dumps({'acoes': len(acoes), 'criados': sum(1 for a in acoes if a['acao']=='create'),
                      'atualizados': sum(1 for a in acoes if a['acao']=='update'),
                      'html': html}, ensure_ascii=False))


if __name__ == '__main__':
    main()
