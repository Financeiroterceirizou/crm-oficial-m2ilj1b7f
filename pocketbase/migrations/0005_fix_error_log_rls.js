// pocketbase/migrations/0005_fix_error_log_rls.js
// F1-T10: negar leitura anônima da fila de recuperação

migrate(
  (app) => {
    const collection = app.findCollectionByNameOrId('error_log')
    collection.listRule = "@request.auth.id != ''"
    collection.viewRule = "@request.auth.id != ''"
    collection.createRule = ''
    collection.updateRule = "@request.auth.role = 'admin'"
    collection.deleteRule = "@request.auth.role = 'admin'"
    app.save(collection)
    console.log('RLS error_log corrigido: leitura exige autenticação')
  },
  (app) => {
    const collection = app.findCollectionByNameOrId('error_log')
    collection.listRule = ''
    collection.viewRule = ''
    collection.createRule = ''
    collection.updateRule = "@request.auth.role = 'admin'"
    collection.deleteRule = "@request.auth.role = 'admin'"
    app.save(collection)
  },
)
