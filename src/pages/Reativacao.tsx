/* CRM Oficial — Fila de Reativação (F4 5ef4b7cd, SPEC-4-002)
   Lista leads antigos elegíveis para nova abordagem, com aprovação humana de lote.
   Nenhum contato parte daqui — a reabordagem é tarefa humana no WhatsApp. */
import { useEffect, useState } from 'react'
import pb from '@/lib/pocketbase/client'

type Fila = {
  total_elegiveis: number
  total_excluidos: number
  total_nao_elegiveis: number
  criterio: { b4_201: string; b4_202: string; fonte: string }
  elegiveis: {
    id: string
    lead_id: string
    nome: string
    email: string
    telefone: string
    origem: string
    motivo_perda: string
    ultima_interacao: string
    captado_em: string
    base_legal: string
    finalidade: string
    registro_versao: string
  }[]
  excluidos: { id: string; lead_id: string; nome: string; motivo_exclusao: string }[]
  nao_elegiveis: {
    id: string
    lead_id: string
    nome: string
    origem: string
    estado_qualificacao: string
    cnpj_presente: string
    captado_ha_90d: string
    sem_interacao_60d: string
  }[]
}

const Reativacao = () => {
  const [fila, setFila] = useState<Fila | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [loteId, setLoteId] = useState('')
  const [aprovando, setAprovando] = useState(false)
  const [authenticated, setAuthenticated] = useState(pb.authStore.isValid)
  const [loginEmail, setLoginEmail] = useState('vinicius@terceirizou.com.br')
  const [loginPassword, setLoginPassword] = useState('')
  const [loginMessage, setLoginMessage] = useState('')

  const fetchFila = async () => {
    setLoading(true)
    setError('')
    try {
      const resp = await fetch(`${pb.baseUrl}/backend/v1/fila-reativacao`, {
        headers: { Authorization: pb.authStore.token },
      })
      if (resp.status === 401) {
        setError('Acesso negado: entre com sua conta para ver a fila (RLS).')
        setFila(null)
        return
      }
      if (!resp.ok) {
        setError(`Falha ao carregar a fila (${resp.status}).`)
        setFila(null)
        return
      }
      setFila((await resp.json()) as Fila)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro de conexão.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void fetchFila()
    const unsub = pb.authStore.onChange((token) => setAuthenticated(Boolean(token)))
    return unsub
  }, [])

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoginMessage('')
    try {
      await pb.collection('users').authWithPassword(loginEmail.trim(), loginPassword)
      setLoginPassword('')
      setLoginMessage('Acesso liberado.')
      await fetchFila()
    } catch (err) {
      setLoginMessage(err instanceof Error ? err.message : 'Não foi possível entrar.')
    }
  }

  const handleAprovar = async () => {
    if (!loteId.trim()) {
      setMessage('Informe o identificador do lote.')
      return
    }
    if (!authenticated || !pb.authStore.token) {
      setMessage('Entre com sua conta para aprovar o lote.')
      return
    }
    setAprovando(true)
    setMessage('')
    try {
      const resp = await fetch(`${pb.baseUrl}/backend/v1/reativacao/aprovar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: pb.authStore.token },
        body: JSON.stringify({
          lote_id: loteId.trim(),
          operador: pb.authStore.model?.email || 'admin',
        }),
      })
      const result = await resp.json()
      if (!resp.ok) {
        setMessage(result.error || `Falha na aprovação (${resp.status}).`)
        return
      }
      setMessage(
        result.status === 'already_exists'
          ? `Lote ${result.lote_id} já existia (estado: ${result.estado}).`
          : `Lote ${result.lote_id} aprovado: ${result.total_incluidos} incluídos, ${result.total_excluidos} excluídos. Nenhum contato foi disparado.`,
      )
      setLoteId('')
      await fetchFila()
    } catch (err) {
      setMessage(err instanceof Error ? err.message : 'Erro de conexão.')
    } finally {
      setAprovando(false)
    }
  }

  return (
    <div className="space-y-6 p-4 sm:p-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900">Fila de Reativação</h1>
        <p className="text-sm text-slate-500 mt-1">
          Leads antigos elegíveis para nova abordagem — critério B4-201 + base legal B4-202
          (legítimo interesse, registro v1.1). Nenhum contato parte do sistema: aprovar o lote
          apenas organiza a fila; a reabordagem é tarefa humana no WhatsApp.
        </p>
      </div>

      {!authenticated && (
        <form
          onSubmit={handleLogin}
          className="rounded-lg border border-blue-100 bg-blue-50/60 p-3"
        >
          <div className="flex flex-col lg:flex-row lg:items-end gap-2">
            <div className="flex-1">
              <label className="block text-[10px] uppercase tracking-wide font-semibold text-slate-500">
                E-mail
              </label>
              <input
                type="email"
                value={loginEmail}
                onChange={(event) => setLoginEmail(event.target.value)}
                className="mt-1 w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-md"
              />
            </div>
            <div className="flex-1">
              <label className="block text-[10px] uppercase tracking-wide font-semibold text-slate-500">
                Senha
              </label>
              <input
                type="password"
                value={loginPassword}
                onChange={(event) => setLoginPassword(event.target.value)}
                className="mt-1 w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-md"
              />
            </div>
            <button
              type="submit"
              className="px-4 py-2 rounded-md bg-blue-600 text-white text-xs font-semibold"
            >
              Entrar
            </button>
          </div>
          {loginMessage && <p className="text-xs text-slate-600 mt-2">{loginMessage}</p>}
        </form>
      )}

      {error && <div className="p-3 rounded-lg bg-red-50 text-red-800 text-sm">{error}</div>}
      {message && (
        <div className="p-3 rounded-lg bg-green-50 text-green-800 text-sm">{message}</div>
      )}

      {loading ? (
        <div className="p-8 text-center text-slate-500">Carregando fila...</div>
      ) : fila ? (
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm font-medium text-slate-500">Elegíveis</div>
              <div className="text-2xl font-bold text-emerald-600">{fila.total_elegiveis}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm font-medium text-slate-500">Excluídos permanentemente</div>
              <div className="text-2xl font-bold text-red-600">{fila.total_excluidos}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4">
              <div className="text-sm font-medium text-slate-500">Ainda não elegíveis</div>
              <div className="text-2xl font-bold text-amber-600">{fila.total_nao_elegiveis}</div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg overflow-x-auto">
            <div className="px-4 py-3 border-b border-slate-200 text-sm font-semibold text-slate-700">
              Elegíveis para reativação
            </div>
            {fila.elegiveis.length === 0 ? (
              <div className="p-6 text-center text-sm text-slate-500">
                Nenhum lead elegível no momento (vazio ≠ zero — critério exige prestador com CNPJ,
                captação ≥ 90 dias e sem interação ≥ 60 dias).
              </div>
            ) : (
              <table className="min-w-full divide-y divide-slate-200 text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase">
                      Lead
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase">
                      Origem
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase">
                      Motivo de perda
                    </th>
                    <th className="px-4 py-2 text-left text-xs font-semibold text-slate-500 uppercase">
                      Base legal
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {fila.elegiveis.map((lead) => (
                    <tr key={lead.id} className="hover:bg-slate-50">
                      <td className="px-4 py-2">
                        <div className="font-medium text-slate-900">{lead.nome}</div>
                        <div className="text-xs text-slate-500">{lead.email || lead.telefone}</div>
                      </td>
                      <td className="px-4 py-2 text-xs text-slate-600">{lead.origem}</td>
                      <td className="px-4 py-2 text-xs text-slate-600">{lead.motivo_perda}</td>
                      <td className="px-4 py-2 text-xs">
                        <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold">
                          {lead.base_legal} · v{lead.registro_versao}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className="bg-white shadow rounded-lg">
            <div className="px-4 py-3 border-b border-slate-200 text-sm font-semibold text-slate-700">
              Aprovar lote (aprovação humana — nenhum contato automático)
            </div>
            <div className="p-4 flex flex-col sm:flex-row gap-2 items-start sm:items-center">
              <input
                value={loteId}
                onChange={(event) => setLoteId(event.target.value)}
                placeholder="Identificador do lote (ex: lote-2026-10-16)"
                className="flex-1 px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-md"
              />
              <button
                onClick={handleAprovar}
                disabled={aprovando || !authenticated || fila.total_elegiveis === 0}
                className="px-4 py-2 rounded-md bg-emerald-600 text-white text-xs font-semibold disabled:opacity-50"
              >
                {aprovando ? 'Aprovando...' : 'Aprovar lote'}
              </button>
            </div>
          </div>

          <details className="bg-white shadow rounded-lg p-4">
            <summary className="text-sm font-semibold text-slate-700 cursor-pointer">
              Excluídos permanentemente ({fila.total_excluidos}) e não elegíveis (
              {fila.total_nao_elegiveis})
            </summary>
            <div className="mt-3 space-y-1 text-xs text-slate-600 max-h-64 overflow-y-auto">
              {fila.excluidos.map((x) => (
                <div key={x.id}>
                  {x.nome} — {x.motivo_exclusao}
                </div>
              ))}
              {fila.nao_elegiveis.map((n) => (
                <div key={n.id}>
                  {n.nome} — CNPJ: {n.cnpj_presente} · 90d: {n.captado_ha_90d} · 60d:{' '}
                  {n.sem_interacao_60d} · qualificação: {n.estado_qualificacao}
                </div>
              ))}
            </div>
          </details>
        </>
      ) : null}
    </div>
  )
}

export default Reativacao
