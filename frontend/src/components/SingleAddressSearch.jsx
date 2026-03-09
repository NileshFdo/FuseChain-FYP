import { useState, useEffect, useRef, useCallback } from 'react';
import { API_URL } from '../config';

function SingleAddressSearch({ initialState }) {
    const [address, setAddress] = useState('');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showAllFeatures, setShowAllFeatures] = useState(false);
    const hasAutoAnalyzed = useRef(false);

    useEffect(() => {
        if (initialState?.address) {
            setAddress(initialState.address);
        }
    }, [initialState]);

    const handleAnalyze = useCallback(async () => {
        if (!address) return;
        setLoading(true);
        setError('');
        setResult(null);
        setShowAllFeatures(false);

        try {
            const res = await fetch(`${API_URL}/risk/analyze/${address}`);
            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || 'Analysis failed');
            }
            setResult(await res.json());
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [address]);

    useEffect(() => {
        if (initialState?.autoAnalyze && address && !hasAutoAnalyzed.current) {
            hasAutoAnalyzed.current = true;
            handleAnalyze();
        }
    }, [initialState, address, handleAnalyze]);

    const getRiskColor = (score) => {
        if (score > 0.75) return 'text-red-500';
        if (score > 0.5) return 'text-yellow-500';
        return 'text-blue-500';
    };

    const getStrokeColor = (score) => {
        if (score > 0.75) return '#ef4444';
        if (score > 0.5) return '#eab308';
        return '#3b82f6';
    };

    const modalityColors = {
        on_chain: { bg: 'bg-emerald-500', text: 'text-emerald-400', bar: '#34d399' },
        market: { bg: 'bg-blue-500', text: 'text-blue-400', bar: '#60a5fa' },
        reddit: { bg: 'bg-orange-500', text: 'text-orange-400', bar: '#fb923c' },
        twitter: { bg: 'bg-sky-500', text: 'text-sky-400', bar: '#38bdf8' },
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
            {/* Search Bar */}
            <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-6 mb-8">
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-slate-100">Single Address Search</h2>
                    <span className="text-slate-400 text-sm font-medium uppercase tracking-wide">Model Transparency & Validation</span>
                </div>

                <div className="flex flex-col md:flex-row gap-4">
                    <div className="w-full md:w-3/4">
                        <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Ethereum Address</label>
                        <input
                            type="text"
                            value={address}
                            onChange={e => setAddress(e.target.value)}
                            placeholder="0x..."
                            className="w-full bg-slate-800 border border-slate-700 rounded-lg py-2.5 px-3 text-slate-200 font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                        />
                    </div>
                    <div className="w-full md:w-1/4 flex items-end">
                        <button
                            className={`w-full px-6 py-2.5 rounded-lg font-medium text-white transition-all shadow-sm flex items-center justify-center gap-2 ${loading ? 'bg-slate-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-md'}`}
                            onClick={handleAnalyze}
                            disabled={loading || !address}
                        >
                            {loading ? 'Analyzing...' : 'Analyze'}
                        </button>
                    </div>
                </div>
                {error && <div className="mt-4 p-3 bg-red-900/30 text-red-300 rounded-lg text-sm border border-red-900/50">{error}</div>}
            </div>

            {result && (
                <div className="space-y-6 animate-fade-in-up">
                    {/* 1. Risk Score + Verdict */}
                    <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-8 flex flex-col md:flex-row items-center gap-8">
                        <div className="relative w-40 h-40 flex-shrink-0">
                            <svg viewBox="0 0 36 36" className="w-full h-full transform -rotate-90">
                                <path className="text-slate-800" strokeWidth="3" stroke="currentColor" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                                <path
                                    stroke={getStrokeColor(result.risk_score)}
                                    strokeDasharray={`${result.risk_score * 100}, 100`}
                                    strokeWidth="3"
                                    strokeLinecap="round"
                                    fill="none"
                                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                                    className="transition-all duration-1000 ease-out"
                                />
                            </svg>
                            <div className="absolute inset-0 flex flex-col items-center justify-center">
                                <span className={`text-4xl font-bold ${getRiskColor(result.risk_score)}`}>
                                    {(result.risk_score * 100).toFixed(1)}%
                                </span>
                                <span className="text-xs font-bold text-slate-500 uppercase">Risk Score</span>
                            </div>
                        </div>

                        <div className="flex-1 text-center md:text-left">
                            <h3 className="text-xl font-bold text-slate-100 mb-2">Analysis Results</h3>
                            <div className="p-3 bg-slate-800 rounded border border-slate-700 mb-4">
                                <span className="block text-xs font-bold text-slate-400 uppercase">Address</span>
                                <span className="font-mono text-slate-300 text-xs truncate block" title={address}>{address}</span>
                            </div>
                            <div className={`inline-block px-4 py-2 rounded-lg font-bold text-sm tracking-wide ${result.is_flagged ? 'bg-red-900/30 text-red-300' : 'bg-green-900/30 text-green-300'}`}>
                                {result.is_flagged ? 'HIGH RISK DETECTED' : 'NORMAL ACTIVITY'}
                            </div>
                        </div>
                    </div>

                    {/* 2. Narrative Explanation */}
                    {result.narrative && (
                        <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-6">
                            <h3 className="text-lg font-bold text-slate-100 mb-3 flex items-center gap-2">
                                Why was this address flagged?
                            </h3>
                            <p className="text-slate-300 leading-relaxed text-sm bg-slate-800/50 p-4 rounded-lg border border-slate-700/50 italic">
                                {result.narrative}
                            </p>
                        </div>
                    )}

                    {/* 3. Key Risk Factors (descriptive) */}
                    {result.top_reasons && result.top_reasons.length > 0 && (
                        <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-6">
                            <h3 className="text-lg font-bold text-slate-100 mb-4 flex items-center gap-2">
                                Key Contributing Factors
                            </h3>
                            <div className="space-y-3">
                                {result.top_reasons.map((reason, idx) => (
                                    <div key={idx} className="p-3 bg-slate-800 rounded-lg border border-slate-700/50 flex items-start gap-3">
                                        <span className={`mt-0.5 w-5 h-5 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-bold ${result.is_flagged ? 'bg-red-900/50 text-red-400' : 'bg-green-900/50 text-green-400'}`}>
                                            {idx + 1}
                                        </span>
                                        <span className="text-sm text-slate-300 leading-relaxed">{reason}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* 4. SHAP Bar Chart — Top 8 Features */}
                    {result.top_shap_features && result.top_shap_features.length > 0 && (
                        <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-6">
                            <h3 className="text-lg font-bold text-slate-100 mb-2 flex items-center gap-2">
                                SHAP Feature Impact
                            </h3>
                            <p className="text-slate-500 text-xs mb-5">Features that most influenced this prediction. Red bars increase risk; green bars decrease it.</p>

                            <div className="space-y-3">
                                {result.top_shap_features.map((feat, idx) => {
                                    const maxVal = Math.max(...result.top_shap_features.map(f => Math.abs(f.shap_value)));
                                    const barWidth = maxVal > 0 ? (Math.abs(feat.shap_value) / maxVal) * 100 : 0;
                                    const isPositive = feat.shap_value > 0;
                                    const modColor = modalityColors[feat.modality] || { bg: 'bg-slate-500', text: 'text-slate-400' };

                                    return (
                                        <div key={idx} className="flex items-center gap-4">
                                            {/* Feature name */}
                                            <div className="w-48 flex-shrink-0 text-right">
                                                <span className="text-xs text-slate-300 font-medium">{feat.display_name}</span>
                                                <span className={`ml-2 w-2 h-2 rounded-full inline-block ${modColor.bg}`}></span>
                                            </div>

                                            {/* Bar */}
                                            <div className="flex-1 h-6 bg-slate-800 rounded overflow-hidden relative">
                                                <div
                                                    className={`absolute top-0 left-0 h-full rounded transition-all duration-700 ease-out ${isPositive ? 'bg-red-500/70' : 'bg-emerald-500/70'}`}
                                                    style={{ width: `${barWidth}%` }}
                                                />
                                                <span className="absolute inset-0 flex items-center px-2 text-xs font-mono text-slate-200 font-medium">
                                                    {isPositive ? '+' : ''}{feat.shap_value.toFixed(3)}
                                                </span>
                                            </div>

                                            {/* Value */}
                                            <div className="w-20 text-right flex-shrink-0">
                                                <span className="text-xs font-mono text-slate-400">
                                                    {feat.value !== undefined && feat.value !== null
                                                        ? (Number.isInteger(feat.value) ? feat.value : feat.value.toFixed(2))
                                                        : '—'}
                                                </span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Legend */}
                            <div className="flex items-center gap-6 mt-5 pt-4 border-t border-slate-800">
                                {Object.entries(modalityColors).map(([key, val]) => (
                                    <div key={key} className="flex items-center gap-1.5">
                                        <span className={`w-2 h-2 rounded-full ${val.bg}`}></span>
                                        <span className="text-xs text-slate-500 capitalize">{key.replace('_', '-')}</span>
                                    </div>
                                ))}
                                <div className="ml-auto flex items-center gap-4">
                                    <div className="flex items-center gap-1.5">
                                        <span className="w-3 h-2 rounded bg-red-500/70"></span>
                                        <span className="text-xs text-slate-500">Increases Risk</span>
                                    </div>
                                    <div className="flex items-center gap-1.5">
                                        <span className="w-3 h-2 rounded bg-emerald-500/70"></span>
                                        <span className="text-xs text-slate-500">Decreases Risk</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* 5. Expandable raw features */}
                    {(result.on_chain_features || result.market_features || result.reddit_features || result.twitter_features) && (
                        <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 overflow-hidden">
                            <button
                                onClick={() => setShowAllFeatures(!showAllFeatures)}
                                className="w-full p-4 flex items-center justify-between text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-colors"
                            >
                                <span className="text-sm font-medium">
                                    {showAllFeatures ? 'Hide' : 'Show'} All Raw Features
                                </span>
                                <span className={`transform transition-transform ${showAllFeatures ? 'rotate-180' : ''}`}>
                                    ▼
                                </span>
                            </button>

                            {showAllFeatures && (
                                <div className="p-6 pt-0 space-y-6 animate-fade-in">
                                    {[
                                        { key: 'on_chain_features', title: 'On-Chain Behavior', color: 'bg-emerald-500' },
                                        { key: 'market_features', title: 'Market Conditions', color: 'bg-blue-500' },
                                        { key: 'reddit_features', title: 'Reddit Context', color: 'bg-orange-500' },
                                        { key: 'twitter_features', title: 'Twitter Context', color: 'bg-sky-500' }
                                    ].map(({ key, title, color }) => {
                                        const features = result[key];
                                        if (!features || Object.keys(features).length === 0) return null;
                                        const shap = result.shap_contributions || {};

                                        return (
                                            <div key={key}>
                                                <h4 className="text-sm font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center gap-2">
                                                    <span className={`w-2 h-2 rounded-full ${color}`}></span>
                                                    {title}
                                                </h4>
                                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                                    {Object.entries(features).map(([featureName, value]) => {
                                                        const contribution = shap[featureName] ?? 0;
                                                        return (
                                                            <div key={featureName} className="bg-slate-800/50 p-3 rounded-lg border border-slate-700/50">
                                                                <div className="flex justify-between items-start mb-1">
                                                                    <span className="text-xs font-medium text-slate-400">{featureName}</span>
                                                                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono font-medium ${contribution > 0 ? 'bg-red-900/30 text-red-400' : 'bg-green-900/30 text-green-400'}`}>
                                                                        {contribution > 0 ? '+' : ''}{contribution.toFixed(3)}
                                                                    </span>
                                                                </div>
                                                                <span className="font-mono text-sm text-slate-200">
                                                                    {typeof value === 'number' ? (Number.isInteger(value) ? value : value.toFixed(4)) : value}
                                                                </span>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export default SingleAddressSearch;
