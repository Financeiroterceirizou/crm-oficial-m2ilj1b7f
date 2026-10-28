// pocketbase/migrations/0026_kanban_so_qualificados.js
// Regra do champion (28/10/2026): o Kanban é o quadro comercial, não a base de leads.
//   - entra no Kanban: apenas lead com estado_qualificacao = 'qualificado';
//   - pendente de aprovação ou sem segmento: aguarda decisão humana;
//   - não qualificado: nunca entra, mas o histórico fica em `leads`.
//
// O que esta migration corrige:
//   A migration 0024 criou 1 deal para CADA um dos 45 leads, sem olhar a qualificação.
//   Resultado: o Kanban mostrava 45 cards, incluindo 4 leads de comércio/indústria que
//   nunca deveriam estar lá e 36 que ainda dependem de aprovação.
//
// O que ela faz:
//   1. remove deals cujo lead NÃO é qualificado, desde que o card ainda esteja em
//      'Novos leads' (ninguém trabalhou nele). Card em etapa posterior é PRESERVADO —
//      apagar destruiria histórico comercial.
//   2. cria o deal que faltar para lead qualificado.
//   3. não toca em nenhum lead (dado de origem intocável).
//
// Rollback: não recria os deals removidos (a 0024 continua no histórico de migrations).

migrate(
  (app) => {
    const dealsCol = app.findCollectionByNameOrId('deals')
    let removidos = 0
    let preservados = 0
    let criados = 0

    // ---------- 1. limpar cards de quem não é qualificado ----------
    const todosDeals = app.findRecordsByFilter('deals', "id != ''", 'created', 5000, 0)
    for (let i = 0; i < todosDeals.length; i++) {
      const deal = todosDeals[i]
      const leadId = deal.getString('lead') || ''
      if (!leadId) continue // card manual, sem lead vinculado: não é nosso

      let lead = null
      try {
        lead = app.findRecordById('leads', leadId)
      } catch (_) {
        lead = null
      }
      if (!lead) continue

      const estado = lead.getString('estado_qualificacao') || ''
      if (estado === 'qualificado') continue

      const etapa = deal.getString('etapa') || ''
      if (etapa === 'Novos leads') {
        try {
          app.delete(deal)
          removidos += 1
        } catch (err) {
          console.log('[0026] falha ao remover deal ' + deal.id + ': ' + err.message)
        }
      } else {
        preservados += 1
        console.log(
          '[0026] preservado: ' +
            lead.getString('nome') +
            ' esta ' +
            estado +
            ' em "' +
            etapa +
            '"',
        )
      }
    }

    // ---------- 2. garantir card para todo qualificado ----------
    const qualificados = app.findRecordsByFilter(
      'leads',
      "estado_qualificacao = 'qualificado'",
      'created',
      5000,
      0,
    )
    for (let j = 0; j < qualificados.length; j++) {
      const lead = qualificados[j]
      const leadId = lead.id

      let existentes = []
      try {
        existentes = app.findRecordsByFilter('deals', "lead = '" + leadId + "'", '-created', 1, 0)
      } catch (_) {
        existentes = []
      }
      if (existentes && existentes.length > 0) continue

      const leadNome = lead.getString('nome') || 'Lead sem nome'
      const leadEmail = lead.getString('email') || ''
      const leadTelefone = lead.getString('telefone') || ''
      const leadOrigem = lead.getString('origem') || 'meta_ads'

      let canal = 'Meta Ads'
      if (leadOrigem === 'cora') canal = 'Cora'
      else if (leadOrigem === 'indicacao') canal = 'Indicação'
      else if (leadOrigem === 'manual') canal = 'Manual'

      let contato = ''
      if (leadTelefone && leadEmail) contato = leadTelefone + ' • ' + leadEmail
      else contato = leadTelefone || leadEmail || ''

      const deal = new Record(dealsCol)
      deal.set('nome', leadNome)
      deal.set('cliente', leadNome)
      deal.set('contato', contato)
      deal.set('valor', 0)
      deal.set('etapa', 'Novos leads')
      deal.set('canal', canal)
      deal.set('probabilidade', 20)
      deal.set('responsavel', 'Nao atribuido')
      deal.set('lead', leadId)
      deal.set('tags', JSON.stringify(['Lead Qualificado', canal]))
      app.save(deal)
      criados += 1
    }

    console.log(
      'Migration 0026 aplicada: ' +
        removidos +
        ' cards removidos (nao qualificados em Novos leads), ' +
        preservados +
        ' preservados (card ja trabalhado), ' +
        criados +
        ' criados (qualificados sem card)',
    )
  },
  (app) => {
    // Sem rollback destrutivo: recriar cards apagados não faz sentido.
    console.log('Migration 0026 revertida (nenhuma acao)')
  },
)
