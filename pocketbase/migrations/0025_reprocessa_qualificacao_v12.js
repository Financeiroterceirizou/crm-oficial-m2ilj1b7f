// pocketbase/migrations/0025_reprocessa_qualificacao_v12.js
// Regra v1.2 (28/10/2026) — decisão do champion: o SEGMENTO decide a validade do lead.
//
// Reconstrói a classificação dos leads JÁ existentes com a regra v1.2, porque:
//   1. a carteira mudou (8 segmentos oficiais; "outro prestador" deixou de valer sozinho);
//   2. os hooks liam `prestador`/`faturamento`, mas a automação grava
//      `prestador_servicos`/`faturamento_medio` — bug que impedia qualquer qualificação;
//   3. os 45 leads estavam todos em regra_versao 1.0.
//
// O que esta migration FAZ:
//   - recalcula estado_qualificacao, score, score_componentes, motivo_decisao, proxima_acao
//     e regra_versao para todos os leads;
//   - registra no histórico o evento {acao:'reprocessamento', regra_versao:'1.2', anterior}.
//
// O que esta migration NÃO faz:
//   - NÃO altera `respostas` do lead (dado de origem é intocável);
//   - NÃO sobrescreve decisão humana: lead com 'revisao_humana' no histórico é preservado.
//
// Rollback: reaplica a regra v1.0 só nos campos de qualificação (o histórico é mantido).
//
// ATENÇÃO ao runtime goja (PocketBase):
//   - `respostas` pode chegar como Uint8Array; decodificar UTF-8 byte a byte (nunca
//     String.fromCharCode direto, que decodifica como Latin-1 e corrompe acento);
//   - String.prototype.normalize('NFD') NÃO existe: usar mapa explícito de acentos;
//   - toda a lógica é inline no callback (top-level não é visível).

migrate(
  (app) => {
    // ---------- parâmetros da regra v1.2 ----------
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
      'outros segmentos de prestacao de servico': SEG_OUTRO,
      'outros segmentos of de prestacao de servico': SEG_OUTRO,
      'locacao manutencao operacao de servicos': SEG_OUTRO,
      'educacao cursos treinamentos': SEG_OUTRO,
      'construcao civil piso industrial': SEG_OUTRO,
      'assessoria de imprensa': SEG_OUTRO,
    }
    const excluidosPalavras = ['comercio', 'industria']
    const decisores = [
      'socio',
      'proprietario',
      'diretor',
      'gerente',
      'ceo',
      'administrador',
      'dono',
    ]
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

    // decodifica bytes UTF-8 corretamente
    const decodificar = (raw) => {
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
      return s
    }

    // ---------- varredura ----------
    let processados = 0
    let preservados = 0
    const contagem = {}

    const leads = app.findRecordsByFilter('leads', "id != ''", 'created', 5000, 0)

    for (let li = 0; li < leads.length; li++) {
      const record = leads[li]

      // 1. decisão humana é intocável
      let hist = []
      const histBruto = record.get('historico')
      let rawHist = ''
      if (typeof histBruto === 'string') {
        rawHist = histBruto
      } else if (
        histBruto &&
        typeof histBruto === 'object' &&
        typeof histBruto.length === 'number'
      ) {
        rawHist = decodificar(histBruto)
      }
      if (rawHist) {
        try {
          const parsed = JSON.parse(rawHist)
          if (Array.isArray(parsed)) hist = parsed
        } catch (_) {
          hist = []
        }
      }
      let temRevisaoHumana = false
      for (let hi = 0; hi < hist.length; hi++) {
        if (hist[hi] && hist[hi].acao === 'revisao_humana') {
          temRevisaoHumana = true
          break
        }
      }
      if (temRevisaoHumana) {
        preservados += 1
        continue
      }

      // 2. respostas
      let resp = {}
      let raw = record.get('respostas')
      if (
        raw !== null &&
        raw !== undefined &&
        typeof raw === 'object' &&
        typeof raw.length === 'number' &&
        typeof raw[0] === 'number'
      ) {
        raw = decodificar(raw)
      }
      if (typeof raw === 'string') {
        try {
          resp = JSON.parse(raw)
        } catch (_) {
          resp = {}
        }
      } else if (raw && typeof raw === 'object') {
        resp = raw
      }

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
      const componentes = {
        segmento_na_carteira: 0,
        receita_ou_faturamento_informado: 0,
        cargo_decisor: 0,
        segmento_excluido: 0,
      }

      if (prestNeg) {
        estado = 'nao_qualificado'
        motivo = 'prestador negativo explicito'
        proxima = 'sem_roteamento'
      } else if (segExcluido) {
        estado = 'nao_qualificado'
        motivo = 'segmento fora do perfil (comercio/industria)'
        proxima = 'sem_roteamento'
        componentes['segmento_excluido'] = -3
      } else if (!seg) {
        estado = 'pendente_revisao'
        motivo = 'segmento nao informado'
        proxima = 'solicitar_complemento_segmento'
      } else if (segOficial === SEG_OUTRO) {
        estado = 'pendente_revisao'
        motivo = 'segmento fora da carteira - aguardando aprovacao (' + segBruto + ')'
        proxima = 'aprovar_segmento'
      } else if (segNaCarteira) {
        score = 2
        componentes['segmento_na_carteira'] = 2
        if (fat) {
          score += 2
          componentes['receita_ou_faturamento_informado'] = 2
        }
        let ehDecisor = false
        for (let di = 0; di < decisores.length; di++) {
          if (cargo.indexOf(decisores[di]) !== -1) {
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
        estado = 'pendente_revisao'
        motivo = 'segmento nao reconhecido - aguardando aprovacao (' + segBruto + ')'
        proxima = 'aprovar_segmento'
      }

      // 3. histórico: registra o reprocessamento (nunca apaga)
      const anterior = record.get('estado_qualificacao') || ''
      if (anterior !== estado) {
        hist.push({
          acao: 'reprocessamento',
          ator: 'migration_0025',
          data: new Date().toISOString(),
          de: anterior,
          para: estado,
          regra_versao: '1.2',
        })
      }

      record.set('estado_qualificacao', estado)
      record.set('score', score)
      record.set('score_componentes', JSON.stringify(componentes))
      record.set('regra_versao', '1.2')
      record.set('motivo_decisao', motivo)
      record.set('proxima_acao', proxima)
      record.set('historico', JSON.stringify(hist))
      app.save(record)

      contagem[estado] = (contagem[estado] || 0) + 1
      processados += 1
    }

    console.log(
      'Migration 0025 aplicada (regra v1.2): ' +
        processados +
        ' leads reprocessados, ' +
        preservados +
        ' preservados por revisao humana. ' +
        JSON.stringify(contagem),
    )
  },
  (app) => {
    // Rollback: devolve os campos de qualificação ao estado neutro da v1.0.
    // Não apaga o histórico (auditoria fica).
    const leads = app.findRecordsByFilter('leads', "id != ''", 'created', 5000, 0)
    for (let i = 0; i < leads.length; i++) {
      const r = leads[i]
      r.set('estado_qualificacao', 'pendente_revisao')
      r.set('score', null)
      r.set('score_componentes', JSON.stringify({}))
      r.set('regra_versao', '1.0')
      r.set('motivo_decisao', 'dados criticos ausentes')
      r.set('proxima_acao', 'aguardar_complemento_dados')
      app.save(r)
    }
    console.log('Migration 0025 revertida: qualificação voltou ao estado neutro')
  },
)
