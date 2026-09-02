// pocketbase/hooks/revisar_lead.js
// F2-T04 - Correcao humana auditavel (SPEC-2-001, CA-2-004).
// POST /backend/v1/revisar-lead
// Body: { lead_id (id do registro) ou dedup_key, decisao, motivo, operador }
//   decisao: 'qualificado' | 'nao_qualificado' | 'excecao' | 'pendente_revisao'
// Aplica a correcao e anexa ao historico: { acao:'revisao_humana', ator, data, decisao,
//   anterior, motivo, regra_versao }. Nunca apaga dados.
// Requer autenticacao (CA-2-005).

routerAdd(
  'POST',
  '/backend/v1/revisar-lead',
  (e) => {
    const body = e.requestInfo().body || {}

    // --- validacao de entrada ---
    const operador = String(body.operador || '').trim()
    if (!operador) {
      return e.json(400, { error: 'operador obrigatorio' })
    }
    const decisao = String(body.decisao || '').trim()
    const validas = ['qualificado', 'nao_qualificado', 'excecao', 'pendente_revisao']
    if (validas.indexOf(decisao) === -1) {
      return e.json(400, { error: 'decisao invalida. Valores: ' + validas.join(', ') })
    }
    const motivoRev = String(body.motivo || '').trim() || 'revisao humana'
    const leadId = String(body.lead_id || '').trim()
    const dedupKey = String(body.dedup_key || '').trim()
    if (!leadId && !dedupKey) {
      return e.json(400, { error: 'lead_id ou dedup_key obrigatorio' })
    }

    // --- localizar o lead ---
    let record = null
    if (leadId) {
      try {
        record = $app.findRecordById('leads', leadId)
      } catch (_) {
        record = null
      }
    }
    if (!record && dedupKey) {
      const achados = $app.findRecordsByFilter('leads', 'dedup_key = {:dk}', '-created', 1, 0, {
        dk: dedupKey,
      })
      if (achados && achados.length > 0) {
        record = achados[0]
      }
    }
    if (!record) {
      return e.json(404, { error: 'lead nao encontrado' })
    }

    // --- estado anterior (para auditoria) ---
    const anterior = record.get('estado_qualificacao') || ''

    // --- historico: append (nunca apaga) ---
    // O campo json pode chegar como Uint8Array/bytes no runtime goja — converter antes.
    let hist = []
    let rawHist = record.get('historico')
    if (
      rawHist !== null &&
      rawHist !== undefined &&
      typeof rawHist === 'object' &&
      typeof rawHist.length === 'number' &&
      typeof rawHist[0] === 'number'
    ) {
      let s = ''
      for (let i = 0; i < rawHist.length; i++) {
        s += String.fromCharCode(rawHist[i])
      }
      rawHist = s
    }
    if (typeof rawHist === 'string') {
      try {
        hist = JSON.parse(rawHist)
      } catch (_) {
        hist = []
      }
    } else if (rawHist && Array.isArray(rawHist)) {
      hist = rawHist
    }
    console.log(
      'F2T04-revisar: rawHist tipo=',
      typeof rawHist,
      'len=',
      rawHist && rawHist.length,
      'hist antes=',
      JSON.stringify(hist).length,
    )
    hist.push({
      acao: 'revisao_humana',
      ator: operador,
      data: new Date().toISOString(),
      decisao: decisao,
      anterior: anterior,
      motivo: motivoRev,
      regra_versao: record.get('regra_versao') || '',
    })
    console.log(
      'F2T04-revisar: hist depois len=',
      hist.length,
      '| ultimo=',
      JSON.stringify(hist[hist.length - 1]),
    )

    // --- aplicar correcao humana (explicita, registrada) ---
    record.set('estado_qualificacao', decisao)
    record.set('motivo_decisao', 'revisao humana: ' + motivoRev)
    if (decisao === 'nao_qualificado') {
      record.set('proxima_acao', 'sem_roteamento')
      record.set('score', null)
    } else if (decisao === 'qualificado') {
      record.set('proxima_acao', 'agendar_reuniao_fechamento')
    } else if (decisao === 'excecao') {
      record.set('proxima_acao', 'revisar_excecao')
    } else {
      record.set('proxima_acao', 'aguardar_revisao_humana')
    }
    record.set('historico', JSON.stringify(hist))
    $app.save(record)

    return e.json(200, {
      status: 'revisado',
      lead_id: record.get('lead_id'),
      id: record.get('id'),
      estado: record.get('estado_qualificacao'),
      score: record.get('score'),
      motivo: record.get('motivo_decisao'),
      regra_versao: record.get('regra_versao'),
    })
  },
  $apis.requireAuth(),
)
