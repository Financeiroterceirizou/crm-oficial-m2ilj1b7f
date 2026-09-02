// pocketbase/hooks/fila_revisao.js
// F2-T04 - Fila de revisao/excecao visivel (SPEC-2-001, CA-2-003).
// GET /backend/v1/fila-revisao
// Lista leads em pendente_revisao ou excecao, com estado, motivo, score e responsavel.
// Requer autenticacao (CA-2-005): sem auth -> 401.

routerAdd(
  'GET',
  '/backend/v1/fila-revisao',
  (e) => {
    const limitRaw = Number(e.request.url.query().get('perPage') || 100)
    const limit = Number.isFinite(limitRaw) ? Math.min(Math.max(Math.trunc(limitRaw), 1), 200) : 100

    const records = $app.findRecordsByFilter(
      'leads',
      "estado_qualificacao = 'pendente_revisao' || estado_qualificacao = 'excecao'",
      '-updated',
      limit,
      0,
    )

    const itens = []
    for (let i = 0; i < records.length; i++) {
      const rec = records[i]
      itens.push({
        id: rec.get('id'),
        nome: rec.get('nome'),
        origem: rec.get('origem'),
        estado: rec.get('estado_qualificacao'),
        score: rec.get('score'),
        motivo: rec.get('motivo_decisao'),
        proxima_acao: rec.get('proxima_acao'),
        responsavel: rec.get('responsavel'),
        regra_versao: rec.get('regra_versao'),
        updated: rec.get('updated'),
      })
    }

    return e.json(200, { total: itens.length, itens })
  },
  $apis.requireAuth(),
)
