// F2-T04 - Fila autenticada de revisão/exceção.
routerAdd('GET', '/backend/v1/fila-revisao', (e) => {
  const raw = Number(e.request.url.query().get('perPage') || 100)
  const limit = Number.isFinite(raw) ? Math.min(Math.max(Math.trunc(raw), 1), 200) : 100
  const records = $app.findRecordsByFilter('leads', "estado_qualificacao = 'pendente_revisao' || estado_qualificacao = 'excecao'", '-updated', limit, 0)
  const itens = []
  for (const rec of records) itens.push({ id: rec.get('id'), nome: rec.get('nome'), origem: rec.get('origem'), estado: rec.get('estado_qualificacao'), score: rec.get('score'), motivo: rec.get('motivo_decisao'), proxima_acao: rec.get('proxima_acao'), responsavel: rec.get('responsavel'), regra_versao: rec.get('regra_versao'), updated: rec.get('updated') })
  return e.json(200, { total: itens.length, itens })
}, $apis.requireAuth())
