// F3-T03 - Borda de agenda: cancelamento, no-show e falha segura (SPEC-3-001 CA-3-003/004).
// POST /backend/v1/agendar-borda
// Body: { lead_id, acao: 'cancelar'|'no_show', operador, motivo }
// - cancelar: chama DELETE no Google Calendar (evento real), marca situacao=cancelado,
//   proxima_acao=reagendar e anexa ao historico (append, nunca apaga).
// - no_show: NAO apaga evento; marca situacao=no_show, proxima_acao=contato_humano e anexa.
// - Falha OAuth/API/slot: 502 sem falso sucesso, registra error_log (fila humana), sem token exposto.
// Requer autenticacao.

routerAdd(
  'POST',
  '/backend/v1/agendar-borda',
  (e) => {
    const body = e.requestInfo().body || {}
    const leadId = String(body.lead_id || '').trim()
    const acao = String(body.acao || '').trim()
    const operador = String(body.operador || '').trim()
    const motivo = String(body.motivo || '').trim() || 'sem motivo informado'

    if (!leadId || !operador) {
      return e.json(400, { error: 'lead_id e operador obrigatorios' })
    }
    if (acao !== 'cancelar' && acao !== 'no_show') {
      return e.json(400, { error: 'acao invalida. Valores: cancelar, no_show' })
    }

    let lead = null
    try {
      lead = $app.findRecordById('leads', leadId)
    } catch (_) {
      lead = null
    }
    if (!lead) return e.json(404, { error: 'lead nao encontrado' })

    const eventId = String(lead.get('calendar_event_id') || '').trim()
    if (!eventId) {
      return e.json(409, {
        status: 'sem_evento',
        motivo: 'lead sem evento de agenda registrado',
        chamada_calendar: false,
      })
    }
    if (lead.get('agendamento_situacao') === acao) {
      // Idempotencia: repetir a mesma borda nao duplica efeito nem historico
      return e.json(200, {
        status: 'already_' + acao,
        lead_id: lead.get('lead_id'),
        situacao: lead.get('agendamento_situacao'),
      })
    }

    // --- historico: append sempre, igual revisar_lead/replay_lead ---
    let hist = []
    const histBruto = lead.get('historico')
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

    const registro = {
      acao: 'agendamento_' + acao,
      ator: operador,
      data: new Date().toISOString(),
      evento: eventId,
      detalhes: motivo,
    }

    if (acao === 'cancelar') {
      // Falha de agenda (OAuth/API/slot) -> sem falso sucesso, fila humana
      const accessToken = $secrets.get('GOOGLE_CALENDAR_ACCESS_TOKEN')
      if (!accessToken) {
        try {
          const errCol = $app.findCollectionByNameOrId('error_log')
          const errRec = new Record(errCol)
          errRec.set('error_id', $security.randomString(12))
          errRec.set('source_event_id', eventId)
          errRec.set('categoria', 'timeout')
          errRec.set('resumo', 'cancelamento sem token Google Calendar: ' + lead.get('lead_id'))
          errRec.set('payload_resumido', 'lead_id=' + lead.get('lead_id') + ';evento=' + eventId)
          errRec.set('tentativa', 1)
          errRec.set('estado', 'pendente')
          errRec.set('dono', 'Henrique Tavano')
          errRec.set('proxima_acao', 'configurar token e cancelar manualmente')
          errRec.set(
            'historico',
            JSON.stringify([
              {
                acao: 'criacao',
                ator: 'agendar_borda',
                data: new Date().toISOString(),
                detalhes: 'cancelamento sem token',
              },
            ]),
          )
          $app.save(errRec)
          console.log('F3T03: cancelamento sem token registrado em error_log')
        } catch (_) {}
        return e.json(502, {
          status: 'falha',
          motivo: 'token_google_calendar_ausente',
          chamada_calendar: true,
        })
      }

      const resposta = $http.send({
        url:
          'https://www.googleapis.com/calendar/v3/calendars/financeiro%40terceirizou.com.br/events/' +
          encodeURIComponent(eventId),
        method: 'DELETE',
        headers: { Authorization: 'Bearer ' + accessToken },
        timeout: 15,
      })
      if (resposta.statusCode < 200 || resposta.statusCode >= 300) {
        try {
          const errCol = $app.findCollectionByNameOrId('error_log')
          const errRec = new Record(errCol)
          errRec.set('error_id', $security.randomString(12))
          errRec.set('source_event_id', eventId)
          errRec.set('categoria', 'timeout')
          errRec.set(
            'resumo',
            'falha ao cancelar evento Google Calendar (HTTP ' +
              resposta.statusCode +
              '): ' +
              lead.get('lead_id'),
          )
          errRec.set('payload_resumido', 'lead_id=' + lead.get('lead_id') + ';evento=' + eventId)
          errRec.set('tentativa', 1)
          errRec.set('estado', 'pendente')
          errRec.set('dono', 'Henrique Tavano')
          errRec.set('proxima_acao', 'cancelar manualmente no calendario')
          errRec.set(
            'historico',
            JSON.stringify([
              {
                acao: 'criacao',
                ator: 'agendar_borda',
                data: new Date().toISOString(),
                detalhes: 'HTTP ' + resposta.statusCode,
              },
            ]),
          )
          $app.save(errRec)
          console.log('F3T03: falha DELETE calendario registrada em error_log')
        } catch (_) {}
        return e.json(502, {
          status: 'falha',
          motivo: 'google_calendar_indisponivel_ou_invalido',
          chamada_calendar: true,
        })
      }
    }

    hist.push(registro)
    lead.set('historico', JSON.stringify(hist))
    lead.set('agendamento_situacao', acao)
    if (acao === 'cancelar') {
      lead.set('agendamento_proxima_acao', 'reagendar')
    } else {
      lead.set('agendamento_proxima_acao', 'contato_humano')
    }
    $app.save(lead)

    return e.json(200, {
      status: acao === 'cancelar' ? 'cancelado' : 'no_show',
      lead_id: lead.get('lead_id'),
      situacao: acao,
      calendario: acao === 'no_show' ? 'evento_mantido' : 'evento_removido',
    })
  },
  $apis.requireAuth(),
)
