// pocketbase/hooks/kanban_sync.js
// Sincronização lead -> Kanban (deals), conforme a regra de segmentos v1.2.
// Decisão do champion em 28/10/2026:
//   - lead QUALIFICADO entra direto no Kanban;
//   - lead SEM SEGMENTO ou FORA DA CARTEIRA fica fora do Kanban até aprovação humana;
//   - lead NÃO QUALIFICADO nunca entra no Kanban, mas permanece no histórico (collection leads).
//
// Roda em after-success (transação já commitada): não segura o DB. Não gera loop porque
// o hook escuta apenas a collection 'leads' e é idempotente (checa deal existente).
//
// Toda a lógica inline (runtime goja: top-level não é visível no callback).

onRecordAfterCreateSuccess((e) => {
  const record = e.record
  if ((record.getString('estado_qualificacao') || '') !== 'qualificado') return
  const leadId = record.id

  let jaExiste = null
  try {
    const achados = $app.findRecordsByFilter('deals', "lead = '" + leadId + "'", '-created', 1, 0)
    if (achados && achados.length > 0) jaExiste = achados[0]
  } catch (_) {
    jaExiste = null
  }
  if (jaExiste) return

  try {
    const dealsCol = $app.findCollectionByNameOrId('deals')
    const leadNome = record.getString('nome') || 'Lead sem nome'
    const leadEmail = record.getString('email') || ''
    const leadTelefone = record.getString('telefone') || ''
    const leadOrigem = record.getString('origem') || 'meta_ads'

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
    $app.save(deal)
    console.log('[kanban_sync] deal criado na entrada do lead ' + leadId)
  } catch (err) {
    console.log('[kanban_sync] falha ao criar deal na entrada: ' + err.message)
  }
}, 'leads')

onRecordAfterUpdateSuccess((e) => {
  const record = e.record
  const estado = record.getString('estado_qualificacao') || ''
  const leadId = record.id

  const deveEstar = estado === 'qualificado'

  let dealExistente = null
  try {
    const achados = $app.findRecordsByFilter('deals', "lead = '" + leadId + "'", '-created', 1, 0)
    if (achados && achados.length > 0) dealExistente = achados[0]
  } catch (_) {
    dealExistente = null
  }

  // ---------- qualificado e ainda não está no Kanban -> cria ----------
  if (deveEstar && !dealExistente) {
    try {
      const dealsCol = $app.findCollectionByNameOrId('deals')
      const leadNome = record.getString('nome') || 'Lead sem nome'
      const leadEmail = record.getString('email') || ''
      const leadTelefone = record.getString('telefone') || ''
      const leadOrigem = record.getString('origem') || 'meta_ads'

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
      $app.save(deal)
      console.log('[kanban_sync] deal criado (lead qualificado) ' + leadId)
    } catch (err) {
      console.log('[kanban_sync] falha ao criar deal: ' + err.message)
    }
    return
  }

  // ---------- deixou de ser qualificado -> sai do Kanban ----------
  // Só remove se o card ainda estiver na etapa inicial. Se já foi movido, houve trabalho
  // comercial: apagar destruiria histórico, então preserva e registra no log.
  if (!deveEstar && dealExistente) {
    try {
      const etapa = dealExistente.getString('etapa') || ''
      if (etapa === 'Novos leads') {
        $app.delete(dealExistente)
        console.log('[kanban_sync] deal removido (lead ' + estado + ') ' + leadId)
      } else {
        console.log(
          '[kanban_sync] deal preservado: lead ' +
            leadId +
            ' esta ' +
            estado +
            ' mas o card ja esta em "' +
            etapa +
            '"',
        )
      }
    } catch (err) {
      console.log('[kanban_sync] falha ao remover deal: ' + err.message)
    }
  }
}, 'leads')
