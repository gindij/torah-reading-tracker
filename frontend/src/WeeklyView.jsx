import { useState, useEffect } from 'react';
import { api } from './api';
import './WeeklyView.css';

export default function WeeklyView({ selectedParsha: initialParsha }) {
  const [parshiot, setParshiot] = useState([]);
  const [selectedParsha, setSelectedParsha] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadParshiot();
  }, []);

  useEffect(() => {
    if (initialParsha && parshiot.length > 0) {
      const parsha = parshiot.find(p => p.title === initialParsha.title);
      if (parsha) {
        setSelectedParsha(parsha);
      }
    }
  }, [initialParsha, parshiot]);

  async function loadParshiot() {
    try {
      const data = await api.getParshiot();
      setParshiot(data);
      if (data.length > 0) {
        setSelectedParsha(data[0]);
      }
    } catch (error) {
      console.error('Error loading parshiot:', error);
    } finally {
      setLoading(false);
    }
  }

  async function toggleAliyah(aliyahNumber, currentStatus) {
    try {
      await api.updateAliyahStatus(selectedParsha.title, aliyahNumber, !currentStatus);
      await loadParshiot();
      const updatedParsha = parshiot.find(p => p.title === selectedParsha.title);
      setSelectedParsha(updatedParsha);
    } catch (error) {
      console.error('Error updating aliyah:', error);
    }
  }

  async function toggleAllAliyot() {
    try {
      const allComplete = selectedParsha.aliyot.every(a => a.is_complete);
      const newStatus = !allComplete;

      for (const aliyah of selectedParsha.aliyot) {
        await api.updateAliyahStatus(selectedParsha.title, aliyah.number, newStatus);
      }

      await loadParshiot();
      const updatedParsha = parshiot.find(p => p.title === selectedParsha.title);
      setSelectedParsha(updatedParsha);
    } catch (error) {
      console.error('Error updating all aliyot:', error);
    }
  }

  if (loading) return <div className="weekly-view">Loading...</div>;
  if (!selectedParsha) return <div className="weekly-view">No parshiot found</div>;

  const completedAliyot = selectedParsha.aliyot.filter(a => a.is_complete).length;
  const totalWords = selectedParsha.aliyot.reduce((sum, a) => sum + (a.word_count || 0), 0);
  const completedWords = selectedParsha.aliyot
    .filter(a => a.is_complete)
    .reduce((sum, a) => sum + (a.word_count || 0), 0);
  const totalVerses = selectedParsha.aliyot.reduce((sum, a) => sum + (a.verse_count || 0), 0);
  const completedVerses = selectedParsha.aliyot
    .filter(a => a.is_complete)
    .reduce((sum, a) => sum + (a.verse_count || 0), 0);
  const allComplete = selectedParsha.aliyot.every(a => a.is_complete);

  return (
    <div className="weekly-view">
      <div className="parsha-selector">
        <label>Select Parsha: </label>
        <select
          value={selectedParsha.title}
          onChange={(e) => setSelectedParsha(parshiot.find(p => p.title === e.target.value))}
        >
          {parshiot.map(parsha => (
            <option key={parsha.title} value={parsha.title}>
              {parsha.title}
            </option>
          ))}
        </select>
      </div>

      <div className="parsha-header">
        <h1>{selectedParsha.title}</h1>
        <p className="parsha-hebrew">{selectedParsha.name}</p>
        <p className="parsha-portion">{selectedParsha.torah_portion}</p>
      </div>

      <div className="parsha-stats">
        <div className="stat-item">
          <span className="stat-label">Aliyot:</span>
          <span className="stat-value">{completedAliyot} / {selectedParsha.aliyot.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Verses:</span>
          <span className="stat-value">{completedVerses.toLocaleString()} / {totalVerses.toLocaleString()}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Words:</span>
          <span className="stat-value">{completedWords.toLocaleString()} / {totalWords.toLocaleString()}</span>
        </div>
      </div>

      <div className="parsha-actions">
        <button
          className="toggle-all-button"
          onClick={toggleAllAliyot}
        >
          {allComplete ? 'Mark All Incomplete' : 'Mark All Complete'}
        </button>
      </div>

      <div className="aliyot-list">
        {selectedParsha.aliyot.map(aliyah => (
          <div
            key={aliyah.number}
            className={`aliyah-card ${aliyah.is_complete ? 'completed' : ''}`}
            onClick={() => toggleAliyah(aliyah.number, aliyah.is_complete)}
          >
            <div className="aliyah-header">
              <span className="aliyah-number">Aliyah {aliyah.number}</span>
              <input
                type="checkbox"
                checked={aliyah.is_complete}
                readOnly
                className="aliyah-checkbox"
              />
            </div>
            <div className="aliyah-verses">{aliyah.verses}</div>
            <div className="aliyah-stats">
              <span>{aliyah.word_count} words</span>
              <span>{aliyah.verse_count} verses</span>
            </div>
            {aliyah.date_completed && (
              <div className="aliyah-date">
                Completed: {new Date(aliyah.date_completed).toLocaleDateString()}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
