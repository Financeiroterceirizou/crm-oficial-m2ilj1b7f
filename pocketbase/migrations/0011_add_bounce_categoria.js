// pocketbase/migrations/0011_add_bounce_categoria.js
// F3-T06: adiciona 'bounce' aos valores do select categoria em error_log.
// Bounce permanente do follow-up precisa de categoria própria na fila humana (CA-3-104).
// ADITIVA (novo valor no select); rollback remove apenas 'bounce'.

migrate(
  (app) => {
    const collection = app.findCollectionByNameOrId('error_log')
    const field = collection.fields.getByName('categoria')
    const vals = field.values || []
    if (vals.indexOf('bounce') === -1) {
      vals.push('bounce')
      field.values = vals
    }
    app.save(collection)
    console.log('Migration 0011 aplicada: categoria bounce adicionada a error_log')
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('error_log')
    const field = collection.fields.getByName('categoria')
    const vals = field.values || []
    const idx = vals.indexOf('bounce')
    if (idx !== -1) {
      vals.splice(idx, 1)
      field.values = vals
    }
    app.save(collection)
    console.log('Migration 0011 revertida: categoria bounce removida')
  },
)
