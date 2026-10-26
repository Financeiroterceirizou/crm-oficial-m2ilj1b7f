import React from 'react'
import { useNavigate } from 'react-router-dom'
import {
  ArrowDownRight,
  ArrowUpRight,
  CheckCircle2,
  ChevronRight,
  ExternalLink,
  Info,
} from 'lucide-react'
import { LineChart, Line, ResponsiveContainer } from 'recharts'
import { KpiCardData } from '@/lib/dashboard-data'

interface GaKpiCardsGridProps {
  cards: KpiCardData[]
  selectedMetric: 'vendas' | 'clientes' | 'conversao' | 'ticketMedio'
  onSelectMetric: (metric: 'vendas' | 'clientes' | 'conversao' | 'ticketMedio') => void
  compareEnabled: boolean
  isLoading?: boolean
  onNavigateToVendas?: () => void
}

export const GaKpiCardsGrid: React.FC<GaKpiCardsGridProps> = ({
  cards,
  selectedMetric,
  onSelectMetric,
  compareEnabled,
  isLoading = false,
  onNavigateToVendas,
}) => {
  const navigate = useNavigate()
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className="bg-white rounded-xl p-4 sm:p-5 border border-slate-200/90 shadow-sm animate-pulse space-y-3"
          >
            <div className="flex justify-between items-center">
              <div className="h-4 bg-slate-200 rounded w-24"></div>
              <div className="h-2 w-2 rounded-full bg-slate-200"></div>
            </div>
            <div className="h-8 bg-slate-200 rounded w-36 my-2"></div>
            <div className="pt-2 border-t border-slate-100 flex justify-between items-center">
              <div className="h-4 bg-slate-200 rounded w-16"></div>
              <div className="h-9 w-24 bg-slate-100 rounded"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => {
        const isSelected = selectedMetric === card.metricKey
        const isVendas = card.metricKey === 'vendas'
        const isClientes = card.metricKey === 'clientes'
        const isVendasOrClientes = isVendas || isClientes

        const handleClick = (e: React.MouseEvent) => {
          onSelectMetric(card.metricKey)
        }

        const handleDoubleClickOrAction = (e: React.MouseEvent) => {
          if (isVendas) {
            e.stopPropagation()
            if (onNavigateToVendas) {
              onNavigateToVendas()
            } else {
              navigate('/vendas')
            }
          } else if (isClientes) {
            e.stopPropagation()
            navigate('/aquisicao')
          }
        }

        return (
          <div
            key={card.id}
            onClick={handleClick}
            className={`group relative bg-white rounded-xl p-4 sm:p-5 cursor-pointer transition-all duration-200 border text-left ${
              isSelected
                ? 'border-blue-500 shadow-md ring-2 ring-blue-500/20'
                : 'border-slate-200/90 shadow-sm hover:border-slate-300 hover:shadow'
            } ${card.recommended ? 'bg-gradient-to-b from-white to-slate-50/50' : ''} ${
              isVendas ? 'hover:border-blue-400 hover:ring-1 hover:ring-blue-400/30' : ''
            }`}
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
                    {isVendas ? 'Ver relatório completo' : 'Métrica em destaque'}
                  </span>
                )}
              </div>

              {/* Status active indicator dot & shortcut link */}
              <div className="flex items-center gap-1.5">
                {isVendas && (
                  <button
                    onClick={handleDoubleClickOrAction}
                    title="Abrir tela de Vendas"
                    className="p-1 rounded text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>
                )}
                {isClientes && (
                  <button
                    onClick={handleDoubleClickOrAction}
                    title="Abrir funil de Aquisição"
                    className="p-1 rounded text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 transition-colors"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </button>
                )}
                <div
                  className={`w-2 h-2 rounded-full transition-colors ${
                    isSelected ? 'bg-blue-600' : 'bg-transparent'
                  }`}
                />
              </div>
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

            {/* Action hint for Vendas */}
            {isVendas && (
              <div
                onClick={handleDoubleClickOrAction}
                className="mt-1 mb-2 inline-flex items-center gap-1 text-[11px] font-medium text-blue-600 hover:text-blue-800 transition-colors"
              >
                <span>Acessar tela de Vendas</span>
                <ChevronRight className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
              </div>
            )}

            {/* Bottom row: Delta & Sparkline side by side */}
            <div className="pt-2 border-t border-slate-100 flex items-center justify-between gap-2">
              {/* Delta badge */}
              <div className="flex flex-col">
                {card.currentValueRaw === 0 && card.deltaPercent === 0 ? (
                  <div className="inline-flex items-center gap-1 text-xs font-semibold text-slate-500">
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
                    <span>0,0%</span>
                  </div>
                ) : (
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
                )}
                {compareEnabled && (
                  <span className="text-[10px] text-slate-400 mt-0.5 leading-none">
                    vs. ant: {card.previousValueFormatted}
                  </span>
                )}
              </div>
              {/* Mini Sparkline in pure GA4 style */}
              <div className="w-24 h-9 sm:w-28 sm:h-10">
                {card.sparkline && card.sparkline.some((s) => s.val > 0) ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={card.sparkline}>
                      <Line
                        type="monotone"
                        dataKey="val"
                        stroke={card.isPositive ? '#059669' : '#e11d48'}
                        strokeWidth={1.8}
                        dot={false}
                        isAnimationActive={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <div className="w-full h-[1.5px] bg-slate-200 rounded-full" />
                  </div>
                )}
              </div>{' '}
            </div>
          </div>
        )
      })}
    </div>
  )
}
