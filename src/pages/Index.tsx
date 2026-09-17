/* CRM Oficial — Página inicial: lista, detalhe e agendamento de leads do PocketBase */
import { useEffect, useState } from 'react'
import pb from '@/lib/pocketbase/client'

interface Lead {
  id: string
  lead_id: string
  opportunity_id: string
  nome: string
  email: string
  telefone: string
  origem: string
  campanha: string
  estagio: string
  responsavel: string
  estado_qualificacao: string
  score: number | null
  motivo_decisao: string
  proxima_acao: string
  estado_agendamento: string
  agendamento_situacao: string
  calendar_event_id: string
  created: string
  updated: string
}

const estagioColors: Record<string, string> = {
  capturado: 'bg-blue-100 text-blue-800',
  aguardando_dados: 'bg-yellow-100 text-yellow-800',
  encerrado_entrada_invalida: 'bg-red-100 text-red-800',
}

const origemColors: Record<string, string> = {
  meta_ads: 'bg-purple-100 text-purple-800',
  cora: 'bg-green-100 text-green-800',
  indicacao: 'bg-orange-100 text-orange-800',
  manual: 'bg-gray-100 text-gray-800',
}

const Index = () => {
  const [leads, setLeads] = useState<Lead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [user, setUser] = useState<any>(null)
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [scheduleDate, setScheduleDate] = useState('')
  const [scheduleTime, setScheduleTime] = useState('')
  const scheduleStart = scheduleDate && scheduleTime ? `${scheduleDate}T${scheduleTime}` : ''
  const [scheduleMessage, setScheduleMessage] = useState('')
  const [scheduleLoading, setScheduleLoading] = useState(false)

  useEffect(() => {
    // Verificar se há usuário logado
    const currentUser = pb.authStore.model
    if (currentUser) {
      setUser(currentUser)
    }

    // Buscar leads
    fetchLeads()
  }, [])

  const fetchLeads = async () => {
    try {
      setLoading(true)
      const records = await pb.collection('leads').getFullList({
        sort: '-created',
      })
      setLeads(records as unknown as Lead[])
      setError(null)
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar leads')
    } finally {
      setLoading(false)
    }
  }

  const handleLogin = async () => {
    try {
      await pb
        .collection('users')
        .authWithPassword('vinicius@terceirizou.com.br', 'Terceirizou@2026')
      setUser(pb.authStore.model)
      fetchLeads()
    } catch (err: any) {
      setError(err.message || 'Erro ao fazer login')
    }
  }

  const handleLogout = () => {
    pb.authStore.clear()
    setUser(null)
    setLeads([])
  }

  const handleSchedule = async () => {
    if (!selectedLead || !scheduleStart) {
      setScheduleMessage('Selecione um horário para continuar.')
      return
    }
    const [data, hora] = scheduleStart.split('T')
    const [h, m] = hora.split(':').map(Number)
    if (m !== 0 && m !== 30) {
      setScheduleMessage('Selecione um horário de 30 em 30 minutos (ex.: 10:00 ou 10:30).')
      return
    }
    const min = h * 60 + m
    const dentroManha = min >= 8 * 60 && min <= 11 * 60 + 30
    const dentroTarde = min >= 13 * 60 + 30 && min <= 17 * 60 + 30
    if (!dentroManha && !dentroTarde) {
      setScheduleMessage('Horário fora do atendimento (08:00–12:00 e 13:30–18:00).')
      return
    }
    const inicio = `${data}T${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:00-03:00`
    // fim = 30 min depois, mantendo o fuso America/Sao_Paulo (-03:00) sem passar por UTC
    const totalMin = h * 60 + m + 30
    const fh = Math.floor(totalMin / 60) % 24
    const fm = totalMin % 60
    const fim = `${data}T${String(fh).padStart(2, '0')}:${String(fm).padStart(2, '0')}:00-03:00`
    setScheduleLoading(true)
    setScheduleMessage('')
    const enviar = async () => {
      return fetch(pb.baseUrl + '/backend/v1/agendar-lead', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: pb.authStore.token,
        },
        body: JSON.stringify({
          lead_id: selectedLead.id,
          inicio,
          fim,
          email: selectedLead.email,
        }),
      })
    }
    const tratar = async (response: Response) => {
      const result = await response.json()
      if (response.ok) {
        setScheduleMessage('Solicitação enviada: ' + (result.status || 'ok'))
        fetchLeads()
      } else {
        setScheduleMessage(
          'Solicitação não concluída: ' +
            (result.motivo || result.error || result.message || 'verifique a configuração'),
        )
      }
    }
    try {
      let response = await enviar()
      if (response.status === 401) {
        // token expirado/inválido (chave JWT muda a cada deploy) — refaz login e tenta de novo
        await pb
          .collection('users')
          .authWithPassword('vinicius@terceirizou.com.br', 'Terceirizou@2026')
        setUser(pb.authStore.model)
        response = await enviar()
      }
      await tratar(response)
    } catch (err: any) {
      setScheduleMessage('Erro de conexão: ' + err.message)
    } finally {
      setScheduleLoading(false)
    }
  }

  const handleBorda = async (acao: 'cancelar' | 'no_show') => {
    if (!selectedLead) return
    const operador = user?.name || user?.email || 'operador'
    const motivo = acao === 'cancelar' ? 'cancelado pelo champion' : 'lead nao compareceu'
    setScheduleLoading(true)
    setScheduleMessage('')
    const enviar = async () => {
      return fetch(pb.baseUrl + '/backend/v1/agendar-borda', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: pb.authStore.token,
        },
        body: JSON.stringify({
          lead_id: selectedLead.id,
          acao,
          operador,
          motivo,
        }),
      })
    }
    const tratar = async (response: Response) => {
      const result = await response.json()
      if (response.ok) {
        setScheduleMessage(
          acao === 'cancelar'
            ? 'Agendamento cancelado: ' + (result.status || 'ok')
            : 'No-show registrado: ' + (result.status || 'ok'),
        )
        fetchLeads()
      } else {
        setScheduleMessage(
          'Não concluído: ' +
            (result.motivo || result.error || result.message || 'verifique a configuração'),
        )
      }
    }
    try {
      let response = await enviar()
      if (response.status === 401) {
        // token expirado/inválido — refaz login e tenta de novo
        await pb
          .collection('users')
          .authWithPassword('vinicius@terceirizou.com.br', 'Terceirizou@2026')
        setUser(pb.authStore.model)
        response = await enviar()
      }
      await tratar(response)
    } catch (err: any) {
      setScheduleMessage('Erro de conexão: ' + err.message)
    } finally {
      setScheduleLoading(false)
    }
  }

  // Tela de login
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full space-y-8 p-8">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">CRM Oficial</h1>
            <p className="mt-2 text-gray-600">Terceirizou — BPO Financeiro</p>
          </div>
          <div className="mt-8 space-y-4">
            <button
              onClick={handleLogin}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Entrar como Administrador
            </button>
            {error && <div className="text-red-600 text-sm text-center">{error}</div>}
          </div>
        </div>
      </div>
    )
  }

  // Tela principal — lista de leads
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">CRM Oficial</h1>
            <p className="text-sm text-gray-500">Terceirizou — BPO Financeiro</p>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">{user.name || user.email}</span>
            <button onClick={handleLogout} className="text-sm text-red-600 hover:text-red-800">
              Sair
            </button>
          </div>
        </div>
      </header>

      {/* Conteúdo */}
      <main className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Resumo */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm font-medium text-gray-500">Total de Leads</div>
            <div className="text-2xl font-bold text-gray-900">{leads.length}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm font-medium text-gray-500">Capturados</div>
            <div className="text-2xl font-bold text-blue-600">
              {leads.filter((l) => l.estagio === 'capturado').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm font-medium text-gray-500">Aguardando Dados</div>
            <div className="text-2xl font-bold text-yellow-600">
              {leads.filter((l) => l.estagio === 'aguardando_dados').length}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-sm font-medium text-gray-500">Encerrados</div>
            <div className="text-2xl font-bold text-red-600">
              {leads.filter((l) => l.estagio === 'encerrado_entrada_invalida').length}
            </div>
          </div>
        </div>

        {/* Tabela de leads */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:px-6 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-lg font-medium text-gray-900">Leads</h2>
            <button onClick={fetchLeads} className="text-sm text-indigo-600 hover:text-indigo-800">
              Atualizar
            </button>
          </div>

          {loading ? (
            <div className="p-8 text-center text-gray-500">Carregando...</div>
          ) : error ? (
            <div className="p-8 text-center text-red-500">{error}</div>
          ) : leads.length === 0 ? (
            <div className="p-8 text-center text-gray-500">Nenhum lead encontrado</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full border-separate border-spacing-0 divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Nome
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Telefone
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Origem
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Estágio
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Responsável
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Qualificação
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Criado em
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider sticky right-0 bg-gray-50 z-10 shadow-[inset_2px_0_0_0_rgba(0,0,0,0.06)]">
                      Ação
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {leads.map((lead) => (
                    <tr key={lead.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {lead.nome}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                        {lead.email || '—'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                        {lead.telefone || '—'}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${origemColors[lead.origem] || 'bg-gray-100 text-gray-800'}`}
                        >
                          {lead.origem}
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${estagioColors[lead.estagio] || 'bg-gray-100 text-gray-800'}`}
                        >
                          {lead.estagio}
                        </span>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                        {lead.responsavel}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm">
                        <span className="font-medium text-gray-900">
                          {lead.estado_qualificacao || '—'}
                        </span>
                        {lead.score !== null && (
                          <span className="ml-2 text-gray-500">({lead.score})</span>
                        )}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(lead.created).toLocaleDateString('pt-BR')}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm sticky right-0 bg-white z-[1]">
                        <button
                          onClick={() => {
                            setSelectedLead(lead)
                            setScheduleMessage('')
                            setScheduleDate('')
                            setScheduleTime('')
                          }}
                          className="text-indigo-600 hover:text-indigo-800"
                        >
                          Abrir
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {selectedLead && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-medium text-gray-900">{selectedLead.nome}</h3>
                <p className="text-sm text-gray-500">{selectedLead.lead_id}</p>
              </div>
              <button
                onClick={() => setSelectedLead(null)}
                className="text-gray-500 hover:text-gray-900"
              >
                Fechar
              </button>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
              <p>
                <strong>Email:</strong> {selectedLead.email || '—'}
              </p>
              <p>
                <strong>Telefone:</strong> {selectedLead.telefone || '—'}
              </p>
              <p>
                <strong>Qualificação:</strong> {selectedLead.estado_qualificacao || '—'}
              </p>
              <p>
                <strong>Score:</strong> {selectedLead.score ?? '—'}
              </p>
              <p className="col-span-2">
                <strong>Motivo:</strong> {selectedLead.motivo_decisao || '—'}
              </p>
              <p className="col-span-2">
                <strong>Próxima ação:</strong> {selectedLead.proxima_acao || '—'}
              </p>
            </div>
            {selectedLead.estado_qualificacao === 'qualificado' ? (
              <div className="mt-6 border-t pt-4">
                <h4 className="font-medium text-gray-900">Solicitar agendamento</h4>
                <p className="text-sm text-gray-500 mt-1">
                  Escolha o início da reunião de 30 minutos.
                </p>
                <div className="mt-3 grid grid-cols-2 gap-3">
                  <input
                    type="date"
                    value={scheduleDate}
                    onChange={(event) => {
                      setScheduleDate(event.target.value)
                      setScheduleTime('')
                    }}
                    className="block w-full border border-gray-300 rounded-md p-2"
                  />
                  <select
                    value={scheduleTime}
                    onChange={(event) => setScheduleTime(event.target.value)}
                    className="block w-full border border-gray-300 rounded-md p-2"
                  >
                    <option value="">Horário</option>
                    {Array.from({ length: 48 }, (_, i) => {
                      const h = String(Math.floor(i / 2)).padStart(2, '0')
                      const m = i % 2 === 0 ? '00' : '30'
                      // Horário de atendimento: 08:00–12:00 e 13:30–18:00
                      const min = h * 60 + Number(m)
                      const dentroManha = min >= 8 * 60 && min <= 11 * 60 + 30
                      const dentroTarde = min >= 13 * 60 + 30 && min <= 17 * 60 + 30
                      if (!dentroManha && !dentroTarde) return null
                      return (
                        <option key={`${h}:${m}`} value={`${h}:${m}`}>
                          {h}:{m}
                        </option>
                      )
                    })}
                  </select>
                </div>
                <button
                  onClick={handleSchedule}
                  disabled={scheduleLoading}
                  className="mt-3 w-full px-4 py-2 text-sm text-white bg-indigo-600 hover:bg-indigo-700 rounded-md disabled:opacity-50"
                >
                  {scheduleLoading ? 'Enviando...' : 'Solicitar agendamento'}
                </button>
                {scheduleMessage && <p className="mt-3 text-sm text-gray-700">{scheduleMessage}</p>}
                {selectedLead.estado_agendamento === 'agendado' &&
                selectedLead.agendamento_situacao !== 'cancelado' &&
                selectedLead.agendamento_situacao !== 'no_show' ? (
                  <div className="mt-4 border-t pt-4">
                    <h4 className="font-medium text-gray-900">Operar agendamento</h4>
                    <p className="text-sm text-gray-500 mt-1">
                      Evento: {selectedLead.calendar_event_id || '—'}
                    </p>
                    <div className="mt-3 flex gap-2">
                      <button
                        onClick={() => handleBorda('cancelar')}
                        disabled={scheduleLoading}
                        className="flex-1 px-4 py-2 text-sm text-white bg-red-600 hover:bg-red-700 rounded-md disabled:opacity-50"
                      >
                        {scheduleLoading ? 'Enviando...' : 'Cancelar agendamento'}
                      </button>
                      <button
                        onClick={() => handleBorda('no_show')}
                        disabled={scheduleLoading}
                        className="flex-1 px-4 py-2 text-sm text-white bg-amber-600 hover:bg-amber-700 rounded-md disabled:opacity-50"
                      >
                        {scheduleLoading ? 'Enviando...' : 'Marcar no-show'}
                      </button>
                    </div>
                  </div>
                ) : null}
              </div>
            ) : (
              <p className="mt-6 text-sm text-gray-500">
                Este lead não está qualificado para agendamento.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default Index