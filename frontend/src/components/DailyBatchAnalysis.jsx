import { useState, useRef } from 'react';
import { API_URL } from '../config';

const RISK_THRESHOLD = 0.5;
const HIGH_RISK_THRESHOLD = 75;
const MEDIUM_RISK_THRESHOLD = 50;

function DailyBatchAnalysis() {
    const [scanResult, setScanResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [selectedFile, setSelectedFile] = useState(null);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) setSelectedFile(file);
    };

    const runAnalysis = async () => {
        if (!selectedFile) {
            alert('Please select a CSV file first');
            return;
        }

        setLoading(true);
        setScanResult(null);

        try {
            const formData = new FormData();
            formData.append('file', selectedFile);

            const res = await fetch(`${API_URL}/risk/analyze-batch?threshold=${RISK_THRESHOLD}`, {
                method: 'POST',
                body: formData
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || `Analysis failed: ${res.status}`);
            }

            const data = await res.json();
            if (!data.results) data.results = [];
            setScanResult(data);
        } catch (err) {
            console.error(err);
            alert(`Analysis failed: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleAddressClick = (result) => {
        const params = new URLSearchParams({
            address: result.wallet_address,
            date: scanResult.analysis_date,
            auto: 'true'
        });
        window.open(`/#single-search?${params.toString()}`, '_blank');
    };

    const getRiskColor = (score) => {
        if (score > HIGH_RISK_THRESHOLD) return 'text-red-500';
        if (score > MEDIUM_RISK_THRESHOLD) return 'text-yellow-500';
        return 'text-green-500';
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
            <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-6 mb-8">
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-slate-100">Daily Batch Analysis</h2>
                    <span className="text-slate-400 text-sm font-medium uppercase tracking-wide">Upload Transaction CSV</span>
                </div>

                <div className="bg-blue-900/20 border border-blue-900/50 rounded-lg p-4 flex gap-3 mb-6">
                    <span className="text-xl">ℹ️</span>
                    <p className="text-sm text-blue-200 leading-relaxed">
                        <strong>Upload Mode:</strong> Upload a CSV with on-chain features (address, date, features).
                        <br /><span className="text-blue-300 text-xs mt-1 block">Click any address to open in new tab.</span>
                    </p>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 items-end">
                    <div className="w-full sm:flex-1">
                        <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">CSV File</label>
                        <div className="relative">
                            <input ref={fileInputRef} type="file" accept=".csv" onChange={handleFileChange} className="hidden" />
                            <button
                                onClick={() => fileInputRef.current?.click()}
                                className="w-full flex items-center justify-between bg-slate-800 border border-slate-700 rounded-lg py-2.5 px-3 text-slate-200 hover:border-blue-500 transition-colors"
                            >
                                <span className="truncate">{selectedFile ? selectedFile.name : 'Choose CSV file...'}</span>
                                <span className="text-slate-400 ml-2"></span>
                            </button>
                        </div>
                    </div>

                    <button
                        className={`w-full sm:w-auto px-6 py-2.5 rounded-lg font-medium text-white transition-all shadow-sm flex items-center justify-center gap-2
                            ${loading || !selectedFile ? 'bg-slate-600 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 hover:shadow-md active:scale-95'}`}
                        onClick={runAnalysis}
                        disabled={loading || !selectedFile}
                    >
                        {loading ? 'Analyzing...' : 'Analyze'}
                    </button>
                </div>
            </div>

            {scanResult && (
                <div className="animate-fade-in-up">
                    {/* Validation Metrics */}
                    {scanResult.has_validation && scanResult.validation && (
                        <div className="bg-gradient-to-r from-emerald-900/30 to-blue-900/30 rounded-xl border border-emerald-800/50 p-6 mb-8">
                            <div className="flex items-center gap-3 mb-4">
                                <h3 className="text-xl font-bold text-emerald-300">Validation Results</h3>
                            </div>

                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                                <div className="bg-slate-900/50 p-4 rounded-lg text-center">
                                    <span className="block text-3xl font-bold text-emerald-400">{(scanResult.validation.accuracy * 100).toFixed(1)}%</span>
                                    <span className="text-xs font-bold text-slate-400 uppercase">Accuracy</span>
                                </div>
                                <div className="bg-slate-900/50 p-4 rounded-lg text-center">
                                    <span className="block text-3xl font-bold text-blue-400">{(scanResult.validation.precision * 100).toFixed(1)}%</span>
                                    <span className="text-xs font-bold text-slate-400 uppercase">Precision</span>
                                </div>
                                <div className="bg-slate-900/50 p-4 rounded-lg text-center">
                                    <span className="block text-3xl font-bold text-purple-400">{(scanResult.validation.recall * 100).toFixed(1)}%</span>
                                    <span className="text-xs font-bold text-slate-400 uppercase">Recall</span>
                                </div>
                                <div className="bg-slate-900/50 p-4 rounded-lg text-center">
                                    <span className="block text-3xl font-bold text-cyan-400">{(scanResult.validation.f1_score * 100).toFixed(1)}%</span>
                                    <span className="text-xs font-bold text-slate-400 uppercase">F1-Score</span>
                                </div>
                            </div>

                            <div className="bg-slate-900/50 rounded-lg p-4">
                                <h4 className="text-sm font-bold text-slate-300 mb-3 text-center">Confusion Matrix</h4>
                                <div className="grid grid-cols-3 gap-2 max-w-md mx-auto text-center text-sm">
                                    <div></div>
                                    <div className="text-slate-400 font-bold text-xs">Pred: Anomaly</div>
                                    <div className="text-slate-400 font-bold text-xs">Pred: Normal</div>

                                    <div className="text-slate-400 font-bold text-xs flex items-center">Actual: Anomaly</div>
                                    <div className="bg-emerald-900/30 border border-emerald-700/50 rounded p-2">
                                        <span className="text-emerald-400 font-bold">{scanResult.validation.true_positives}</span>
                                        <span className="block text-[10px] text-emerald-500">TP</span>
                                    </div>
                                    <div className="bg-red-900/30 border border-red-700/50 rounded p-2">
                                        <span className="text-red-400 font-bold">{scanResult.validation.false_negatives}</span>
                                        <span className="block text-[10px] text-red-500">FN</span>
                                    </div>

                                    <div className="text-slate-400 font-bold text-xs flex items-center">Actual: Normal</div>
                                    <div className="bg-red-900/30 border border-red-700/50 rounded p-2">
                                        <span className="text-red-400 font-bold">{scanResult.validation.false_positives}</span>
                                        <span className="block text-[10px] text-red-500">FP</span>
                                    </div>
                                    <div className="bg-emerald-900/30 border border-emerald-700/50 rounded p-2">
                                        <span className="text-emerald-400 font-bold">{scanResult.validation.true_negatives}</span>
                                        <span className="block text-[10px] text-emerald-500">TN</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Summary Stats */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                        <div className="bg-slate-900 p-5 rounded-xl border border-slate-800 text-center">
                            <span className="block text-2xl font-bold text-cyan-500">{scanResult.total_addresses}</span>
                            <span className="text-xs font-bold text-slate-400 uppercase">Total</span>
                        </div>
                        <div className="bg-slate-900 p-5 rounded-xl border border-slate-800 text-center">
                            <span className="block text-2xl font-bold text-red-500">{scanResult.flagged_count}</span>
                            <span className="text-xs font-bold text-slate-400 uppercase">Flagged</span>
                        </div>
                        <div className="bg-slate-900 p-5 rounded-xl border border-slate-800 text-center">
                            <span className="block text-2xl font-bold text-orange-500">{scanResult.high_risk_count}</span>
                            <span className="text-xs font-bold text-slate-400 uppercase">High Risk</span>
                        </div>
                        <div className="bg-slate-900 p-5 rounded-xl border border-slate-800 text-center">
                            <span className="block text-2xl font-bold text-green-500">{scanResult.low_risk_count}</span>
                            <span className="text-xs font-bold text-slate-400 uppercase">Low Risk</span>
                        </div>
                    </div>

                    <h3 className="text-lg font-bold text-slate-100 mb-4 pl-2 border-l-4 border-blue-500">
                        Results for {scanResult.analysis_date}
                    </h3>

                    <div className="bg-slate-900 rounded-xl border border-slate-800 overflow-hidden">
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-slate-800">
                                <thead className="bg-slate-950">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase">Address</th>
                                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase">Risk</th>
                                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase">Status</th>
                                        {scanResult.has_validation && <th className="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase">Truth</th>}
                                        {scanResult.has_validation && <th className="px-6 py-3 text-center text-xs font-bold text-slate-400 uppercase">Correct</th>}
                                        <th className="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase">Indicator</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-800">
                                    {scanResult.results.map((r, i) => (
                                        <tr
                                            key={i}
                                            className={`hover:bg-slate-800 cursor-pointer transition-colors ${scanResult.has_validation && !r.is_correct ? 'bg-red-900/10' : ''}`}
                                            onClick={() => handleAddressClick(r)}
                                        >
                                            <td className="px-6 py-4 text-sm font-mono text-blue-400 underline">
                                                {r.wallet_address.slice(0, 10)}...{r.wallet_address.slice(-6)}
                                            </td>
                                            <td className={`px-6 py-4 text-sm font-bold ${getRiskColor(r.risk_score)}`}>
                                                {r.risk_score}%
                                            </td>
                                            <td className="px-6 py-4 text-sm">
                                                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${r.is_flagged ? 'bg-red-900/30 text-red-300' : 'bg-green-900/30 text-green-300'}`}>
                                                    {r.is_flagged ? 'Flagged' : 'Normal'}
                                                </span>
                                            </td>
                                            {scanResult.has_validation && (
                                                <td className="px-6 py-4 text-sm">
                                                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${r.ground_truth ? 'bg-red-900/30 text-red-300' : 'bg-green-900/30 text-green-300'}`}>
                                                        {r.ground_truth ? 'Anomaly' : 'Normal'}
                                                    </span>
                                                </td>
                                            )}
                                            {scanResult.has_validation && (
                                                <td className="px-6 py-4 text-center">{r.is_correct ? '✅' : '❌'}</td>
                                            )}
                                            <td className="px-6 py-4 text-sm text-slate-500 italic">{r.top_reason}</td>
                                        </tr>
                                    ))}
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
