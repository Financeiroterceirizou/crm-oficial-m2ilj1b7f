// F3-T05 - Sequência de follow-up idempotente via Resend (SPEC-3-002 CA-3-101/102).
// POST /backend/v1/followup-lead
// Body: { lead_id, tentativa (1..3, opcional; sem tentativa = repete a tentativa atual, ou 1 na 1a vez) }
// - Valida: config aprovada (RN-3-101), lead qualificado + e-mail válido + base legal (RN-3-102).
// - Envia APENAS o e-mail do modelo aprovado (cadencia_followup_v1.json v1.1) — sem copy nova.
// - Idempotência: chave lead_id + cadencia + tentativa; repetição devolve already_sent sem nova chamada.
//   Repetir a chamada NUNCA auto-avança a tentativa — avançar é papel do scheduler (F3-T06),
//   que passa a tentativa explícita no body.
// - Falha Resend (4xx/5xx/timeout): 502 sem falso sucesso + error_log (fila humana), sem chave exposta.
// - Paradas (resposta/agendamento/no_show/descadastro/bounce) são da F3-T06 — aqui só o disparo.
// Requer autenticacao.
// NOTA runtime Skip: constantes/helpers declarados DENTRO do callback do routerAdd —
// escopo de módulo não fica visível ao handler (padrão de agendar_lead.js/agendar_borda.js).
// v0.0.54: paradas checadas antes do envio; secrets lidas a cada request via $secrets.get.

routerAdd(
  'POST',
  '/backend/v1/followup-lead',
  (e) => {
    // Modelos aprovados pelo champion (cadencia_followup_v1.json v1.1, 2026-09-16).
    // Fonte: config aprovada no repo; variaveis {{nome}} e {{link_agenda}}.
    const MODELOS = [
      {
        ordem: 1,
        dia: 'D+0',
        assunto: '{{nome}}, sua gestão financeira organizada — vale 15 minutos?',
        corpo:
          'Bom dia {{nome}}!\n\nRecebi seu contato pelo nosso formulário. Antes de qualquer proposta, quero entender o seu financeiro: como estão as contas a pagar e a receber, e o quanto o dono ainda faz na mão.\n\nA Terceirizou faz o financeiro de prestadores de serviço: organiza os dados, entrega fluxo de caixa e DRE, e dá direção para a decisão. Mais do que terceirizar o financeiro.\n\nSe fizer sentido, escolha um horário aqui: {{link_agenda}}\nSe preferir, responda este e-mail com uma pergunta direta — respondo de imediato.\n\nVinícius Oliveira da Costa\nTerceirizou — mais do que terceirizar o financeiro\nterceirizou.com.br',
      },
      {
        ordem: 2,
        dia: 'D+1',
        assunto: 'O que muda quando o financeiro sai da mão do dono',
        corpo:
          'Bom dia {{nome}}!\n\nA maioria dos prestadores que atendo chega com o mesmo cenário: contas misturadas, fluxo de caixa na cabeça do dono e decisão sem número.\n\nDepois que assumimos a gestão: caixa organizado, relatórios legíveis e o dono decide com dado — sem virar refém do financeiro no fim do mês.\n\nQuero te mostrar isso com o SEU número, não com exemplo. 15 minutos resolvem.\n\n{{link_agenda}}\n\nVinícius Oliveira da Costa\nTerceirizou — mais do que terceirizar o financeiro\nterceirizou.com.br',
      },
      {
        ordem: 3,
        dia: 'D+2',
        assunto: 'Encerro por aqui, {{nome}} — a porta fica aberta',
        corpo:
          'Bom dia {{nome}}!\n\nNão quero insistir. Se o momento não é agora, tudo bem — encerro a sequência por aqui.\n\nDeixo só o essencial: quando o financeiro começar a pesar na sua operação, o primeiro passo é uma conversa de 15 minutos. A porta fica aberta.\n\n{{link_agenda}}\n\nQualquer dúvida estamos à disposição.\n\nVinícius Oliveira da Costa\nTerceirizou — mais do que terceirizar o financeiro\nterceirizou.com.br',
      },
    ]

    const CADENCIA_VERSAO = '1.1'
    const MODELOS_VERSAO = '1.0'
    const REMETENTE = 'Terceirizou <financeiro@terceirizou.com.br>'
    const LINK_AGENDA = 'https://crm-oficial-65bb8.goskip.app'

    function escapeHtml(s) {
      return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
    }

    function corpoHtml(texto) {
      const linhas = String(texto).split('\n')
      let html = ''
      for (const linha of linhas) {
        if (linha.trim() === '') {
          html += '<br>'
        } else {
          html +=
            '<p style="margin:0 0 12px 0;font-family:Arial,sans-serif;font-size:14px;line-height:1.5;color:#222">' +
            escapeHtml(linha) +
            '</p>'
        }
      }
      html +=
        '<p style="font-family:Arial,sans-serif;font-size:11px;color:#999"><a href="{{link_descadastro}}" style="color:#999">Não quero mais receber estes e-mails</a></p>'
      return html
    }

    const body = e.requestInfo().body || {}
    const leadId = String(body.lead_id || '').trim()
    if (!leadId) return e.json(400, { error: 'lead_id obrigatorio' })

    let lead = null
    try {
      lead = $app.findRecordById('leads', leadId)
    } catch (_) {
      lead = null
    }
    if (!lead) return e.json(404, { error: 'lead nao encontrado' })

    // --- RN-3-101: config aprovada (versao com modelos aprovados) ---
    if (!CADENCIA_VERSAO || MODELOS.length !== 3) {
      return e.json(409, {
        status: 'bloqueado',
        motivo: 'configuracao_cadencia_nao_aprovada',
        chamada_resend: false,
      })
    }

    // --- RN-3-103: parada ativa -> zero envio, historico preservado ---
    if (lead.get('followup_estado') === 'parado') {
      return e.json(409, {
        status: 'bloqueado',
        motivo: 'followup_parado:' + (lead.get('followup_parada') || 'sem_motivo'),
        chamada_resend: false,
      })
    }

    // --- RN-3-102: elegibilidade ---
    if (lead.get('estado_qualificacao') !== 'qualificado') {
      return e.json(409, {
        status: 'bloqueado',
        motivo: 'lead_nao_qualificado',
        chamada_resend: false,
      })
    }
    const email = String(lead.get('email') || '').trim()
    if (!email || email.indexOf('@') < 1 || email.indexOf('.') < 0) {
      return e.json(409, {
        status: 'bloqueado',
        motivo: 'email_invalido_ou_ausente',
        chamada_resend: false,
      })
    }
    // Base legal LGPD registrada (interesse legitimo — lead interagiu com formulario/anuncio)
    const origem = String(lead.get('origem') || '').trim()
    if (!origem) {
      return e.json(409, {
        status: 'bloqueado',
        motivo: 'sem_base_legal_registrada',
        chamada_resend: false,
      })
    }

    // --- Tentativa da cadência ---
    // Sem tentativa no body: repete a tentativa atual (ou 1 na primeira vez).
    // Avançar a cadência é papel do scheduler (F3-T06), que passa a tentativa explícita.
    let tentativa = Number(body.tentativa || 0)
    if (!Number.isInteger(tentativa) || tentativa < 1 || tentativa > 3) {
      const atual = Number(lead.get('followup_tentativa') || 0)
      tentativa = atual >= 1 && atual <= 3 ? atual : 1
    }
    const modelo = MODELOS[tentativa - 1]
    const chave = leadId + ':followup:v' + CADENCIA_VERSAO + ':t' + tentativa

    // --- Idempotência (CA-3-102): repetir não envia de novo ---
    if (lead.get('followup_idempotency_key') === chave && lead.get('followup_ultimo_envio_id')) {
      return e.json(200, {
        status: 'already_sent',
        lead_id: lead.get('lead_id'),
        tentativa: tentativa,
        resend_email_id: lead.get('followup_ultimo_envio_id'),
      })
    }

    // --- Render dos modelos aprovados (sem copy nova) ---
    const nome = String(lead.get('nome') || '').trim()
    const assunto = modelo.assunto.split('{{nome}}').join(nome)
    const corpoTexto = modelo.corpo
      .split('{{nome}}')
      .join(nome)
      .split('{{link_agenda}}')
      .join(LINK_AGENDA)
    const html = corpoHtml(corpoTexto)

    // --- Envio via Resend ---
    const apiKey = $secrets.get('RESEND_API_KEY')
    if (!apiKey) {
      try {
        const errCol = $app.findCollectionByNameOrId('error_log')
        const errRec = new Record(errCol)
        errRec.set('error_id', $security.randomString(12))
        errRec.set('source_event_id', leadId)
        errRec.set('categoria', 'timeout')
        errRec.set('resumo', 'follow-up sem RESEND_API_KEY no cofre: ' + lead.get('lead_id'))
        errRec.set('payload_resumido', 'lead_id=' + leadId + ';tentativa=' + tentativa)
        errRec.set('tentativa', 1)
        errRec.set('estado', 'pendente')
        errRec.set('dono', 'Henrique Tavano')
        errRec.set('proxima_acao', 'configurar RESEND_API_KEY no cofre do Skip')
        errRec.set(
          'historico',
          JSON.stringify([
            {
              acao: 'criacao',
              ator: 'followup_lead',
              data: new Date().toISOString(),
              detalhes: 'sem chave resend',
            },
          ]),
        )
        $app.save(errRec)
      } catch (_) {}
      return e.json(503, {
        status: 'pendente_configuracao',
        motivo: 'resend_api_key_ausente',
        chamada_resend: false,
      })
    }

    const idempotencyKey = 'followup/' + chave
    let resposta = null
    try {
      resposta = $http.send({
        url: 'https://api.resend.com/emails',
        method: 'POST',
        headers: {
          Authorization: 'Bearer ' + apiKey,
          'Content-Type': 'application/json',
          'User-Agent': 'terceirizou-crm-followup/1.0',
          'Idempotency-Key': idempotencyKey,
        },
        body: JSON.stringify({
          from: REMETENTE,
          to: [email],
          bcc: ['financeiro@terceirizou.com.br'],
          subject: assunto,
          text: corpoTexto,
          html: html,
        }),
        timeout: 15,
      })
    } catch (_) {
      resposta = null
    }

    // --- Falha Resend: sem falso sucesso, fila humana (CA-3-104) ---
    if (
      !resposta ||
      resposta.statusCode < 200 ||
      resposta.statusCode >= 300 ||
      !resposta.json ||
      !resposta.json.id
    ) {
      try {
        const errCol = $app.findCollectionByNameOrId('error_log')
        const errRec = new Record(errCol)
        errRec.set('error_id', $security.randomString(12))
        errRec.set('source_event_id', leadId)
        errRec.set('categoria', 'timeout')
        errRec.set(
          'resumo',
          'falha envio follow-up Resend (' +
            (resposta ? 'HTTP ' + resposta.statusCode : 'erro de transporte') +
            '): ' +
            lead.get('lead_id'),
        )
        errRec.set(
          'payload_resumido',
          'lead_id=' +
            leadId +
            ';tentativa=' +
            tentativa +
            ';http=' +
            (resposta ? resposta.statusCode : 'transport_error'),
        )
        errRec.set('tentativa', 1)
        errRec.set('estado', 'pendente')
        errRec.set('dono', 'Henrique Tavano')
        errRec.set(
          'proxima_acao',
          'verificar dominio/chave/indisponibilidade Resend e reenviar manualmente',
        )
        errRec.set(
          'historico',
          JSON.stringify([
            {
              acao: 'criacao',
              ator: 'followup_lead',
              data: new Date().toISOString(),
              detalhes: resposta ? 'HTTP ' + resposta.statusCode : 'erro de transporte',
            },
          ]),
        )
        $app.save(errRec)
      } catch (_) {}
      lead.set('followup_estado', 'falha')
      lead.set('followup_proxima_acao', 'verificar_resend_e_reenviar')
      $app.save(lead)
      return e.json(502, {
        status: 'falha',
        motivo: resposta ? 'resend_indisponivel_ou_invalido' : 'resend_erro_de_transporte',
        chamada_resend: true,
      })
    }

    // --- Sucesso: grava referência + versão + histórico append-only ---
    let hist = []
    const histBruto = lead.get('followup_historico')
    let rawHist = null
    if (histBruto === null || histBruto === undefined) {
      rawHist = ''
    } else if (typeof histBruto === 'string') {
      rawHist = histBruto
    } else if (typeof histBruto === 'object' && typeof histBruto.length === 'number') {
      let s = ''
      let ok = true
      for (let i = 0; i < histBruto.length; i++) {
        const c = histBruto[i]
        if (typeof c === 'number') {
          s += String.fromCharCode(c)
        } else {
          ok = false
          break
        }
      }
      rawHist = ok ? s : ''
    } else {
      rawHist = ''
    }
    if (typeof rawHist === 'string' && rawHist.length > 0) {
      try {
        const parsed = JSON.parse(rawHist)
        if (Array.isArray(parsed)) hist = parsed
      } catch (_) {
        hist = []
      }
    }
    if (!Array.isArray(hist)) hist = []

    hist.push({
      acao: 'followup_enviado',
      tentativa: tentativa,
      modelo_versao: MODELOS_VERSAO,
      cadencia_versao: CADENCIA_VERSAO,
      resend_email_id: resposta.json.id,
      destinatario_mascarado: email.replace(/^(.).*(@.*)$/, '$1***$2'),
      data: new Date().toISOString(),
    })

    lead.set('followup_estado', 'enviado')
    lead.set('followup_ultimo_envio_id', resposta.json.id)
    lead.set('followup_tentativa', tentativa)
    lead.set('followup_idempotency_key', chave)
    lead.set(
      'followup_proxima_acao',
      tentativa < 3 ? 'aguardar_intervalo_proxima_tentativa' : 'cadencia_concluida',
    )
    lead.set('followup_historico', JSON.stringify(hist))
    $app.save(lead)

    return e.json(201, {
      status: 'sent',
      lead_id: lead.get('lead_id'),
      tentativa: tentativa,
      resend_email_id: resposta.json.id,
      cadencia_versao: CADENCIA_VERSAO,
      modelo_versao: MODELOS_VERSAO,
    })
  },
  $apis.requireAuth(),
)
