import React, { useState } from 'react'
import { PIPELINE_STAGES, PipelineDeal, PipelineStageId } from '@/lib/pipeline-data'
import { PipelineColumn } from './PipelineColumn'
import { DealModal, NewDealDialog } from './DealModal'
import { toast } from '@/hooks/use-toast'

interface PipelineKanbanBoardProps {
  deals: PipelineDeal[]
  onUpdateDeals: (deals: PipelineDeal[]) => void
}

export const PipelineKanbanBoard: React.FC<PipelineKanbanBoardProps> = ({
  deals,
  onUpdateDeals,
}) => {
  const [draggingDealId, setDraggingDealId] = useState<string | null>(null)
  const [selectedDeal, setSelectedDeal] = useState<PipelineDeal | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [newDealOpen, setNewDealOpen] = useState(false)
  const [targetStageForNew, setTargetStageForNew] = useState<PipelineStageId>('new_leads')

  const handleDragStart = (e: React.DragEvent, dealId: string) => {
    setDraggingDealId(dealId)
    e.dataTransfer.setData('text/plain', dealId)
    e.dataTransfer.effectAllowed = 'move'
  }

  const handleDragEnd = () => {
    setDraggingDealId(null)
  }

  const handleDropDeal = (dealId: string, targetStageId: string) => {
    setDraggingDealId(null)
    const validStage = PIPELINE_STAGES.find((s) => s.id === targetStageId)
    if (!validStage) return

    const targetDeal = deals.find((d) => d.id === dealId)
    if (!targetDeal) return

    if (targetDeal.stageId === targetStageId) {
      return // Já está nessa etapa
    }

    const previousStageName = PIPELINE_STAGES.find((s) => s.id === targetDeal.stageId)?.title

    const updatedDeals = deals.map((d) => {
      if (d.id === dealId) {
        return {
          ...d,
          stageId: targetStageId as PipelineStageId,
          probability: targetStageId === 'won' ? 100 : d.probability,
        }
      }
      return d
    })

    onUpdateDeals(updatedDeals)

    toast({
      title: 'Etapa atualizada!',
      description: `"${targetDeal.title}" movido para "${validStage.title}".`,
    })
  }

  const handleCardClick = (deal: PipelineDeal) => {
    setSelectedDeal(deal)
    setIsModalOpen(true)
  }

  const handleQuickAdd = (stageId: string) => {
    setTargetStageForNew(stageId as PipelineStageId)
    setNewDealOpen(true)
  }

  const handleAddNewDeal = (newDeal: PipelineDeal) => {
    onUpdateDeals([newDeal, ...deals])
    toast({
      title: 'Oportunidade adicionada!',
      description: `"${newDeal.title}" cadastrado com sucesso no pipeline.`,
    })
  }

  const handleDeleteDeal = (dealId: string) => {
    const remaining = deals.filter((d) => d.id !== dealId)
    onUpdateDeals(remaining)
    toast({
      title: 'Oportunidade removida',
      description: 'O negócio foi excluído do pipeline.',
    })
  }

  return (
    <div className="relative">
      {/* Board Scroll Container (Horizontal scroll on mobile/tablet) */}
      <div className="overflow-x-auto pb-6 pt-1 px-1 -mx-1">
        <div className="inline-flex gap-4 min-w-full items-start">
          {PIPELINE_STAGES.map((stage) => {
            const stageDeals = deals.filter((d) => d.stageId === stage.id)
            return (
              <PipelineColumn
                key={stage.id}
                stage={stage}
                deals={stageDeals}
                onDragStart={handleDragStart}
                onDragEnd={handleDragEnd}
                onDropDeal={handleDropDeal}
                draggingDealId={draggingDealId}
                onCardClick={handleCardClick}
                onQuickAddDeal={handleQuickAdd}
              />
            )
          })}
        </div>
      </div>

      {/* Details Modal */}
      <DealModal
        deal={selectedDeal}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedDeal(null)
        }}
        onDeleteDeal={handleDeleteDeal}
      />

      {/* New Deal Dialog */}
      <NewDealDialog
        isOpen={newDealOpen}
        onClose={() => setNewDealOpen(false)}
        initialStageId={targetStageForNew}
        onAddDeal={handleAddNewDeal}
      />
    </div>
  )
}
