// pocketbase/hooks/webhook_lead.js
// F1-T05+F1-T08: Webhook com logging de erros
// POST /backend/v1/webhook/lead

routerAdd('POST', '/backend/v1/webhook/lead', (e) => {
  const body = e.requestInfo().body

  // Função auxiliar para registrar erro
  function logError(categoria, resumo, payloadResumido, sourceEventId) {
    try {
      const errCol = $app.findCollectionByNameOrId('error_log')
      const errRec = new Record(errCol)
      errRec.set('error_id', $security.randomString(12))
      errRec.set('source_event_id', sourceEventId || '')
      errRec.set('categoria', categoria)
      errRec.set('resumo', resumo)
      errRec.set('payload_resumido', payloadResumido || '')
      errRec.set('tentativa', 1)
      errRec.set('estado', 'pendente')
      errRec.set('dono', 'Henrique Tavano')
      errRec.set('proxima_acao', 'Verificar origem do erro e corrigir')
      errRec.set(
        'historico',
        JSON.stringify([
          {
            acao: 'criacao',
            ator: 'webhook',
            data: new Date().toISOString(),
            detalhes: resumo,
          },
        ]),
      )
      $app.save(errRec)
      console.log('Erro registrado: ' + categoria + ' - ' + resumo)
    } catch (err) {
      console.log('Falha ao registrar erro: ' + err.message)
    }
  }

  // Validar body
  if (!body || typeof body !== 'object') {
    logError('schema_invalido', 'Body não é JSON válido', '', '')
    return e.json(400, { error: 'Body inválido' })
  }

  // Validar campos obrigatórios
  if (!body.nome) {
    logError(
      'validacao',
      'Campo obrigatório ausente: nome',
      body.email || '',
      body.source_event_id || '',
    )
    return e.json(400, { error: 'Campo obrigatório ausente: nome' })
  }

  // Validar origem
  const origem = body.origem || 'manual'
  const origensValidas = ['meta_ads', 'cora', 'indicacao', 'manual']
  if (!origensValidas.includes(origem)) {
    logError(
      'validacao',
      'Origem inválida: ' + origem,
      body.email || '',
      body.source_event_id || '',
    )
    return e.json(400, { error: 'Origem inválida: ' + origem })
  }

  // Gerar dedup_key
  const email = body.email || ''
  const dataRef = body.data_envio || body.data_hora || new Date().toISOString()
  const dedupKey = $security.sha256(email + dataRef)

  // Verificar idempotência
  const existing = $app.findRecordsByFilter('leads', 'dedup_key = {:dk}', '-created', 1, 0, {
    dk: dedupKey,
  })

  if (existing && existing.length > 0) {
    const record = existing[0]
    record.set('nome', body.nome)
    record.set('email', email)
    record.set('telefone', body.telefone || '')
    record.set('campanha', body.campanha || body.conjunto_anuncio || '')
    record.set('anuncio_criativo', body.anuncio_criativo || body.nome_anuncio || '')

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
      acao: 'atualizacao',
      ator: 'webhook',
      data: new Date().toISOString(),
      detalhes: 'Lead atualizado via replay idempotente',
    })
    record.set('historico', JSON.stringify(hist))

    $app.save(record)
    console.log('Lead atualizado (idempotente): ' + dedupKey)
    return e.json(200, {
      status: 'updated',
      lead_id: record.get('lead_id'),
      dedup_key: dedupKey,
    })
  }

  // Criar novo lead
  const col = $app.findCollectionByNameOrId('leads')
  const record = new Record(col)
  record.set('lead_id', $security.randomString(12))
  record.set('opportunity_id', $security.randomString(12))
  record.set('nome', body.nome)
  record.set('email', email)
  record.set('telefone', body.telefone || '')
  record.set('origem', origem)
  record.set('campanha', body.campanha || body.conjunto_anuncio || '')
  record.set('anuncio_criativo', body.anuncio_criativo || body.nome_anuncio || '')
  record.set(
    'respostas',
    JSON.stringify({
      prestador: body.prestador || '',
      segmento: body.segmento || '',
      cargo: body.cargo || '',
      gestao_financeira: body.gestao_financeira || '',
      maior_problema: body.maior_problema || '',
      motivacao: body.motivacao || '',
      cnpj_cpf: body.cnpj_cpf || '',
      tipo_empresa: body.tipo_empresa || '',
      servico_desejado: body.servico_desejado || '',
      ramo_atividade: body.ramo_atividade || '',
      estado: body.estado || '',
      cidade: body.cidade || '',
      preferencia: body.preferencia_atendimento || '',
    }),
  )
  record.set('estagio', 'capturado')
  record.set('responsavel', body.responsavel || 'Henrique Tavano')
  record.set('dedup_key', dedupKey)
  record.set('source_event_id', body.source_event_id || $security.randomString(16))
  record.set(
    'historico',
    JSON.stringify([
      {
        acao: 'criacao',
        ator: 'webhook',
        data: new Date().toISOString(),
        detalhes: 'Lead recebido via webhook de ' + origem,
      },
    ]),
  )

  $app.save(record)
  console.log('Lead criado via webhook: ' + body.nome + ' (' + dedupKey + ')')

  return e.json(201, {
    status: 'created',
    lead_id: record.get('lead_id'),
    opportunity_id: record.get('opportunity_id'),
    dedup_key: dedupKey,
  })
})
