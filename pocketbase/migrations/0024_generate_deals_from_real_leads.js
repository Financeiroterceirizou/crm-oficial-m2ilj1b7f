// pocketbase/migrations/0024_generate_deals_from_real_leads.js
// 1. Adicionar campo 'lead' (relação opcional com 'leads') e 'contato' na collection 'deals'
// 2. Remover os 12 negócios fictícios de exemplo restantes na collection 'deals'
// 3. Gerar 1 deal para cada um dos 66 leads reais da collection 'leads':
//    - nome: lead.nome (ou "Oportunidade - " + lead.nome)
//    - cliente: lead.nome
//    - valor: 0 (sem fabricar valores)
//    - etapa: 'Novos leads'
//    - canal: 'Meta Ads' (ou mapeado de lead.origem)
//    - probabilidade: 20 (baixa / padrão)
//    - responsavel: 'Nao atribuido'
//    - lead: lead.id
//    - tags: ['Lead Real', 'Meta Ads']
//    - data/hora: preserva created/updated a partir da data de criação do lead
// Idempotente: se já existir deal vinculado ao lead (por lead.id ou cliente/email), não duplica.

migrate(
  (app) => {
    const dealsCol = app.findCollectionByNameOrId('deals')
    const leadsCol = app.findCollectionByNameOrId('leads')

    // 1. Garantir campo 'lead' (relation) na collection deals
    if (!dealsCol.fields.getByName('lead')) {
      dealsCol.fields.add(
        new RelationField({
          name: 'lead',
          collectionId: leadsCol.id,
          maxSelect: 1,
          required: false,
        }),
      )
    }

    // Garantir campo 'contato' (text) na collection deals
    if (!dealsCol.fields.getByName('contato')) {
      dealsCol.fields.add(
        new TextField({
          name: 'contato',
          required: false,
        }),
      )
    }

    // Garantir índice em lead
    dealsCol.addIndex('idx_deals_lead', false, 'lead', '')

    app.save(dealsCol)

    // 2. Remover os 12 deals fictícios de exemplo (seed da migration 0017)
    // Os seed fictícios têm nomes específicos como 'Clínica Odonto Prime', 'Grupo Alpha Logística', etc.
    // e NÃO possuem campo 'lead' preenchido.
    const seedNomes = [
      'Clínica Odonto Prime',
      'Grupo Alpha Logística',
      'TechWave Soluções Digitais',
      'Restaurante Sabor & Arte',
      'Vanguard Engenharia Civil',
      'BioSaúde Distribuidora',
      'Escola Aquarela Kids',
      'Nexus Hub Coworking',
      'Nova Era Auto Peças',
      'Solaris Energia Renovável',
      'Rede Farma Popular (3 lojas)',
      'Studio Pilates Vida & Equilíbrio',
      'Atlas Transportes & Cargas',
      'Mundo Pet Veterinária 24h',
      'Inovare Arquitetura de Interiores',
    ]

    for (let i = 0; i < seedNomes.length; i++) {
      try {
        app
          .db()
          .newQuery('DELETE FROM deals WHERE nome = {:nome} AND (lead IS NULL OR lead = "")')
          .bind({ nome: seedNomes[i] })
          .execute()
      } catch (err) {
        console.log('[0024] Erro ao deletar seed deal:', seedNomes[i], err)
      }
    }

    // 3. Buscar todos os leads reais
    const allLeads = app.findRecordsByFilter('leads', "id != ''", 'created', 200, 0)
    console.log('[0024] Total de leads encontrados:', allLeads.length)

    let createdDealsCount = 0
    let skippedDealsCount = 0

    for (let i = 0; i < allLeads.length; i++) {
      const lead = allLeads[i]
      const leadId = lead.id
      const leadNome = lead.getString('nome') || 'Lead sem nome'
      const leadEmail = lead.getString('email') || ''
      const leadTelefone = lead.getString('telefone') || ''
      const leadOrigem = lead.getString('origem') || 'meta_ads'
      const leadCreated = lead.getString('created') || new Date().toISOString()

      // Canal formatado amigável
      let canalFormatado = 'Meta Ads'
      if (leadOrigem === 'cora') canalFormatado = 'Cora'
      else if (leadOrigem === 'indicacao') canalFormatado = 'Indicação'
      else if (leadOrigem === 'manual') canalFormatado = 'Manual'

      // Contato com telefone e/ou email
      let contatoStr = ''
      if (leadTelefone && leadEmail) {
        contatoStr = leadTelefone + ' • ' + leadEmail
      } else {
        contatoStr = leadTelefone || leadEmail || 'Contato via Meta'
      }

      // Tags amigáveis
      const tags = ['Novo Lead']
      if (leadOrigem === 'meta_ads') {
        tags.push('Meta Ads')
      }

      // Checagem de idempotência: verificar se já existe deal para este lead
      const existingDeals = app.findRecordsByFilter('deals', "lead = '" + leadId + "'", '', 1, 0)

      if (existingDeals && existingDeals.length > 0) {
        skippedDealsCount++
        continue
      }

      // Criar o deal real
      const dealRec = new Record(dealsCol)
      dealRec.set('nome', leadNome)
      dealRec.set('cliente', leadNome)
      dealRec.set('contato', contatoStr)
      dealRec.set('valor', 0)
      dealRec.set('etapa', 'Novos leads')
      dealRec.set('canal', canalFormatado)
      dealRec.set('probabilidade', 20)
      dealRec.set('responsavel', 'Nao atribuido')
      dealRec.set('lead', leadId)
      dealRec.set('tags', JSON.stringify(tags))

      app.save(dealRec)

      // Preservar created e updated com a data do lead
      if (leadCreated) {
        try {
          app
            .db()
            .newQuery(
              'UPDATE deals SET created = {:created}, updated = {:updated} WHERE id = {:id}',
            )
            .bind({
              created: leadCreated,
              updated: leadCreated,
              id: dealRec.id,
            })
            .execute()
        } catch (e) {
          console.log('[0024] Erro ao sincronizar datas do deal:', e)
        }
      }

      createdDealsCount++
    }

    console.log(
      '[0024] Concluído: ' +
        createdDealsCount +
        ' deals criados a partir dos leads reais, ' +
        skippedDealsCount +
        ' já existentes pulados.',
    )
  },
  (app) => {
    // Reverter: remover deals gerados dos leads
    try {
      app.db().newQuery('DELETE FROM deals WHERE lead IS NOT NULL AND lead != ""').execute()
    } catch (_) {}
  },
)
