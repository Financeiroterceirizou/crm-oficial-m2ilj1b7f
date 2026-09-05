// F3-T02 - Autoagendamento idempotente para lead qualificado.
// POST /backend/v1/agendar-lead
// Não cria falso sucesso: sem token Google em cofre retorna 503 e mantém atendimento humano.

routerAdd(
  'POST',
  '/backend/v1/agendar-lead',
  (e) => {
    const body = e.requestInfo().body || {}
    const leadId = String(body.lead_id || '').trim()
    const inicio = String(body.inicio || '').trim()
    const fim = String(body.fim || '').trim()
    const email = String(body.email || '').trim()
    if (!leadId || !inicio || !fim)
      return e.json(400, { error: 'lead_id, inicio e fim obrigatorios' })

    let lead = null
    try {
      lead = $app.findRecordById('leads', leadId)
    } catch (_) {
      lead = null
    }
    if (!lead) return e.json(404, { error: 'lead nao encontrado' })

    if (lead.get('estado_qualificacao') !== 'qualificado') {
      return e.json(409, {
        status: 'bloqueado',
        motivo: 'lead nao qualificado',
        chamada_calendar: false,
      })
    }

    const inicioMs = Date.parse(inicio)
    const fimMs = Date.parse(fim)
    if (
      !Number.isFinite(inicioMs) ||
      !Number.isFinite(fimMs) ||
      fimMs - inicioMs !== 30 * 60 * 1000
    ) {
      return e.json(400, { error: 'janela deve ter exatamente 30 minutos' })
    }
    const partes = inicio.match(/^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})/)
    if (!partes || !inicio.match(/-03:00$|-02:00$/)) {
      return e.json(400, { error: 'inicio deve usar o fuso America/Sao_Paulo' })
    }
    const ano = Number(partes[1])
    const mes = Number(partes[2])
    const diaMes = Number(partes[3])
    const hora = Number(partes[4])
    const minuto = Number(partes[5])
    const dia = new Date(Date.UTC(ano, mes - 1, diaMes)).getUTCDay()
    const manha = hora >= 9 && (hora < 12 || (hora === 11 && minuto <= 30))
    const tarde = hora >= 14 && (hora < 18 || (hora === 17 && minuto <= 30))
    if (dia === 0 || dia === 6 || minuto % 30 !== 0 || !(manha || tarde)) {
      return e.json(409, {
        status: 'bloqueado',
        motivo: 'fora_da_janela_aprovada',
        chamada_calendar: false,
      })
    }

    const chave = leadId + ':reuniao:' + inicio
    if (lead.get('agendamento_idempotency_key') === chave && lead.get('calendar_event_id')) {
      return e.json(200, {
        status: 'already_scheduled',
        lead_id: lead.get('lead_id'),
        calendar_event_id: lead.get('calendar_event_id'),
      })
    }

    const accessToken = $secrets.get('GOOGLE_CALENDAR_ACCESS_TOKEN')
    if (!accessToken) {
      lead.set('estado_agendamento', 'pendente_configuracao')
      lead.set('agendamento_owner', 'Henrique Tavano')
      lead.set('agendamento_proxima_acao', 'configurar_token_google_calendar_e_tentar_novamente')
      lead.set('agendamento_idempotency_key', chave)
      $app.save(lead)
      return e.json(503, {
        status: 'pendente_configuracao',
        motivo: 'token_google_calendar_ausente',
        chamada_calendar: false,
      })
    }

    const resposta = $http.send({
      url: 'https://www.googleapis.com/calendar/v3/calendars/financeiro%40terceirizou.com.br/events',
      method: 'POST',
      headers: { Authorization: 'Bearer ' + accessToken, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        summary: 'Reunião Terceirizou — ' + lead.get('nome'),
        description: 'lead_id: ' + lead.get('lead_id'),
        start: { dateTime: inicio, timeZone: 'America/Sao_Paulo' },
        end: { dateTime: fim, timeZone: 'America/Sao_Paulo' },
        attendees: email ? [{ email }] : [],
      }),
      timeout: 15,
    })
    if (
      resposta.statusCode < 200 ||
      resposta.statusCode >= 300 ||
      !resposta.json ||
      !resposta.json.id
    ) {
      lead.set('estado_agendamento', 'falha')
      lead.set('agendamento_owner', 'Henrique Tavano')
      lead.set('agendamento_proxima_acao', 'agendamento_humano')
      $app.save(lead)
      return e.json(502, {
        status: 'falha',
        motivo: 'google_calendar_indisponivel_ou_invalido',
        chamada_calendar: true,
      })
    }

    lead.set('estado_agendamento', 'agendado')
    lead.set('calendar_event_id', resposta.json.id)
    lead.set('agendamento_inicio', inicio)
    lead.set('agendamento_fim', fim)
    lead.set('agendamento_owner', 'Henrique Tavano')
    lead.set('agendamento_proxima_acao', 'aguardar_reuniao')
    lead.set('agendamento_idempotency_key', chave)
    $app.save(lead)
    return e.json(201, {
      status: 'scheduled',
      lead_id: lead.get('lead_id'),
      calendar_event_id: resposta.json.id,
    })
  },
  $apis.requireAuth(),
)
