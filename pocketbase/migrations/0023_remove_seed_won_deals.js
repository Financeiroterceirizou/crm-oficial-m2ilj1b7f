migrate(
  (app) => {
    // 1. Remover deals fictícios de exemplo que possuem etapa 'Fechado (ganho)'
    // Mantém intactos todos os deals de outras etapas (Novos leads, Contato feito, Proposta enviada, Negociação)
    try {
      app.db().newQuery("DELETE FROM deals WHERE etapa = 'Fechado (ganho)'").execute()
    } catch (e) {
      console.log('Erro ou coleção deals inexistente ao remover deals ganhos:', e)
    }
  },
  (app) => {
    // Reversão não é necessária pois os registros apagados eram dados de seed fictícios
  },
)
