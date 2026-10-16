// pocketbase/migrations/0013_add_reativacao_fields.js
// F4 5ef4b7cd: contrato estruturado de reativação (SPEC-4-002 realinhada 16/10/2026).
//
// ADITIVA — não altera dados existentes:
//   motivo_perda         text   (motivo de perda explícito consultável — B4-201: SEM lista de valores)
//   ultima_interacao     date   (última interação registrada; fallback = updated)
//   estado_fila          select (elegivel/na_fila/aprovado/excluido)
//   motivo_exclusao      text   (motivo quando excluído da fila)
//   reativacao_registro  json   (comprovação da base legal — registro v1.1, append-only)
//
// Collection reativacao_lote: lote aprovado por humano (RN-4-203: nenhum contato
// automático; a aprovação registra a validação da base por qualquer usuário — B4-202 16/10).
//
// Rollback: remove apenas estes campos e a collection.

migrate(
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    const nomes = new Set(collection.fields.map((f) => f.name))
    const novos = [
      new TextField({ name: 'motivo_perda', required: false }),
      new DateField({ name: 'ultima_interacao', required: false }),
      new SelectField({
        name: 'estado_fila',
        required: false,
        maxSelect: 1,
        values: ['elegivel', 'na_fila', 'aprovado', 'excluido'],
      }),
      new TextField({ name: 'motivo_exclusao', required: false }),
      new JSONField({ name: 'reativacao_registro', required: false }),
    ]
    for (const f of novos) {
      if (!nomes.has(f.name)) collection.fields.add(f)
    }
    app.save(collection)
    console.log('Migration 0013 aplicada: campos de reativacao adicionados a leads')

    const existe = (() => {
      try {
        app.findCollectionByNameOrId('reativacao_lote')
        return true
      } catch (_) {
        return false
      }
    })()
    if (!existe) {
      const lote = new Collection({
        name: 'reativacao_lote',
        type: 'base',
        // RLS: leitura pública para teste (padrão error_log); alteração só admin.
        // A aprovação de lote passa pela rota autenticada /backend/v1/reativacao/aprovar.
        listRule: '',
        viewRule: '',
        createRule: '',
        updateRule: "@request.auth.role = 'admin'",
        deleteRule: "@request.auth.role = 'admin'",
        fields: [
          { name: 'lote_id', type: 'text', required: true },
          { name: 'criterio_aplicado', type: 'json', required: false },
          { name: 'regra_versao', type: 'text', required: true },
          { name: 'leads_incluidos', type: 'json', required: false },
          { name: 'leads_excluidos', type: 'json', required: false },
          { name: 'total_incluidos', type: 'number', required: false },
          { name: 'total_excluidos', type: 'number', required: false },
          { name: 'aprovado_por', type: 'text', required: false },
          { name: 'aprovado_em', type: 'text', required: false },
          {
            name: 'estado',
            type: 'select',
            required: true,
            values: ['aguardando', 'aprovado', 'executado', 'cancelado'],
            maxSelect: 1,
            defaultValue: 'aguardando',
          },
          { name: 'observacao', type: 'text', required: false },
          { name: 'created', type: 'autodate', onCreate: true, onUpdate: false },
          { name: 'updated', type: 'autodate', onCreate: true, onUpdate: true },
        ],
        indexes: [
          'CREATE UNIQUE INDEX idx_lote_id_reativacao ON reativacao_lote (lote_id)',
          'CREATE INDEX idx_estado_reativacao_lote ON reativacao_lote (estado)',
        ],
      })
      app.save(lote)
      console.log('Migration 0013 aplicada: collection reativacao_lote criada')
    }
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    for (const nome of [
      'motivo_perda',
      'ultima_interacao',
      'estado_fila',
      'motivo_exclusao',
      'reativacao_registro',
    ]) {
      try {
        collection.fields.removeByName(nome)
      } catch (_) {}
    }
    app.save(collection)
    try {
      const lote = app.findCollectionByNameOrId('reativacao_lote')
      app.delete(lote)
      console.log('Migration 0013 revertida: campos e collection removidos')
    } catch (_) {}
  },
)
