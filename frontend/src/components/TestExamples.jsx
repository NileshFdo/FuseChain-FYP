
function TestExamples({ onSelect }) {
    const examples = [
        {
            address: '0xf0e472ef169824777296f02fb2a8e9eeaa6b511d',
            normal: '2017-05-31',
            anomaly: '2021-10-07'
        },
        {
            address: '0x31fce7fd6931f7b5a6a756a219496f1eb0fdc54e',
            normal: '2018-04-10',
            anomaly: '2017-07-16'
        },
        {
            address: '0x578259a8ad60a9d49a86b036bcead82536a17f70',
            normal: '2019-04-06',
            anomaly: '2021-03-24'
        },
        {
            address: '0xa01dd79c6a09cd5d51278dba059114bc2cb5ebce',
            normal: '2021-09-16',
            anomaly: '2021-09-14'
        },
        {
            address: '0x6674d1c75384465a09855719a94e13b5b8591302',
            normal: '2018-01-14',
            anomaly: '2021-03-29'
        }
    ];

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
            <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-8 mb-8">
                <h2 className="text-2xl font-bold text-slate-100 mb-2">Test Candidates</h2>
                <p className="text-slate-400 mb-6">Pre-selected addresses with known anomalous behavior</p>

                <div className="bg-blue-900/20 border border-blue-900/50 rounded-lg p-4 flex items-start gap-3">
                    <span className="text-xl">ℹ️</span>
                    <p className="text-sm text-blue-200 mt-0.5">
                        Select a <strong className="font-semibold">Normal</strong> or <strong className="font-semibold">Anomalous</strong> date to auto-fill the Single Search tab.
                    </p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6">
                {examples.map((ex, i) => (
                    <div key={i} className="bg-slate-900 rounded-lg border border-slate-800 p-6 hover:shadow-md hover:border-blue-700 transition-all group">
                        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-slate-800">
                            <div className="bg-slate-800 p-2 rounded-lg text-xl"></div>
                            <span className="font-mono text-sm text-slate-300 truncate w-full" title={ex.address}>
                                {ex.address}
                            </span>
                        </div>

                        <div className="space-y-3">
                            <button
                                onClick={() => onSelect(ex.address, ex.normal)}
                                className="w-full flex items-center justify-between px-4 py-2 bg-slate-800 hover:bg-slate-750 border border-slate-700 rounded text-sm text-slate-300 transition-colors group/btn"
                            >
                                <span className="flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-sm"></span> Normal
                                </span>
                                <span className="font-mono text-xs text-slate-500 group-hover/btn:text-slate-400">{ex.normal}</span>
                            </button>

                            <button
                                onClick={() => onSelect(ex.address, ex.anomaly)}
                                className="w-full flex items-center justify-between px-4 py-2 bg-slate-800 hover:bg-red-900/20 border border-slate-700 hover:border-red-800 rounded text-sm text-slate-300 transition-colors group/btn"
                            >
                                <span className="flex items-center gap-2">
                                    <span className="w-2 h-2 rounded-full bg-red-500 shadow-sm animate-pulse"></span> Anomaly
                                </span>
                                <span className="font-mono text-xs text-slate-500 group-hover/btn:text-slate-400">{ex.anomaly}</span>
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default TestExamples;
