import React, { useState } from 'react'
import { PIPELINE_STAGES, PipelineDeal, PipelineStageId } from '@/lib/pipeline-data'
import { PipelineColumn } from './PipelineColumn'
import { DealModal, NewDealDialog } from './DealModal'
import { DealsService } from '@/services/deals'
import { toast } from '@/hooks/use-toast'

interface PipelineKanbanBoardProps {
  deals: PipelineDeal[]
  onUpdateDeals: (deals: PipelineDeal[]) => void
  onDealCreated?: (deal: PipelineDeal) => void
  onDealUpdated?: (deal: PipelineDeal) => void
  onDealDeleted?: (dealId: string) => void
}

export const PipelineKanbanBoard: React.FC<PipelineKanbanBoardProps> = ({
  deals,
  onUpdateDeals,
  onDealCreated,
  onDealUpdated,
  onDealDeleted,
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

  const handleDropDeal = async (dealId: string, targetStageId: string) => {
    setDraggingDealId(null)
    const validStage = PIPELINE_STAGES.find((s) => s.id === targetStageId)
    if (!validStage) return

    const targetDeal = deals.find((d) => d.id === dealId)
    if (!targetDeal) return

    if (targetDeal.stageId === targetStageId) {
      return // Já está nessa etapa
    }

    const previousStageId = targetDeal.stageId
    const previousProbability = targetDeal.probability

    // 1. Atualização otimista imediata na UI
    const optimisticDeals = deals.map((d) => {
      if (d.id === dealId) {
        return {
          ...d,
          stageId: targetStageId as PipelineStageId,
          probability:
            targetStageId === 'won' ? 100 : targetStageId === 'negotiation' ? 80 : d.probability,
        }
      }
      return d
    })
    onUpdateDeals(optimisticDeals)

    // 2. Persistência real no PocketBase com rollback se falhar
    try {
      const persistedDeal = await DealsService.updateStage(dealId, targetStageId as PipelineStageId)
      // Confirma e atualiza o deal com dados finais retornados pelo banco
      onUpdateDeals(deals.map((d) => (d.id === dealId ? persistedDeal : d)))
      toast({
        title: 'Etapa atualizada!',
        description: `"${targetDeal.title}" movido para "${validStage.title}".`,
      })
    } catch (err) {
      console.error('Falha ao atualizar etapa no banco, realizando rollback:', err)
      // Rollback otimista
      const rollbackDeals = deals.map((d) => {
        if (d.id === dealId) {
          return {
            ...d,
            stageId: previousStageId,
            probability: previousProbability,
          }
        }
        return d
      })
      onUpdateDeals(rollbackDeals)

      toast({
        title: 'Erro ao mover negócio',
        description: `Não foi possível transferir para "${validStage.title}". Alteração revertida.`,
        variant: 'destructive',
      })
    }
  }

  const handleCardClick = (deal: PipelineDeal) => {
    setSelectedDeal(deal)
    setIsModalOpen(true)
  }

  const handleQuickAdd = (stageId: string) => {
    setTargetStageForNew(stageId as PipelineStageId)
    setNewDealOpen(true)
  }

  const handleCreated = (newDeal: PipelineDeal) => {
    onDealCreated?.(newDeal)
  }

  const handleUpdated = (updatedDeal: PipelineDeal) => {
    onDealUpdated?.(updatedDeal)
    setSelectedDeal(updatedDeal)
  }

  const handleDeleted = (dealId: string) => {
    onDealDeleted?.(dealId)
    setIsModalOpen(false)
    setSelectedDeal(null)
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

      {/* Details & Edit Modal */}
      <DealModal
        deal={selectedDeal}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setSelectedDeal(null)
        }}
        onDealUpdated={handleUpdated}
        onDealDeleted={handleDeleted}
      />

      {/* New Deal Dialog */}
      <NewDealDialog
        isOpen={newDealOpen}
        onClose={() => setNewDealOpen(false)}
        initialStageId={targetStageForNew}
        onDealCreated={handleCreated}
      />
    </div>
  )
}
