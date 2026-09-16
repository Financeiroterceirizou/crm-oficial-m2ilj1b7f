// F3-T06 - Parada do follow-up (SPEC-3-002 CA-3-103/104).
// POST /backend/v1/followup-parada
// Body: { lead_id, parada, operador, motivo }
//   parada: resposta|agendamento|cancelamento|no_show|descadastro|bounce_permanente
// - Registra a parada: followup_estado=parado, followup_parada=<motivo>, historico append-only.
// - Idempotente: repetir a MESMA parada nao duplica historico (200 already_stopped).
// - bounce_permanente: cria registro em error_log (fila humana, dono Henrique Tavano).
// - limpar=true remove a parada (rollback operacional, com registro no historico).
// Requer autenticacao.
// NOTA runtime Skip: tudo declarado DENTRO do callback (escopo de modulo nao visivel ao handler).

routerAdd(
  'POST',
  '/backend/v1/followup-parada',
  (e) => {
    const PARADAS = [
      'resposta',
      'agendamento',
      'cancelamento',
      'no_show',
      'descadastro',
      'bounce_permanente',
    ]

    const body = e.requestInfo().body || {}
    const leadId = String(body.lead_id || '').trim()
    const parada = String(body.parada || '').trim()
    const operador = String(body.operador || '').trim()
    const motivo = String(body.motivo || '').trim() || 'sem motivo informado'
    const limpar = body.limpar === true

    if (!leadId || !operador) {
      return e.json(400, { error: 'lead_id e operador obrigatorios' })
    }

    let lead = null
    try {
      lead = $app.findRecordById('leads', leadId)
    } catch (_) {
      lead = null
    }
    if (!lead) return e.json(404, { error: 'lead nao encontrado' })

    // --- historico append-only (mesma leitura defensiva de agendar_borda) ---
    function lerHist() {
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
      return hist
    }

    // --- limpar parada (rollback operacional) ---
    if (limpar) {
      if (!lead.get('followup_parada')) {
        return e.json(200, { status: 'sem_parada', lead_id: lead.get('lead_id') })
      }
      const hist = lerHist()
      hist.push({
        acao: 'followup_parada_limpa',
        parada_anterior: lead.get('followup_parada'),
        ator: operador,
        data: new Date().toISOString(),
        detalhes: motivo,
      })
      lead.set('followup_parada', '')
      lead.set('followup_estado', 'ativo')
      lead.set('followup_proxima_acao', 'retomar_cadencia')
      lead.set('followup_historico', JSON.stringify(hist))
      $app.save(lead)
      return e.json(200, {
        status: 'parada_limpa',
        lead_id: lead.get('lead_id'),
      })
    }

    if (PARADAS.indexOf(parada) === -1) {
      return e.json(400, { error: 'parada invalida. Valores: ' + PARADAS.join(', ') })
    }

    // --- Idempotencia: mesma parada nao duplica efeito nem historico ---
    if (lead.get('followup_estado') === 'parado' && lead.get('followup_parada') === parada) {
      return e.json(200, {
        status: 'already_stopped',
        lead_id: lead.get('lead_id'),
        parada: parada,
      })
    }

    const hist = lerHist()
    hist.push({
      acao: 'followup_parada',
      parada: parada,
      ator: operador,
      data: new Date().toISOString(),
      detalhes: motivo,
    })

    lead.set('followup_estado', 'parado')
    lead.set('followup_parada', parada)
    lead.set('followup_proxima_acao', parada === 'descadastro' ? 'nao_contatar' : 'contato_humano')
    lead.set('followup_historico', JSON.stringify(hist))
    $app.save(lead)

    // --- bounce_permanente: fila humana (CA-3-104) ---
    if (parada === 'bounce_permanente') {
      try {
        const errCol = $app.findCollectionByNameOrId('error_log')
        const errRec = new Record(errCol)
        errRec.set('error_id', $security.randomString(12))
        errRec.set('source_event_id', leadId)
        errRec.set('categoria', 'bounce')
        errRec.set('resumo', 'bounce permanente no follow-up: ' + lead.get('lead_id'))
        errRec.set('payload_resumido', 'lead_id=' + leadId + ';parada=bounce_permanente')
        errRec.set('tentativa', 1)
        errRec.set('estado', 'pendente')
        errRec.set('dono', 'Henrique Tavano')
        errRec.set('proxima_acao', 'validar e-mail do lead e corrigir cadastro')
        errRec.set(
          'historico',
          JSON.stringify([
            {
              acao: 'criacao',
              ator: 'followup_parada',
              data: new Date().toISOString(),
              detalhes: motivo,
            },
          ]),
        )
        $app.save(errRec)
      } catch (_) {}
    }

    return e.json(200, {
      status: 'parado',
      lead_id: lead.get('lead_id'),
      parada: parada,
      proxima_acao: lead.get('followup_proxima_acao'),
    })
  },
  $apis.requireAuth(),
)
