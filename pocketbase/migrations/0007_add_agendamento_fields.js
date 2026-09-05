// pocketbase/migrations/0007_add_agendamento_fields.js
// F3-T02: campos mínimos para autoagendamento idempotente no Google Calendar.
// Aditiva; rollback remove somente os campos desta migration.

migrate(
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    const nomes = new Set(collection.fields.map((f) => f.name))
    const novos = [
      new TextField({ name: 'estado_agendamento', required: false }),
      new TextField({ name: 'calendar_event_id', required: false }),
      new DateField({ name: 'agendamento_inicio', required: false }),
      new DateField({ name: 'agendamento_fim', required: false }),
      new TextField({ name: 'agendamento_owner', required: false }),
      new TextField({ name: 'agendamento_proxima_acao', required: false }),
      new TextField({ name: 'agendamento_idempotency_key', required: false }),
    ]
    for (const f of novos) {
      if (!nomes.has(f.name)) collection.fields.add(f)
    }
    app.save(collection)
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    for (const nome of [
      'estado_agendamento',
      'calendar_event_id',
      'agendamento_inicio',
      'agendamento_fim',
      'agendamento_owner',
      'agendamento_proxima_acao',
      'agendamento_idempotency_key',
    ]) {
      try {
        collection.fields.removeByName(nome)
      } catch (_) {}
    }
    app.save(collection)
  },
)
