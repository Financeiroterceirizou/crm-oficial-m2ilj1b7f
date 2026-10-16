// pocketbase/migrations/0016_add_leads_reativacao_indexes.js
// F4 contrato de reativação (5ef4b7cd): item (d) do desenho aprovado pelo champion
// em 16/10/2026 — índices de consulta da fila em leads.
// Idempotente: adiciona só o índice que ainda não existe (compara SQL exato).
// Rollback: remove apenas estes dois índices.

migrate(
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    const novos = [
      'CREATE INDEX `idx_leads_estado_fila` ON `leads` (`estado_fila`)',
      'CREATE INDEX `idx_leads_ultima_interacao` ON `leads` (`ultima_interacao`)',
    ]
    const atuais = []
    const existentes = collection.indexes
    for (let i = 0; i < existentes.length; i++) atuais.push(String(existentes[i]))
    let mudou = false
    for (let j = 0; j < novos.length; j++) {
      if (atuais.indexOf(novos[j]) === -1) {
        atuais.push(novos[j])
        mudou = true
      }
    }
    if (mudou) {
      collection.indexes = atuais
      app.save(collection)
      console.log('Migration 0016 aplicada: índices de reativação adicionados a leads')
    } else {
      console.log('Migration 0016: índices já presentes, nada a fazer')
    }
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    const remover = ['idx_leads_estado_fila', 'idx_leads_ultima_interacao']
    const atuais = []
    const existentes = collection.indexes
    for (let i = 0; i < existentes.length; i++) {
      const s = String(existentes[i])
      let manter = true
      for (let j = 0; j < remover.length; j++) {
        if (s.indexOf(remover[j]) !== -1) manter = false
      }
      if (manter) atuais.push(s)
    }
    collection.indexes = atuais
    app.save(collection)
    console.log('Migration 0016 revertida: índices de reativação removidos')
  },
)
