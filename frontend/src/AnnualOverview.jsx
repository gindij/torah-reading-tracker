import { useState, useEffect } from 'react';
import { api } from './api';
import './AnnualOverview.css';

export default function AnnualOverview({ onParshaClick }) {
  const [parshiot, setParshiot] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadParshiot();
  }, []);

  async function loadParshiot() {
    try {
      const data = await api.getParshiot();
      setParshiot(data);
    } catch (error) {
      console.error('Error loading parshiot:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="annual-overview">Loading...</div>;

  // Group parshiot by book
  const parshiotByBook = parshiot.reduce((acc, parsha) => {
    const book = parsha.book || 'Unknown';
    if (!acc[book]) {
      acc[book] = [];
    }
    acc[book].push(parsha);
    return acc;
  }, {});

  const bookOrder = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy'];
  const orderedBooks = bookOrder.filter(book => parshiotByBook[book]);

  const calculateBookStats = (bookParshiot) => {
    const totalAliyot = bookParshiot.reduce((sum, p) => sum + p.aliyot.length, 0);
    const completedAliyot = bookParshiot.reduce(
      (sum, p) => sum + p.aliyot.filter(a => a.is_complete).length,
      0
    );
    const totalWords = bookParshiot.reduce(
      (sum, p) => sum + p.aliyot.reduce((s, a) => s + (a.word_count || 0), 0),
      0
    );
    const completedWords = bookParshiot.reduce(
      (sum, p) => sum + p.aliyot.filter(a => a.is_complete).reduce((s, a) => s + (a.word_count || 0), 0),
      0
    );
    const totalVerses = bookParshiot.reduce(
      (sum, p) => sum + p.aliyot.reduce((s, a) => s + (a.verse_count || 0), 0),
      0
    );
    const completedVerses = bookParshiot.reduce(
      (sum, p) => sum + p.aliyot.filter(a => a.is_complete).reduce((s, a) => s + (a.verse_count || 0), 0),
      0
    );
    return { totalAliyot, completedAliyot, totalWords, completedWords, totalVerses, completedVerses };
  };

  return (
    <div className="annual-overview">
      <h1>Annual Overview</h1>
      {orderedBooks.map(book => {
        const bookStats = calculateBookStats(parshiotByBook[book]);
        return (
          <div key={book} className="book-section">
            <h2 className="book-header">{book}</h2>
            <div className="book-stats">
              <div className="book-stat">
                <span className="stat-label">Aliyot:</span>
                <span className="stat-value">
                  {bookStats.completedAliyot} / {bookStats.totalAliyot}
                  <span className="stat-percentage">
                    ({bookStats.totalAliyot > 0 ? Math.round((bookStats.completedAliyot / bookStats.totalAliyot) * 100) : 0}%)
                  </span>
                </span>
              </div>
              <div className="book-stat">
                <span className="stat-label">Verses:</span>
                <span className="stat-value">
                  {bookStats.completedVerses.toLocaleString()} / {bookStats.totalVerses.toLocaleString()}
                  <span className="stat-percentage">
                    ({bookStats.totalVerses > 0 ? Math.round((bookStats.completedVerses / bookStats.totalVerses) * 100) : 0}%)
                  </span>
                </span>
              </div>
              <div className="book-stat">
                <span className="stat-label">Words:</span>
                <span className="stat-value">
                  {bookStats.completedWords.toLocaleString()} / {bookStats.totalWords.toLocaleString()}
                  <span className="stat-percentage">
                    ({bookStats.totalWords > 0 ? Math.round((bookStats.completedWords / bookStats.totalWords) * 100) : 0}%)
                  </span>
                </span>
              </div>
            </div>
            <div className="parshiot-grid">
              {parshiotByBook[book].map(parsha => {
                const completedAliyot = parsha.aliyot.filter(a => a.is_complete).length;
                const totalAliyot = parsha.aliyot.length;
                const percentage = totalAliyot > 0 ? (completedAliyot / totalAliyot) * 100 : 0;

                const parshaWords = parsha.aliyot.reduce((sum, a) => sum + (a.word_count || 0), 0);
                const parshaVerses = parsha.aliyot.reduce((sum, a) => sum + (a.verse_count || 0), 0);
                const wordPercentage = bookStats.totalWords > 0 ? (parshaWords / bookStats.totalWords * 100).toFixed(1) : 0;
                const versePercentage = bookStats.totalVerses > 0 ? (parshaVerses / bookStats.totalVerses * 100).toFixed(1) : 0;

                return (
                  <div
                    key={parsha.title}
                    className="parsha-overview-card"
                    onClick={() => onParshaClick(parsha)}
                  >
                    <h3>{parsha.title.replace('Parashat ', '')}</h3>
                    <div className="parsha-progress-bar">
                      <div
                        className="parsha-progress-fill"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <div className="parsha-progress-text">
                      {completedAliyot} / {totalAliyot}
                    </div>
                    <div className="parsha-book-stats">
                      <div>{wordPercentage}% words</div>
                      <div>{versePercentage}% verses</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
}
