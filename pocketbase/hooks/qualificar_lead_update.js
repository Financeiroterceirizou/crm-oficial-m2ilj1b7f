// F2-T03 - Reclassificação determinística quando `respostas` muda.
// A lógica segue a mesma regra v1 do hook de criação.

onRecordUpdate((e) => {
  const record = e.record
  const ser = (v) => { if (v === null || v === undefined) return ''; if (typeof v === 'string') { try { return JSON.stringify(JSON.parse(v)) } catch (_) { return v } } return JSON.stringify(v) }
  let antes = ''
  try { if (record.original()) antes = ser(record.original().get('respostas')) } catch (_) { antes = '' }
  if (antes === ser(record.get('respostas'))) { e.next(); return }
  // Reutiliza a mesma decisão da criação, sem salvar dentro do callback.
  const carteira = ['casas de repouso ilpi','associacoes protecao veicular','vistorias veicular','escritorios arquitetura','agencias marketing','consultorias ambientais','consultorias negocio','clinicas estetica','outros segmentos prestacao servico']
  const excluidos = ['comercio','industria'], decisores = ['socio','proprietario','diretor','gerente','ceo','administrador','dono']
  const norm = (v) => v === null || v === undefined ? '' : String(v).trim().toLowerCase().replace(/_/g, ' ')
  let resp = {}; const raw = record.get('respostas')
  if (typeof raw === 'string') { try { resp = JSON.parse(raw) } catch (_) {} } else if (raw && typeof raw === 'object') resp = raw
  const prest = norm(resp.prestador), seg = norm(resp.segmento), cargo = norm(resp.cargo), fat = norm(resp.faturamento)
  let estado = 'pendente_revisao', score = null, motivo = 'score abaixo do limiar', proxima = 'aguardar_revisao_humana'
  const comp = { segmento_na_carteira: 0, receita_ou_faturamento_informado: 0, cargo_decisor: 0, segmento_excluido: 0 }
  if (['nao','não','false','0','n'].indexOf(prest) !== -1) { estado = 'nao_qualificado'; motivo = 'prestador negativo explicito'; proxima = 'sem_roteamento' }
  else if (excluidos.indexOf(seg) !== -1) { estado = 'nao_qualificado'; motivo = 'segmento fora do perfil (comercio/industria)'; proxima = 'sem_roteamento' }
  else if (!seg || !cargo) { motivo = 'dados criticos ausentes'; proxima = 'aguardar_complemento_dados' }
  else if (carteira.indexOf(seg) === -1) { estado = 'excecao'; motivo = 'segmento nao mapeado'; proxima = 'revisar_excecao' }
  else { score = 2 + (fat ? 2 : 0); comp.segmento_na_carteira = 2; if (fat) comp.receita_ou_faturamento_informado = 2; for (const d of decisores) if (cargo.indexOf(d) !== -1) { score += 1; comp.cargo_decisor = 1; break } if (score >= 4) { estado = 'qualificado'; motivo = 'score acima do limiar'; proxima = 'agendar_reuniao_fechamento' } }
  record.set('estado_qualificacao', estado); record.set('score', score); record.set('score_componentes', JSON.stringify(comp)); record.set('regra_versao', '1.0'); record.set('motivo_decisao', motivo); record.set('proxima_acao', proxima)
  e.next()
}, 'leads')
