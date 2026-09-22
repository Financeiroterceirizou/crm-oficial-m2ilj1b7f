// F4 cd704a1c - Prova tecnica timeboxed do conector Meta via Composio (SPEC-4-001, B4-103).
// POST /backend/v1/meta-prova
// Nao ingere nada no CRM: valida chave, conexão ativa, conta aprovada, amostra de campanhas
// e insights da janela. Falha = lacuna visivel, sem falso sucesso (CA-4-101/104).
// Somente leitura - nunca escreve no Meta.
// v0.0.70: schemas reais do Composio — argumentos ad_account_id (LIST_CAMPAIGNS/LIST_ADS),
// object_id + time_range{since,until} (GET_INSIGHTS); user_id obrigatorio no execute.
// NOTA runtime Skip: tudo declarado DENTRO do callback (escopo de modulo nao visivel ao handler).

routerAdd(
  'POST',
  '/backend/v1/meta-prova',
  (e) => {
    const CONTA_APROVADA = 'act_629165959070277' // B4-101: confirmada por escrito pelo champion (22/09)
    const JANELA_DIAS = 30 // B4-104: amostra sugerida (confirmacao formal antes da ingestao)

    const apiKeyBruta = $secrets.get('COMPOSIO_API')
    const apiKey = apiKeyBruta
      ? String(apiKeyBruta)
          .trim()
          .replace(/^["']+/g, '')
          .replace(/["']+$/g, '')
      : ''
    if (!apiKey) {
      return e.json(503, {
        status: 'pendente_configuracao',
        motivo: 'composio_api_key_ausente',
        prova_aprovada: false,
      })
    }
    const H = {
      'x-api-key': apiKey,
      'Content-Type': 'application/json',
      'User-Agent': 'terceirizou-crm-fase4/1.0',
    }

    // --- helper: executa tool Composio (leitura) ---
    function executar(toolSlug, args, connectedAccountId, userId) {
      const payload = { arguments: args, connectedAccountId: connectedAccountId, user_id: userId }
      let r = null
      try {
        r = $http.send({
          url: 'https://backend.composio.dev/api/v3.1/tools/execute/' + toolSlug,
          method: 'POST',
          headers: H,
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

    // --- 1. conexão ativa no toolkit metaads (pega userId do dono) ---
    let contas = null
    try {
      contas = $http.send({
        url: 'https://backend.composio.dev/api/v3.1/connected_accounts?toolkit_slug=metaads',
        method: 'GET',
        headers: H,
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
        lacuna: 'nenhuma conta metaads ativa no Composio ou API indisponivel',
      })
    }
    // primeira conta ACTIVE (pode haver contas EXPIRED na lista)
    let conta = null
    for (let i = 0; i < contas.json.items.length; i++) {
      if (contas.json.items[i].status === 'ACTIVE') {
        conta = contas.json.items[i]
        break
      }
    }
    if (!conta) {
      return e.json(502, {
        status: 'falha',
        etapa: 'connected_accounts',
        prova_aprovada: false,
        lacuna: 'nenhuma conta metaads com status ACTIVE (todas expiradas)',
      })
    }
    const connectedAccountId = conta.id

    // --- 2. userId do dono da conexão (obrigatorio no execute) ---
    let detalhe = null
    try {
      detalhe = $http.send({
        url: 'https://backend.composio.dev/api/v3.1/connected_accounts/' + connectedAccountId,
        method: 'GET',
        headers: H,
        timeout: 20,
      })
    } catch (_) {
      detalhe = null
    }
    const userId = detalhe && detalhe.json ? detalhe.json.userId || detalhe.json.user_id : null
    if (!userId) {
      return e.json(502, {
        status: 'falha',
        etapa: 'user_id',
        prova_aprovada: false,
        lacuna: 'nao foi possivel obter o userId da conexao Composio',
      })
    }

    // --- 3. conta de anúncios aprovada acessivel (B4-101) ---
    const provaContas = executar('METAADS_GET_AD_ACCOUNTS', {}, connectedAccountId, userId)
    let contaAprovadaEncontrada = false
    if (provaContas.ok && provaContas.data) {
      if (JSON.stringify(provaContas.data).indexOf(CONTA_APROVADA) !== -1) {
        contaAprovadaEncontrada = true
      }
    }
    if (!contaAprovadaEncontrada) {
      return e.json(502, {
        status: 'falha',
        etapa: 'conta_aprovada',
        connected_account_id: connectedAccountId,
        prova_aprovada: false,
        lacuna: 'conta ' + CONTA_APROVADA + ' nao acessivel pela conexao (RN-4-101: zero ingestao)',
      })
    }

    // --- 4. amostra: campanhas (schema real: ad_account_id + fields) ---
    const amostra = executar(
      'METAADS_LIST_CAMPAIGNS',
      {
        ad_account_id: CONTA_APROVADA,
        limit: 10,
        fields: ['id', 'name', 'objective', 'status', 'effective_status'],
      },
      connectedAccountId,
      userId,
    )
    let campanhas = []
    if (amostra.ok && amostra.data && amostra.data.data) {
      campanhas = amostra.data.data
    }

    // --- 5. insights da campanha mais recente (schema real: object_id + time_range) ---
    let amostraInsights = null
    if (campanhas.length > 0) {
      const hoje = new Date()
      const ini = new Date(hoje.getTime() - JANELA_DIAS * 24 * 3600 * 1000)
      const fmt = (d) => d.toISOString().slice(0, 10)
      const r = executar(
        'METAADS_GET_INSIGHTS',
        {
          object_id: campanhas[0].id,
          time_range: { since: fmt(ini), until: fmt(hoje) },
        },
        connectedAccountId,
        userId,
      )
      amostraInsights = r.ok ? r.data : { falha: r.http }
    } else {
      amostraInsights = { nota: 'sem campanhas na conta para insights' }
    }

    const aprovada = campanhas.length > 0

    return e.json(aprovada ? 200 : 502, {
      status: aprovada ? 'prova_aprovada' : 'prova_falhou',
      connected_account_id: connectedAccountId,
      conta_aprovada: CONTA_APROVADA,
      conta_aprovada_encontrada: contaAprovadaEncontrada,
      campanhas_na_amostra: campanhas.length,
      campanhas_resumo: campanhas.slice(0, 6).map((c) => ({
        id: c.id,
        nome: c.name,
        status: c.status,
      })),
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
