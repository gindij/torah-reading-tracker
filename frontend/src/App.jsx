import { useState } from 'react';
import WeeklyView from './WeeklyView';
import AnnualOverview from './AnnualOverview';
import Stats from './Stats';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('annual');
  const [selectedParsha, setSelectedParsha] = useState(null);

  const handleParshaClick = (parsha) => {
    setSelectedParsha(parsha);
    setCurrentView('weekly');
  };

  const handleBackToAnnual = () => {
    setCurrentView('annual');
    setSelectedParsha(null);
  };

  return (
    <div className="app">
      <nav className="navbar">
        <h1 className="app-title">Torah Reading Tracker</h1>
        <div className="nav-buttons">
          {currentView === 'weekly' && (
            <button onClick={handleBackToAnnual}>
              Back to Overview
            </button>
          )}
          {currentView === 'annual' && (
            <button className="active">
              Annual Overview
            </button>
          )}
        </div>
      </nav>

      <main className="main-content">
        <Stats />
        {currentView === 'weekly' && <WeeklyView selectedParsha={selectedParsha} />}
        {currentView === 'annual' && <AnnualOverview onParshaClick={handleParshaClick} />}
      </main>
    </div>
  );
}

export default App;
