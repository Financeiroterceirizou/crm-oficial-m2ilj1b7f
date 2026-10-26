// pocketbase/migrations/0019_truncate_leads_for_google_sheets_import.js
// Solicitação explícita do usuário: "Zerar os dados de leads que vamos importar da planilha do google na sequência"
// Apaga TODOS os registros da collection `leads` no PocketBase, mantendo o esquema intacto.

migrate(
  (app) => {
    const col = app.findCollectionByNameOrId('leads')
    const antes = app.countRecords('leads')
    console.log(`[0019_truncate_leads] Registros em leads antes do truncate: ${antes}`)

    // app.truncateCollection remove todos os registros da collection de forma eficiente e segura
    try {
      app.truncateCollection(col)
    } catch (err) {
      console.log(
        `[0019_truncate_leads] Erro em truncateCollection (${err}), tentando DELETE direto`,
      )
      app.db().newQuery('DELETE FROM leads').execute()
    }

    const depois = app.countRecords('leads')
    console.log(`[0019_truncate_leads] Registros em leads apos truncate: ${depois}`)
  },
  (app) => {
    // Truncate de dados de limpeza operacional não possui restauração no rollback de migração
    console.log('[0019_truncate_leads] Rollback da migração de truncate: nada a restaurar')
  },
)
