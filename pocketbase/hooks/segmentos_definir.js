// pocketbase/hooks/segmentos_definir.js
// Aprovação de segmento (regra v1.2) — decisão do champion em 28/10/2026.
// POST /backend/v1/segmentos/definir
// Body: { lead_id, acao, segmento?, operador, observacao? }
//   acao = 'definir_segmento' -> grava o segmento oficial em respostas e deixa a regra reclassificar
//          'aprovar'          -> aprova o lead como válido mesmo fora da carteira (aval humano)
//          'nao_qualificar'   -> encerra o lead fora do perfil
// Toda decisão fica no histórico (append, nunca apaga). Rota pública: o app
// inteiro funciona sem login (mesmo padrão de pipeline/vendas), a validação
// (ação, segmento oficial, lead existente) acontece aqui no servidor.
//
// ATENÇÃO runtime goja: toda a lógica inline no callback; JSON pode vir como
// Uint8Array e precisa de decodificação UTF-8 byte a byte (String.fromCharCode
// direto decodifica Latin-1 e corrompe acento).

routerAdd('POST', '/backend/v1/segmentos/definir', (e) => {
  const body = e.requestInfo().body || {}

  const operador = String(body.operador || '').trim()
  if (!operador) return e.json(400, { error: 'operador obrigatorio' })

  const acao = String(body.acao || '').trim()
  const acoes = ['definir_segmento', 'aprovar', 'nao_qualificar']
  if (acoes.indexOf(acao) === -1) {
    return e.json(400, { error: 'acao invalida. Valores: ' + acoes.join(', ') })
  }

  const leadId = String(body.lead_id || '').trim()
  if (!leadId) return e.json(400, { error: 'lead_id obrigatorio' })

  const oficial = [
    'Escritório de Arquitetura',
    'Escritório de Advocacia',
    'Clínica de Saúde e Estética',
    'Agência de Marketing',
    'Casa de Repouso (ILPI)',
    'Associação de Proteção Veicular',
    'Vistoria Veicular',
    'Consultoria em Geral',
    'Outro Segmento de Prestação de Serviço',
    'Segmento que não atendemos',
  ]
  const segmento = String(body.segmento || '').trim()
  if (acao === 'definir_segmento' && oficial.indexOf(segmento) === -1) {
    return e.json(400, { error: 'segmento invalido: ' + segmento })
  }

  let record = null
  try {
    record = $app.findRecordById('leads', leadId)
  } catch (_) {
    return e.json(404, { error: 'lead nao encontrado' })
  }

  // ---------- decodificação UTF-8 de bytes ----------
  const decodificar = (raw) => {
    const bytes = []
    for (let i = 0; i < raw.length; i++) bytes.push(raw[i] & 0xff)
    let s = ''
    let bi = 0
    while (bi < bytes.length) {
      const b0 = bytes[bi]
      if (b0 < 0x80) {
        s += String.fromCharCode(b0)
        bi += 1
      } else if (b0 >= 0xc0 && b0 < 0xe0 && bi + 1 < bytes.length) {
        s += String.fromCharCode(((b0 & 0x1f) << 6) | (bytes[bi + 1] & 0x3f))
        bi += 2
      } else if (b0 >= 0xe0 && b0 < 0xf0 && bi + 2 < bytes.length) {
        s += String.fromCharCode(
          ((b0 & 0x0f) << 12) | ((bytes[bi + 1] & 0x3f) << 6) | (bytes[bi + 2] & 0x3f),
        )
        bi += 3
      } else if (b0 >= 0xf0 && bi + 3 < bytes.length) {
        const cp =
          ((b0 & 0x07) << 18) |
          ((bytes[bi + 1] & 0x3f) << 12) |
          ((bytes[bi + 2] & 0x3f) << 6) |
          (bytes[bi + 3] & 0x3f)
        const par = cp - 0x10000
        s += String.fromCharCode(0xd800 + (par >> 10), 0xdc00 + (par & 0x3ff))
        bi += 4
      } else {
        bi += 1
      }
    }
    return s
  }

  const lerJson = (valor) => {
    let raw = valor
    if (
      raw !== null &&
      raw !== undefined &&
      typeof raw === 'object' &&
      typeof raw.length === 'number' &&
      typeof raw[0] === 'number'
    ) {
      raw = decodificar(raw)
    }
    if (typeof raw === 'string') {
      try {
        return JSON.parse(raw)
      } catch (_) {
        return {}
      }
    }
    return raw && typeof raw === 'object' ? raw : {}
  }

  const estadoAnterior = record.get('estado_qualificacao') || ''
  const historico = lerJson(record.get('historico'))
  const hist = Array.isArray(historico) ? historico : []
  const observacao = String(body.observacao || '').trim()
  const agora = new Date().toISOString()

  if (acao === 'definir_segmento') {
    // 1. grava o segmento oficial nas respostas — o hook de update reclassifica
    const respostas = lerJson(record.get('respostas'))
    respostas['segmento'] = segmento
    record.set('respostas', JSON.stringify(respostas))
    hist.push({
      acao: 'segmento_definido',
      ator: operador,
      data: agora,
      segmento: segmento,
      observacao: observacao,
      regra_versao: '1.3',
    })
    record.set('historico', JSON.stringify(hist))
    $app.save(record)

    // 2. devolve o resultado já reclassificado pelo hook
    const atual = $app.findRecordById('leads', leadId)
    return e.json(200, {
      status: 'segmento_definido',
      lead_id: atual.get('lead_id'),
      id: atual.get('id'),
      segmento: segmento,
      estado: atual.get('estado_qualificacao'),
      motivo: atual.get('motivo_decisao'),
      proxima_acao: atual.get('proxima_acao'),
      score: atual.get('score'),
      anterior: estadoAnterior,
    })
  }

  // ---------- decisão humana explícita (aprovar / não qualificar) ----------
  const decisao = acao === 'aprovar' ? 'qualificado' : 'nao_qualificado'
  const motivo =
    acao === 'aprovar'
      ? 'revisao humana: segmento aprovado' + (segmento ? ' (' + segmento + ')' : '')
      : 'revisao humana: nao qualificado' + (observacao ? ' (' + observacao + ')' : '')

  if (acao === 'aprovar' && segmento) {
    // registra também o segmento aprovado para o relatório ficar coerente
    const respostas = lerJson(record.get('respostas'))
    respostas['segmento'] = segmento
    record.set('respostas', JSON.stringify(respostas))
  }

  record.set('estado_qualificacao', decisao)
  record.set('motivo_decisao', motivo)
  if (decisao === 'nao_qualificado') {
    record.set('proxima_acao', 'sem_roteamento')
    record.set('score', null)
  } else {
    record.set('proxima_acao', 'agendar_reuniao_fechamento')
  }
  hist.push({
    acao: 'aprovacao_segmento',
    ator: operador,
    data: agora,
    decisao: decisao,
    anterior: estadoAnterior,
    segmento: segmento || '',
    observacao: observacao,
    motivo: motivo,
    regra_versao: '1.3',
  })
  record.set('historico', JSON.stringify(hist))
  $app.save(record)

  return e.json(200, {
    status: 'decidido',
    lead_id: record.get('lead_id'),
    id: record.get('id'),
    estado: record.get('estado_qualificacao'),
    motivo: record.get('motivo_decisao'),
    proxima_acao: record.get('proxima_acao'),
    score: record.get('score'),
    anterior: estadoAnterior,
  })
})
