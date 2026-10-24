migrate(
  (app) => {
    // 1. Criar collection deals se não existir
    let dealsCol
    try {
      dealsCol = app.findCollectionByNameOrId('deals')
    } catch (_) {
      dealsCol = new Collection({
        name: 'deals',
        type: 'base',
        listRule: '',
        viewRule: '',
        createRule: '',
        updateRule: '',
        deleteRule: '',
        fields: [
          { name: 'nome', type: 'text', required: true },
          { name: 'cliente', type: 'text' },
          { name: 'valor', type: 'number', min: 0 },
          {
            name: 'etapa',
            type: 'select',
            required: true,
            values: [
              'Novos leads',
              'Contato feito',
              'Proposta enviada',
              'Negociação',
              'Fechado (ganho)',
            ],
            maxSelect: 1,
          },
          { name: 'canal', type: 'text' },
          { name: 'probabilidade', type: 'number', min: 0, max: 100 },
          { name: 'responsavel', type: 'text' },
          { name: 'tags', type: 'json' },
          { name: 'data_fechamento', type: 'date' },
          { name: 'created', type: 'autodate', onCreate: true, onUpdate: false },
          { name: 'updated', type: 'autodate', onCreate: true, onUpdate: true },
        ],
        indexes: [
          'CREATE INDEX idx_deals_etapa ON deals (etapa)',
          'CREATE INDEX idx_deals_canal ON deals (canal)',
          'CREATE INDEX idx_deals_responsavel ON deals (responsavel)',
          'CREATE INDEX idx_deals_created ON deals (created DESC)',
        ],
      })
      app.save(dealsCol)
    }

    // 2. Se a collection estiver vazia, popular com negócios iniciais
    const existingCount = app.countRecords('deals')
    if (existingCount === 0) {
      const seedDeals = [
        {
          nome: 'Clínica Odonto Prime',
          cliente: 'Dra. Camila Albuquerque',
          valor: 3800,
          etapa: 'Novos leads',
          canal: 'Meta Ads',
          probabilidade: 20,
          responsavel: 'Lucas Silveira',
          tags: ['BPO Completo', 'Urgente'],
        },
        {
          nome: 'Grupo Alpha Logística',
          cliente: 'Marcos Vinícius',
          valor: 7500,
          etapa: 'Novos leads',
          canal: 'Google Orgânico',
          probabilidade: 25,
          responsavel: 'Mariana Costa',
          tags: ['Conciliação', 'Grande Porte'],
        },
        {
          nome: 'TechWave Soluções Digitais',
          cliente: 'Fernanda Rocha',
          valor: 4900,
          etapa: 'Novos leads',
          canal: 'Indicação',
          probabilidade: 30,
          responsavel: 'Rafael Prado',
          tags: ['Consultoria'],
        },
        {
          nome: 'Restaurante Sabor & Arte',
          cliente: 'Antônio Ferreira',
          valor: 2600,
          etapa: 'Novos leads',
          canal: 'Meta Ads',
          probabilidade: 15,
          responsavel: 'Lucas Silveira',
          tags: ['Contas a Pagar'],
        },
        {
          nome: 'Vanguard Engenharia Civil',
          cliente: 'Eng. Roberto Dias',
          valor: 9200,
          etapa: 'Contato feito',
          canal: 'Google Ads',
          probabilidade: 40,
          responsavel: 'Mariana Costa',
          tags: ['BPO + Fiscal', 'Reunião Agendada'],
        },
        {
          nome: 'BioSaúde Distribuidora',
          cliente: 'Patrícia Nogueira',
          valor: 5800,
          etapa: 'Contato feito',
          canal: 'Meta Ads',
          probabilidade: 35,
          responsavel: 'Rafael Prado',
          tags: ['Diagnóstico'],
        },
        {
          nome: 'Escola Aquarela Kids',
          cliente: 'Beatriz Vasconcelos',
          valor: 3200,
          etapa: 'Contato feito',
          canal: 'Indicação',
          probabilidade: 45,
          responsavel: 'Lucas Silveira',
          tags: ['Mensalidade'],
        },
        {
          nome: 'Nexus Hub Coworking',
          cliente: 'Diego Brandão',
          valor: 6400,
          etapa: 'Proposta enviada',
          canal: 'Google Orgânico',
          probabilidade: 60,
          responsavel: 'Mariana Costa',
          tags: ['Proposta v2', 'Decisor Envolvido'],
        },
        {
          nome: 'Nova Era Auto Peças',
          cliente: 'Sérgio Ramos',
          valor: 8100,
          etapa: 'Proposta enviada',
          canal: 'Google Ads',
          probabilidade: 65,
          responsavel: 'Rafael Prado',
          tags: ['Plano Anual'],
        },
        {
          nome: 'Solaris Energia Renovável',
          cliente: 'Gustavo Mendonça',
          valor: 11500,
          etapa: 'Proposta enviada',
          canal: 'Indicação',
          probabilidade: 70,
          responsavel: 'Lucas Silveira',
          tags: ['Enterprise', 'Prioridade Alta'],
        },
        {
          nome: 'Rede Farma Popular (3 lojas)',
          cliente: 'Juliana Pires',
          valor: 14200,
          etapa: 'Negociação',
          canal: 'Meta Ads',
          probabilidade: 85,
          responsavel: 'Mariana Costa',
          tags: ['Ajuste Jurídico', 'Fechamento Próximo'],
        },
        {
          nome: 'Studio Pilates Vida & Equilíbrio',
          cliente: 'Larissa Moura',
          valor: 2900,
          etapa: 'Negociação',
          canal: 'Google Orgânico',
          probabilidade: 80,
          responsavel: 'Lucas Silveira',
          tags: ['Desconto Pontualidade'],
        },
        {
          nome: 'Atlas Transportes & Cargas',
          cliente: 'Carlos Eduardo Lima',
          valor: 12800,
          etapa: 'Fechado (ganho)',
          canal: 'Indicação',
          probabilidade: 100,
          responsavel: 'Rafael Prado',
          tags: ['Contrato 12m', 'Onboarding Iniciado'],
        },
        {
          nome: 'Mundo Pet Veterinária 24h',
          cliente: 'Dra. Gabriela Sales',
          valor: 6900,
          etapa: 'Fechado (ganho)',
          canal: 'Meta Ads',
          probabilidade: 100,
          responsavel: 'Mariana Costa',
          tags: ['Contrato 12m', 'BPO Completo'],
        },
        {
          nome: 'Inovare Arquitetura de Interiores',
          cliente: 'Helena Duarte',
          valor: 5400,
          etapa: 'Fechado (ganho)',
          canal: 'Google Orgânico',
          probabilidade: 100,
          responsavel: 'Lucas Silveira',
          tags: ['Primeira Parcela Paga'],
        },
      ]

      for (let i = 0; i < seedDeals.length; i++) {
        const item = seedDeals[i]
        const rec = new Record(dealsCol)
        rec.set('nome', item.nome)
        rec.set('cliente', item.cliente)
        rec.set('valor', item.valor)
        rec.set('etapa', item.etapa)
        rec.set('canal', item.canal)
        rec.set('probabilidade', item.probabilidade)
        rec.set('responsavel', item.responsavel)
        rec.set('tags', JSON.stringify(item.tags))
        app.save(rec)
      }
    }
  },
  (app) => {
    try {
      const collection = app.findCollectionByNameOrId('deals')
      app.delete(collection)
    } catch (_) {}
  },
)
