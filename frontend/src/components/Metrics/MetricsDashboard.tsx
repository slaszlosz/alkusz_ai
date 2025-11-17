import { useState, useEffect } from 'react';
import { Activity, DollarSign, Clock, Database, TrendingUp, Zap, Target } from 'lucide-react';
import { metricsApi, type MetricsStats } from '../../lib/api';

export default function MetricsDashboard() {
  const [stats, setStats] = useState<MetricsStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<number | undefined>(24);

  useEffect(() => {
    loadStats();
  }, [timeRange]);

  const loadStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await metricsApi.getStats(timeRange);
      setStats(data);
    } catch (err: any) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError('Nem sikerült betölteni a metrikákat');
      }
    } finally {
      setLoading(false);
    }
  };

  const formatNumber = (num: number, decimals: number = 0): string => {
    return num.toLocaleString('hu-HU', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    });
  };

  const formatCurrency = (amount: number): string => {
    return `$${amount.toFixed(4)}`;
  };

  if (loading) {
    return (
      <div className="metrics-dashboard">
        <div className="metrics-header">
          <h2>Monitoring és Metrikák</h2>
        </div>
        <div className="metrics-loading">
          <Activity className="animate-spin" size={40} />
          <p>Adatok betöltése...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="metrics-dashboard">
        <div className="metrics-header">
          <h2>Monitoring és Metrikák</h2>
        </div>
        <div className="metrics-error">
          <p>{error}</p>
          <p style={{ fontSize: '14px', color: '#7f8c8d', marginTop: '10px' }}>
            Még nincs adat. Próbálj ki néhány lekérdezést a Chat felületen!
          </p>
        </div>
      </div>
    );
  }

  if (!stats) return null;

  return (
    <div className="metrics-dashboard">
      <div className="metrics-header">
        <h2>Monitoring és Metrikák</h2>
        <div className="time-range-selector">
          <button
            className={timeRange === 1 ? 'active' : ''}
            onClick={() => setTimeRange(1)}
          >
            Utolsó 1 óra
          </button>
          <button
            className={timeRange === 24 ? 'active' : ''}
            onClick={() => setTimeRange(24)}
          >
            Utolsó 24 óra
          </button>
          <button
            className={timeRange === undefined ? 'active' : ''}
            onClick={() => setTimeRange(undefined)}
          >
            Összes idő
          </button>
        </div>
      </div>

      <div className="metrics-grid">
        {/* Total Queries */}
        <div className="metric-card primary">
          <div className="metric-icon">
            <Activity size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Összes lekérdezés</div>
            <div className="metric-value">{formatNumber(stats.total_queries)}</div>
            <div className="metric-subtitle">
              {timeRange ? `Utolsó ${timeRange} órában` : 'Minden idők'}
            </div>
          </div>
        </div>

        {/* Total Tokens */}
        <div className="metric-card">
          <div className="metric-icon">
            <Database size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Token használat</div>
            <div className="metric-value">{formatNumber(stats.tokens.total)}</div>
            <div className="metric-subtitle">
              Átlag: {formatNumber(stats.tokens.avg_per_query, 1)} / lekérdezés
            </div>
          </div>
        </div>

        {/* Total Costs */}
        <div className="metric-card success">
          <div className="metric-icon">
            <DollarSign size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Összes költség</div>
            <div className="metric-value">{formatCurrency(stats.costs_usd.total)}</div>
            <div className="metric-subtitle">
              Átlag: {formatCurrency(stats.costs_usd.avg_per_query)} / lekérdezés
            </div>
          </div>
        </div>

        {/* Average Latency */}
        <div className="metric-card warning">
          <div className="metric-icon">
            <Clock size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Átlagos válaszidő</div>
            <div className="metric-value">{formatNumber(stats.latency_ms.avg_total)} ms</div>
            <div className="metric-subtitle">Teljes feldolgozási idő</div>
          </div>
        </div>

        {/* First Token Latency */}
        {stats.latency_ms.avg_first_token && (
          <div className="metric-card">
            <div className="metric-icon">
              <Zap size={24} />
            </div>
            <div className="metric-content">
              <div className="metric-label">Első token latencia</div>
              <div className="metric-value">{formatNumber(stats.latency_ms.avg_first_token)} ms</div>
              <div className="metric-subtitle">Streaming válasz kezdete</div>
            </div>
          </div>
        )}

        {/* Retrieval Latency */}
        <div className="metric-card">
          <div className="metric-icon">
            <TrendingUp size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Keresési idő</div>
            <div className="metric-value">{formatNumber(stats.latency_ms.avg_retrieval)} ms</div>
            <div className="metric-subtitle">Átlagos RAG keresési idő</div>
          </div>
        </div>

        {/* Average Sources */}
        <div className="metric-card">
          <div className="metric-icon">
            <Target size={24} />
          </div>
          <div className="metric-content">
            <div className="metric-label">Források száma</div>
            <div className="metric-value">{formatNumber(stats.retrieval.avg_sources, 1)}</div>
            <div className="metric-subtitle">
              Relevancia: {formatNumber(stats.retrieval.avg_relevance * 100, 1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Performance Breakdown */}
      <div className="metrics-breakdown">
        <h3>Teljesítmény részletei</h3>
        <div className="breakdown-grid">
          <div className="breakdown-item">
            <div className="breakdown-label">Keresési idő</div>
            <div className="breakdown-bar">
              <div
                className="breakdown-fill retrieval"
                style={{
                  width: `${(stats.latency_ms.avg_retrieval / stats.latency_ms.avg_total) * 100}%`,
                }}
              ></div>
            </div>
            <div className="breakdown-value">{formatNumber(stats.latency_ms.avg_retrieval)} ms</div>
          </div>

          {stats.latency_ms.avg_first_token && (
            <div className="breakdown-item">
              <div className="breakdown-label">Első token</div>
              <div className="breakdown-bar">
                <div
                  className="breakdown-fill first-token"
                  style={{
                    width: `${(stats.latency_ms.avg_first_token / stats.latency_ms.avg_total) * 100}%`,
                  }}
                ></div>
              </div>
              <div className="breakdown-value">{formatNumber(stats.latency_ms.avg_first_token)} ms</div>
            </div>
          )}

          <div className="breakdown-item">
            <div className="breakdown-label">Teljes válaszidő</div>
            <div className="breakdown-bar">
              <div className="breakdown-fill total" style={{ width: '100%' }}></div>
            </div>
            <div className="breakdown-value">{formatNumber(stats.latency_ms.avg_total)} ms</div>
          </div>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="metrics-breakdown">
        <h3>Költség elemzés</h3>
        <div className="cost-details">
          <div className="cost-item">
            <span>Összes költség:</span>
            <strong>{formatCurrency(stats.costs_usd.total)}</strong>
          </div>
          <div className="cost-item">
            <span>Lekérdezésenként:</span>
            <strong>{formatCurrency(stats.costs_usd.avg_per_query)}</strong>
          </div>
          <div className="cost-item">
            <span>1000 token ára:</span>
            <strong>
              {formatCurrency((stats.costs_usd.total / stats.tokens.total) * 1000)}
            </strong>
          </div>
        </div>
      </div>
    </div>
  );
}
