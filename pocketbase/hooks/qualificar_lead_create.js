// pocketbase/hooks/qualificar_lead_create.js
// F2-T03 - Classificacao deterministica na criacao do lead (SPEC-2-001, CA-2-001/002).
// Aplica a regra v1 aprovada na F2-T01 (config/regra_qualificacao_v1.json):
// estados, pesos, limiares, ordem de decisao, motivo e proxima acao.
// Pre-commit (onRecordCreate): seta os campos no proprio record, SEM $app.save()
// dentro do callback - nao gera loop.
// Toda a logica e inline (regra de escopo do runtime do Skip: top-level nao e visivel no callback).

onRecordCreate((e) => {
  const record = e.record

  // --- parametros da regra v1 (copiados de config/regra_qualificacao_v1.json) ---
  const carteira = [
    'casas de repouso ilpi',
    'associacoes protecao veicular',
    'vistorias veicular',
    'escritorios arquitetura',
    'agencias marketing',
    'consultorias ambientais',
    'consultorias negocio',
    'clinicas estetica',
    'outros segmentos prestacao servico',
  ]
  const excluidos = ['comercio', 'industria']
  const decisores = ['socio', 'proprietario', 'diretor', 'gerente', 'ceo', 'administrador', 'dono']
  const limiarQualificado = 4
  const versaoRegra = '1.0'

  // --- normalizacao identica ao validador Python aprovado na F2-T01 ---
  const norm = (v) => {
    if (v === null || v === undefined) return ''
    return String(v).trim().toLowerCase().replace(/_/g, ' ')
  }

  // --- leitura das respostas (campo json pode vir string, objeto OU Uint8Array/array de bytes no runtime goja) ---
  let resp = {}
  let raw = record.get('respostas')
  if (
    raw !== null &&
    raw !== undefined &&
    typeof raw === 'object' &&
    typeof raw.length === 'number' &&
    typeof raw[0] === 'number'
  ) {
    // bytes -> string (sem passar por JSON.stringify para nao corromper o conteudo)
    let s = ''
    for (let i = 0; i < raw.length; i++) {
      s += String.fromCharCode(raw[i])
    }
    raw = s
  }
  if (typeof raw === 'string') {
    try {
      resp = JSON.parse(raw)
    } catch (e) {
      resp = {}
    }
  } else if (raw && typeof raw === 'object') {
    resp = raw
  }

  const prest = norm(resp['prestador'])
  const seg = norm(resp['segmento'])
  const cargo = norm(resp['cargo'])
  const fat = norm(resp['faturamento'])
  const prestNeg =
    prest === 'nao' || prest === 'não' || prest === 'false' || prest === '0' || prest === 'n'
  const prestSim = prest === 'sim' || prest === 's'
  const segExcluido = excluidos.indexOf(seg) !== -1
  const segCarteira = carteira.indexOf(seg) !== -1

  // --- aplicacao da regra na ordem exata da v1 ---
  let estado = 'pendente_revisao'
  let score = null
  let motivo = 'score abaixo do limiar'
  let proxima = 'aguardar_revisao_humana'
  let componentes = {
    segmento_na_carteira: 0,
    receita_ou_faturamento_informado: 0,
    cargo_decisor: 0,
    segmento_excluido: 0,
  }

  if (prestNeg) {
    // 1. prestador negativo explicito -> nao_qualificado (regra inegociavel)
    estado = 'nao_qualificado'
    motivo = 'prestador negativo explicito'
    proxima = 'sem_roteamento'
  } else if ((prestSim && segExcluido) || (prestNeg && segCarteira)) {
    // 2. conflito entre prestador e segmento -> revisao
    estado = 'pendente_revisao'
    motivo = 'conflito prestador x segmento'
    proxima = 'aguardar_revisao_humana'
  } else if (segExcluido) {
    // 3. segmento excluido (comercio/industria) -> nao_qualificado
    estado = 'nao_qualificado'
    motivo = 'segmento fora do perfil (comercio/industria)'
    proxima = 'sem_roteamento'
  } else if (!seg || !cargo) {
    // 4. dados criticos ausentes (sem segmento ou cargo) -> revisao
    estado = 'pendente_revisao'
    motivo = 'dados criticos ausentes'
    proxima = 'aguardar_complemento_dados'
  } else if (!segCarteira) {
    // 5. segmento nao mapeado -> excecao
    estado = 'excecao'
    motivo = 'segmento nao mapeado'
    proxima = 'revisar_excecao'
  } else {
    // 6. pontuacao
    score = 0
    if (segCarteira) {
      score += 2
      componentes['segmento_na_carteira'] = 2
    }
    if (fat) {
      score += 2
      componentes['receita_ou_faturamento_informado'] = 2
    }
    let ehDecisor = false
    for (let i = 0; i < decisores.length; i++) {
      if (cargo.indexOf(decisores[i]) !== -1) {
        ehDecisor = true
        break
      }
    }
    if (ehDecisor) {
      score += 1
      componentes['cargo_decisor'] = 1
    }
    if (score >= limiarQualificado) {
      estado = 'qualificado'
      motivo = 'score acima do limiar'
      proxima = 'agendar_reuniao_fechamento'
    } else {
      estado = 'pendente_revisao'
      motivo = 'score abaixo do limiar'
      proxima = 'aguardar_revisao_humana'
    }
  }

  // --- escrita dos campos de qualificacao (F2-T02) ---
  record.set('estado_qualificacao', estado)
  record.set('score', score)
  record.set('score_componentes', JSON.stringify(componentes))
  record.set('regra_versao', versaoRegra)
  record.set('motivo_decisao', motivo)
  record.set('proxima_acao', proxima)

  e.next()
}, 'leads')
