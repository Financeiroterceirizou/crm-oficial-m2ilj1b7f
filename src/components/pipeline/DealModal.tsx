import React, { useState } from 'react'
import { Calendar, CheckCircle2, DollarSign, Plus, Sparkles, Tag, User, X } from 'lucide-react'
import {
  PipelineDeal,
  PipelineStageId,
  PIPELINE_STAGES,
  formatCurrencyBRL,
  getChannelBadgeStyle,
} from '@/lib/pipeline-data'

interface DealModalProps {
  deal: PipelineDeal | null
  isOpen: boolean
  onClose: () => void
  onSaveDeal?: (deal: PipelineDeal) => void
  onDeleteDeal?: (dealId: string) => void
}

export const DealModal: React.FC<DealModalProps> = ({
  deal,
  isOpen,
  onClose,
  onSaveDeal,
  onDeleteDeal,
}) => {
  if (!isOpen || !deal) return null

  const stage = PIPELINE_STAGES.find((s) => s.id === deal.stageId)
  const channelStyle = getChannelBadgeStyle(deal.channel)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in">
      <div
        className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-lg w-full overflow-hidden animate-in zoom-in-95 duration-150"
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-200 flex items-start justify-between bg-slate-50/70">
          <div>
            <div className="flex items-center gap-2">
              <span
                className={`px-2 py-0.5 text-xs font-semibold rounded-full border ${stage?.badgeBg} ${stage?.badgeText}`}
              >
                {stage?.title}
              </span>
              <span
                className={`px-2 py-0.5 text-xs rounded font-medium border ${channelStyle.bg} ${channelStyle.text} ${channelStyle.border}`}
              >
                {deal.channel}
              </span>
            </div>
            <h3 className="text-lg font-bold text-slate-900 mt-2">{deal.title}</h3>
            <p className="text-xs text-slate-500 mt-0.5">Contato: {deal.contactName}</p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200/50"
            aria-label="Fechar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-4 sm:p-5 space-y-4 text-xs sm:text-sm">
          <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3.5 rounded-lg border border-slate-200/80">
            <div>
              <span className="text-slate-500 text-xs block">Valor da Oportunidade</span>
              <span className="text-lg font-bold text-slate-900">
                {formatCurrencyBRL(deal.value)}
              </span>
            </div>
            <div>
              <span className="text-slate-500 text-xs block">Probabilidade</span>
              <span className="text-lg font-bold text-blue-600">{deal.probability}%</span>
            </div>
          </div>

          <div className="space-y-2 text-xs">
            <div className="flex items-center justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500 flex items-center gap-1.5">
                <User className="w-3.5 h-3.5 text-slate-400" />
                Responsável comercial
              </span>
              <div className="flex items-center gap-2 font-medium text-slate-800">
                <div
                  className={`w-5 h-5 rounded-full ${deal.owner.avatarBg} text-white flex items-center justify-center text-[9px] font-bold`}
                >
                  {deal.owner.initials}
                </div>
                <span>{deal.owner.name}</span>
              </div>
            </div>

            <div className="flex items-center justify-between py-1.5 border-b border-slate-100">
              <span className="text-slate-500 flex items-center gap-1.5">
                <Calendar className="w-3.5 h-3.5 text-slate-400" />
                Criado em / Tempo na etapa
              </span>
              <span className="font-medium text-slate-800">
                {deal.createdAt} • {deal.daysInStage} dias nesta etapa
              </span>
            </div>

            {deal.tags && deal.tags.length > 0 && (
              <div className="pt-2">
                <span className="text-slate-500 text-xs block mb-1.5">Tags associadas:</span>
                <div className="flex flex-wrap gap-1.5">
                  {deal.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* GA4 Attribution note */}
          <div className="bg-amber-50/70 border border-amber-200/80 rounded-lg p-3 flex items-start gap-2.5 text-xs text-amber-900">
            <Sparkles className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold">Atribuição GA4 de Primeira Interação</p>
              <p className="text-amber-800/90 mt-0.5 text-[11px] leading-relaxed">
                Origem mapeada como <strong>{deal.channel}</strong> através da sessão inicial.
                Métrica correlacionada ao relatório de canais de aquisição.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between">
          {onDeleteDeal ? (
            <button
              onClick={() => {
                onDeleteDeal(deal.id)
                onClose()
              }}
              className="text-xs text-red-600 hover:text-red-700 font-medium px-2 py-1 rounded hover:bg-red-50"
            >
              Excluir negócio
            </button>
          ) : (
            <div />
          )}

          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white rounded-md text-xs font-medium transition-colors"
          >
            Fechar detalhes
          </button>
        </div>
      </div>
    </div>
  )
}

interface NewDealDialogProps {
  isOpen: boolean
  onClose: () => void
  initialStageId?: PipelineStageId
  onAddDeal: (deal: PipelineDeal) => void
}

export const NewDealDialog: React.FC<NewDealDialogProps> = ({
  isOpen,
  onClose,
  initialStageId = 'new_leads',
  onAddDeal,
}) => {
  const [title, setTitle] = useState('')
  const [contactName, setContactName] = useState('')
  const [value, setValue] = useState('4500')
  const [channel, setChannel] = useState('Meta Ads')
  const [stageId, setStageId] = useState<PipelineStageId>(initialStageId)
  const [ownerName, setOwnerName] = useState('Lucas Silveira')

  if (!isOpen) return null

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) return

    const numValue = Number(value.replace(/[^0-9.]/g, '')) || 3000
    const ownersMap: Record<string, { initials: string; avatarBg: string }> = {
      'Lucas Silveira': { initials: 'LS', avatarBg: 'bg-blue-600' },
      'Mariana Costa': { initials: 'MC', avatarBg: 'bg-emerald-600' },
      'Rafael Prado': { initials: 'RP', avatarBg: 'bg-amber-600' },
    }

    const newDeal: PipelineDeal = {
      id: `deal-${Date.now()}`,
      title: title.trim(),
      contactName: contactName.trim() || 'Contato Principal',
      value: numValue,
      channel,
      stageId,
      owner: {
        name: ownerName,
        initials: ownersMap[ownerName]?.initials || 'CO',
        avatarBg: ownersMap[ownerName]?.avatarBg || 'bg-slate-700',
      },
      daysInStage: 1,
      probability: stageId === 'won' ? 100 : stageId === 'negotiation' ? 80 : 25,
      createdAt: 'Criado agora',
      tags: ['Novo Lead'],
    }

    onAddDeal(newDeal)
    setTitle('')
    setContactName('')
    onClose()
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in">
      <div
        className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-md w-full overflow-hidden animate-in zoom-in-95 duration-150"
        role="dialog"
      >
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-blue-600 text-white flex items-center justify-center">
              <Plus className="w-4 h-4" />
            </div>
            <h3 className="font-bold text-slate-900 text-sm">Nova Oportunidade no Pipeline</h3>
          </div>
          <button onClick={onClose} className="p-1 rounded-md text-slate-400 hover:text-slate-600">
            <X className="w-4 h-4" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-3.5 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">
              Nome da Empresa / Cliente *
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex: Clínica Alpha Saúde"
              className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Nome do Contato</label>
              <input
                type="text"
                value={contactName}
                onChange={(e) => setContactName(e.target.value)}
                placeholder="Ex: Carlos Santos"
                className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">
                Valor Previsto (R$) *
              </label>
              <input
                type="number"
                required
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="4500"
                className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Canal de Origem</label>
              <select
                value={channel}
                onChange={(e) => setChannel(e.target.value)}
                className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="Meta Ads">Meta Ads</option>
                <option value="Google Orgânico">Google Orgânico</option>
                <option value="Google Ads">Google Ads</option>
                <option value="Indicação">Indicação</option>
                <option value="Email Marketing">Email Marketing</option>
                <option value="Tráfego Direto">Tráfego Direto</option>
              </select>
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Etapa Inicial</label>
              <select
                value={stageId}
                onChange={(e) => setStageId(e.target.value as PipelineStageId)}
                className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                {PIPELINE_STAGES.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.title}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Responsável Comercial</label>
            <select
              value={ownerName}
              onChange={(e) => setOwnerName(e.target.value)}
              className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="Lucas Silveira">Lucas Silveira</option>
              <option value="Mariana Costa">Mariana Costa</option>
              <option value="Rafael Prado">Rafael Prado</option>
            </select>
          </div>

          <div className="pt-3 border-t border-slate-200 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-3 py-1.5 rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50 font-medium"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-medium shadow-sm transition-colors"
            >
              Criar Oportunidade
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
