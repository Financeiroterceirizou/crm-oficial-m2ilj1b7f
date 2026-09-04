// F2-T04 - Revisão humana auditável; nunca apaga o histórico.
routerAdd('POST', '/backend/v1/revisar-lead', (e) => {
  const body = e.requestInfo().body || {}, operador = String(body.operador || '').trim(), decisao = String(body.decisao || '').trim()
  if (!operador) return e.json(400, { error: 'operador obrigatorio' })
  const validas = ['qualificado','nao_qualificado','excecao','pendente_revisao']
  if (validas.indexOf(decisao) === -1) return e.json(400, { error: 'decisao invalida. Valores: ' + validas.join(', ') })
  const motivo = String(body.motivo || '').trim() || 'revisao humana', id = String(body.lead_id || '').trim(), dk = String(body.dedup_key || '').trim()
  if (!id && !dk) return e.json(400, { error: 'lead_id ou dedup_key obrigatorio' })
  let record = null
  if (id) try { record = $app.findRecordById('leads', id) } catch (_) { record = null }
  if (!record && dk) { const found = $app.findRecordsByFilter('leads', 'dedup_key = {:dk}', '-created', 1, 0, { dk }); if (found.length) record = found[0] }
  if (!record) return e.json(404, { error: 'lead nao encontrado' })
  const anterior = record.get('estado_qualificacao') || '', bruto = record.get('historico')
  let hist = []; if (typeof bruto === 'string') { try { const parsed = JSON.parse(bruto); if (Array.isArray(parsed)) hist = parsed } catch (_) {} }
  hist.push({ acao: 'revisao_humana', ator: operador, data: new Date().toISOString(), decisao, anterior, motivo, regra_versao: record.get('regra_versao') || '' })
  record.set('estado_qualificacao', decisao); record.set('motivo_decisao', 'revisao humana: ' + motivo); record.set('proxima_acao', decisao === 'qualificado' ? 'agendar_reuniao_fechamento' : decisao === 'nao_qualificado' ? 'sem_roteamento' : decisao === 'excecao' ? 'revisar_excecao' : 'aguardar_revisao_humana'); if (decisao === 'nao_qualificado') record.set('score', null); record.set('historico', JSON.stringify(hist)); $app.save(record)
  return e.json(200, { status: 'revisado', lead_id: record.get('lead_id'), id: record.get('id'), estado: record.get('estado_qualificacao'), score: record.get('score'), motivo: record.get('motivo_decisao'), regra_versao: record.get('regra_versao') })
}, $apis.requireAuth())
