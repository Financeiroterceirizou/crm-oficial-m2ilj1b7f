// pocketbase/migrations/0004_create_error_log.js
// F1-T08: Collection error_log para fila de recuperação de erros

migrate(
  (app) => {
    const collection = new Collection({
      name: 'error_log',
      type: 'base',
      // RLS: público para leitura (teste); admin cria/atualiza/remove
      listRule: '',
      viewRule: '',
      createRule: '',
      updateRule: "@request.auth.role = 'admin'",
      deleteRule: "@request.auth.role = 'admin'",
      fields: [
        { name: 'error_id', type: 'text', required: true },
        { name: 'received_at', type: 'autodate', onCreate: true, onUpdate: false },
        { name: 'source_event_id', type: 'text', required: false },
        {
          name: 'categoria',
          type: 'select',
          required: true,
          values: [
            'validacao',
            'permissao',
            'timeout',
            'duplicidade',
            'schema_invalido',
            'desconhecido',
          ],
          maxSelect: 1,
        },
        { name: 'resumo', type: 'text', required: true },
        { name: 'payload_resumido', type: 'text', required: false },
        { name: 'tentativa', type: 'number', required: true, defaultValue: 1 },
        {
          name: 'estado',
          type: 'select',
          required: true,
          values: ['pendente', 'em_analise', 'resolvido', 'encerrado'],
          maxSelect: 1,
          defaultValue: 'pendente',
        },
        { name: 'dono', type: 'text', required: false },
        { name: 'proxima_acao', type: 'text', required: false },
        { name: 'resolvido_em', type: 'text', required: false },
        { name: 'resolvido_por', type: 'text', required: false },
        { name: 'resultado', type: 'text', required: false },
        { name: 'historico', type: 'json', required: false },
        { name: 'created', type: 'autodate', onCreate: true, onUpdate: false },
        { name: 'updated', type: 'autodate', onCreate: true, onUpdate: true },
      ],
      indexes: [
        'CREATE INDEX idx_estado_error_log ON error_log (estado)',
        'CREATE INDEX idx_categoria_error_log ON error_log (categoria)',
      ],
    })
    app.save(collection)
    console.log('Collection error_log criada com sucesso')
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('error_log')
    app.delete(collection)
    console.log('Collection error_log removida')
  },
)
