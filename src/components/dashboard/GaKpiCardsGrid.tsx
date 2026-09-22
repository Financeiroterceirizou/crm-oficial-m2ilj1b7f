import React from 'react'
import { ArrowDownRight, ArrowUpRight, CheckCircle2, Info } from 'lucide-react'
import { LineChart, Line, ResponsiveContainer } from 'recharts'
import { KpiCardData } from '@/lib/dashboard-data'

interface GaKpiCardsGridProps {
  cards: KpiCardData[]
  selectedMetric: 'vendas' | 'clientes' | 'conversao' | 'ticketMedio'
  onSelectMetric: (metric: 'vendas' | 'clientes' | 'conversao' | 'ticketMedio') => void
  compareEnabled: boolean
}

export const GaKpiCardsGrid: React.FC<GaKpiCardsGridProps> = ({
  cards,
  selectedMetric,
  onSelectMetric,
  compareEnabled,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => {
        const isSelected = selectedMetric === card.metricKey
        const isVendasOrClientes = card.metricKey === 'vendas' || card.metricKey === 'clientes'

        return (
          <div
            key={card.id}
            onClick={() => onSelectMetric(card.metricKey)}
            className={`group relative bg-white rounded-xl p-4 sm:p-5 cursor-pointer transition-all duration-200 border text-left ${
              isSelected
                ? 'border-blue-500 shadow-md ring-2 ring-blue-500/20'
                : 'border-slate-200/90 shadow-sm hover:border-slate-300 hover:shadow'
            } ${card.recommended ? 'bg-gradient-to-b from-white to-slate-50/50' : ''}`}
          >
            {/* Top row: Title + Recommended tag */}
            <div className="flex items-start justify-between gap-2 mb-2">
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <h3 className="text-xs sm:text-sm font-medium text-slate-600 group-hover:text-slate-900 transition-colors">
                    {card.title}
                  </h3>
                  <div
                    title={card.benchmarkDesc}
                    className="text-slate-400 hover:text-slate-600 cursor-help"
                  >
                    <Info className="w-3 h-3" />
                  </div>
                </div>

                {card.recommended && (
                  <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded w-fit mt-1 border border-blue-200/70">
                    <CheckCircle2 className="w-2.5 h-2.5" />
                    Métrica em destaque
                  </span>
                )}
              </div>

              {/* Status active indicator dot */}
              <div
                className={`w-2 h-2 rounded-full transition-colors ${
                  isSelected ? 'bg-blue-600' : 'bg-transparent'
                }`}
              />
            </div>

            {/* Middle row: Big Value */}
            <div className="my-2">
              <div
                className={`text-2xl sm:text-3xl font-bold tracking-tight ${
                  isVendasOrClientes ? 'text-slate-900' : 'text-slate-800'
                }`}
              >
                {card.currentValueFormatted}
              </div>
            </div>

            {/* Bottom row: Delta & Sparkline side by side */}
            <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
              {/* Delta badge */}
              <div className="flex flex-col">
                <div
                  className={`inline-flex items-center gap-0.5 text-xs font-semibold ${
                    card.isPositive ? 'text-emerald-700' : 'text-rose-700'
                  }`}
                >
                  {card.isPositive ? (
                    <ArrowUpRight className="w-4 h-4 stroke-[2.5]" />
                  ) : (
                    <ArrowDownRight className="w-4 h-4 stroke-[2.5]" />
                  )}
                  <span>
                    {card.isPositive ? '+' : ''}
                    {card.deltaPercent.toFixed(1)}%
                  </span>
                </div>
                {compareEnabled && (
                  <span className="text-[10px] text-slate-400 mt-0.5 leading-none">
                    vs. ant: {card.previousValueFormatted}
                  </span>
                )}
              </div>

              {/* Mini Sparkline in pure GA4 style */}
              <div className="w-24 h-9 sm:w-28 sm:h-10">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={card.sparkline}>
                    <Line
                      type="monotone"
                      dataKey="val"
                      stroke={isSelected ? '#2563eb' : card.isPositive ? '#059669' : '#e11d48'}
                      strokeWidth={1.8}
                      dot={false}
                      isAnimationActive={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
