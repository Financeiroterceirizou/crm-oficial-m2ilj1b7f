// pocketbase/hooks/reativacao_aprovar.js
// F4 5ef4b7cd: aprovação humana de lote (RN-4-203). POST /backend/v1/reativacao/aprovar
// Nenhum contato é disparado — a fila só organiza; reabordagem é tarefa humana no
// WhatsApp (decisão 16/10). Idempotente por lote_id. Autenticação obrigatória (RN-4-205).

routerAdd(
  'POST',
  '/backend/v1/reativacao/aprovar',
  (e) => {
    const body = e.requestInfo().body || {}
    const loteId = String(body.lote_id || '').trim()
    const operador = String(body.operador || 'admin').trim()
    const observacao = String(body.observacao || '').trim()
    if (!loteId) return e.json(400, { error: 'Campos obrigatórios: lote_id' })

    // Idempotência: mesmo lote_id retorna o estado atual, sem duplicar.
    const existentes = $app.findRecordsByFilter(
      'reativacao_lote',
      'lote_id = {:lid}',
      '-created',
      1,
      0,
      { lid: loteId },
    )
    if (existentes.length > 0) {
      const rec = existentes[0]
      return e.json(200, {
        status: 'already_exists',
        lote_id: rec.get('lote_id'),
        estado: rec.get('estado'),
        aprovado_por: rec.get('aprovado_por'),
        total_incluidos: rec.get('total_incluidos'),
        total_excluidos: rec.get('total_excluidos'),
      })
    }

    // Recalcula a fila no momento da aprovação — nunca reutiliza lista envelhecida.
    const registros = $app.findRecordsByFilter('leads', '', '-created', 500, 0)
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
      const valor = String(resp.prestador ?? resp.prestador_de_servico ?? resp.tipo_prestador || '')
        .trim()
        .toLowerCase()
      return valor === 'sim' || valor === 's' || valor === 'true' || valor === '1' || valor === 'yes'
    }

    const elegiveis = []
    const excluidos = []

    for (let i = 0; i < registros.length; i++) {
      const rec = registros[i]
      const criadoMs = rec.getDateTime('created').string()
      const ultimaRaw = rec.get('ultima_interacao')
      const ultimaMs = ultimaRaw
        ? rec.getDateTime('ultima_interacao').string()
        : rec.getDateTime('updated').string()
      const captadoHa90 = criadoMs ? agora - new Date(criadoMs).getTime() >= noventa : false
      const semInteracao60 = ultimaMs ? agora - new Date(ultimaMs).getTime() >= sessenta : false

      const parada = String(rec.get('followup_parada') || '')
      const estadoFila = String(rec.get('estado_fila') || '')
      const motivoPerda = String(rec.get('motivo_perda') || '').toLowerCase()

      if (estadoFila === 'excluido') {
        excluidos.push({
          lead_id: rec.get('lead_id'),
          motivo: rec.get('motivo_exclusao') || 'excluido_da_fila',
        })
        continue
      }
      if (estadoFila === 'aprovado') {
        excluidos.push({ lead_id: rec.get('lead_id'), motivo: 'aprovado_em_lote' })
        continue
      }
      if (parada === 'descadastro' || parada === 'nao_contatar' || parada === 'bounce') {
        excluidos.push({ lead_id: rec.get('lead_id'), motivo: 'parada_permanente_' + parada })
        continue
      }
      if (
        motivoPerda.indexOf('nao tenho interesse') !== -1 ||
        motivoPerda.indexOf('não tenho interesse') !== -1 ||
        motivoPerda.indexOf('objecao') !== -1 ||
        motivoPerda.indexOf('objeção') !== -1
      ) {
        excluidos.push({ lead_id: rec.get('lead_id'), motivo: 'objecao_do_titular' })
        continue
      }
      // B4-201 revisto 23/10/2026: prestador de serviço BASTA (com ou sem CNPJ).
      if (
        !temPrestador(rec) ||
        String(rec.get('estado_qualificacao') || '') !== 'qualificado' ||
        !captadoHa90 ||
        !semInteracao60
      ) {
        excluidos.push({ lead_id: rec.get('lead_id'), motivo: 'nao_elegivel_no_momento' })
        continue
      }
      elegiveis.push(rec.get('lead_id'))
    }

    // Marca os elegíveis como aprovados e registra a comprovação da base (v1.1).
    const agoraIso = new Date().toISOString()
    try {
      for (let i = 0; i < registros.length; i++) {
        const rec = registros[i]
        if (elegiveis.indexOf(String(rec.get('lead_id'))) === -1) continue
        let registro = rec.get('reativacao_registro')
        if (
          registro !== null &&
          registro !== undefined &&
          typeof registro === 'object' &&
          typeof registro.length === 'number' &&
          typeof registro[0] === 'number'
        ) {
          let s = ''
          for (let i = 0; i < registro.length; i++) s += String.fromCharCode(registro[i])
          registro = s
        }
        if (typeof registro === 'string') {
          try {
            registro = JSON.parse(registro)
          } catch (_) {
            registro = null
          }
        }
        if (!registro || typeof registro !== 'object' || Array.isArray(registro)) registro = {}
        registro.base = 'legitimo_interesse'
        registro.finalidade = 'reativacao_comercial'
        registro.versao = '1.1'
        registro.data_avaliacao = agoraIso
        registro.avaliado_por = operador
        rec.set('reativacao_registro', JSON.stringify(registro))
        rec.set('estado_fila', 'aprovado')
        $app.save(rec)
      }
    } catch (err) {
      return e.json(500, { error: 'falha_marcando_leads', detalhe: String(err) })
    }

    let lote
    try {
      lote = new Record($app.findCollectionByNameOrId('reativacao_lote'))
    } catch (err) {
      return e.json(500, { error: 'falha_criando_lote', detalhe: String(err) })
    }
    lote.set('lote_id', loteId)
    lote.set('regra_versao', '1.1')
    lote.set(
      'criterio_aplicado',
      JSON.stringify({
        b4_201: 'prestador_de_servico + captado_90d + sem_interacao_60d (CNPJ complementar — revisto 23/10/2026)',
        b4_202: 'base_legal_legitimo_interesse_v1.1',
      }),
    )
    lote.set('leads_incluidos', JSON.stringify(elegiveis))
    lote.set('leads_excluidos', JSON.stringify(excluidos))
    lote.set('total_incluidos', elegiveis.length)
    lote.set('total_excluidos', excluidos.length)
    lote.set('aprovado_por', operador)
    lote.set('aprovado_em', agoraIso)
    lote.set('estado', 'aprovado')
    lote.set('observacao', observacao)
    try {
      $app.save(lote)
    } catch (err) {
      return e.json(500, { error: 'falha_salvando_lote', detalhe: String(err) })
    }

    return e.json(201, {
      status: 'lote_aprovado',
      lote_id: loteId,
      total_incluidos: elegiveis.length,
      total_excluidos: excluidos.length,
      contato_disparado: false,
    })
  },
  $apis.requireAuth(),
)
