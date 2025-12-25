import { useState, useEffect } from 'react';
import { api } from './api';
import './Stats.css';

export default function Stats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  async function loadStats() {
    try {
      const data = await api.getStats();
      setStats(data);
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="stats-container">Loading stats...</div>;
  if (!stats) return <div className="stats-container">Failed to load stats</div>;

  return (
    <div className="stats-container">
      <h2>Overall Progress</h2>
      <div className="stats-grid">
        <StatCard
          label="Words"
          completed={stats.completed.words}
          total={stats.total.words}
          percentage={stats.percentage.words}
        />
        <StatCard
          label="Verses"
          completed={stats.completed.verses}
          total={stats.total.verses}
          percentage={stats.percentage.verses}
        />
        <StatCard
          label="Aliyot"
          completed={stats.completed.aliyot}
          total={stats.total.aliyot}
          percentage={stats.percentage.aliyot}
        />
      </div>
    </div>
  );
}

function StatCard({ label, completed, total, percentage }) {
  return (
    <div className="stat-card">
      <h3>{label}</h3>
      <div className="stat-numbers">
        {completed.toLocaleString()} / {total.toLocaleString()}
      </div>
      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${percentage}%` }}></div>
      </div>
      <div className="stat-percentage">{percentage}%</div>
    </div>
  );
}
