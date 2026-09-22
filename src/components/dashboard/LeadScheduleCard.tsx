import React, { useEffect, useMemo, useState } from 'react'
import {
  CalendarDays,
  CheckCircle2,
  CircleAlert,
  Eye,
  LogIn,
  LogOut,
  Mail,
  Phone,
  RefreshCw,
  Search,
  UserRound,
  X,
} from 'lucide-react'
import pb from '@/lib/pocketbase/client'

type LeadRecord = {
  id: string
  lead_id: string
  nome: string
  email: string
  telefone: string
  origem: string
  estagio: string
  responsavel: string
  estado_qualificacao: string
  score: number | null
  motivo_decisao: string
  proxima_acao: string
  estado_agendamento: string
  agendamento_inicio: string
  created: string
}

const origemColors: Record<string, string> = {
  meta_ads: 'bg-purple-100 text-purple-800',
  cora: 'bg-emerald-100 text-emerald-800',
  indicacao: 'bg-amber-100 text-amber-800',
  manual: 'bg-slate-100 text-slate-700',
}

const qualificationColors: Record<string, string> = {
  qualificado: 'bg-emerald-100 text-emerald-800',
  pendente_revisao: 'bg-amber-100 text-amber-800',
  nao_qualificado: 'bg-red-100 text-red-800',
}

function formatDate(value: string) {
  if (!value) return '—'
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleDateString('pt-BR')
}

function pad(value: number) {
  return String(value).padStart(2, '0')
}

export const LeadScheduleCard: React.FC = () => {
  const [leads, setLeads] = useState<LeadRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedLead, setSelectedLead] = useState<LeadRecord | null>(null)
  const [scheduleStart, setScheduleStart] = useState('')
  const [scheduleMessage, setScheduleMessage] = useState('')
  const [scheduleLoading, setScheduleLoading] = useState(false)
  const [authenticated, setAuthenticated] = useState(pb.authStore.isValid)
  const [loginEmail, setLoginEmail] = useState('vinicius@terceirizou.com.br')
  const [loginPassword, setLoginPassword] = useState('')
  const [loginMessage, setLoginMessage] = useState('')
  const [loginLoading, setLoginLoading] = useState(false)

  const loadLeads = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await pb.collection('leads').getList<LeadRecord>(1, 200, {
        sort: '-created',
      })
      setLeads(response.items)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível carregar os leads.')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadLeads()
    const unsubscribe = pb.authStore.onChange((token) => setAuthenticated(Boolean(token)))
    return unsubscribe
  }, [])

  const filteredLeads = useMemo(() => {
    const term = searchTerm.trim().toLowerCase()
    if (!term) return leads
    return leads.filter((lead) =>
      [lead.nome, lead.email, lead.telefone, lead.origem, lead.estado_qualificacao]
        .join(' ')
        .toLowerCase()
        .includes(term),
    )
  }, [leads, searchTerm])

  const handleLogin = async (event: React.FormEvent) => {
    event.preventDefault()
    setLoginLoading(true)
    setLoginMessage('')
    try {
      await pb.collection('users').authWithPassword(loginEmail.trim(), loginPassword)
      setLoginPassword('')
      setLoginMessage('Acesso liberado para agendamento.')
    } catch (err) {
      setLoginMessage(err instanceof Error ? err.message : 'Não foi possível entrar.')
    } finally {
      setLoginLoading(false)
    }
  }

  const openLead = (lead: LeadRecord) => {
    setSelectedLead(lead)
    setScheduleStart('')
    setScheduleMessage('')
  }

  const handleSchedule = async () => {
    if (!selectedLead || !scheduleStart) {
      setScheduleMessage('Selecione o início da reunião.')
      return
    }
    if (!authenticated || !pb.authStore.token) {
      setScheduleMessage('Entre como administrador para solicitar o agendamento.')
      return
    }

    const [date, time] = scheduleStart.split('T')
    const [hour, minute] = time.split(':').map(Number)
    const totalMinutes = hour * 60 + minute + 30
    const endHour = Math.floor(totalMinutes / 60)
    const endMinute = totalMinutes % 60
    const inicio = `${date}T${pad(hour)}:${pad(minute)}:00-03:00`
    const fim = `${date}T${pad(endHour)}:${pad(endMinute)}:00-03:00`

    setScheduleLoading(true)
    setScheduleMessage('')
    try {
      const response = await fetch(`${pb.baseUrl}/backend/v1/agendar-lead`, {
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
      const result = (await response.json()) as { status?: string; motivo?: string; error?: string }
      if (!response.ok) {
        setScheduleMessage(
          result.motivo || result.error || `Solicitação não concluída (${response.status}).`,
        )
        return
      }
      setScheduleMessage(
        result.status === 'already_scheduled'
          ? 'Este lead já possui esse agendamento.'
          : 'Solicitação enviada. Confira o retorno do Google Calendar.',
      )
      await loadLeads()
    } catch (err) {
      setScheduleMessage(
        err instanceof Error ? err.message : 'Erro de conexão ao solicitar agendamento.',
      )
    } finally {
      setScheduleLoading(false)
    }
  }

  return (
    <section
      aria-label="Leads e agendamento"
      className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden"
    >
      <div className="p-4 sm:p-5 border-b border-slate-200/80">
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <CalendarDays className="w-4 h-4 text-blue-600" />
              <h2 className="text-base font-semibold text-slate-900">Leads e agendamento</h2>
              <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-blue-100 text-blue-800">
                CRM ao vivo
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Consulte o lead, veja a qualificação e solicite uma reunião de 30 minutos.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => void loadLeads()}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
              Atualizar leads
            </button>
            {authenticated && (
              <button
                type="button"
                onClick={() => pb.authStore.clear()}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50"
              >
                <LogOut className="w-3.5 h-3.5" />
                Sair
              </button>
            )}
          </div>
        </div>

        <div className="mt-4 flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1 max-w-md">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Pesquisar lead, e-mail ou telefone..."
              className="w-full pl-8 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-md focus:outline-none focus:bg-white focus:border-blue-500"
            />
          </div>
          <span className="self-center text-[11px] text-slate-500">
            Mostrando {filteredLeads.length} de {leads.length}
          </span>
        </div>

        <form
          onSubmit={handleLogin}
          className="mt-4 rounded-lg border border-blue-100 bg-blue-50/60 p-3"
        >
          <div className="flex flex-col lg:flex-row lg:items-end gap-2">
            <div className="flex-1">
              <label className="block text-[10px] uppercase tracking-wide font-semibold text-slate-500">
                E-mail administrador
              </label>
              <input
                type="email"
                value={loginEmail}
                onChange={(event) => setLoginEmail(event.target.value)}
                className="mt-1 w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-md focus:outline-none focus:border-blue-500"
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
                placeholder={authenticated ? 'Acesso já liberado' : 'Digite a senha'}
                className="mt-1 w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-md focus:outline-none focus:border-blue-500"
              />
            </div>
            <button
              type="submit"
              disabled={loginLoading || authenticated}
              className="inline-flex items-center justify-center gap-1.5 px-4 py-2 rounded-md bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700 disabled:opacity-50"
            >
              <LogIn className="w-3.5 h-3.5" />
              {authenticated
                ? 'Acesso liberado'
                : loginLoading
                  ? 'Entrando...'
                  : 'Entrar para agendar'}
            </button>
          </div>
          {loginMessage && <p className="mt-2 text-[11px] text-slate-600">{loginMessage}</p>}
        </form>
      </div>

      {error && (
        <div className="m-4 rounded-md border border-red-200 bg-red-50 p-3 text-xs text-red-700 flex items-center gap-2">
          <CircleAlert className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50/90 border-b border-slate-200 text-slate-600 font-semibold">
              <th className="py-3 px-4 min-w-[190px]">Lead</th>
              <th className="py-3 px-4 min-w-[150px]">Origem</th>
              <th className="py-3 px-4 min-w-[150px]">Qualificação</th>
              <th className="py-3 px-4 min-w-[130px]">Criado em</th>
              <th className="py-3 px-4 min-w-[100px]">Ação</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading && (
              <tr>
                <td colSpan={5} className="py-8 px-4 text-center text-slate-400">
                  Carregando leads reais do CRM...
                </td>
              </tr>
            )}
            {!loading && filteredLeads.length === 0 && (
              <tr>
                <td colSpan={5} className="py-8 px-4 text-center text-slate-400">
                  Nenhum lead encontrado.
                </td>
              </tr>
            )}
            {!loading &&
              filteredLeads.slice(0, 100).map((lead) => (
                <tr key={lead.id} className="hover:bg-blue-50/40 align-top">
                  <td className="py-3 px-4">
                    <div className="font-semibold text-slate-900">{lead.nome || 'Sem nome'}</div>
                    <div className="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
                      <Mail className="w-3 h-3" />
                      {lead.email || '—'}
                    </div>
                    <div className="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1">
                      <Phone className="w-3 h-3" />
                      {lead.telefone || '—'}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`inline-flex rounded-full px-2 py-1 text-[10px] font-semibold ${origemColors[lead.origem] || 'bg-slate-100 text-slate-700'}`}
                    >
                      {lead.origem || '—'}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`inline-flex rounded-full px-2 py-1 text-[10px] font-semibold ${qualificationColors[lead.estado_qualificacao] || 'bg-slate-100 text-slate-700'}`}
                    >
                      {lead.estado_qualificacao || 'sem classificação'}
                      {lead.score !== null && lead.score !== undefined ? ` (${lead.score})` : ''}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-500">{formatDate(lead.created)}</td>
                  <td className="py-3 px-4">
                    <button
                      type="button"
                      onClick={() => openLead(lead)}
                      className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      Abrir
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      {selectedLead && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-slate-900/60" onClick={() => setSelectedLead(null)} />
          <div className="relative z-10 w-full max-w-lg rounded-xl bg-white shadow-2xl p-5">
            <div className="flex items-start justify-between gap-3 border-b border-slate-100 pb-3">
              <div>
                <h3 className="text-lg font-semibold text-slate-900">{selectedLead.nome}</h3>
                <p className="text-[11px] text-slate-500">
                  {selectedLead.lead_id || selectedLead.id}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedLead(null)}
                className="p-1 text-slate-400 hover:text-slate-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-xs text-slate-700">
              <div>
                <strong>E-mail:</strong>
                <br />
                {selectedLead.email || '—'}
              </div>
              <div>
                <strong>Telefone:</strong>
                <br />
                {selectedLead.telefone || '—'}
              </div>
              <div>
                <strong>Qualificação:</strong>
                <br />
                {selectedLead.estado_qualificacao || '—'}{' '}
                {selectedLead.score !== null && selectedLead.score !== undefined
                  ? `(${selectedLead.score})`
                  : ''}
              </div>
              <div>
                <strong>Agendamento:</strong>
                <br />
                {selectedLead.estado_agendamento || '—'}
              </div>
              <div className="col-span-2">
                <strong>Motivo:</strong>
                <br />
                {selectedLead.motivo_decisao || '—'}
              </div>
              <div className="col-span-2">
                <strong>Próxima ação:</strong>
                <br />
                {selectedLead.proxima_acao || '—'}
              </div>
            </div>
            {selectedLead.estado_qualificacao === 'qualificado' ? (
              <div className="mt-5 border-t border-slate-100 pt-4">
                <h4 className="font-semibold text-slate-900">Solicitar agendamento</h4>
                <p className="mt-1 text-[11px] text-slate-500">
                  Escolha um horário de 30 minutos, de segunda a sexta, das 9h às 12h ou das 14h às
                  18h.
                </p>
                <input
                  type="datetime-local"
                  value={scheduleStart}
                  onChange={(event) => setScheduleStart(event.target.value)}
                  className="mt-3 block w-full rounded-md border border-slate-200 p-2 text-sm"
                />
                <button
                  type="button"
                  onClick={() => void handleSchedule()}
                  disabled={scheduleLoading || !authenticated}
                  className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  <CalendarDays className="w-4 h-4" />
                  {scheduleLoading
                    ? 'Enviando...'
                    : authenticated
                      ? 'Solicitar agendamento'
                      : 'Entre para agendar'}
                </button>
                {scheduleMessage && (
                  <p className="mt-3 text-xs text-slate-600">{scheduleMessage}</p>
                )}
              </div>
            ) : (
              <p className="mt-5 border-t border-slate-100 pt-4 text-xs text-slate-500">
                Este lead não está qualificado para agendamento.
              </p>
            )}
          </div>
        </div>
      )}
    </section>
  )
}
