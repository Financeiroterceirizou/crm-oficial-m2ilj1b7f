// 0027 — Adiciona a etapa 'Aguardando Aprovação' ao select `etapa` da collection `deals`.
// Posicionada entre 'Negociação' e 'Fechado (ganho)' no quadro kanban da Aquisição.
// Idempotente: se o valor já existir, a migração é no-op. Não altera nenhum deal existente.
migrate(
  (app) => {
    const col = app.findCollectionByNameOrId('deals')
    const etapaField = col.fields.getByName('etapa')

    const valores = etapaField.values || []
    if (valores.indexOf('Aguardando Aprovação') !== -1) {
      return // já aplicado
    }

    // Insere antes de 'Fechado (ganho)' para manter a ordem do funil
    const idxGanho = valores.indexOf('Fechado (ganho)')
    if (idxGanho === -1) {
      valores.push('Aguardando Aprovação')
    } else {
      valores.splice(idxGanho, 0, 'Aguardando Aprovação')
    }
    etapaField.values = valores
    app.save(col)
  },
  (app) => {
    const col = app.findCollectionByNameOrId('deals')
    const etapaField = col.fields.getByName('etapa')
    const valores = (etapaField.values || []).filter(function (v) {
      return v !== 'Aguardando Aprovação'
    })
    etapaField.set('values', valores)
    app.save(col)
  },
)
