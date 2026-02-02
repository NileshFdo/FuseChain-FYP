import { useState } from 'react';
import Header from './components/Header';
import DailyBatchAnalysis from './components/DailyBatchAnalysis';
import SingleAddressSearch from './components/SingleAddressSearch';
import TestExamples from './components/TestExamples';
import ModelDetails from './components/ModelDetails';
import './index.css';

function getInitialState() {
  const hash = window.location.hash;

  // check for single-search with params
  if (hash.startsWith('#single-search')) {
    const queryString = hash.split('?')[1];
    if (queryString) {
      const params = new URLSearchParams(queryString);
      const address = params.get('address');
      const date = params.get('date');
      const auto = params.get('auto') === 'true';

      if (address) {
        return {
          tab: 'single',
          searchState: { address, date, autoAnalyze: auto }
        };
      }
    }

    // fallback to localStorage for backwards compat
    const pending = localStorage.getItem('fusechain_pending_analysis');
    if (pending) {
      try {
        const data = JSON.parse(pending);
        localStorage.removeItem('fusechain_pending_analysis');
        return {
          tab: 'single',
          searchState: {
            address: data.address,
            date: data.date,
            autoAnalyze: data.autoAnalyze || false
          }
        };
      } catch (e) {
        console.error('Failed to parse pending analysis', e);
      }
    }
    return { tab: 'single', searchState: null };
  }

  return { tab: 'daily', searchState: null };
}

const initialState = getInitialState();

function App() {
  const [activeTab, setActiveTab] = useState(initialState.tab);
  const [initialSearchState] = useState(initialState.searchState);

  return (
    <div className="min-h-screen bg-slate-950 font-sans text-slate-100">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="pb-20">
        {activeTab === 'daily' && <DailyBatchAnalysis />}
        {activeTab === 'single' && <SingleAddressSearch initialState={initialSearchState} />}
        {activeTab === 'test' && <TestExamples />}
        {activeTab === 'model' && <ModelDetails />}
      </main>
    </div>
  );
}

export default App;
