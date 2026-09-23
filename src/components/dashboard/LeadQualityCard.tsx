import React, { useEffect, useMemo, useState } from 'react'
import {
  BarChart3,
  CalendarDays,
  CircleAlert,
  Database,
  RefreshCw,
  Target,
  Users,
} from 'lucide-react'
import pb from '@/lib/pocketbase/client'

type QualityLead = {
  id: string
  created: string
  origem?: string
  campanha?: string
  meta_campanha_nome?: string
  meta_status?: string
  respostas?: unknown
  estado_agendamento?: string
  agendamento_inicio?: string
  agendamento_situacao?: string
}

type QualityResult = {
  hasPrestador: boolean
  hasCnpj: boolean
  qualified: boolean
}

type CampaignBucket = {
  key: string
  origem: string
  campanha: string
  source: string
  recebidos: number
  qualificados: number
  dadosCompletos: number
  agendados: number
}

const WINDOW_DAYS = 28

function parseJsonObject(value: unknown): Record<string, unknown> {
  if (!value) return {}
  if (typeof value === 'string') {
    try {
      const parsed = JSON.parse(value)
      return parsed && typeof parsed === 'object' ? (parsed as Record<string, unknown>) : {}
    } catch {
      return {}
    }
  }
  if (Array.isArray(value) && value.every((item) => typeof item === 'number')) {
    try {
      const parsed = JSON.parse(String.fromCharCode(...value))
      return parsed && typeof parsed === 'object' ? (parsed as Record<string, unknown>) : {}
    } catch {
      return {}
    }
  }
  return typeof value === 'object' ? (value as Record<string, unknown>) : {}
}

function normalize(value: unknown) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/_/g, ' ')
}

function hasValue(value: unknown) {
  return String(value || '').trim().length > 0
}

function hasCnpj(value: unknown) {
  const digits = String(value || '').replace(/\D/g, '')
  return digits.length === 14 && !/^0+$/.test(digits)
}

function getQualityResult(lead: QualityLead): QualityResult {
  const respostas = parseJsonObject(lead.respostas)
  const prestadorValue =
    respostas.prestador ?? respostas.prestador_de_servico ?? respostas.tipo_prestador
  const cnpjValue = respostas.cnpj_cpf ?? respostas.cnpj ?? respostas.documento
  const prestador = normalize(prestadorValue)
  const hasPrestador = ['sim', 's', 'true', '1', 'yes'].includes(prestador)
  const cnpj = hasCnpj(cnpjValue)

  return {
    hasPrestador: hasValue(prestadorValue),
    hasCnpj: hasCnpj(cnpjValue),
    qualified: hasPrestador && cnpj,
  }
}

function isScheduled(lead: QualityLead) {
  const state = normalize(lead.estado_agendamento)
  const situation = normalize(lead.agendamento_situacao)
  if (situation === 'cancelado' || situation === 'no show') return false
  if (state === 'agendado') return true
  return Boolean(lead.agendamento_inicio) && !['falha', 'pendente configuracao'].includes(state)
}

function formatDate(value: Date) {
  return value.toLocaleDateString('pt-BR')
}

function formatPercent(value: number) {
  return `${value.toLocaleString('pt-BR', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%`
}

function formatCount(value: number | null) {
  return value === null ? 'Sem dado' : value.toLocaleString('pt-BR')
}

export const LeadQualityCard: React.FC = () => {
  const [leads, setLeads] = useState<QualityLead[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [windowEnd, setWindowEnd] = useState(() => new Date())
  const [invalidDateCount, setInvalidDateCount] = useState(0)

  const loadLeads = async () => {
    setLoading(true)
    setError('')
    setWindowEnd(new Date())
    try {
      const response = await pb.collection('leads').getFullList<QualityLead>({ sort: '-created' })
      setLeads(response)
      setInvalidDateCount(
        response.filter((lead) => !Number.isFinite(Date.parse(lead.created))).length,
      )
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Não foi possível carregar a qualidade dos leads.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadLeads()
  }, [])

  const windowStart = useMemo(
    () => new Date(windowEnd.getTime() - WINDOW_DAYS * 24 * 60 * 60 * 1000),
    [windowEnd],
  )

  const periodLeads = useMemo(
    () =>
      leads.filter((lead) => {
        const created = Date.parse(lead.created)
        return (
          Number.isFinite(created) &&
          created >= windowStart.getTime() &&
          created <= windowEnd.getTime()
        )
      }),
    [leads, windowEnd, windowStart],
  )

  const buckets = useMemo<CampaignBucket[]>(() => {
    const grouped = new Map<string, CampaignBucket>()

    for (const lead of periodLeads) {
      const origem = hasValue(lead.origem) ? String(lead.origem).trim() : 'Origem não informada'
      const metaCampaign = hasValue(lead.meta_campanha_nome)
        ? String(lead.meta_campanha_nome).trim()
        : ''
      const declaredCampaign = hasValue(lead.campanha) ? String(lead.campanha).trim() : ''
      const campanha = metaCampaign || declaredCampaign || 'Campanha não informada'
      const source = metaCampaign
        ? 'CRM + espelho Meta'
        : declaredCampaign
          ? 'CRM — campanha declarada'
          : 'CRM — origem sem campanha'
      const key = `${origem}::${campanha}`
      const current = grouped.get(key) || {
        key,
        origem,
        campanha,
        source,
        recebidos: 0,
        qualificados: 0,
        dadosCompletos: 0,
        agendados: 0,
      }
      if (metaCampaign && current.source !== 'CRM + espelho Meta') {
        current.source = 'CRM + espelho Meta'
      }
      const quality = getQualityResult(lead)

      current.recebidos += 1
      if (quality.hasPrestador && quality.hasCnpj) current.dadosCompletos += 1
      if (quality.qualified) current.qualificados += 1
      if (isScheduled(lead)) current.agendados += 1
      grouped.set(key, current)
    }

    return Array.from(grouped.values()).sort((a, b) => {
      if (b.recebidos !== a.recebidos) return b.recebidos - a.recebidos
      return a.campanha.localeCompare(b.campanha, 'pt-BR')
    })
  }, [periodLeads])

  const totals = useMemo(() => {
    const recebidos = buckets.reduce((total, bucket) => total + bucket.recebidos, 0)
    const qualificados = buckets.reduce((total, bucket) => total + bucket.qualificados, 0)
    const dadosCompletos = buckets.reduce((total, bucket) => total + bucket.dadosCompletos, 0)
    const agendados = buckets.reduce((total, bucket) => total + bucket.agendados, 0)
    const qualityIsComplete = recebidos > 0 && dadosCompletos === recebidos

    return {
      recebidos,
      qualificados: dadosCompletos > 0 ? qualificados : null,
      qualidade: qualityIsComplete && recebidos > 0 ? (qualificados / recebidos) * 100 : null,
      agendados,
      dadosCompletos,
    }
  }, [buckets])

  return (
    <section
      aria-label="Qualidade de leads por campanha"
      className="bg-white rounded-xl border border-slate-200/90 shadow-sm overflow-hidden"
    >
      <div className="p-4 sm:p-5 border-b border-slate-200/80">
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-blue-600" />
              <h2 className="text-base font-semibold text-slate-900">
                Qualidade de leads por campanha
              </h2>
              <span className="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-blue-100 text-blue-800">
                CRM ao vivo
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Recebidos, qualificados e agendados por origem/campanha no período aprovado.
            </p>
          </div>
          <button
            type="button"
            onClick={() => void loadLeads()}
            className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-md border border-slate-200 text-xs font-medium text-slate-600 hover:bg-slate-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Atualizar qualidade
          </button>
        </div>

        <div className="mt-4 rounded-lg border border-blue-100 bg-blue-50/60 p-3 text-[11px] text-slate-600">
          <div className="flex items-start gap-2">
            <CalendarDays className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
            <div>
              <strong className="text-slate-800">Período:</strong> últimos {WINDOW_DAYS} dias —{' '}
              {formatDate(windowStart)} a {formatDate(windowEnd)}.
              <br />
              <strong className="text-slate-800">Fonte:</strong> collection CRM <code>leads</code>,
              campo <code>created</code>, respostas de prestador/CNPJ e campos de agendamento;
              campanha Meta quando o espelho estiver disponível.
              <br />
              <strong className="text-slate-800">Critério aprovado B4-203:</strong> qualificado =
              prestador de serviço + CNPJ; qualidade = qualificados ÷ recebidos × 100.
              <br />
              <span className="text-slate-500">Conversão não é calculada nesta task.</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 mt-4">
          <div className="rounded-lg border border-slate-200 bg-slate-50/60 p-3">
            <span className="flex items-center gap-1 text-[10px] uppercase tracking-wide text-slate-500">
              <Users className="w-3 h-3" /> Recebidos
            </span>
            <strong className="block mt-1 text-xl text-slate-900">
              {formatCount(totals.recebidos)}
            </strong>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50/60 p-3">
            <span className="flex items-center gap-1 text-[10px] uppercase tracking-wide text-slate-500">
              <Target className="w-3 h-3" /> Qualificados
            </span>
            <strong className="block mt-1 text-xl text-slate-900">
              {formatCount(totals.qualificados)}
            </strong>
            {totals.dadosCompletos < totals.recebidos && totals.recebidos > 0 && (
              <span className="block mt-1 text-[10px] text-amber-700">
                {totals.dadosCompletos} de {totals.recebidos} com dados completos
              </span>
            )}
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50/60 p-3">
            <span className="flex items-center gap-1 text-[10px] uppercase tracking-wide text-slate-500">
              <BarChart3 className="w-3 h-3" /> Qualidade
            </span>
            <strong className="block mt-1 text-xl text-slate-900">
              {totals.qualidade === null ? 'Sem dado' : formatPercent(totals.qualidade)}
            </strong>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50/60 p-3">
            <span className="flex items-center gap-1 text-[10px] uppercase tracking-wide text-slate-500">
              <CalendarDays className="w-3 h-3" /> Agendados
            </span>
            <strong className="block mt-1 text-xl text-slate-900">
              {formatCount(totals.agendados)}
            </strong>
          </div>
        </div>
      </div>

      {error && (
        <div className="m-4 rounded-md border border-red-200 bg-red-50 p-3 text-xs text-red-700 flex items-center gap-2">
          <CircleAlert className="w-4 h-4 shrink-0" />
          {error}
        </div>
      )}

      {!loading && invalidDateCount > 0 && (
        <div className="m-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-xs text-amber-800 flex items-center gap-2">
          <CircleAlert className="w-4 h-4 shrink-0" />
          {invalidDateCount} lead(s) sem data de criação válida não entraram no período. O sistema
          não os tratou como zero.
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="bg-slate-50/90 border-b border-slate-200 text-slate-600 font-semibold">
              <th className="py-3 px-4 min-w-[190px]">Origem / campanha</th>
              <th className="py-3 px-4 min-w-[110px]">Recebidos</th>
              <th className="py-3 px-4 min-w-[130px]">Qualificados</th>
              <th className="py-3 px-4 min-w-[140px]">Qualidade</th>
              <th className="py-3 px-4 min-w-[110px]">Agendados</th>
              <th className="py-3 px-4 min-w-[190px]">Fonte e observação</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {loading && (
              <tr>
                <td colSpan={6} className="py-8 px-4 text-center text-slate-400">
                  Carregando dados reais do CRM...
                </td>
              </tr>
            )}
            {!loading && buckets.length === 0 && (
              <tr>
                <td colSpan={6} className="py-8 px-4 text-center text-slate-500">
                  Nenhum lead recebido nos últimos {WINDOW_DAYS} dias.
                </td>
              </tr>
            )}
            {!loading &&
              buckets.map((bucket) => {
                const qualityComplete = bucket.dadosCompletos === bucket.recebidos
                const quality =
                  qualityComplete && bucket.recebidos > 0
                    ? (bucket.qualificados / bucket.recebidos) * 100
                    : null
                const incomplete = bucket.recebidos - bucket.dadosCompletos

                return (
                  <tr key={bucket.key} className="hover:bg-blue-50/40 align-top">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{bucket.campanha}</div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        Origem: {bucket.origem}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-slate-700 font-semibold">{bucket.recebidos}</td>
                    <td className="py-3 px-4 text-slate-700">
                      {bucket.dadosCompletos === 0 ? (
                        <span className="text-slate-500">Sem dado</span>
                      ) : (
                        <>
                          <strong>{bucket.qualificados}</strong>
                          {incomplete > 0 && (
                            <span className="block text-[10px] text-amber-700">
                              {bucket.dadosCompletos}/{bucket.recebidos} avaliados
                            </span>
                          )}
                        </>
                      )}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-flex rounded-full px-2 py-1 text-[10px] font-semibold ${
                          quality === null
                            ? 'bg-slate-100 text-slate-600'
                            : 'bg-emerald-100 text-emerald-800'
                        }`}
                      >
                        {quality === null ? 'Sem dado' : formatPercent(quality)}
                      </span>
                      {incomplete > 0 && (
                        <div className="mt-1 text-[10px] text-amber-700">Dados incompletos</div>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-700">{bucket.agendados}</td>
                    <td className="py-3 px-4 text-[11px] text-slate-500">
                      <div>{bucket.source}</div>
                      {bucket.campanha === 'Campanha não informada' && (
                        <div className="text-amber-700">
                          Campanha vazia não foi convertida em zero.
                        </div>
                      )}
                      {incomplete > 0 && (
                        <div className="text-amber-700">
                          {incomplete} sem prestador e/ou CNPJ completo.
                        </div>
                      )}
                    </td>
                  </tr>
                )
              })}
          </tbody>
        </table>
      </div>

      <div className="px-4 py-3 border-t border-slate-100 text-[10px] text-slate-500 flex items-center gap-2">
        <Database className="w-3.5 h-3.5" />
        <span>
          Leitura pura do CRM. Nenhuma campanha, lead ou regra de qualificação é alterada por este
          painel.
        </span>
      </div>
    </section>
  )
}
