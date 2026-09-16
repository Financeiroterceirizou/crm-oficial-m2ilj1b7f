// pocketbase/migrations/0009_add_followup_fields.js
// F3-T05: campos mínimos para sequência de follow-up idempotente via Resend.
//
// ADITIVA — não altera dados existentes, apenas acrescenta campos:
//   followup_estado            text   (agendado/enviado/falha/parado)
//   followup_idempotency_key   text   (lead_id + cadencia + tentativa)
//   followup_ultimo_envio_id   text   (resend_email_id da última tentativa)
//   followup_tentativa         number (tentativa atual da cadência: 1..3)
//   followup_proxima_acao      text   (ação recomendada)
//   followup_historico         json   (append-only: cada tentativa e resultado)
//
// Rollback: remove apenas estes campos (não toca nas outras colunas).
// Padrão da migration 0006 (F2-T02) e 0007 (F3-T02); aplicada via MCP.

migrate(
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    const nomes = new Set(collection.fields.map((f) => f.name))
    const novos = [
      new TextField({ name: 'followup_estado', required: false }),
      new TextField({ name: 'followup_idempotency_key', required: false }),
      new TextField({ name: 'followup_ultimo_envio_id', required: false }),
      new NumberField({ name: 'followup_tentativa', required: false }),
      new TextField({ name: 'followup_proxima_acao', required: false }),
      new JSONField({ name: 'followup_historico', required: false }),
    ]
    for (const f of novos) {
      if (!nomes.has(f.name)) collection.fields.add(f)
    }
    app.save(collection)
    console.log('Migration 0009 aplicada: campos de follow-up adicionados a leads')
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    for (const nome of [
      'followup_estado',
      'followup_idempotency_key',
      'followup_ultimo_envio_id',
      'followup_tentativa',
      'followup_proxima_acao',
      'followup_historico',
    ]) {
      try {
        collection.fields.removeByName(nome)
      } catch (_) {}
    }
    app.save(collection)
    console.log('Migration 0009 revertida: campos de follow-up removidos')
  },
)
