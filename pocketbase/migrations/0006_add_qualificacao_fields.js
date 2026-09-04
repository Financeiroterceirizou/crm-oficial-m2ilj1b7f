// pocketbase/migrations/0006_add_qualificacao_fields.js
// F2-T02: Adicionar campos de qualificação, pontuação e roteamento à collection leads.
// Migration aditiva; rollback remove somente os seis campos criados aqui.

migrate(
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    const nomes = new Set(collection.fields.map((f) => f.name))
    const novos = [
      new TextField({ name: 'estado_qualificacao', required: false }),
      new NumberField({ name: 'score', required: false }),
      new JSONField({ name: 'score_componentes', required: false }),
      new TextField({ name: 'regra_versao', required: false }),
      new TextField({ name: 'motivo_decisao', required: false }),
      new TextField({ name: 'proxima_acao', required: false }),
    ]
    for (const f of novos) {
      if (!nomes.has(f.name)) collection.fields.add(f)
    }
    app.save(collection)
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    for (const nome of ['estado_qualificacao', 'score', 'score_componentes', 'regra_versao', 'motivo_decisao', 'proxima_acao']) {
      try { collection.fields.removeByName(nome) } catch (_) {}
    }
    app.save(collection)
  },
)
