// F4 cd704a1c - Prova tecnica timeboxed do conector Meta via Composio (SPEC-4-001, B4-103).
// POST /backend/v1/meta-prova
// Nao ingere nada no CRM: autentica, lista escopos/tools, valida a conta aprovada,
// le amostra (campanhas + insights da janela) e registra limites. Falha = lacuna visivel,
// sem falso sucesso (CA-4-101/104). Somente leitura - nunca escreve no Meta.
// NOTA runtime Skip: tudo declarado DENTRO do callback (escopo de modulo nao visivel ao handler).

routerAdd(
  'POST',
  '/backend/v1/meta-prova',
  (e) => {
    const CONTA_APROVADA = 'act_629165959070277' // B4-101: confirmada por escrito pelo champion (22/09)
    const JANELA_DIAS = 30 // B4-104: amostra sugerida (confirmacao formal antes da ingestao)

    const apiKey = $secrets.get('COMPOSIO_API')
    if (!apiKey) {
      return e.json(503, {
        status: 'pendente_configuracao',
        motivo: 'composio_api_key_ausente',
        prova_aprovada: false,
      })
    }

    const headers = {
      'x-api-key': apiKey,
      'Content-Type': 'application/json',
      'User-Agent': 'terceirizou-crm-fase4/1.0',
    }

    // --- 1. conexão ativa no toolkit metaads ---
    let contas = null
    try {
      contas = $http.send({
        url: 'https://backend.composio.dev/api/v3.1/connected_accounts?toolkit_slug=metaads',
        method: 'GET',
        headers: headers,
        timeout: 20,
      })
    } catch (_) {
      contas = null
    }
    if (
      !contas ||
      contas.statusCode < 200 ||
      contas.statusCode >= 300 ||
      !contas.json ||
      !contas.json.items ||
      contas.json.items.length === 0
    ) {
      return e.json(502, {
        status: 'falha',
        etapa: 'connected_accounts',
        http: contas ? contas.statusCode : 'transport_error',
        prova_aprovada: false,
        lacuna: 'nenhuma conta metaads conectada no Composio ou API indisponivel',
      })
    }
    const conta = contas.json.items[0]
    const connectedAccountId = conta.id

    // --- 2. tools disponiveis (diagnostico de slugs reais) ---
    let tools = null
    try {
      tools = $http.send({
        url: 'https://backend.composio.dev/api/v3.1/tools?toolkit_slug=metaads',
        method: 'GET',
        headers: headers,
        timeout: 20,
      })
    } catch (_) {
      tools = null
    }
    const slugs = []
    if (tools && tools.json && tools.json.items) {
      for (let i = 0; i < tools.json.items.length; i++) {
        const s = String(tools.json.items[i].slug || '')
        if (
          s.indexOf('ACCOUNT') !== -1 ||
          s.indexOf('CAMPAIGN') !== -1 ||
          s.indexOf('INSIGHT') !== -1 ||
          s.indexOf('ADS') !== -1
        ) {
          slugs.push(s)
        }
      }
    }

    // --- 3. executa METAADS_GET_AD_ACCOUNTS (leitura) ---
    function executar(toolSlug, args) {
      const payload = { arguments: args || {}, connectedAccountId: connectedAccountId }
      let r = null
      try {
        r = $http.send({
          url: 'https://backend.composio.dev/api/v3.1/tools/execute/' + toolSlug,
          method: 'POST',
          headers: headers,
          body: JSON.stringify(payload),
          timeout: 25,
        })
      } catch (_) {
        r = null
      }
      if (!r || r.statusCode < 200 || r.statusCode >= 300 || !r.json) {
        return { ok: false, http: r ? r.statusCode : 'transport_error', data: null }
      }
      if (r.json.successful === false) {
        return { ok: false, http: r.statusCode, data: r.json.error || 'tool_failed' }
      }
      return {
        ok: true,
        http: r.statusCode,
        data: r.json.data !== undefined ? r.json.data : r.json,
      }
    }

    const provaContas = executar('METAADS_GET_AD_ACCOUNTS', {})
    let contaAprovadaEncontrada = false
    if (provaContas.ok && provaContas.data) {
      const texto = JSON.stringify(provaContas.data)
      if (texto.indexOf(CONTA_APROVADA) !== -1) contaAprovadaEncontrada = true
    }

    // --- 4. amostra: campanhas da conta aprovada ---
    let amostraCampanhas = null
    if (contaAprovadaEncontrada) {
      const r = executar('METAADS_LIST_CAMPAIGNS', { account_id: CONTA_APROVADA, limit: 10 })
      amostraCampanhas = r.ok ? r.data : { falha: r.http }
    }

    // --- 5. insights da janela (B4-104) na primeira campanha da amostra ---
    let amostraInsights = null
    if (amostraCampanhas && !amostraCampanhas.falha) {
      let primeira = null
      const arr =
        amostraCampanhas && typeof amostraCampanhas === 'object'
          ? amostraCampanhas.data || amostraCampanhas
          : null
      if (Array.isArray(arr) && arr.length > 0) primeira = arr[0]
      else if (arr && arr.data && Array.isArray(arr.data) && arr.length === undefined)
        primeira = arr.data[0]
      if (primeira && (primeira.id || primeira.campaign_id)) {
        const hoje = new Date()
        const ini = new Date(hoje.getTime() - JANELA_DIAS * 24 * 3600 * 1000)
        const fmt = (d) => d.toISOString().slice(0, 10)
        const r = executar('METAADS_GET_INSIGHTS', {
          object_id: primeira.id || primeira.campaign_id,
          date_range: { since: fmt(ini), until: fmt(hoje) },
        })
        amostraInsights = r.ok ? r.data : { falha: r.http }
      } else {
        amostraInsights = { nota: 'sem campanha na amostra para insights' }
      }
    }

    const aprovada = contaAprovadaEncontrada && amostraCampanhas && !amostraCampanhas.falha

    return e.json(aprovada ? 200 : 502, {
      status: aprovada ? 'prova_aprovada' : 'prova_falhou',
      connected_account_id: connectedAccountId,
      conta_aprovada_encontrada: contaAprovadaEncontrada,
      tools_leitura_disponiveis: slugs,
      amostra_campanhas: amostraCampanhas,
      amostra_insights: amostraInsights,
      janela_dias: JANELA_DIAS,
      prova_aprovada: aprovada,
      nota: aprovada
        ? 'prova tecnica timeboxed OK - escopos de leitura homologados; sem ingestao nesta prova'
        : 'lacuna visivel: conector permanece inativo (RN-4-101)',
    })
  },
  $apis.requireAuth(),
)
