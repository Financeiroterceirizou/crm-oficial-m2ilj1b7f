// pocketbase/hooks/qualificar_lead_create.js
// F2-T03 - Classificacao deterministica na criacao do lead (SPEC-2-001, CA-2-001/002).
// REGRA v1.2 (28/10/2026) - decisao do champion: o SEGMENTO decide a validade.
//  8 segmentos oficiais -> qualificado | outro/desconhecido -> aprovacao
//  comercio/industria -> nao qualifica | sem segmento -> pedir complemento
// Score deixou de ser porteiro (era >=4 e o maximo atingivel era 3).
// Pre-commit (onRecordCreate): seta os campos no proprio record, SEM $app.save()
// dentro do callback - nao gera loop.
// Toda a logica e inline (regra de escopo do runtime do Skip: top-level nao e visivel no callback).

onRecordCreate((e) => {
  const record = e.record

  // ===================== REGRA v1.3 (17/11/2026) =====================
  // Decisão do champion: o SEGMENTO decide a validade do lead.
  //   8 segmentos oficiais -> qualificado
  //   "Outro Segmento de Prestação de Serviço" -> fila de aprovação (não valida sozinho)
  //   fora da lista / não reconhecido -> fila de aprovação
  //   "Segmento que não atendemos" -> não qualifica (regra inegociável, v1.3)
  //   comércio e indústria -> não qualifica (regra inegociável)
  //   sem segmento -> pedir complemento
  const oficiais = [
    'escritorio de arquitetura',
    'escritorio de advocacia',
    'clinica de saude e estetica',
    'agencia de marketing',
    'casa de repouso ilpi',
    'associacao de protecao veicular',
    'vistoria veicular',
    'consultoria em geral',
  ]
  const SEG_OUTRO = 'outro segmento de prestacao de servico'
  // Grafias antigas do formulário -> segmento oficial. Sem este mapa a base antiga
  // nunca casa: o formulário mandava "consultoria_/_assessoria", "saúde_/_estética_/_clínicas".
  // Inclui o erro de digitação "outros_segmentos_of_de_prestação_de_serviço" visto na origem.
  const legado = {
    'consultoria assessoria': 'consultoria em geral',
    'consultorias ambientais': 'consultoria em geral',
    'consultorias de negocio': 'consultoria em geral',
    'saude estetica clinicas': 'clinica de saude e estetica',
    'clinicas de estetica': 'clinica de saude e estetica',
    'agencias de marketing': 'agencia de marketing',
    'casas de repouso ilpi': 'casa de repouso ilpi',
    'associacoes de protecao veicular': 'associacao de protecao veicular',
    'vistorias veicular': 'vistoria veicular',
    'escritorios de arquitetura': 'escritorio de arquitetura',
    'escritorios de advocacia': 'escritorio de advocacia',
    'outros segmentos de prestacao de servico': 'outro segmento de prestacao de servico',
    'outros segmentos of de prestacao de servico': 'outro segmento de prestacao de servico',
    'locacao manutencao operacao de servicos': 'outro segmento de prestacao de servico',
    'educacao cursos treinamentos': 'outro segmento de prestacao de servico',
    'construcao civil piso industrial': 'outro segmento de prestacao de servico',
    'assessoria de imprensa': 'outro segmento de prestacao de servico',
  }
  const excluidosPalavras = ['comercio', 'industria']
  const decisores = ['socio', 'proprietario', 'diretor', 'gerente', 'ceo', 'administrador', 'dono']
  const SEG_NAO_ATENDEMOS = 'segmento que nao atendemos'
  const versaoRegra = '1.3'

  // String.prototype.normalize('NFD') NÃO funciona no goja (runtime do PocketBase).
  const SEM_ACENTO = {
    á: 'a',
    à: 'a',
    â: 'a',
    ã: 'a',
    ä: 'a',
    é: 'e',
    è: 'e',
    ê: 'e',
    ë: 'e',
    í: 'i',
    ì: 'i',
    î: 'i',
    ï: 'i',
    ó: 'o',
    ò: 'o',
    ô: 'o',
    õ: 'o',
    ö: 'o',
    ú: 'u',
    ù: 'u',
    û: 'u',
    ü: 'u',
    ç: 'c',
    ñ: 'n',
  }
  const norm = (v) => {
    if (v === null || v === undefined) return ''
    let s = String(v).trim().toLowerCase()
    let out = ''
    for (let i = 0; i < s.length; i++) {
      const ch = s.charAt(i)
      out += SEM_ACENTO[ch] !== undefined ? SEM_ACENTO[ch] : ch
    }
    return out
      .replace(/_/g, ' ')
      .replace(/\//g, ' ')
      .replace(/-/g, ' ')
      .replace(/\(/g, ' ')
      .replace(/\)/g, ' ')
      .replace(/\s+/g, ' ')
      .trim()
  }

  // --- respostas: string, objeto OU Uint8Array (runtime goja) ---
  let resp = {}
  let raw = record.get('respostas')
  if (
    raw !== null &&
    raw !== undefined &&
    typeof raw === 'object' &&
    typeof raw.length === 'number' &&
    typeof raw[0] === 'number'
  ) {
    // bytes -> UTF-8 CORRETO. String.fromCharCode byte a byte decodifica como Latin-1
    // e corrompe qualquer acento ("escritórios" vira "escritÃ³rios").
    const bytes = []
    for (let i = 0; i < raw.length; i++) bytes.push(raw[i] & 0xff)
    let s = ''
    let bi = 0
    while (bi < bytes.length) {
      const b0 = bytes[bi]
      if (b0 < 0x80) {
        s += String.fromCharCode(b0)
        bi += 1
      } else if (b0 >= 0xc0 && b0 < 0xe0 && bi + 1 < bytes.length) {
        s += String.fromCharCode(((b0 & 0x1f) << 6) | (bytes[bi + 1] & 0x3f))
        bi += 2
      } else if (b0 >= 0xe0 && b0 < 0xf0 && bi + 2 < bytes.length) {
        s += String.fromCharCode(
          ((b0 & 0x0f) << 12) | ((bytes[bi + 1] & 0x3f) << 6) | (bytes[bi + 2] & 0x3f),
        )
        bi += 3
      } else if (b0 >= 0xf0 && bi + 3 < bytes.length) {
        const cp =
          ((b0 & 0x07) << 18) |
          ((bytes[bi + 1] & 0x3f) << 12) |
          ((bytes[bi + 2] & 0x3f) << 6) |
          (bytes[bi + 3] & 0x3f)
        const par = cp - 0x10000
        s += String.fromCharCode(0xd800 + (par >> 10), 0xdc00 + (par & 0x3ff))
        bi += 4
      } else {
        bi += 1
      }
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

  // --- leitura com as DUAS grafias de chave ---
  // BUG CORRIGIDO em 28/10/2026: os hooks liam 'prestador' e 'faturamento', mas a
  // automação grava 'prestador_servicos' e 'faturamento_medio'. Resultado: em 45 leads
  // o prestador nunca era lido e o faturamento nunca pontuava — a regra v1 exigia
  // score >= 4, e o máximo atingível era 3. NENHUM lead podia ser qualificado.
  const pick = (a, b) => {
    const va = resp[a]
    const vb = resp[b]
    if (va !== null && va !== undefined && String(va).trim() !== '') return va
    if (vb !== null && vb !== undefined && String(vb).trim() !== '') return vb
    return ''
  }
  const segBruto = pick('segmento', 'segmento')
  const seg = norm(segBruto)
  const cargo = norm(pick('cargo', 'cargo'))
  const fat = norm(pick('faturamento', 'faturamento_medio'))
  const prest = norm(pick('prestador', 'prestador_servicos'))
  const prestNeg = prest === 'nao' || prest === 'false' || prest === '0' || prest === 'n'

  const segPalavras = seg.split(' ')
  const segExcluido = excluidosPalavras.some((p) => segPalavras.indexOf(p) !== -1)
  const segOficial = legado[seg] !== undefined ? legado[seg] : seg
  const segNaCarteira = oficiais.indexOf(segOficial) !== -1

  let estado = 'pendente_revisao'
  let score = null
  let motivo = 'segmento nao informado'
  let proxima = 'solicitar_complemento_segmento'
  let componentes = {
    segmento_na_carteira: 0,
    receita_ou_faturamento_informado: 0,
    cargo_decisor: 0,
    segmento_excluido: 0,
  }

  if (prestNeg) {
    // 1. prestador negativo explícito -> não qualifica (regra inegociável)
    estado = 'nao_qualificado'
    motivo = 'prestador negativo explicito'
    proxima = 'sem_roteamento'
  } else if (segExcluido) {
    // 2. comércio / indústria em qualquer grafia -> não qualifica
    estado = 'nao_qualificado'
    motivo = 'segmento fora do perfil (comercio/industria)'
    proxima = 'sem_roteamento'
    componentes['segmento_excluido'] = -3
  } else if (!seg) {
    // 3. sem segmento (formulário de Cadastro não pergunta) -> pedir complemento
    estado = 'pendente_revisao'
    motivo = 'segmento nao informado'
    proxima = 'solicitar_complemento_segmento'
  } else if (segOficial === SEG_NAO_ATENDEMOS) {
    // 3b. "Segmento que não atendemos" (escolha humana na tela /segmentos):
    //     regra inegociável — NÃO qualifica, SEM score (igual comércio/indústria).
    estado = 'nao_qualificado'
    motivo = 'segmento que a empresa nao atende'
    proxima = 'sem_roteamento'
    componentes['segmento_excluido'] = -3
  } else if (segOficial === SEG_OUTRO) {
    // 4. "outro prestador" é confissão de que o segmento não é conhecido:
    //    NÃO valida sozinho — vai para aprovação com a declaração do lead.
    estado = 'pendente_revisao'
    motivo = 'segmento fora da carteira - aguardando aprovacao (' + segBruto + ')'
    proxima = 'aprovar_segmento'
  } else if (segNaCarteira) {
    // 5. segmento oficial -> válido. Score fica como diagnóstico, não como porteiro.
    score = 2
    componentes['segmento_na_carteira'] = 2
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
    estado = 'qualificado'
    motivo = 'segmento valido (regra v1.2)'
    proxima = 'agendar_reuniao_fechamento'
  } else {
    // 6. segmento não reconhecido -> aprovação
    estado = 'pendente_revisao'
    motivo = 'segmento nao reconhecido - aguardando aprovacao (' + segBruto + ')'
    proxima = 'aprovar_segmento'
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
