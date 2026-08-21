// pocketbase/hooks/webhook_lead.js
// F1-T05: Webhook para receber leads do Google Apps Script
// POST /backend/v1/webhook/lead

routerAdd('POST', '/backend/v1/webhook/lead', (e) => {
  const body = e.requestInfo().body

  // Validar campos obrigatórios
  if (!body || !body.nome) {
    return e.json(400, { error: 'Campo obrigatório ausente: nome' })
  }

  // Determinar origem
  const origem = body.origem || 'manual'
  const origensValidas = ['meta_ads', 'cora', 'indicacao', 'manual']
  if (!origensValidas.includes(origem)) {
    return e.json(400, { error: 'Origem inválida: ' + origem })
  }

  // Gerar dedup_key: SHA-256(email + data_envio ou timestamp)
  const email = body.email || ''
  const dataRef = body.data_envio || body.data_hora || new Date().toISOString()
  const dedupKey = $security.sha256(email + dataRef)

  // Verificar idempotência via findRecordsByFilter
  const existing = $app.findRecordsByFilter('leads', 'dedup_key = {:dk}', '-created', 1, 0, {
    dk: dedupKey,
  })

  if (existing && existing.length > 0) {
    // Lead já existe — atualizar campos permitidos
    const record = existing[0]
    record.set('nome', body.nome)
    record.set('email', email)
    record.set('telefone', body.telefone || '')
    record.set('campanha', body.campanha || body.conjunto_anuncio || '')
    record.set('anuncio_criativo', body.anuncio_criativo || body.nome_anuncio || '')

    // Atualizar histórico
    var hist = []
    var histRaw = record.get('historico')
    if (histRaw) {
      if (Array.isArray(histRaw)) {
        hist = histRaw
      } else if (typeof histRaw === 'string') {
        try {
          hist = JSON.parse(histRaw)
        } catch (_) {
          hist = []
        }
      }
    }
    hist.push({
      acao: 'atualizacao',
      ator: 'webhook',
      data: new Date().toISOString(),
      detalhes: 'Lead atualizado via replay idempotente',
    })
    // PocketBase JSON fields aceitam objetos JS diretamente
    record.set('historico', hist)

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
  record.set('respostas', {
    prestador: body.prestador || body['e_prestador'] || '',
    segmento: body.segmento || body.segmento_atuacao || '',
    cargo: body.cargo || '',
    gestao_financeira: body.gestao_financeira || '',
    maior_problema: body.maior_problema || '',
    motivacao: body.motivacao || body.motivacao_busca || '',
    cnpj_cpf: body.cnpj_cpf || '',
    tipo_empresa: body.tipo_empresa || '',
    servico_desejado: body.servico_desejado || '',
    ramo_atividade: body.ramo_atividade || '',
    estado: body.estado || '',
    cidade: body.cidade || '',
    preferencia: body.preferencia_atendimento || '',
  })
  record.set('estagio', 'capturado')
  record.set('responsavel', body.responsavel || 'Henrique Tavano')
  record.set('dedup_key', dedupKey)
  record.set('source_event_id', body.source_event_id || $security.randomString(16))
  record.set('historico', [
    {
      acao: 'criacao',
      ator: 'webhook',
      data: new Date().toISOString(),
      detalhes: 'Lead recebido via webhook de ' + origem,
    },
  ])

  $app.save(record)
  console.log('Lead criado via webhook: ' + body.nome + ' (' + dedupKey + ')')

  return e.json(201, {
    status: 'created',
    lead_id: record.get('lead_id'),
    opportunity_id: record.get('opportunity_id'),
    dedup_key: dedupKey,
  })
})
