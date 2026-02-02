function ModelDetails() {

    const metrics = {
        accuracy: 72.0,
        precision: 73.5,
        recall: 68.8,
        f1Score: 71.1,
        rocAuc: 0.79
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
            {/* Intro Header */}
            <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-8 mb-8 text-center">
                <h2 className="text-3xl font-bold text-slate-100 mb-2">Model Architecture & Methodology</h2>
                <span className="text-blue-400 font-medium block mb-6">Understanding FuseChain&apos;s Multimodal Detection Framework</span>

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
                        { num: 3, title: 'Labeling & Balancing', items: ['Z-score threshold (|z| > 1.5)', 'Balance to 50:50 ratio', 'Before feature selection'] },
                        { num: 4, title: 'Feature Selection', items: ['Weka InfoGain ranking', 'Top 4 on-chain features', 'Ablation study validation'] },
                        { num: 5, title: 'Feature Fusion', items: ['4 On-chain + 3 Social', '+ 3 Market features', '10 total features'] },
                        { num: 6, title: 'Address-Level Split', items: ['Split by address (80/20)', 'All days per address together', 'Prevents data leakage'] }
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
                <h3 className="text-xl font-bold text-slate-100 border-l-4 border-indigo-500 pl-4 mb-6">Feature Set </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                        {
                            title: 'On-Chain Features (4)',
                            color: 'border-t-4 border-cyan-500',
                            items: [
                                'normal_total_cnt',
                                'uniq_peers_cnt',
                                'burst_max_tx_5m',
                                'normal_sent_cnt'
                            ]
                        },
                        {
                            title: 'Social Signals (3)',
                            color: 'border-t-4 border-purple-500',
                            items: [
                                'reddit_fraud_mention_ratio',
                                'reddit_total_activity',
                                'reddit_avg_sentiment'
                            ]
                        },
                        {
                            title: 'Market Dynamics (3)',
                            color: 'border-t-4 border-pink-500',
                            items: [
                                'eth_volatility_7d',
                                'eth_daily_return',
                                'eth_intraday_volatility'
                            ]
                        }
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
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                    {[
                        { label: 'Accuracy', val: `${metrics.accuracy.toFixed(1)}%`, color: 'text-cyan-400' },
                        { label: 'Precision', val: `${metrics.precision.toFixed(1)}%`, color: 'text-blue-400' },
                        { label: 'Recall', val: `${metrics.recall.toFixed(1)}%`, color: 'text-purple-400' },
                        { label: 'F1 Score', val: `${metrics.f1Score.toFixed(2)}`, color: 'text-yellow-400' },
                        { label: 'AUC-ROC', val: `${metrics.rocAuc.toFixed(2)}`, color: 'text-pink-400' }
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
                            <strong className="text-blue-400">On-Chain Dominance:</strong> Transaction count (normal_total_cnt) accounts for 63% of model importance, indicating on-chain behavior is the strongest anomaly indicator.
                        </li>
                        <li className="text-slate-400 text-sm leading-relaxed">
                            <strong className="text-blue-400">Feature Selection Impact:</strong> Removing active_span_min improved model AUC, showing ablation study value.
                        </li>
                        <li className="text-slate-400 text-sm leading-relaxed">
                            <strong className="text-blue-400">Off-Chain Context:</strong> Social and market features provide ~5% additional signal for robustness.
                        </li>
                    </ul>
                </div>

                <div className="bg-slate-900 rounded-xl border border-slate-800 p-6 shadow-sm">
                    <h3 className="text-xl font-bold text-slate-100 mb-4 border-b border-slate-800 pb-2">Methodology Innovations</h3>
                    <ul className="space-y-3">
                        <li className="text-slate-400 text-sm leading-relaxed">
                            <strong className="text-emerald-400">Balance-First Strategy:</strong> Dataset balanced to 50:50 before feature selection and Weka analysis.
                        </li>
                        <li className="text-slate-400 text-sm leading-relaxed">
                            <strong className="text-emerald-400">Address-Level Split:</strong> All days per address stay in same split to prevent temporal leakage.
                        </li>
                        <li className="text-slate-400 text-sm leading-relaxed">
                            <strong className="text-emerald-400">Explainable AI:</strong> Real-time SHAP feature contribution analysis provides transparency.
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

export default ModelDetails;
