import React from 'react'
import { ArrowUpRight, CheckCircle2, DollarSign, Percent, TrendingUp } from 'lucide-react'
import { PipelineDeal, formatCurrencyBRL } from '@/lib/pipeline-data'
import { DatePeriod, COMPARISON_LABELS } from '@/lib/dashboard-data'

interface PipelineSummaryProps {
  deals: PipelineDeal[]
  period: DatePeriod
}

export const PipelineSummary: React.FC<PipelineSummaryProps> = ({ deals, period }) => {
  // Cálculos baseados nos deals atuais
  const openDeals = deals.filter((d) => d.stageId !== 'won')
  const wonDeals = deals.filter((d) => d.stageId === 'won')

  const totalOpenValue = openDeals.reduce((acc, d) => acc + d.value, 0)
  const totalWonValue = wonDeals.reduce((acc, d) => acc + d.value, 0)
  const totalAllValue = deals.reduce((acc, d) => acc + d.value, 0)

  const countTotal = deals.length
  const countWon = wonDeals.length
  const countOpen = openDeals.length

  const conversionRate = countTotal > 0 ? (countWon / countTotal) * 100 : 0
  const avgTicket = countTotal > 0 ? totalAllValue / countTotal : 0

  const compLabel = COMPARISON_LABELS[period]

  const metrics = [
    {
      id: 'open-pipeline',
      title: 'Total em aberto no pipeline',
      subtitle: `${countOpen} oportunidades em andamento`,
      value: formatCurrencyBRL(totalOpenValue),
      icon: DollarSign,
      deltaPercent: '+18,4%',
      isPositive: true,
      compDesc: `${compLabel}: R$ ${(totalOpenValue * 0.84).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      accentColor: 'text-blue-600 bg-blue-50',
    },
    {
      id: 'won-deals',
      title: 'Negócios fechados (ganhos)',
      subtitle: `${formatCurrencyBRL(totalWonValue)} faturados`,
      value: `${countWon} contratos`,
      icon: CheckCircle2,
      deltaPercent: '+25,0%',
      isPositive: true,
      compDesc: `${compLabel}: ${Math.max(1, countWon - 1)} fechamentos`,
      accentColor: 'text-emerald-600 bg-emerald-50',
    },
    {
      id: 'ticket-medio',
      title: 'Ticket médio das propostas',
      subtitle: 'Média ponderada por oportunidade',
      value: formatCurrencyBRL(avgTicket),
      icon: TrendingUp,
      deltaPercent: '+4,8%',
      isPositive: true,
      compDesc: `${compLabel}: R$ ${(avgTicket * 0.95).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      accentColor: 'text-purple-600 bg-purple-50',
    },
    {
      id: 'conversion-rate',
      title: 'Taxa de conversão (Lead → Ganho)',
      subtitle: 'Eficiência de passagem pelo funil',
      value: `${conversionRate.toFixed(1).replace('.', ',')}%`,
      icon: Percent,
      deltaPercent: '+2,3 p.p.',
      isPositive: true,
      compDesc: `${compLabel}: ${Math.max(1, conversionRate - 2.3)
        .toFixed(1)
        .replace('.', ',')}%`,
      accentColor: 'text-amber-600 bg-amber-50',
    },
  ]

  return (
    <section aria-label="Resumo do Pipeline de Aquisição">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((m) => {
          const Icon = m.icon
          return (
            <div
              key={m.id}
              className="bg-white rounded-xl border border-slate-200/90 p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between relative overflow-hidden"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 truncate block">
                    {m.title}
                  </span>
                  <div className="mt-1.5 flex items-baseline gap-2">
                    <span className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
                      {m.value}
                    </span>
                  </div>
                </div>
                <div className={`p-2 rounded-lg shrink-0 ${m.accentColor}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>

              <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs">
                <span className="text-slate-500 text-[11px] truncate" title={m.subtitle}>
                  {m.subtitle}
                </span>
                <span className="inline-flex items-center gap-0.5 font-semibold text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded text-[10px]">
                  <ArrowUpRight className="w-3 h-3" />
                  {m.deltaPercent}
                </span>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
