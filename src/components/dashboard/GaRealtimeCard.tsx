import React from 'react'
import { Activity, MapPin, Users2, TrendingUp } from 'lucide-react'
import { RealtimeData } from '@/lib/dashboard-data'

interface GaRealtimeCardProps {
  realtime: RealtimeData
}

export const GaRealtimeCard: React.FC<GaRealtimeCardProps> = ({ realtime }) => {
  return (
    <div className="bg-gradient-to-br from-slate-900 to-[#1e293b] text-white rounded-xl border border-slate-800 shadow-lg p-5">
      {/* Top Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
            Tempo Real
          </span>
        </div>
        <span className="text-[11px] text-slate-400">Últimos 30 minutos</span>
      </div>

      {/* Big Counter */}
      <div className="py-4 flex items-baseline gap-3">
        <span className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white font-mono">
          {realtime.usersLast30Min}
        </span>
        <div className="flex flex-col">
          <span className="text-xs font-semibold text-slate-200">Leads ativos navegando</span>
          <span className="text-[11px] text-emerald-400 flex items-center gap-1">
            <TrendingUp className="w-3 h-3" />
            +14% vs. mesma hora ontem
          </span>
        </div>
      </div>

      {/* Mini real-time horizontal bar graph */}
      <div className="space-y-1 mb-5">
        <div className="text-[11px] font-medium text-slate-300">
          Minuto a minuto (volume recente)
        </div>
        <div className="flex items-end gap-1 h-10 pt-1">
          {[4, 7, 5, 8, 12, 9, 6, 11, 14, 18, 15, 12, 16, 20, 22, 19, 24, 21, 18, 23].map(
            (val, idx) => (
              <div
                key={idx}
                className="flex-1 bg-blue-500/80 hover:bg-blue-400 rounded-t transition-all"
                style={{ height: `${(val / 25) * 100}%` }}
                title={`${val} ações`}
              />
            ),
          )}
        </div>
      </div>

      {/* Grid of Top Pages and Top Cities */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-3 border-t border-slate-800 text-xs">
        {/* Active Landing Pages */}
        <div>
          <div className="flex items-center gap-1.5 text-slate-400 text-[11px] font-semibold uppercase tracking-wider mb-2">
            <Users2 className="w-3.5 h-3.5" />
            <span>Páginas em Conversão</span>
          </div>
          <div className="space-y-1.5">
            {realtime.activePages.map((p, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between text-slate-300 hover:text-white"
              >
                <span className="truncate max-w-[130px] font-mono text-[11px]">{p.path}</span>
                <span className="font-mono text-emerald-400 font-semibold">{p.count}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Top Cities */}
        <div>
          <div className="flex items-center gap-1.5 text-slate-400 text-[11px] font-semibold uppercase tracking-wider mb-2">
            <MapPin className="w-3.5 h-3.5" />
            <span>Cidades Ativas</span>
          </div>
          <div className="space-y-1.5">
            {realtime.topCities.map((c, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between text-slate-300 hover:text-white"
              >
                <span className="truncate max-w-[130px]">{c.city}</span>
                <span className="font-mono text-blue-400 font-semibold">{c.active}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
