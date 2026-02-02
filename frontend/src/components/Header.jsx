function Header({ activeTab, setActiveTab }) {
    const tabs = [
        { id: 'daily', label: 'Daily Analysis' },
        { id: 'single', label: 'Single Address' },
        { id: 'test', label: 'Test Samples' },
        { id: 'model', label: 'Model Details' },
    ];

    return (
        <header className="bg-slate-900 border-b border-slate-700 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex">
                        <div className="flex-shrink-0 flex items-center gap-2">
                            <h1 className="text-xl font-bold text-blue-400 tracking-tight">
                                FuseChain
                            </h1>
                        </div>
                        <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                            {tabs.map((tab) => (
                                <button
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors
                                        ${activeTab === tab.id
                                            ? 'border-blue-500 text-white'
                                            : 'border-transparent text-slate-400 hover:border-slate-600 hover:text-slate-200'
                                        }`}
                                >
                                    {tab.label}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </header>
    );
}

export default Header;
