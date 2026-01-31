import { useState } from 'react';
import Header from './components/Header';
import DailyBatchAnalysis from './components/DailyBatchAnalysis';
import SingleAddressSearch from './components/SingleAddressSearch';
import TestExamples from './components/TestExamples';
import ModelDetails from './components/ModelDetails';
import './index.css';

function App() {
  const [activeTab, setActiveTab] = useState('daily');
  const [initialSearchState, setInitialSearchState] = useState(null);

  const handleTestSelect = (addr, date) => {
    setInitialSearchState({ address: addr, date: date });
    setActiveTab('single');
  };

  return (
    <div className="min-h-screen bg-slate-950 font-sans text-slate-100">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="pb-20">
        {activeTab === 'daily' && <DailyBatchAnalysis />}
        {activeTab === 'single' && <SingleAddressSearch initialState={initialSearchState} />}
        {activeTab === 'test' && <TestExamples onSelect={handleTestSelect} />}
        {activeTab === 'model' && <ModelDetails />}
      </main>
    </div>
  );
}

export default App;
