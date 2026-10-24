// pocketbase/hooks/fila_reativacao.js
// F4 5ef4b7cd: fila de reativação assistida (SPEC-4-002 realinhada 16/10/2026).
// GET /backend/v1/fila-reativacao
// Condições (registro base legal v1.1 + B4-201 revisto 23/10/2026): prestador de serviço
// (CNPJ é dado complementar, não critério); captado >= 90d;
// sem interação >= 60d; sem descadastro/nao_contatar/bounce (permanente); sem objeção
// (incl. "não tenho interesse agora"); registro de base gerado na montagem.
// RLS: exige autenticação (401) — RN-4-205. Vazio ≠ zero — RN-4-204.

routerAdd(
  'GET',
  '/backend/v1/fila-reativacao',
  (e) => {
    const limitRaw = Number(e.request.url.query().get('perPage') || 200)
    const limit = Number.isFinite(limitRaw) ? Math.min(Math.max(Math.trunc(limitRaw), 1), 500) : 200

    const registros = $app.findRecordsByFilter('leads', '', '-created', limit, 0)
    const agora = new Date().getTime()
    const noventa = 90 * 24 * 60 * 60 * 1000
    const sessenta = 60 * 24 * 60 * 60 * 1000

    const temCnpj = (rec) => {
      // Dado COMPLEMENTAR (decisão champion 23/10/2026) — nunca critério de elegibilidade.
      // Padrão provado em qualificar_lead_create.js: campo JSON pode chegar como
      // string, objeto OU array de bytes (Uint8Array) no runtime goja do PocketBase.
      let raw = rec.get('respostas')
      if (
        raw !== null &&
        raw !== undefined &&
        typeof raw === 'object' &&
        typeof raw.length === 'number' &&
        typeof raw[0] === 'number'
      ) {
        let s = ''
        for (let i = 0; i < raw.length; i++) s += String.fromCharCode(raw[i])
        raw = s
      }
      let resp = null
      if (typeof raw === 'string') {
        try {
          resp = JSON.parse(raw)
        } catch (_) {
          resp = null
        }
      } else if (raw && typeof raw === 'object') {
        resp = raw
      }
      if (!resp || typeof resp !== 'object') return false
      const chaves = Object.keys(resp)
      for (let c = 0; c < chaves.length; c++) {
        if (String(chaves[c]).toLowerCase().indexOf('cnpj') !== -1) {
          const valor = String(resp[chaves[c]] || '').trim()
          if (valor !== '' && valor !== '-' && valor !== 'null') return true
        }
      }
      return false
    }

    const temPrestador = (rec) => {
      // Prestador de serviço é o critério (decisão champion 23/10/2026) — CNPJ não entra.
      let raw = rec.get('respostas')
      if (
        raw !== null &&
        raw !== undefined &&
        typeof raw === 'object' &&
        typeof raw.length === 'number' &&
        typeof raw[0] === 'number'
      ) {
        let s = ''
        for (let i = 0; i < raw.length; i++) s += String.fromCharCode(raw[i])
        raw = s
      }
      let resp = null
      if (typeof raw === 'string') {
        try {
          resp = JSON.parse(raw)
        } catch (_) {
          resp = null
        }
      } else if (raw && typeof raw === 'object') {
        resp = raw
      }
      if (!resp || typeof resp !== 'object') return false
      const valor = String(
        (resp.prestador ?? resp.prestador_de_servico ?? resp.tipo_prestador) || '',
      )
        .trim()
        .toLowerCase()
      return (
        valor === 'sim' || valor === 's' || valor === 'true' || valor === '1' || valor === 'yes'
      )
    }

    const temObjecao = (rec) => {
      const parada = String(rec.get('followup_parada') || '')
      if (parada === 'descadastro' || parada === 'nao_contatar' || parada === 'bounce') return true
      const motivo = String(rec.get('motivo_perda') || '').toLowerCase()
      if (
        motivo.indexOf('nao tenho interesse') !== -1 ||
        motivo.indexOf('não tenho interesse') !== -1 ||
        motivo.indexOf('objecao') !== -1 ||
        motivo.indexOf('objeção') !== -1
      ) {
        return true
      }
      return false
    }

    const elegiveis = []
    const excluidos = []
    const semDado = []

    for (let i = 0; i < registros.length; i++) {
      const rec = registros[i]
      const criado = rec.getDateTime('created')
      const ultima = rec.get('ultima_interacao')
        ? rec.getDateTime('ultima_interacao')
        : rec.getDateTime('updated')
      const captadoMs = criado ? new Date(criado.string()).getTime() : 0
      const interacaoMs = ultima ? new Date(ultima.string()).getTime() : 0
      const captadoHa90 = captadoMs > 0 && agora - captadoMs >= noventa
      const semInteracao60 = interacaoMs > 0 && agora - interacaoMs >= sessenta

      const cnpj = temCnpj(rec)
      const prestador = temPrestador(rec)
      const qualificado = String(rec.get('estado_qualificacao') || '') === 'qualificado'
      const parada = String(rec.get('followup_parada') || '')
      const estadoFila = String(rec.get('estado_fila') || '')

      if (estadoFila === 'excluido') {
        excluidos.push({
          id: rec.get('id'),
          lead_id: rec.get('lead_id'),
          nome: rec.get('nome'),
          motivo_exclusao: rec.get('motivo_exclusao') || 'excluido_da_fila',
        })
        continue
      }
      if (estadoFila === 'aprovado') {
        excluidos.push({
          id: rec.get('id'),
          lead_id: rec.get('lead_id'),
          nome: rec.get('nome'),
          motivo_exclusao: 'aprovado_em_lote',
        })
        continue
      }
      if (parada === 'descadastro' || parada === 'nao_contatar' || parada === 'bounce') {
        excluidos.push({
          id: rec.get('id'),
          lead_id: rec.get('lead_id'),
          nome: rec.get('nome'),
          motivo_exclusao: 'parada_permanente_' + parada,
        })
        continue
      }
      if (temObjecao(rec)) {
        excluidos.push({
          id: rec.get('id'),
          lead_id: rec.get('lead_id'),
          nome: rec.get('nome'),
          motivo_exclusao: 'objecao_do_titular',
        })
        continue
      }
      // B4-201 revisto 23/10/2026: prestador de serviço BASTA (com ou sem CNPJ).
      if (!prestador || !qualificado || !captadoHa90 || !semInteracao60) {
        semDado.push({
          id: rec.get('id'),
          lead_id: rec.get('lead_id'),
          nome: rec.get('nome'),
          origem: rec.get('origem'),
          estado_qualificacao: rec.get('estado_qualificacao') || 'sem_dado',
          prestador: prestador ? 'sim' : 'nao',
          cnpj_presente: cnpj ? 'sim' : 'nao',
          captado_ha_90d: captadoHa90 ? 'sim' : 'nao',
          sem_interacao_60d: semInteracao60 ? 'sim' : 'nao',
        })
        continue
      }
      elegiveis.push({
        id: rec.get('id'),
        lead_id: rec.get('lead_id'),
        nome: rec.get('nome'),
        email: rec.get('email'),
        telefone: rec.get('telefone'),
        origem: rec.get('origem'),
        motivo_perda: rec.get('motivo_perda') || 'sem_motivo_registrado',
        ultima_interacao: ultima ? ultima.string() : '',
        captado_em: criado ? criado.string() : '',
        base_legal: 'legitimo_interesse',
        finalidade: 'reativacao_comercial',
        registro_versao: '1.1',
      })
    }

    return e.json(200, {
      total_elegiveis: elegiveis.length,
      total_excluidos: excluidos.length,
      total_nao_elegiveis: semDado.length,
      criterio: {
        b4_201:
          'prestador_de_servico + captado_90d + sem_interacao_60d (CNPJ complementar — revisto 23/10/2026)',
        b4_202: 'base_legal_legitimo_interesse_v1.1',
        fonte:
          'SPEC-4-002 realinhada 16/10/2026, B4-201 revisto 23/10/2026 + 06_notas/registro-base-legal-b4-202.md v1.1',
      },
      elegiveis,
      excluidos,
      nao_elegiveis: semDado,
    })
  },
  $apis.requireAuth(),
)
