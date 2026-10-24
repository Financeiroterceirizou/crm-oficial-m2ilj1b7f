import pb from '@/lib/pocketbase/client'
import { PipelineDeal, PipelineStageId, PIPELINE_STAGES } from '@/lib/pipeline-data'

export type DealEtapaPocketBase =
  | 'Novos leads'
  | 'Contato feito'
  | 'Proposta enviada'
  | 'Negociação'
  | 'Fechado (ganho)'

export interface DealRecord {
  id: string
  nome: string
  cliente?: string
  valor?: number
  etapa: DealEtapaPocketBase
  canal?: string
  probabilidade?: number
  responsavel?: string
  tags?: string[] | string
  data_fechamento?: string
  created: string
  updated: string
}

export interface CreateDealInput {
  nome: string
  cliente?: string
  valor?: number
  etapa: DealEtapaPocketBase
  canal?: string
  probabilidade?: number
  responsavel?: string
  tags?: string[]
  data_fechamento?: string
}

export interface UpdateDealInput {
  nome?: string
  cliente?: string
  valor?: number
  etapa?: DealEtapaPocketBase
  canal?: string
  probabilidade?: number
  responsavel?: string
  tags?: string[]
  data_fechamento?: string
}

// Mapeamentos entre PipelineStageId do frontend e etapa da collection no PocketBase
const STAGE_ID_TO_ETAPA: Record<PipelineStageId, DealEtapaPocketBase> = {
  new_leads: 'Novos leads',
  contacted: 'Contato feito',
  proposal_sent: 'Proposta enviada',
  negotiation: 'Negociação',
  won: 'Fechado (ganho)',
}

const ETAPA_TO_STAGE_ID: Record<string, PipelineStageId> = {
  'Novos leads': 'new_leads',
  'Contato feito': 'contacted',
  'Proposta enviada': 'proposal_sent',
  Negociação: 'negotiation',
  'Fechado (ganho)': 'won',
}

export function stageIdToEtapa(stageId: PipelineStageId): DealEtapaPocketBase {
  return STAGE_ID_TO_ETAPA[stageId] || 'Novos leads'
}

export function etapaToStageId(etapa: string): PipelineStageId {
  return ETAPA_TO_STAGE_ID[etapa] || 'new_leads'
}

// Helpers para avatar e cores por responsável
const OWNER_PALETTE: Record<string, { initials: string; avatarBg: string }> = {
  'Lucas Silveira': { initials: 'LS', avatarBg: 'bg-blue-600' },
  'Mariana Costa': { initials: 'MC', avatarBg: 'bg-emerald-600' },
  'Rafael Prado': { initials: 'RP', avatarBg: 'bg-amber-600' },
}

export function getOwnerDetails(name?: string) {
  const safeName = name?.trim() || 'Comercial'
  if (OWNER_PALETTE[safeName]) {
    return { name: safeName, ...OWNER_PALETTE[safeName] }
  }

  // Gera iniciais a partir do nome
  const parts = safeName.split(/\s+/).filter(Boolean)
  const initials =
    parts.length >= 2
      ? `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase()
      : safeName.slice(0, 2).toUpperCase() || 'CO'

  return {
    name: safeName,
    initials,
    avatarBg: 'bg-indigo-600',
  }
}

// Converte DealRecord do PocketBase para PipelineDeal da UI
export function recordToPipelineDeal(record: DealRecord): PipelineDeal {
  let tags: string[] = []
  if (Array.isArray(record.tags)) {
    tags = record.tags
  } else if (typeof record.tags === 'string' && record.tags.trim()) {
    try {
      const parsed = JSON.parse(record.tags)
      if (Array.isArray(parsed)) tags = parsed
    } catch {
      tags = [record.tags]
    }
  }

  // Calcula dias na etapa a partir de `updated` ou `created`
  const lastDate = record.updated ? new Date(record.updated) : new Date(record.created)
  const diffTime = Math.max(0, Date.now() - lastDate.getTime())
  const daysInStage = Math.max(1, Math.floor(diffTime / (1000 * 60 * 60 * 24)))

  // Formatação de data amigável
  let createdAtFormatted = 'Hoje'
  if (record.created) {
    const cDate = new Date(record.created)
    createdAtFormatted = cDate.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
    })
  }

  return {
    id: record.id,
    title: record.nome || 'Sem título',
    contactName: record.cliente || 'Contato não informado',
    value: typeof record.valor === 'number' ? record.valor : 0,
    channel: record.canal || 'Meta Ads',
    stageId: etapaToStageId(record.etapa),
    owner: getOwnerDetails(record.responsavel),
    daysInStage,
    probability:
      typeof record.probabilidade === 'number'
        ? record.probabilidade
        : record.etapa === 'Fechado (ganho)'
          ? 100
          : 20,
    createdAt: createdAtFormatted,
    tags,
  }
}

export const DealsService = {
  /**
   * Lista todos os deals cadastrados, ordenados por data de criação desc
   */
  async list(): Promise<PipelineDeal[]> {
    const records = await pb.collection('deals').getFullList<DealRecord>({
      sort: '-created',
    })
    return records.map(recordToPipelineDeal)
  },

  /**
   * Busca um deal específico por ID
   */
  async getById(id: string): Promise<PipelineDeal> {
    const record = await pb.collection('deals').getOne<DealRecord>(id)
    return recordToPipelineDeal(record)
  },

  /**
   * Cria um novo deal
   */
  async create(input: CreateDealInput): Promise<PipelineDeal> {
    const payload = {
      nome: input.nome.trim(),
      cliente: input.cliente?.trim() || '',
      valor: input.valor ?? 0,
      etapa: input.etapa,
      canal: input.canal?.trim() || 'Meta Ads',
      probabilidade: input.probabilidade ?? (input.etapa === 'Fechado (ganho)' ? 100 : 20),
      responsavel: input.responsavel?.trim() || 'Lucas Silveira',
      tags: input.tags ?? ['Novo Lead'],
      data_fechamento: input.data_fechamento || null,
    }

    const record = await pb.collection('deals').create<DealRecord>(payload)
    return recordToPipelineDeal(record)
  },

  /**
   * Atualiza a etapa de um deal (usado no drag & drop)
   */
  async updateStage(id: string, stageId: PipelineStageId): Promise<PipelineDeal> {
    const etapa = stageIdToEtapa(stageId)
    const probabilidade = stageId === 'won' ? 100 : stageId === 'negotiation' ? 80 : undefined

    const updatePayload: Record<string, unknown> = { etapa }
    if (probabilidade !== undefined) {
      updatePayload.probabilidade = probabilidade
    }

    const record = await pb.collection('deals').update<DealRecord>(id, updatePayload)
    return recordToPipelineDeal(record)
  },

  /**
   * Atualização geral de um deal (edição pelo modal)
   */
  async update(id: string, input: UpdateDealInput): Promise<PipelineDeal> {
    const updatePayload: Record<string, unknown> = {}

    if (input.nome !== undefined) updatePayload.nome = input.nome.trim()
    if (input.cliente !== undefined) updatePayload.cliente = input.cliente.trim()
    if (input.valor !== undefined) updatePayload.valor = input.valor
    if (input.etapa !== undefined) updatePayload.etapa = input.etapa
    if (input.canal !== undefined) updatePayload.canal = input.canal
    if (input.probabilidade !== undefined) updatePayload.probabilidade = input.probabilidade
    if (input.responsavel !== undefined) updatePayload.responsavel = input.responsavel
    if (input.tags !== undefined) updatePayload.tags = input.tags
    if (input.data_fechamento !== undefined) updatePayload.data_fechamento = input.data_fechamento

    const record = await pb.collection('deals').update<DealRecord>(id, updatePayload)
    return recordToPipelineDeal(record)
  },

  /**
   * Exclui um deal
   */
  async delete(id: string): Promise<boolean> {
    await pb.collection('deals').delete(id)
    return true
  },
}
