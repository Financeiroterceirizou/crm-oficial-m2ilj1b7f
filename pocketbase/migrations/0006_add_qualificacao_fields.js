// pocketbase/migrations/0006_add_qualificacao_fields.js
// F2-T02: Adicionar campos de qualificação, pontuação e roteamento à collection leads.
//
// ADITIVA — não altera dados existentes, apenas acrescenta campos:
//   estado_qualificacao  text   (resultado da regra v1)
//   score                number (pontuação total)
//   score_componentes    json   (componentes nomeados p/ decisão explicável)
//   regra_versao         text   (versão da regra usada na decisão)
//   motivo_decisao       text   (motivo legível)
//   proxima_acao         text   (ação recomendada)
//
// Rollback: remove apenas estes campos (não toca nas outras colunas).
// Aplicada direto no Skip Cloud via MCP (sem deploy manual).

migrate(
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')

    // Evita duplicar se a migration rodar mais de uma vez
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
      if (!nomes.has(f.name)) {
        collection.fields.add(f)
      }
    }
    app.save(collection)
    console.log('Migration 0006 aplicada: campos de qualificação adicionados a leads')
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('leads')
    const remover = [
      'estado_qualificacao',
      'score',
      'score_componentes',
      'regra_versao',
      'motivo_decisao',
      'proxima_acao',
    ]
    for (const nome of remover) {
      try {
        collection.fields.removeByName(nome)
      } catch (_) {
        // campo já não existe
      }
    }
    app.save(collection)
    console.log('Migration 0006 revertida: campos de qualificação removidos')
  },
)
