import React, { useState, useEffect } from 'react'
import {
  Calendar,
  CheckCircle2,
  DollarSign,
  Edit2,
  Loader2,
  Plus,
  Sparkles,
  Tag,
  Trash2,
  User,
  X,
} from 'lucide-react'
import {
  PipelineDeal,
  PipelineStageId,
  PIPELINE_STAGES,
  formatCurrencyBRL,
  getChannelBadgeStyle,
} from '@/lib/pipeline-data'
import { DealsService, CreateDealInput, UpdateDealInput, stageIdToEtapa } from '@/services/deals'
import { toast } from '@/hooks/use-toast'

interface DealModalProps {
  deal: PipelineDeal | null
  isOpen: boolean
  onClose: () => void
  onDealUpdated?: (updatedDeal: PipelineDeal) => void
  onDealDeleted?: (dealId: string) => void
}

export const DealModal: React.FC<DealModalProps> = ({
  deal,
  isOpen,
  onClose,
  onDealUpdated,
  onDealDeleted,
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)

  // Campos de edição
  const [title, setTitle] = useState('')
  const [contactName, setContactName] = useState('')
  const [contactInfo, setContactInfo] = useState('')
  const [value, setValue] = useState('')
  const [channel, setChannel] = useState('Meta Ads')
  const [stageId, setStageId] = useState<PipelineStageId>('new_leads')
  const [probability, setProbability] = useState('20')
  const [ownerName, setOwnerName] = useState('Nao atribuido')
  const [tagsInput, setTagsInput] = useState('')

  useEffect(() => {
    if (deal) {
      setTitle(deal.title)
      setContactName(deal.contactName)
      setContactInfo(deal.contactInfo || '')
      setValue(deal.value.toString())
      setChannel(deal.channel)
      setStageId(deal.stageId)
      setProbability(deal.probability.toString())
      setOwnerName(deal.owner.name)
      setTagsInput(deal.tags ? deal.tags.join(', ') : '')
      setIsEditing(false)
    }
  }, [deal, isOpen])

  if (!isOpen || !deal) return null

  const stage = PIPELINE_STAGES.find((s) => s.id === deal.stageId)
  const channelStyle = getChannelBadgeStyle(deal.channel)

  const handleSaveEdit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) {
      toast({
        title: 'Nome obrigatório',
        description: 'Preencha o nome da empresa ou oportunidade.',
        variant: 'destructive',
      })
      return
    }

    try {
      setIsSubmitting(true)
      const numValue = Number(value.replace(/[^0-9.]/g, '')) || 0
      const numProb = Math.min(100, Math.max(0, Number(probability) || 0))
      const tags = tagsInput
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)

      const updateInput: UpdateDealInput = {
        nome: title.trim(),
        cliente: contactName.trim(),
        contato: contactInfo.trim(),
        valor: numValue,
        etapa: stageIdToEtapa(stageId),
        canal: channel,
        probabilidade: numProb,
        responsavel: ownerName === 'Não atribuído' ? 'Nao atribuido' : ownerName,
        tags,
      }

      const updated = await DealsService.update(deal.id, updateInput)
      toast({
        title: 'Negócio atualizado!',
        description: `As informações de "${updated.title}" foram salvas.`,
      })
      onDealUpdated?.(updated)
      setIsEditing(false)
    } catch (err) {
      console.error('Erro ao atualizar negócio:', err)
      toast({
        title: 'Erro ao salvar',
        description: 'Não foi possível salvar as alterações no banco de dados.',
        variant: 'destructive',
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDelete = async () => {
    const confirmDelete = window.confirm(
      `Deseja realmente excluir a oportunidade "${deal.title}"? Esta ação não pode ser desfeita.`,
    )
    if (!confirmDelete) return

    try {
      setIsDeleting(true)
      await DealsService.delete(deal.id)
      toast({
        title: 'Oportunidade excluída',
        description: `"${deal.title}" foi removido do CRM.`,
      })
      onDealDeleted?.(deal.id)
      onClose()
    } catch (err) {
      console.error('Erro ao excluir negócio:', err)
      toast({
        title: 'Erro ao excluir',
        description: 'Não foi possível remover o registro do banco de dados.',
        variant: 'destructive',
      })
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-xs animate-in fade-in">
      <div
        className="bg-white rounded-xl shadow-2xl border border-slate-200 max-w-lg w-full overflow-hidden animate-in zoom-in-95 duration-150 max-h-[90vh] flex flex-col"
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-slate-200 flex items-start justify-between bg-slate-50/70 shrink-0">
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
            <p className="text-xs text-slate-500 mt-0.5">
              Contato: <strong className="text-slate-700">{deal.contactName}</strong>
              {deal.contactInfo && <span className="text-slate-400"> • {deal.contactInfo}</span>}
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-200/50"
            aria-label="Fechar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content body */}
        <div className="p-4 sm:p-5 overflow-y-auto space-y-4 text-xs sm:text-sm flex-1">
          {isEditing ? (
            <form id="edit-deal-form" onSubmit={handleSaveEdit} className="space-y-3.5 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Nome da Empresa / Oportunidade *
                </label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Nome do Cliente</label>
                  <input
                    type="text"
                    value={contactName}
                    onChange={(e) => setContactName(e.target.value)}
                    className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Telefone / Email
                  </label>
                  <input
                    type="text"
                    value={contactInfo}
                    onChange={(e) => setContactInfo(e.target.value)}
                    placeholder="(00) 00000-0000 • email@exemplo.com"
                    className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Valor (R$)</label>
                  <input
                    type="number"
                    value={value}
                    onChange={(e) => setValue(e.target.value)}
                    className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">
                    Probabilidade (%)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={probability}
                    onChange={(e) => setProbability(e.target.value)}
                    className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Etapa Atual</label>
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
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Responsável Comercial
                </label>
                <select
                  value={ownerName === 'Nao atribuido' ? 'Não atribuído' : ownerName}
                  onChange={(e) => setOwnerName(e.target.value)}
                  className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  <option value="Não atribuído">Não atribuído</option>
                  <option value="Henrique Tavano Sammartino">Henrique Tavano Sammartino</option>
                  <option value="Vinícius Oliveira da Costa">Vinícius Oliveira da Costa</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Tags (separadas por vírgula)
                </label>
                <input
                  type="text"
                  value={tagsInput}
                  onChange={(e) => setTagsInput(e.target.value)}
                  placeholder="Ex: BPO Completo, Urgente, Contrato Anual"
                  className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
              </div>
            </form>
          ) : (
            <>
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
                    Métrica correlacionada ao relatório de canais de aquisição no PocketBase.
                  </p>
                </div>
              </div>
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between shrink-0">
          <div>
            {!isEditing && (
              <button
                type="button"
                onClick={handleDelete}
                disabled={isDeleting}
                className="inline-flex items-center gap-1.5 text-xs text-red-600 hover:text-red-700 font-medium px-2.5 py-1.5 rounded hover:bg-red-50 transition-colors disabled:opacity-50"
              >
                {isDeleting ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <Trash2 className="w-3.5 h-3.5" />
                )}
                <span>Excluir negócio</span>
              </button>
            )}
          </div>

          <div className="flex items-center gap-2">
            {isEditing ? (
              <>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  disabled={isSubmitting}
                  className="px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-200/60 rounded-md transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  form="edit-deal-form"
                  disabled={isSubmitting}
                  className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-xs font-medium shadow-sm transition-colors disabled:opacity-50"
                >
                  {isSubmitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Salvar alterações</span>
                </button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => setIsEditing(true)}
                  className="inline-flex items-center gap-1 px-3 py-1.5 border border-slate-300 text-slate-700 hover:bg-slate-100 rounded-md text-xs font-medium transition-colors"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                  <span>Editar</span>
                </button>
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-1.5 bg-slate-800 hover:bg-slate-900 text-white rounded-md text-xs font-medium transition-colors"
                >
                  Fechar
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

interface NewDealDialogProps {
  isOpen: boolean
  onClose: () => void
  initialStageId?: PipelineStageId
  onDealCreated?: (deal: PipelineDeal) => void
}

export const NewDealDialog: React.FC<NewDealDialogProps> = ({
  isOpen,
  onClose,
  initialStageId = 'new_leads',
  onDealCreated,
}) => {
  const [title, setTitle] = useState('')
  const [contactName, setContactName] = useState('')
  const [contactInfo, setContactInfo] = useState('')
  const [value, setValue] = useState('0')
  const [channel, setChannel] = useState('Meta Ads')
  const [stageId, setStageId] = useState<PipelineStageId>(initialStageId)
  const [ownerName, setOwnerName] = useState('Não atribuído')
  const [tagsInput, setTagsInput] = useState('Novo Lead')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (isOpen) {
      setStageId(initialStageId)
      setTitle('')
      setContactName('')
      setContactInfo('')
      setValue('0')
      setChannel('Meta Ads')
      setOwnerName('Não atribuído')
      setTagsInput('Novo Lead')
    }
  }, [isOpen, initialStageId])

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) {
      toast({
        title: 'Nome obrigatório',
        description: 'Informe o nome da empresa ou prospect.',
        variant: 'destructive',
      })
      return
    }

    try {
      setIsSubmitting(true)
      const numValue = Number(value.replace(/[^0-9.]/g, '')) || 0
      const tags = tagsInput
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean)

      const createInput: CreateDealInput = {
        nome: title.trim(),
        cliente: contactName.trim() || title.trim(),
        contato: contactInfo.trim(),
        valor: numValue,
        etapa: stageIdToEtapa(stageId),
        canal: channel,
        probabilidade: stageId === 'won' ? 100 : stageId === 'negotiation' ? 80 : 20,
        responsavel: ownerName === 'Não atribuído' ? 'Nao atribuido' : ownerName,
        tags: tags.length > 0 ? tags : ['Novo Lead'],
      }

      const created = await DealsService.create(createInput)
      toast({
        title: 'Oportunidade cadastrada!',
        description: `"${created.title}" adicionado ao pipeline com sucesso.`,
      })

      onDealCreated?.(created)
      onClose()
    } catch (err) {
      console.error('Erro ao criar negócio no PocketBase:', err)
      toast({
        title: 'Erro ao criar',
        description: 'Não foi possível gravar a oportunidade no banco de dados.',
        variant: 'destructive',
      })
    } finally {
      setIsSubmitting(false)
    }
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
              <label className="block font-semibold text-slate-700 mb-1">Telefone / Email</label>
              <input
                type="text"
                value={contactInfo}
                onChange={(e) => setContactInfo(e.target.value)}
                placeholder="Ex: (11) 99999-9999"
                className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Valor Previsto (R$)</label>
              <input
                type="number"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="0"
                className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
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
          </div>

          <div className="grid grid-cols-2 gap-3">
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
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Responsável</label>
              <select
                value={ownerName}
                onChange={(e) => setOwnerName(e.target.value)}
                className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
              >
                <option value="Não atribuído">Não atribuído</option>
                <option value="Henrique Tavano Sammartino">Henrique Tavano Sammartino</option>
                <option value="Vinícius Oliveira da Costa">Vinícius Oliveira da Costa</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Tags</label>
            <input
              type="text"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              placeholder="Ex: BPO, Prioridade"
              className="w-full px-3 py-2 rounded-md border border-slate-300 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>

          <div className="pt-3 border-t border-slate-200 flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-3 py-1.5 rounded-md border border-slate-300 text-slate-600 hover:bg-slate-50 font-medium"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-md bg-blue-600 hover:bg-blue-700 text-white font-medium shadow-sm transition-colors disabled:opacity-50"
            >
              {isSubmitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              <span>Criar Oportunidade</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
