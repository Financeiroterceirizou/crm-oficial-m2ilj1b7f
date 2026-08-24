// pocketbase/hooks/replay_lead.js
// F1-T09: Endpoint de replay manual de leads
// POST /backend/v1/replay/lead

routerAdd('POST', '/backend/v1/replay/lead', (e) => {
  const body = e.requestInfo().body

  // Validar campos obrigatórios
  if (!body || !body.dedup_key || !body.motivo || !body.operador) {
    return e.json(400, { error: 'Campos obrigatórios: dedup_key, motivo, operador' })
  }

  const dedupKey = body.dedup_key
  const motivo = body.motivo
  const operador = body.operador

  // Buscar lead existente pela dedup_key
  const leads = $app.findRecordsByFilter('leads', 'dedup_key = {:dk}', '-created', 1, 0, {
    dk: dedupKey,
  })

  if (!leads || leads.length === 0) {
    return e.json(404, { error: 'Lead não encontrado para dedup_key: ' + dedupKey })
  }

  const record = leads[0]
  const leadId = record.get('lead_id')

  // Atualizar histórico com entrada de replay
  var hist = []
  var raw = record.get('historico')
  if (raw) {
    if (typeof raw === 'string') {
      try {
        hist = JSON.parse(raw)
      } catch (_) {}
    } else if (Array.isArray(raw)) {
      hist = raw
    }
  }
  hist.push({
    acao: 'replay_manual',
    ator: operador,
    data: new Date().toISOString(),
    detalhes: 'Replay manual executado. Motivo: ' + motivo,
  })
  record.set('historico', JSON.stringify(hist))

  $app.save(record)

  // Tentar registrar no error_log se houver erro_id
  if (body.error_id) {
    try {
      var errLogs = $app.findRecordsByFilter('error_log', 'error_id = {:eid}', '-created', 1, 0, {
        eid: body.error_id,
      })
      if (errLogs && errLogs.length > 0) {
        var errRec = errLogs[0]
        errRec.set('estado', 'resolvido')
        errRec.set('resolvido_em', new Date().toISOString())
        errRec.set('resolvido_por', operador)
        errRec.set('resultado', 'Replay manual executado com sucesso')
        $app.save(errRec)
      }
    } catch (_) {}
  }

  console.log('Replay manual executado: lead ' + leadId + ' por ' + operador)
  return e.json(200, {
    status: 'replayed',
    lead_id: leadId,
    dedup_key: dedupKey,
    operador: operador,
    motivo: motivo,
  })
})
