import React from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { TimeSeriesPoint } from '@/lib/dashboard-data'

interface GaMainChartCardProps {
  data: TimeSeriesPoint[]
  selectedMetric: 'vendas' | 'clientes' | 'conversao' | 'ticketMedio'
  compareEnabled: boolean
}

export const GaMainChartCard: React.FC<GaMainChartCardProps> = ({
  data,
  selectedMetric,
  compareEnabled,
}) => {
  const metricConfig = {
    vendas: {
      title: 'Vendas ao longo do tempo (Receita total)',
      primaryLabel: 'Vendas (período atual)',
      primaryKey: 'vendas',
      prevLabel: 'Vendas (período anterior)',
      prevKey: 'vendasAnterior',
      unit: 'R$',
      color: '#2563eb', // blue
      colorPrev: '#93c5fd', // soft blue
      formatter: (val: number) =>
        `R$ ${val.toLocaleString('pt-BR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`,
    },
    clientes: {
      title: 'Novos Clientes adquiridos ao longo do tempo',
      primaryLabel: 'Novos Clientes (período atual)',
      primaryKey: 'clientes',
      prevLabel: 'Novos Clientes (período anterior)',
      prevKey: 'clientesAnterior',
      unit: '',
      color: '#0d9488', // teal/greenish like GA4 secondary
      colorPrev: '#99f6e4',
      formatter: (val: number) => `${val.toLocaleString('pt-BR')} clientes`,
    },
    conversao: {
      title: 'Taxa de Conversão de Oportunidades',
      primaryLabel: 'Conversão atual (%)',
      primaryKey: 'conversao',
      prevLabel: 'Conversão anterior (%)',
      prevKey: 'conversao',
      unit: '%',
      color: '#8b5cf6',
      colorPrev: '#c4b5fd',
      formatter: (val: number) => `${val}%`,
    },
    ticketMedio: {
      title: 'Ticket Médio de Contratos',
      primaryLabel: 'Ticket Médio',
      primaryKey: 'vendas',
      prevLabel: 'Ticket Médio anterior',
      prevKey: 'vendasAnterior',
      unit: 'R$',
      color: '#f59e0b',
      colorPrev: '#fde68a',
      formatter: (val: number) => `R$ ${val}`,
    },
  }[selectedMetric]

  return (
    <div className="bg-white rounded-xl border border-slate-200/90 shadow-sm p-4 sm:p-6">
      {/* Chart Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-2 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
            <h2 className="text-sm sm:text-base font-semibold text-slate-900">
              {metricConfig.title}
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Gráfico de linhas interativo com grade e comparação de tendências diárias
          </p>
        </div>

        {/* Legend status indicators */}
        <div className="flex items-center gap-4 text-xs font-medium text-slate-600">
          <div className="flex items-center gap-1.5">
            <span
              className="w-3 h-1.5 rounded-full"
              style={{ backgroundColor: metricConfig.color }}
            />
            <span>Período atual</span>
          </div>

          {compareEnabled && (
            <div className="flex items-center gap-1.5">
              <span
                className="w-3 h-1.5 rounded-full border border-dashed"
                style={{ backgroundColor: metricConfig.colorPrev }}
              />
              <span className="text-slate-500">Período comparado</span>
            </div>
          )}
        </div>
      </div>

      {/* Main Area / Line Chart */}
      <div className="w-full h-72 sm:h-80 md:h-96">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id="primaryAreaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={metricConfig.color} stopOpacity={0.25} />
                <stop offset="95%" stopColor={metricConfig.color} stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="prevAreaGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={metricConfig.colorPrev} stopOpacity={0.15} />
                <stop offset="95%" stopColor={metricConfig.colorPrev} stopOpacity={0.0} />
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
              tickLine={false}
              axisLine={false}
              tick={{ fill: '#64748b', fontSize: 11 }}
              tickFormatter={(v) =>
                selectedMetric === 'vendas'
                  ? v >= 1000
                    ? `${(v / 1000).toFixed(0)}k`
                    : `${v}`
                  : `${v}`
              }
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
                            <span
                              className="w-2 h-2 rounded-full"
                              style={{ backgroundColor: metricConfig.color }}
                            />
                            <span>{metricConfig.primaryLabel}:</span>
                          </span>
                          <span className="font-bold text-white">
                            {metricConfig.formatter(Number(payload[0]?.value) || 0)}
                          </span>
                        </div>

                        {compareEnabled && payload[1] && (
                          <div className="flex items-center justify-between gap-4 text-slate-300">
                            <span className="flex items-center gap-1.5">
                              <span
                                className="w-2 h-2 rounded-full"
                                style={{ backgroundColor: metricConfig.colorPrev }}
                              />
                              <span>{metricConfig.prevLabel}:</span>
                            </span>
                            <span className="font-semibold text-slate-200">
                              {metricConfig.formatter(Number(payload[1]?.value) || 0)}
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
                dataKey={metricConfig.prevKey}
                name={metricConfig.prevLabel}
                stroke={metricConfig.colorPrev}
                strokeDasharray="4 4"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#prevAreaGrad)"
              />
            )}

            <Area
              type="monotone"
              dataKey={metricConfig.primaryKey}
              name={metricConfig.primaryLabel}
              stroke={metricConfig.color}
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#primaryAreaGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Dual Series secondary view: Vendas + Clientes correlation badge */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-2">
        <span>
          Visualização padrão do Analytics: série temporal comparativa com amortecimento cúbico.
        </span>
        <span className="font-mono text-[11px] bg-slate-100 px-2 py-0.5 rounded text-slate-700">
          Amostra 100% dos eventos
        </span>
      </div>
    </div>
  )
}
