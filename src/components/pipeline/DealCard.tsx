import React from 'react'
import { Clock, GripVertical, MoreVertical, Tag, User } from 'lucide-react'
import { PipelineDeal, formatCurrencyBRL, getChannelBadgeStyle } from '@/lib/pipeline-data'

interface DealCardProps {
  deal: PipelineDeal
  onDragStart: (e: React.DragEvent, dealId: string) => void
  onDragEnd: (e: React.DragEvent) => void
  onMoveToStage?: (dealId: string, targetStageId: string) => void
  isDragging?: boolean
  onClick?: () => void
}

export const DealCard: React.FC<DealCardProps> = ({
  deal,
  onDragStart,
  onDragEnd,
  isDragging,
  onClick,
}) => {
  const channelStyle = getChannelBadgeStyle(deal.channel)

  return (
    <div
      draggable
      onDragStart={(e) => onDragStart(e, deal.id)}
      onDragEnd={onDragEnd}
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          onClick?.()
        }
      }}
      className={`group relative bg-white rounded-lg border border-slate-200/90 p-3.5 shadow-sm hover:shadow-md hover:border-blue-300 transition-all cursor-grab active:cursor-grabbing select-none text-left ${
        isDragging ? 'opacity-40 scale-[0.98] ring-2 ring-blue-500 shadow-lg' : ''
      }`}
    >
      {/* Top row: Client name and quick grip handle */}
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <h4 className="font-semibold text-slate-900 text-sm leading-snug group-hover:text-blue-600 transition-colors truncate">
            {deal.title}
          </h4>
          <p
            className="text-xs text-slate-500 truncate flex items-center gap-1 mt-0.5"
            title={
              deal.contactInfo ? `${deal.contactName} (${deal.contactInfo})` : deal.contactName
            }
          >
            <User className="w-3 h-3 text-slate-400 shrink-0" />
            <span className="truncate">{deal.contactName}</span>
          </p>
        </div>
        <div className="text-slate-300 group-hover:text-slate-400 transition-colors shrink-0">
          <GripVertical className="w-4 h-4" />
        </div>
      </div>

      {/* Middle: Deal value in R$ highlighted */}
      <div className="mt-2.5 flex items-baseline justify-between">
        <div>
          <span className="text-xs text-slate-400 font-medium">Valor:</span>
          <div className="text-sm font-bold text-slate-900 tracking-tight">
            {formatCurrencyBRL(deal.value)}
          </div>
        </div>
        <div className="text-right">
          <span className="text-[10px] text-slate-400 uppercase font-semibold">Prob.</span>
          <div className="text-xs font-semibold text-slate-600">{deal.probability}%</div>
        </div>
      </div>

      {/* Channel / Origem tag */}
      <div className="mt-2.5 flex flex-wrap items-center gap-1.5">
        <span
          className={`px-2 py-0.5 text-[11px] rounded font-medium border ${channelStyle.bg} ${channelStyle.text} ${channelStyle.border}`}
        >
          {deal.channel}
        </span>
        {deal.tags && deal.tags.length > 0 && (
          <span className="px-1.5 py-0.5 text-[10px] rounded bg-slate-100 text-slate-600 border border-slate-200/60 truncate max-w-[120px]">
            {deal.tags[0]}
          </span>
        )}
      </div>

      {/* Bottom bar: Responsible person (avatar) and days in stage */}
      <div className="mt-3 pt-2.5 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
        <div className="flex items-center gap-1.5" title={`Responsável: ${deal.owner.name}`}>
          <div
            className={`w-6 h-6 rounded-full ${deal.owner.avatarBg} text-white flex items-center justify-center text-[10px] font-bold shadow-xs`}
          >
            {deal.owner.initials}
          </div>
          <span className="text-[11px] text-slate-600 font-medium truncate max-w-[90px]">
            {deal.owner.name.split(' ')[0]}
          </span>
        </div>

        <div
          className="flex items-center gap-1 text-[11px] text-slate-400"
          title={`No estágio há ${deal.daysInStage} dias`}
        >
          <Clock className="w-3 h-3 text-slate-400" />
          <span>{deal.daysInStage}d</span>
        </div>
      </div>
    </div>
  )
}
