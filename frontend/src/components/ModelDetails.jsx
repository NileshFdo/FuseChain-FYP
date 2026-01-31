
function ModelDetails() {
    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
            {/* Intro Header */}
            <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-8 mb-8 text-center">
                <h2 className="text-3xl font-bold text-slate-100 mb-2">Model Architecture & Methodology</h2>
                <span className="text-blue-400 font-medium block mb-6">Understanding FuseChain's Multimodal Detection Framework</span>

                <div className="bg-blue-900/20 border border-blue-900/50 rounded-lg p-6 max-w-3xl mx-auto">
                    <p className="text-slate-300 leading-relaxed">
                        ℹ️ <strong>Research Framework:</strong> FuseChain implements a supervised multimodal anomaly detection system that fuses on-chain transaction features with off-chain market and social signals to identify unusual behavioral patterns in Ethereum addresses.
                    </p>
                </div>
            </div>

            {/* Methodology Pipeline */}
            <div className="mb-12">
                <h3 className="text-xl font-bold text-slate-100 border-l-4 border-blue-500 pl-4 mb-6">Methodology Pipeline</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[
                        { num: 1, title: 'Data Collection', items: ['On-Chain: ETH txs (2017-2021)', 'Market: CoinMarketCap OHLCV', 'Social: Reddit sentiment'] },
                        { num: 2, title: 'Temporal Alignment', items: ['Daily aggregation', 'UTC timestamp sync', 'Forward-fill missing values'] },
                        { num: 3, title: 'Baseline Computation', items: ['Mean/Std per address', 'Z-score calculation', 'Labeling (|z| > 1.5)'] },
                        { num: 4, title: 'Balanced Sampling', items: ['Stratified sampling', '1:1 Anomaly/Normal ratio', 'Preserve context'] },
                        { num: 5, title: 'Feature Fusion', items: ['Combine 3 domains', 'StandardScaler Norm', '~30 Features total'] },
                        { num: 6, title: 'XGBoost Training', items: ['80/20 Split', 'Grid Search', 'Eval: F1, ROC-AUC'] }
                    ].map((step) => (
                        <div key={step.num} className="bg-slate-900 p-6 rounded-lg border border-slate-800 shadow-sm hover:shadow-md transition-shadow flex gap-4">
                            <span className="text-4xl font-black text-slate-800" style={{ WebkitTextStroke: '1px #475569' }}>{step.num}</span>
                            <div>
                                <h4 className="font-bold text-slate-200 mb-3">{step.title}</h4>
                                <ul className="space-y-2">
                                    {step.items.map((item, i) => (
                                        <li key={i} className="text-sm text-slate-400 flex items-start gap-2">
                                            <span className="text-blue-500 font-bold">›</span> {item}
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Feature Domain */}
            <div className="mb-12">
                <h3 className="text-xl font-bold text-slate-100 border-l-4 border-indigo-500 pl-4 mb-6">Multimodal Feature Domain</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                        { title: '🔗 On-Chain Features', color: 'border-t-4 border-cyan-500', items: ['Tx Frequency (Burst/Daily)', 'Unique Peers', 'Volume (ETH Sent/Recv)', 'Temporal Intervals'] },
                        { title: '💬 Social Signals', color: 'border-t-4 border-purple-500', items: ['Fraud Keyword Ratio', 'Sentiment Analysis', 'Activity Spikes', 'Anomaly Correlation'] },
                        { title: '📈 Market Dynamics', color: 'border-t-4 border-pink-500', items: ['Price Volatility (7d)', 'Intraday Movement', 'Volume/Price Correlation', 'Stress Indicators'] }
                    ].map((card, idx) => (
                        <div key={idx} className={`bg-slate-900 p-6 rounded-lg shadow-sm border border-slate-800 ${card.color}`}>
                            <h3 className="font-bold text-lg text-slate-200 mb-4">{card.title}</h3>
                            <ul className="space-y-2">
                                {card.items.map((item, i) => (
                                    <li key={i} className="text-sm text-slate-400 flex items-center gap-2">
                                        <span className="w-1.5 h-1.5 bg-slate-600 rounded-full"></span> {item}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            </div>

            {/* Metrics */}
            <div className="mb-12">
                <h3 className="text-xl font-bold text-slate-100 border-l-4 border-emerald-500 pl-4 mb-6">Performance Metrics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {[
                        { label: 'Accuracy', val: '75.4%', color: 'text-cyan-400' },
                        { label: 'AUC-ROC', val: '0.83', color: 'text-purple-400' },
                        { label: 'Precision', val: '76.0%', color: 'text-pink-400' },
                        { label: 'F1 Score', val: '0.75', color: 'text-yellow-400' }
                    ].map((m, i) => (
                        <div key={i} className="bg-slate-900 p-6 rounded-lg border border-slate-800 shadow-sm text-center">
                            <span className={`block text-3xl font-extrabold mb-1 ${m.color}`}>{m.val}</span>
                            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">{m.label}</span>
                        </div>
                    ))}
                </div>
            </div>
            {/* Research Findings & Innovations */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 shadow-sm">
                    <h3 className="text-xl font-bold text-slate-100 mb-4 border-b border-slate-800 pb-2">Key Research Findings</h3>
                    <ul className="space-y-3">
                        <li className="text-slate-400 text-sm leading-relaxed">
                            <strong className="text-blue-400">Cross-Domain Correlation:</strong> Addresses flagged as high-risk on-chain often coincide with negative sentiment spikes on Reddit (r/ethereum).
                        </li>
                        <li className="text-slate-400 text-sm leading-relaxed">
                            <strong className="text-blue-400">Burst Behavior:</strong> Fraudulent bots exhibit "burst" transaction patterns that are statistically distinct from human users (z-score &gt; 3.0).
                        </li>
                        <li className="text-slate-400 text-sm leading-relaxed">
                            <strong className="text-blue-400">Market Sensitivity:</strong> Anomaly detection precision improves by 14% when incorporating market volatility features.
                        </li>
                    </ul>
                </div>

                <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 shadow-sm">
                    <h3 className="text-xl font-bold text-slate-100 mb-4 border-b border-slate-800 pb-2">Methodology Innovations</h3>
                    <ul className="space-y-3">
                        <li className="text-slate-400 text-sm leading-relaxed">
                            <strong className="text-emerald-400">Pseudo-Labeling via Z-Score:</strong> We utilize statistical outlier detection (z &gt; 2.0) on historical data to generate reliable training labels.
                        </li>
                        <li className="text-slate-400 text-sm leading-relaxed">
                            <strong className="text-emerald-400">Multimodal Fusion:</strong> Concatenating dense feature vectors from three distinct domains (Block, Social, Market) before XGBoost training.
                        </li>
                        <li className="text-slate-400 text-sm leading-relaxed">
                            <strong className="text-emerald-400">Explainable AI (XAI):</strong> Real-time SHAP-like feature contribution analysis provides transparency for every detection.
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default ModelDetails;
