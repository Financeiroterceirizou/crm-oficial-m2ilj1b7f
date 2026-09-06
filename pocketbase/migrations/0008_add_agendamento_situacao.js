// pocketbase/migrations/0008_add_agendamento_situacao.js
// F3-T03: campo de situação do agendamento para cancelamento/no-show.
// ADITIVA — acrescenta apenas agendamento_situacao à collection leads.
// Rollback: remove somente este campo.

migrate(
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    const nomes = new Set(collection.fields.map((f) => f.name))
    if (!nomes.has('agendamento_situacao')) {
      collection.fields.add(
        new SelectField({
          name: 'agendamento_situacao',
          required: false,
          values: ['ativo', 'cancelado', 'no_show'],
          maxSelect: 1,
        }),
      )
    }
    app.save(collection)
    console.log('Migration 0008 aplicada: agendamento_situacao adicionado a leads')
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    try {
      collection.fields.removeByName('agendamento_situacao')
    } catch (_) {
      // campo já não existe
    }
    app.save(collection)
    console.log('Migration 0008 revertida: agendamento_situacao removido')
  },
)
