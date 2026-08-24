/* CRM Oficial — Fila de Recuperação: visualização e replay de erros */
import { useEffect, useState } from 'react'
import pb from '@/lib/pocketbase/client'

interface ErrorLog {
  id: string
  error_id: string
  source_event_id: string
  categoria: string
  resumo: string
  payload_resumido: string
  tentativa: number
  estado: string
  dono: string
  proxima_acao: string
  resolvido_em: string
  resolvido_por: string
  resultado: string
  created: string
}

const categoriaColors: Record<string, string> = {
  validacao: 'bg-yellow-100 text-yellow-800',
  permissao: 'bg-red-100 text-red-800',
  timeout: 'bg-orange-100 text-orange-800',
  duplicidade: 'bg-purple-100 text-purple-800',
  schema_invalido: 'bg-gray-100 text-gray-800',
  desconhecido: 'bg-gray-100 text-gray-800',
}

const estadoColors: Record<string, string> = {
  pendente: 'bg-red-100 text-red-800',
  em_analise: 'bg-yellow-100 text-yellow-800',
  resolvido: 'bg-green-100 text-green-800',
  encerrado: 'bg-gray-100 text-gray-800',
}

const FilaRecuperacao = () => {
  const [errors, setErrors] = useState<ErrorLog[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedError, setSelectedError] = useState<ErrorLog | null>(null)
  const [replayMotivo, setReplayMotivo] = useState('')
  const [replayLoading, setReplayLoading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchErrors()
  }, [])

  const fetchErrors = async () => {
    try {
      setLoading(true)
      const records = await pb.collection('error_log').getFullList({ sort: '-created' })
      setErrors(records as unknown as ErrorLog[])
    } catch (err: any) {
      console.error('Erro ao buscar error_log:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleReplay = async (error: ErrorLog) => {
    if (!replayMotivo.trim()) {
      setMessage('Preencha o motivo do replay')
      return
    }

    setReplayLoading(true)
    setMessage('')

    try {
      const response = await fetch('/backend/v1/replay/lead', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dedup_key: error.source_event_id || error.error_id,
          motivo: replayMotivo,
          operador: pb.authStore.model?.name || 'admin',
          error_id: error.error_id,
        }),
      })

      const result = await response.json()

      if (response.ok) {
        setMessage('Replay executado com sucesso: ' + result.lead_id)
        setSelectedError(null)
        setReplayMotivo('')
        fetchErrors()
      } else {
        setMessage('Erro no replay: ' + (result.error || 'Desconhecido'))
      }
    } catch (err: any) {
      setMessage('Erro de conexão: ' + err.message)
    } finally {
      setReplayLoading(false)
    }
  }

  const pendentes = errors.filter((e) => e.estado === 'pendente')
  const emAnalise = errors.filter((e) => e.estado === 'em_analise')
  const resolvidos = errors.filter((e) => e.estado === 'resolvido')

  return (
    <div className="space-y-6">
      {/* Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm font-medium text-gray-500">Total</div>
          <div className="text-2xl font-bold text-gray-900">{errors.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm font-medium text-gray-500">Pendentes</div>
          <div className="text-2xl font-bold text-red-600">{pendentes.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm font-medium text-gray-500">Em Análise</div>
          <div className="text-2xl font-bold text-yellow-600">{emAnalise.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm font-medium text-gray-500">Resolvidos</div>
          <div className="text-2xl font-bold text-green-600">{resolvidos.length}</div>
        </div>
      </div>

      {message && (
        <div
          className={`p-4 rounded-lg ${message.includes('sucesso') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}
        >
          {message}
        </div>
      )}

      {/* Tabela */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-medium text-gray-900">Fila de Recuperação</h2>
          <button onClick={fetchErrors} className="text-sm text-indigo-600 hover:text-indigo-800">
            Atualizar
          </button>
        </div>

        {loading ? (
          <div className="p-8 text-center text-gray-500">Carregando...</div>
        ) : errors.length === 0 ? (
          <div className="p-8 text-center text-gray-500">Nenhum erro registrado</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Categoria
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Resumo
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Estado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Dono
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Criado
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                    Ação
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {errors.map((error) => (
                  <tr key={error.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${categoriaColors[error.categoria] || 'bg-gray-100 text-gray-800'}`}
                      >
                        {error.categoria}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-900 max-w-xs truncate">
                      {error.resumo}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span
                        className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${estadoColors[error.estado] || 'bg-gray-100 text-gray-800'}`}
                      >
                        {error.estado}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                      {error.dono || '—'}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                      {new Date(error.created).toLocaleDateString('pt-BR')}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {error.estado === 'pendente' && (
                        <button
                          onClick={() => setSelectedError(error)}
                          className="text-sm text-indigo-600 hover:text-indigo-800"
                        >
                          Replay
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal de Replay */}
      {selectedError && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Replay Manual</h3>
            <div className="space-y-3 text-sm text-gray-600">
              <p>
                <strong>Categoria:</strong> {selectedError.categoria}
              </p>
              <p>
                <strong>Resumo:</strong> {selectedError.resumo}
              </p>
              <p>
                <strong>Error ID:</strong> {selectedError.error_id}
              </p>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700">Motivo do replay *</label>
              <textarea
                value={replayMotivo}
                onChange={(e) => setReplayMotivo(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2 text-sm"
                rows={3}
                placeholder="Ex: Corrigido o campo ausente no formulário"
              />
            </div>
            <div className="mt-4 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setSelectedError(null)
                  setReplayMotivo('')
                }}
                className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900"
              >
                Cancelar
              </button>
              <button
                onClick={() => handleReplay(selectedError)}
                disabled={replayLoading}
                className="px-4 py-2 text-sm text-white bg-indigo-600 hover:bg-indigo-700 rounded-md disabled:opacity-50"
              >
                {replayLoading ? 'Executando...' : 'Executar Replay'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default FilaRecuperacao
