import { useState, useEffect } from 'react';
import { API_URL } from '../config';

function DailyBatchAnalysis() {
    const [selectedDate, setSelectedDate] = useState('');
    const [availableDates, setAvailableDates] = useState([]);
    const [scanResult, setScanResult] = useState(null);
    const [loading, setLoading] = useState(false);

    const [threshold] = useState(0.5);
    const [onlyAnomalous] = useState(true);
    const [limit] = useState(100);

    useEffect(() => {
        fetch(`${API_URL}/risk/available-dates`)
            .then(res => res.json())
            .then(data => {
                setAvailableDates(data.dates);
                if (data.dates.length > 0) setSelectedDate(data.dates[0]);
            })
            .catch(err => console.error(err));
    }, []);

    const runScan = async () => {
        if (!selectedDate) return;
        setLoading(true);
        try {
            const q = `?threshold=${threshold}&only_anomalous=${onlyAnomalous}&limit=${limit}`;
            const res = await fetch(`${API_URL}/risk/scan-date/${selectedDate}${q}`);
            const data = await res.json();
            setScanResult(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
            <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-6 mb-8">
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-slate-100">Daily Batch Analysis</h2>
                    <span className="text-slate-400 text-sm font-medium uppercase tracking-wide">Production Simulation Mode</span>
                </div>

                <div className="bg-blue-900/20 border border-blue-900/50 rounded-lg p-4 flex gap-3 mb-6">
                    <span className="text-xl">ℹ️</span>
                    <p className="text-sm text-blue-200 leading-relaxed">
                        <strong>Production Flow Simulation:</strong> This simulates an end-of-day analysis where an exchange feeds all address transaction data.
                        The model evaluates each address against its historical baseline and current market/social context to generate risk scores.
                    </p>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 items-end">
                    <div className="w-full sm:w-1/3">
                        <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Analysis Date</label>
                        <div className="relative">
                            <select
                                value={selectedDate}
                                onChange={e => setSelectedDate(e.target.value)}
                                className="w-full appearance-none bg-slate-800 border border-slate-700 rounded-lg py-2.5 px-3 pr-10 text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-shadow"
                            >
                                {availableDates.map(d => <option key={d} value={d}>{d}</option>)}
                            </select>
                            <span className="absolute right-3 top-2.5 pointer-events-none text-slate-400">📅</span>
                        </div>
                    </div>

                    <button
                        className={`w-full sm:w-auto px-6 py-2.5 rounded-lg font-medium text-white transition-all shadow-sm flex items-center justify-center gap-2
              ${loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-md active:transform active:scale-95'}`}
                        onClick={runScan}
                        disabled={loading}
                    >
                        {loading ? 'Running Analysis...' : '🔍 Run Daily Analysis'}
                    </button>
                </div>
            </div>

            {scanResult && (
                <div className="animate-fade-in-up">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm text-center">
                            <span className="block text-3xl font-bold text-cyan-500 mb-1">{scanResult.total_wallets}</span>
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Total Analyzed</span>
                        </div>
                        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm text-center">
                            <span className="block text-3xl font-bold text-red-500 mb-1">{scanResult.flagged_count}</span>
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Flagged High Risk</span>
                        </div>
                        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm text-center">
                            <span className="block text-3xl font-bold text-yellow-500 mb-1">{scanResult.avg_probability}%</span>
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Avg Risk Score</span>
                        </div>
                    </div>

                    <h3 className="text-xl font-bold text-slate-100 mb-4 pl-2 border-l-4 border-blue-500">Analysis Results for {selectedDate}</h3>

                    <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-sm overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-slate-800">
                                <thead className="bg-slate-950">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">Address</th>
                                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">Risk Score</th>
                                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">Status</th>
                                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">Top Indicator</th>
                                    </tr>
                                </thead>
                                <tbody className="bg-slate-900 divide-y divide-slate-800">
                                    {scanResult.results.map((r, i) => (
                                        <tr key={i} className="hover:bg-slate-800 transition-colors">
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-300">{r.wallet_address}</td>
                                            <td className={`px-6 py-4 whitespace-nowrap text-sm font-bold ${r.risk_score > 75 ? 'text-red-500' : 'text-slate-200'}`}>
                                                {r.risk_score}%
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${r.is_flagged ? 'bg-red-900/30 text-red-300' : 'bg-green-900/30 text-green-300'
                                                    }`}>
                                                    {r.is_flagged ? 'Flagged' : 'Normal'}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500 italic">{r.top_reason}</td>
                                        </tr>
                                    ))}
                                    {scanResult.results.length === 0 && (
                                        <tr><td colSpan="4" className="px-6 py-8 text-center text-slate-500">No anomalies found for this date.</td></tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}

export default DailyBatchAnalysis;
