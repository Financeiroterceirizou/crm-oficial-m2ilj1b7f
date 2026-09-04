// F2-T03 - Classificação determinística na criação do lead.
// A regra é inline para compatibilidade com o runtime Goja do PocketBase.

onRecordCreate((e) => {
  const record = e.record
  const carteira = ['casas de repouso ilpi','associacoes protecao veicular','vistorias veicular','escritorios arquitetura','agencias marketing','consultorias ambientais','consultorias negocio','clinicas estetica','outros segmentos prestacao servico']
  const excluidos = ['comercio','industria']
  const decisores = ['socio','proprietario','diretor','gerente','ceo','administrador','dono']
  const norm = (v) => v === null || v === undefined ? '' : String(v).trim().toLowerCase().replace(/_/g, ' ')
  let resp = {}
  let raw = record.get('respostas')
  if (typeof raw === 'string') { try { resp = JSON.parse(raw) } catch (_) { resp = {} } }
  else if (raw && typeof raw === 'object') resp = raw
  const prest = norm(resp.prestador), seg = norm(resp.segmento), cargo = norm(resp.cargo), fat = norm(resp.faturamento)
  const prestNeg = ['nao','não','false','0','n'].indexOf(prest) !== -1
  const prestSim = ['sim','s'].indexOf(prest) !== -1
  const segExcluido = excluidos.indexOf(seg) !== -1
  const segCarteira = carteira.indexOf(seg) !== -1
  let estado = 'pendente_revisao', score = null, motivo = 'score abaixo do limiar', proxima = 'aguardar_revisao_humana'
  const componentes = { segmento_na_carteira: 0, receita_ou_faturamento_informado: 0, cargo_decisor: 0, segmento_excluido: 0 }
  if (prestNeg) { estado = 'nao_qualificado'; motivo = 'prestador negativo explicito'; proxima = 'sem_roteamento' }
  else if ((prestSim && segExcluido) || (prestNeg && segCarteira)) { estado = 'pendente_revisao'; motivo = 'conflito prestador x segmento'; proxima = 'aguardar_revisao_humana' }
  else if (segExcluido) { estado = 'nao_qualificado'; motivo = 'segmento fora do perfil (comercio/industria)'; proxima = 'sem_roteamento' }
  else if (!seg || !cargo) { estado = 'pendente_revisao'; motivo = 'dados criticos ausentes'; proxima = 'aguardar_complemento_dados' }
  else if (!segCarteira) { estado = 'excecao'; motivo = 'segmento nao mapeado'; proxima = 'revisar_excecao' }
  else {
    score = 2 + (fat ? 2 : 0)
    componentes.segmento_na_carteira = 2
    if (fat) componentes.receita_ou_faturamento_informado = 2
    let decisor = false
    for (const d of decisores) if (cargo.indexOf(d) !== -1) decisor = true
    if (decisor) { score += 1; componentes.cargo_decisor = 1 }
    if (score >= 4) { estado = 'qualificado'; motivo = 'score acima do limiar'; proxima = 'agendar_reuniao_fechamento' }
  }
  record.set('estado_qualificacao', estado)
  record.set('score', score)
  record.set('score_componentes', JSON.stringify(componentes))
  record.set('regra_versao', '1.0')
  record.set('motivo_decisao', motivo)
  record.set('proxima_acao', proxima)
  e.next()
}, 'leads')
