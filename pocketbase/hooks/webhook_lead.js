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

  // Mapear campos do formulário para o schema do leads
  const leadData = {
    lead_id: $security.randomString(12),
    opportunity_id: $security.randomString(12),
    nome: body.nome,
    email: email,
    telefone: body.telefone || '',
    origem: origem,
    campanha: body.campanha || body.conjunto_anuncio || '',
    anuncio_criativo: body.anuncio_criativo || body.nome_anuncio || '',
    respostas: {
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
    },
    estagio: 'capturado',
    responsavel: body.responsavel || 'Henrique Tavano',
    dedup_key: dedupKey,
    source_event_id: body.source_event_id || $security.randomString(16),
    historico: [
      {
        acao: 'criacao',
        ator: 'webhook',
        data: new Date().toISOString(),
        detalhes: 'Lead recebido via webhook de ' + origem,
      },
    ],
  }

  // Verificar se já existe lead com esta dedup_key (idempotência)
  try {
    const existing = $app.findFirstRecordByData('leads', 'dedup_key', dedupKey)
    // Lead já existe — atualizar campos permitidos
    existing.set('nome', leadData.nome)
    existing.set('email', leadData.email)
    existing.set('telefone', leadData.telefone)
    existing.set('campanha', leadData.campanha)
    existing.set('anuncio_criativo', leadData.anuncio_criativo)
    existing.set('respostas', leadData.respostas)
    existing.set('updated', new Date().toISOString())

    // Adicionar entrada no histórico
    const historico = existing.get('historico') || []
    historico.push({
      acao: 'atualizacao',
      ator: 'webhook',
      data: new Date().toISOString(),
      detalhes: 'Lead atualizado via replay idempotente',
    })
    existing.set('historico', historico)

    $app.save(existing)
    console.log('Lead atualizado (idempotente): ' + dedupKey)
    return e.json(200, {
      status: 'updated',
      lead_id: existing.get('lead_id'),
      dedup_key: dedupKey,
    })
  } catch (_) {
    // Lead não existe — criar novo
  }

  // Criar novo lead
  const col = $app.findCollectionByNameOrId('leads')
  const record = new (require('pbjs').Record)(col)
  record.set('lead_id', leadData.lead_id)
  record.set('opportunity_id', leadData.opportunity_id)
  record.set('nome', leadData.nome)
  record.set('email', leadData.email)
  record.set('telefone', leadData.telefone)
  record.set('origem', leadData.origem)
  record.set('campanha', leadData.campanha)
  record.set('anuncio_criativo', leadData.anuncio_criativo)
  record.set('respostas', leadData.respostas)
  record.set('estagio', leadData.estagio)
  record.set('responsavel', leadData.responsavel)
  record.set('dedup_key', leadData.dedup_key)
  record.set('source_event_id', leadData.source_event_id)
  record.set('historico', leadData.historico)

  $app.save(record)
  console.log('Lead criado via webhook: ' + leadData.nome + ' (' + dedupKey + ')')

  return e.json(201, {
    status: 'created',
    lead_id: leadData.lead_id,
    opportunity_id: leadData.opportunity_id,
    dedup_key: dedupKey,
  })
})
