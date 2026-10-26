import React from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts'
import { TimeSeriesPoint } from '@/lib/dashboard-data'
import { TrendingUp } from 'lucide-react'

interface VendasChartCardProps {
  data: TimeSeriesPoint[]
  compareEnabled: boolean
  isLoading?: boolean
  responsavelFilter: string
}

export const VendasChartCard: React.FC<VendasChartCardProps> = ({
  data,
  compareEnabled,
  isLoading = false,
  responsavelFilter,
}) => {
  if (isLoading) {
    return (
      <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm p-4 sm:p-6 animate-pulse">
        <div className="flex justify-between items-center pb-4 border-b border-slate-100 mb-4">
          <div className="space-y-1.5">
            <div className="h-5 bg-slate-200 rounded w-64"></div>
            <div className="h-3.5 bg-slate-100 rounded w-48"></div>
          </div>
          <div className="h-4 bg-slate-200 rounded w-32"></div>
        </div>
        <div className="w-full h-72 sm:h-80 md:h-96 bg-slate-50 rounded-lg flex items-center justify-center">
          <span className="text-xs text-slate-400 font-medium">
            Carregando evolução da receita...
          </span>
        </div>
      </div>
    )
  }

  const formatCurrency = (val: number) =>
    `R$ ${val.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`

  const isZeroState =
    data.length === 0 || data.every((d) => d.vendas === 0 && d.vendasAnterior === 0)

  const subtext =
    responsavelFilter === 'all'
      ? 'Receita consolidada de vendas fechadas pela equipe comercial'
      : `Receita gerada por ${responsavelFilter}`

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm p-4 sm:p-6">
      {/* Chart Header */}{' '}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-2 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1 rounded-md bg-blue-50 text-blue-600">
              <TrendingUp className="w-4 h-4" />
            </div>
            <h2 className="text-sm sm:text-base font-semibold text-slate-900">
              Evolução da Receita de Vendas
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">{subtext}</p>
        </div>

        {/* Legend status indicators */}
        <div className="flex items-center gap-4 text-xs font-medium text-slate-600">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-1.5 rounded-full bg-blue-600" />
            <span>Período atual</span>
          </div>

          {compareEnabled && (
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-1.5 rounded-full border border-dashed border-blue-400 bg-blue-200" />
              <span className="text-slate-500">Período anterior (tracejado)</span>
            </div>
          )}
        </div>
      </div>
      {/* Main Area / Line Chart */}
      <div className="w-full h-72 sm:h-80 md:h-96 relative">
        {isZeroState && (
          <div className="absolute inset-0 z-10 flex flex-col items-center justify-center pointer-events-none text-center px-4">
            <div className="bg-white/90 backdrop-blur-xs px-4 py-3 rounded-lg border border-slate-200 shadow-sm max-w-sm">
              <p className="text-xs font-semibold text-slate-700">
                Nenhuma venda registrada no período
              </p>
              <p className="text-[11px] text-slate-500 mt-0.5">
                Conforme novas oportunidades forem marcadas como 'Fechado (ganho)', a curva de
                receita será projetada automaticamente aqui.
              </p>
            </div>
          </div>
        )}

        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
            <defs>
              <linearGradient id="vendasAreaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2563eb" stopOpacity={0.25} />
                <stop offset="95%" stopColor="#2563eb" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="vendasPrevGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#93c5fd" stopOpacity={0.15} />
                <stop offset="95%" stopColor="#93c5fd" stopOpacity={0.0} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />

            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={{ stroke: '#cbd5e1' }}
              tick={{ fill: '#64748b', fontSize: 11 }}
              dy={5}
            />

            <YAxis
              domain={[0, isZeroState ? 1000 : 'auto']}
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickFormatter={(v) => (v >= 1000 ? `${(v / 1000).toFixed(0)}k` : `${v}`)}
            />

            <Tooltip
              content={({ active, payload, label }) => {
                if (active && payload && payload.length) {
                  return (
                    <div className="bg-slate-900/95 text-white text-xs rounded-lg shadow-xl p-3 border border-slate-700 backdrop-blur-sm">
                      <div className="font-semibold text-slate-300 border-b border-slate-700/80 pb-1 mb-2">
                        Data / Horário: {label}
                      </div>
                      <div className="space-y-1.5">
                        <div className="flex items-center justify-between gap-4">
                          <span className="flex items-center gap-1.5">
                            <span className="w-2 h-2 rounded-full bg-blue-500" />
                            <span>Receita atual:</span>
                          </span>
                          <span className="font-bold text-white">
                            {formatCurrency(Number(payload[0]?.value) || 0)}
                          </span>
                        </div>

                        {compareEnabled && payload[1] && (
                          <div className="flex items-center justify-between gap-4 text-slate-300">
                            <span className="flex items-center gap-1.5">
                              <span className="w-2 h-2 rounded-full bg-blue-300" />
                              <span>Receita anterior:</span>
                            </span>
                            <span className="font-semibold text-slate-200">
                              {formatCurrency(Number(payload[1]?.value) || 0)}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  )
                }
                return null
              }}
            />

            {compareEnabled && (
              <Area
                type="monotone"
                dataKey="vendasAnterior"
                name="Período anterior"
                stroke="#93c5fd"
                strokeDasharray="4 4"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#vendasPrevGrad)"
              />
            )}

            <Area
              type="monotone"
              dataKey="vendas"
              name="Receita atual"
              stroke="#2563eb"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#vendasAreaGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-2">
        <span>Gráfico visual estilo Google Analytics 4 com comparação de tendências diárias.</span>
        <span className="font-mono text-[11px] bg-slate-100 px-2 py-0.5 rounded text-slate-700">
          Base: Negócios ganhos
        </span>
      </div>
    </div>
  )
}
