import React, { useState } from 'react'
import { PipelineDeal, PipelineStageConfig, formatCurrencyBRL } from '@/lib/pipeline-data'
import { DealCard } from './DealCard'
import { Plus } from 'lucide-react'

interface PipelineColumnProps {
  stage: PipelineStageConfig
  deals: PipelineDeal[]
  onDragStart: (e: React.DragEvent, dealId: string) => void
  onDragEnd: (e: React.DragEvent) => void
  onDropDeal: (dealId: string, targetStageId: string) => void
  draggingDealId: string | null
  onCardClick?: (deal: PipelineDeal) => void
  onQuickAddDeal?: (stageId: string) => void
}

export const PipelineColumn: React.FC<PipelineColumnProps> = ({
  stage,
  deals,
  onDragStart,
  onDragEnd,
  onDropDeal,
  draggingDealId,
  onCardClick,
  onQuickAddDeal,
}) => {
  const [isDragOver, setIsDragOver] = useState(false)

  const totalValue = deals.reduce((acc, d) => acc + d.value, 0)
  const count = deals.length

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    if (!isDragOver) setIsDragOver(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    // Só desativa se o leave não for para um filho
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX
    const y = e.clientY
    if (x < rect.left || x >= rect.right || y < rect.top || y >= rect.bottom) {
      setIsDragOver(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    const dealId = e.dataTransfer.getData('text/plain') || draggingDealId
    if (dealId) {
      onDropDeal(dealId, stage.id)
    }
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`flex flex-col flex-shrink-0 w-80 bg-slate-50/90 rounded-xl border transition-all ${
        isDragOver ? 'border-blue-500 bg-blue-50/40 ring-2 ring-blue-500/20' : 'border-slate-200/90'
      }`}
    >
      {/* Column Header (Nome da etapa, contagem e soma de valor R$) */}
      <div
        className={`p-3.5 bg-white rounded-t-xl border-b border-slate-200/80 border-t-4 ${stage.accentBorder}`}
      >
        <div className="flex items-center justify-between gap-2">
          <div className="flex items-center gap-2 min-w-0">
            <span className={`w-2.5 h-2.5 rounded-full ${stage.color} shrink-0`} />
            <h3 className="font-semibold text-slate-900 text-sm truncate">{stage.title}</h3>
          </div>

          <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-slate-100 text-slate-700 border border-slate-200">
            {count}
          </span>
        </div>

        <div className="mt-2 flex items-center justify-between text-xs">
          <span className="text-slate-400 font-medium">Total da etapa:</span>
          <span className="font-bold text-slate-800 font-mono text-xs">
            {formatCurrencyBRL(totalValue)}
          </span>
        </div>
      </div>

      {/* Cards List / Drop Target */}
      <div className="p-2.5 flex-1 flex flex-col gap-2.5 min-h-[380px] overflow-y-auto max-h-[calc(100vh-320px)] scrollbar-thin">
        {deals.map((deal) => (
          <DealCard
            key={deal.id}
            deal={deal}
            onDragStart={onDragStart}
            onDragEnd={onDragEnd}
            isDragging={draggingDealId === deal.id}
            onClick={() => onCardClick?.(deal)}
          />
        ))}

        {deals.length === 0 && (
          <div
            className={`flex-1 flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-lg text-center transition-colors ${
              isDragOver
                ? 'border-blue-400 bg-blue-50/60 text-blue-700'
                : 'border-slate-200 text-slate-400 bg-white/40'
            }`}
          >
            <p className="text-xs font-medium">Nenhum negócio nesta etapa</p>
            <p className="text-[11px] text-slate-400 mt-0.5">Arraste um cartão para cá</p>
          </div>
        )}

        {/* Quick Add Button */}
        {onQuickAddDeal && (
          <button
            onClick={() => onQuickAddDeal(stage.id)}
            className="w-full mt-1 py-2 px-3 border border-dashed border-slate-300 hover:border-blue-400 hover:bg-blue-50/50 rounded-lg text-xs font-medium text-slate-500 hover:text-blue-600 flex items-center justify-center gap-1.5 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Adicionar oportunidade</span>
          </button>
        )}
      </div>
    </div>
  )
}
