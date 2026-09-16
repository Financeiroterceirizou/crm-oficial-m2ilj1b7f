// pocketbase/migrations/0010_add_followup_parada.js
// F3-T06: campo de parada do follow-up (SPEC-3-002 CA-3-103).
//   followup_parada  text  (resposta/agendamento/cancelamento/no_show/
//                           descadastro/bounce_permanente; vazio = sem parada)
// ADITIVA; rollback remove apenas o campo. Padrão da 0006/0007/0009.

migrate(
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    const nomes = new Set(collection.fields.map((f) => f.name))
    if (!nomes.has('followup_parada')) {
      collection.fields.add(new TextField({ name: 'followup_parada', required: false }))
    }
    app.save(collection)
    console.log('Migration 0010 aplicada: followup_parada adicionado a leads')
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    try {
      collection.fields.removeByName('followup_parada')
    } catch (_) {}
    app.save(collection)
    console.log('Migration 0010 revertida: followup_parada removido')
  },
)
