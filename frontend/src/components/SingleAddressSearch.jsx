import { useState, useEffect, useRef, useCallback } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import { API_URL } from '../config';

const HIGH_RISK_THRESHOLD = 75;
const MEDIUM_RISK_THRESHOLD = 50;

function SingleAddressSearch({ initialState }) {
    const [address, setAddress] = useState('');
    const [date, setDate] = useState('');
    const [availableDates, setAvailableDates] = useState([]);
    const [result, setResult] = useState(null);
    const [historyData, setHistoryData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const hasAutoAnalyzed = useRef(false);

    useEffect(() => {
        fetch(`${API_URL}/risk/available-dates`)
            .then(res => res.json())
            .then(data => {
                const dates = data.dates || [];
                setAvailableDates(dates);
                if (dates.length > 0 && !initialState) {
                    setDate(dates[0]);
                }
            })
            .catch(err => console.error('Failed to fetch dates:', err));
    }, [initialState]);

    useEffect(() => {
        if (initialState) {
            if (initialState.address) setAddress(initialState.address);
            if (initialState.date) {
                setDate(initialState.date);
                setAvailableDates(prev => {
                    if (!prev.includes(initialState.date)) {
                        return [initialState.date, ...prev].sort().reverse();
                    }
                    return prev;
                });
            }
        }
    }, [initialState]);

    const handleAnalyze = useCallback(async () => {
        if (!address || !date) return;
        setLoading(true);
        setError('');
        setResult(null);
        setHistoryData(null);

        try {
            const res1 = await fetch(`${API_URL}/risk/analyze-address?address=${address}&date=${date}`);
            if (!res1.ok) {
                const errData = await res1.json();
                throw new Error(errData.detail || 'Analysis failed');
            }
            setResult(await res1.json());

            const res2 = await fetch(`${API_URL}/risk/wallet-history/${address}`);
            if (res2.ok) {
                const data2 = await res2.json();
                if (data2.history) {
                    data2.history = data2.history.filter(h => h.date <= date);
                }
                setHistoryData(data2);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [address, date]);

    // Auto-analyze when coming from batch with autoAnalyze flag
    useEffect(() => {
        if (initialState?.autoAnalyze && address && date && !hasAutoAnalyzed.current) {
            hasAutoAnalyzed.current = true;
            handleAnalyze();
        }
    }, [initialState, address, date, handleAnalyze]);

    const getRiskColor = (score) => {
        if (score > HIGH_RISK_THRESHOLD) return 'text-red-500';
        if (score > MEDIUM_RISK_THRESHOLD) return 'text-yellow-500';
        return 'text-blue-500';
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
            <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-6 mb-8">
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-slate-100">Single Address Search</h2>
                    <span className="text-slate-400 text-sm font-medium uppercase tracking-wide">Model Transparency & Validation</span>
                </div>

                <div className="flex flex-col md:flex-row gap-4">
                    <div className="w-full md:w-1/2">
                        <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Ethereum Address</label>
                        <input
                            type="text"
                            value={address}
                            onChange={e => setAddress(e.target.value)}
                            placeholder="0x..."
                            className="w-full bg-slate-800 border border-slate-700 rounded-lg py-2.5 px-3 text-slate-200 font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                        />
                    </div>
                    <div className="w-full md:w-1/4">
                        <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Date</label>
                        <div className="relative">
                            <select
                                value={date}
                                onChange={e => setDate(e.target.value)}
                                className="w-full appearance-none bg-slate-800 border border-slate-700 rounded-lg py-2.5 px-3 pr-10 text-slate-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                            >
                                {availableDates.map(d => <option key={d} value={d}>{d}</option>)}
                            </select>
                            <span className="absolute right-3 top-2.5 pointer-events-none text-slate-400"></span>
                        </div>
                    </div>
                    <div className="w-full md:w-1/4 flex items-end">
                        <button
                            className={`w-full px-6 py-2.5 rounded-lg font-medium text-white transition-all shadow-sm flex items-center justify-center gap-2 ${loading ? 'bg-slate-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-md'}`}
                            onClick={handleAnalyze}
                            disabled={loading}
                        >
                            {loading ? 'Analyzing...' : 'Analyze'}
                        </button>
                    </div>
                </div>
                {error && <div className="mt-4 p-3 bg-red-900/30 text-red-300 rounded-lg text-sm border border-red-900/50">{error}</div>}
            </div>

            {result && (
                <div className="space-y-8 animate-fade-in-up">
                    {/* Risk Score Gauge */}
                    <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-8 flex flex-col md:flex-row items-center gap-8">
                        <div className="relative w-40 h-40 flex-shrink-0">
                            <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
                                <path className="text-slate-800" strokeWidth="3" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                <path
                                    className={`${getRiskColor(result.risk_score)} transition-all duration-1000 ease-out`}
                                    strokeDasharray={`${result.risk_score}, 100`}
                                    strokeWidth="3"
                                    strokeLinecap="round"
                                    stroke="currentColor"
                                    fill="none"
                                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                />
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className="text-4xl font-bold text-slate-100">{result.risk_score}</span>
                                <span className="text-xs font-bold text-slate-500 uppercase">Risk Score</span>
                            </div>
                        </div>

                        <div className="flex-1 text-center md:text-left">
                            <h3 className="text-xl font-bold text-slate-100 mb-2">Analysis Results</h3>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
                                <div className="p-3 bg-slate-800 rounded border border-slate-700">
                                    <span className="block text-xs font-bold text-slate-400 uppercase">Date</span>
                                    <span className="font-mono text-slate-300">{date}</span>
                                </div>
                                <div className="p-3 bg-slate-800 rounded border border-slate-700">
                                    <span className="block text-xs font-bold text-slate-400 uppercase">Address</span>
                                    <span className="font-mono text-slate-300 text-xs truncate block" title={address}>{address}</span>
                                </div>
                            </div>
                            <div className={`inline-block px-4 py-2 rounded-lg font-bold text-sm tracking-wide ${result.is_flagged ? 'bg-red-900/30 text-red-300' : 'bg-green-900/30 text-green-300'}`}>
                                {result.is_flagged ? 'HIGH RISK DETECTED' : 'NORMAL ACTIVITY'}
                            </div>
                        </div>
                    </div>

                    {/* Feature Analysis */}
                    {result.feature_analysis && result.feature_analysis.length > 0 && (
                        <div>
                            <div className="mb-6">
                                <h3 className="text-xl font-bold text-slate-100">Detection Analysis</h3>
                                <p className="text-slate-400 text-sm">Comparison against historical baseline</p>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                                {result.feature_analysis.map((feat, i) => (
                                    <div key={i} className="bg-slate-900 p-6 rounded-xl border border-slate-800 shadow-sm hover:shadow-md transition-shadow">
                                        <div className="flex justify-between items-start mb-4">
                                            <h4 className="font-bold text-slate-200 text-sm">{feat.feature}</h4>
                                            <span className={`px-2 py-1 rounded text-xs font-mono font-medium ${Math.abs(feat.z_score) > 2 ? 'bg-red-900/30 text-red-300' : 'bg-slate-800 text-slate-400'}`}>
                                                z={feat.z_score.toFixed(2)}
                                            </span>
                                        </div>

                                        {feat.explanation && (
                                            <div className="mb-4 p-3 bg-red-900/20 text-red-300 text-xs rounded border border-red-900/40 leading-relaxed">
                                                {feat.explanation}
                                            </div>
                                        )}

                                        <div className="space-y-3">
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-slate-500 font-medium text-xs uppercase">Current</span>
                                                <span className="font-mono font-bold text-slate-200 bg-slate-800 px-2 py-0.5 rounded">{feat.value}</span>
                                            </div>
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-slate-500 font-medium text-xs uppercase">Baseline</span>
                                                <span className="font-mono text-slate-500">{feat.baseline}</span>
                                            </div>
                                            <div className="pt-2 border-t border-slate-800 flex justify-between items-center text-sm">
                                                <span className="text-slate-500 font-medium text-xs uppercase">Change</span>
                                                <span className={`font-mono font-bold ${feat.change_pct > 0 ? 'text-emerald-500' : 'text-red-500'}`}>
                                                    {feat.change_pct > 0 ? '+' : ''}{feat.change_pct}%
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* History Chart */}
                    {historyData && historyData.history && historyData.history.length > 0 && (
                        <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-6">
                            <div className="mb-6 flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
                                <div>
                                    <h3 className="text-xl font-bold text-slate-100">Historical Activity (up to {date})</h3>
                                    <p className="text-slate-400 text-sm">Past activity pattern</p>
                                </div>

                                {historyData.stats && (
                                    <div className="flex gap-4">
                                        <div className="text-center px-4 py-2 bg-slate-800 rounded border border-slate-700">
                                            <span className="block text-lg font-bold text-blue-500">{historyData.stats.avg_risk_score}</span>
                                            <span className="text-[10px] font-bold text-slate-500 uppercase">Avg Score</span>
                                        </div>
                                        <div className="text-center px-4 py-2 bg-slate-800 rounded border border-slate-700">
                                            <span className="block text-lg font-bold text-purple-500">{historyData.stats.avg_daily_tx}</span>
                                            <span className="text-[10px] font-bold text-slate-500 uppercase">Avg Tx</span>
                                        </div>
                                    </div>
                                )}
                            </div>

                            <div className="h-[300px] w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={historyData.history}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                        <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} minTickGap={30} dy={10} />
                                        <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} tickLine={false} axisLine={false} domain={[0, 100]} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px' }}
                                            itemStyle={{ color: '#f8fafc', fontSize: '13px' }}
                                        />
                                        <Line type="monotone" dataKey="risk_score" stroke="#3b82f6" strokeWidth={3} dot={{ r: 3, fill: '#3b82f6', strokeWidth: 0 }} activeDot={{ r: 6 }} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default SingleAddressSearch;
