migrate(
  (app) => {
    // Backfill idempotente nos registros existentes da collection deals
    // Reatribuir:
    // - Lucas Silveira -> Henrique Tavano Sammartino
    // - Mariana Costa -> Vinícius Oliveira da Costa
    // - Rafael Prado -> alternar entre os dois (metade para cada)

    try {
      // 1. Atualizar deals de Lucas Silveira -> Henrique Tavano Sammartino
      app
        .db()
        .newQuery(
          "UPDATE deals SET responsavel = 'Henrique Tavano Sammartino' WHERE responsavel = 'Lucas Silveira'",
        )
        .execute()

      // 2. Atualizar deals de Mariana Costa -> Vinícius Oliveira da Costa
      app
        .db()
        .newQuery(
          "UPDATE deals SET responsavel = 'Vinícius Oliveira da Costa' WHERE responsavel = 'Mariana Costa'",
        )
        .execute()

      // 3. Atualizar deals de Rafael Prado -> alternar metade para cada
      // Busca os registros de Rafael Prado ordenados por id/created
      const rafaelDeals = app.findRecordsByFilter(
        'deals',
        "responsavel = 'Rafael Prado'",
        'created',
        1000,
        0,
      )

      for (let i = 0; i < rafaelDeals.length; i++) {
        const deal = rafaelDeals[i]
        const novoResponsavel =
          i % 2 === 0 ? 'Henrique Tavano Sammartino' : 'Vinícius Oliveira da Costa'
        deal.set('responsavel', novoResponsavel)
        app.save(deal)
      }
    } catch (e) {
      console.log('Erro ou collection inexistente na migração 0018:', e)
    }
  },
  (app) => {
    // Reversão opcional (não estritamente necessária para backfill idempotente)
  },
)
