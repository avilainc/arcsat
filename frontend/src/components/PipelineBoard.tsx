import React, { useState, useEffect } from 'react';
import api from '../services/api';

interface Deal {
  id: string;
  title: string;
  value: number;
  customer_name: string;
  customer_id: string;
  created_at: string;
  probability: number;
  expected_close_date?: string;
  description?: string;
}

interface Stage {
  stage: string;
  order: number;
  color: string;
  deals: Deal[];
  count: number;
  total_value: number;
}

const PipelineBoard: React.FC = () => {
  const [pipeline, setPipeline] = useState<Stage[]>([]);
  const [loading, setLoading] = useState(true);
  const [draggedDeal, setDraggedDeal] = useState<Deal | null>(null);
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    loadPipeline();
    loadMetrics();
  }, []);

  const loadPipeline = async () => {
    try {
      setLoading(true);
      const res = await api.get('/pipeline/board');
      setPipeline(res.data.stages);
    } catch (error) {
      console.error('Erro ao carregar pipeline:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMetrics = async () => {
    try {
      const res = await api.get('/pipeline/metrics');
      setMetrics(res.data);
    } catch (error) {
      console.error('Erro ao carregar métricas:', error);
    }
  };

  const handleDragStart = (deal: Deal) => {
    setDraggedDeal(deal);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDrop = async (stage: string) => {
    if (!draggedDeal) return;

    try {
      await api.post('/pipeline/move', {
        deal_id: draggedDeal.id,
        new_stage: stage
      });
      setDraggedDeal(null);
      loadPipeline();
    } catch (error) {
      console.error('Erro ao mover deal:', error);
      alert('Erro ao mover deal');
    }
  };

  const handleWin = async (dealId: string) => {
    if (!window.confirm('Marcar este deal como ganho?')) return;

    try {
      await api.post(`/pipeline/deal/${dealId}/win`);
      alert('Deal ganho! 🎉');
      loadPipeline();
      loadMetrics();
    } catch (error) {
      console.error('Erro ao marcar como ganho:', error);
      alert('Erro ao marcar deal como ganho');
    }
  };

  const handleLose = async (dealId: string) => {
    const reason = window.prompt('Motivo da perda?');
    if (reason === null) return;

    try {
      await api.post(`/pipeline/deal/${dealId}/lose?reason=${encodeURIComponent(reason)}`);
      alert('Deal marcado como perdido');
      loadPipeline();
      loadMetrics();
    } catch (error) {
      console.error('Erro ao marcar como perdido:', error);
      alert('Erro ao marcar deal como perdido');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-xl">Carregando pipeline...</div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800">Pipeline de Vendas</h1>
        <p className="text-gray-600">Gerencie seus negócios em andamento</p>
      </div>

      {/* Métricas */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Win Rate</p>
            <p className="text-2xl font-bold text-green-600">{metrics.win_rate}%</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Deals Ganhos</p>
            <p className="text-2xl font-bold text-gray-800">{metrics.total_won_deals}</p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Valor Médio</p>
            <p className="text-2xl font-bold text-blue-600">
              R$ {metrics.avg_deal_value.toLocaleString('pt-BR')}
            </p>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">Total Ganho</p>
            <p className="text-2xl font-bold text-green-600">
              R$ {metrics.total_won_value.toLocaleString('pt-BR')}
            </p>
          </div>
        </div>
      )}

      {/* Board Kanban */}
      <div className="flex gap-4 overflow-x-auto pb-4">
        {pipeline.map((stage) => (
          <div
            key={stage.stage}
            className="flex-shrink-0 w-80 bg-gray-100 rounded-lg p-4"
            onDragOver={handleDragOver}
            onDrop={() => handleDrop(stage.stage)}
          >
            {/* Cabeçalho da Coluna */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-bold text-lg" style={{ color: stage.color }}>
                  {stage.stage}
                </h3>
                <span className="bg-white px-2 py-1 rounded text-sm font-semibold">
                  {stage.count}
                </span>
              </div>
              <p className="text-sm text-gray-600 font-semibold">
                R$ {stage.total_value.toLocaleString('pt-BR')}
              </p>
            </div>

            {/* Deals */}
            <div className="space-y-3 max-h-screen overflow-y-auto">
              {stage.deals.map((deal) => (
                <div
                  key={deal.id}
                  draggable
                  onDragStart={() => handleDragStart(deal)}
                  className="bg-white p-4 rounded-lg shadow hover:shadow-lg transition cursor-move"
                >
                  <h4 className="font-semibold text-gray-800 mb-2">{deal.title}</h4>
                  <p className="text-sm text-gray-600 mb-2">{deal.customer_name}</p>

                  <div className="flex justify-between items-center mb-3">
                    <span className="text-green-600 font-bold">
                      R$ {deal.value.toLocaleString('pt-BR')}
                    </span>
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                      {deal.probability}%
                    </span>
                  </div>

                  {deal.expected_close_date && (
                    <p className="text-xs text-gray-500 mb-2">
                      📅 {new Date(deal.expected_close_date).toLocaleDateString('pt-BR')}
                    </p>
                  )}

                  {deal.description && (
                    <p className="text-xs text-gray-600 mb-3 line-clamp-2">
                      {deal.description}
                    </p>
                  )}

                  <div className="flex gap-2">
                    <button
                      onClick={() => handleWin(deal.id)}
                      className="flex-1 bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700"
                    >
                      ✅ Ganho
                    </button>
                    <button
                      onClick={() => handleLose(deal.id)}
                      className="flex-1 bg-red-600 text-white px-3 py-1 rounded text-sm hover:bg-red-700"
                    >
                      ❌ Perdido
                    </button>
                  </div>
                </div>
              ))}

              {stage.deals.length === 0 && (
                <div className="text-center text-gray-400 py-8">
                  Nenhum deal neste estágio
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Conversão por Estágio */}
      {metrics && metrics.conversion_rates && (
        <div className="bg-white p-6 rounded-lg shadow mt-6">
          <h3 className="text-lg font-semibold mb-4">Taxa de Conversão por Estágio</h3>
          <div className="space-y-3">
            {metrics.conversion_rates.map((rate: any, idx: number) => (
              <div key={idx} className="flex items-center gap-4">
                <div className="w-48 text-sm text-gray-600">
                  {rate.from} → {rate.to}
                </div>
                <div className="flex-1 h-4 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-500"
                    style={{ width: `${Math.min(rate.conversion_rate, 100)}%` }}
                  ></div>
                </div>
                <div className="w-16 text-right font-semibold">
                  {rate.conversion_rate.toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tempo Médio por Estágio */}
      {metrics && metrics.avg_time_by_stage && (
        <div className="bg-white p-6 rounded-lg shadow mt-6">
          <h3 className="text-lg font-semibold mb-4">Tempo Médio por Estágio</h3>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {metrics.avg_time_by_stage.map((time: any, idx: number) => (
              <div key={idx} className="text-center p-4 bg-gray-50 rounded">
                <p className="text-sm text-gray-600 mb-1">{time.stage}</p>
                <p className="text-2xl font-bold text-gray-800">{time.avg_days}</p>
                <p className="text-xs text-gray-500">dias</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PipelineBoard;
