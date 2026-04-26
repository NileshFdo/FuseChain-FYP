import { useState, useEffect } from 'react';
import { API_URL } from '../config';

function FileTable({ files, title, description, onDownload }) {
    return (
        <div className="mb-8">
            <div className="flex items-center gap-3 mb-4">
                <h3 className="text-lg font-bold text-slate-100">{title}</h3>
            </div>
            <p className="text-slate-400 text-sm mb-4">{description}</p>

            <div className="bg-slate-900 rounded-xl border border-slate-800 shadow-sm overflow-hidden">
                <table className="min-w-full divide-y divide-slate-800">
                    <thead className="bg-slate-950">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">File Name</th>
                            <th className="px-6 py-3 text-left text-xs font-bold text-slate-400 uppercase tracking-wider">Addresses</th>
                            <th className="px-6 py-3 text-center text-xs font-bold text-slate-400 uppercase tracking-wider">Download</th>
                        </tr>
                    </thead>
                    <tbody className="bg-slate-900 divide-y divide-slate-800">
                        {files.map((file, i) => (
                            <tr key={i} className="hover:bg-slate-800 transition-colors">
                                <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-300">{file.name}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">{file.addresses}</td>
                                <td className="px-6 py-4 whitespace-nowrap text-center">
                                    <button
                                        onClick={() => onDownload(file.name)}
                                        className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
                                    >
                                        Download
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function TestExamples() {
    const [labeledFiles, setLabeledFiles] = useState([]);
    const [unlabeledFiles, setUnlabeledFiles] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch(`${API_URL}/risk/sample-files`)
            .then(res => {
                if (!res.ok) throw new Error('Failed to fetch sample files');
                return res.json();
            })
            .then(data => {
                setLabeledFiles(data.labeled || []);
                setUnlabeledFiles(data.unlabeled || []);
            })
            .catch(err => {
                console.error('Error fetching sample files:', err);
                setLabeledFiles([]);
                setUnlabeledFiles([]);
            })
            .finally(() => setLoading(false));
    }, []);

    const downloadFile = (filename) => {
        const a = document.createElement('a');
        a.href = `${API_URL}/risk/sample-files/${filename}`;
        a.download = filename;
        a.rel = 'noopener noreferrer';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
            <div className="bg-slate-900 rounded-xl shadow-sm border border-slate-800 p-8 mb-8">
                <h2 className="text-2xl font-bold text-slate-100 mb-2">Sample Test Files</h2>
                <p className="text-slate-400 mb-6">Download sample CSVs from the training dataset for testing</p>

                <div className="bg-blue-900/20 border border-blue-900/50 rounded-lg p-4 flex items-start gap-3">
                    <div className="text-sm text-blue-200">
                        <p><strong className="font-semibold">Two types of samples:</strong></p>
                        <ul className="mt-2 space-y-1">
                            <li>• <span className="text-slate-300 font-medium">Labeled</span> - Contains Class column for validation (shows accuracy metrics)</li>
                            <li>• <span className="text-slate-300 font-medium">Unlabeled</span> - No labels (blind testing, like production)</li>
                        </ul>
                    </div>
                </div>
            </div>

            {loading ? (
                <div className="text-center text-slate-400 py-12">Loading sample files...</div>
            ) : (
                <>
                    <FileTable
                        files={labeledFiles}
                        title="Labeled Samples"
                        description="CSVs with ground truth labels - model predictions will be compared with actual anomaly/normal status"
                        onDownload={downloadFile}
                    />

                    <FileTable
                        files={unlabeledFiles}
                        title="Unlabeled Samples"
                        description="CSVs without labels - simulates real production scenario where labels are unknown"
                        onDownload={downloadFile}
                    />
                </>
            )}
        </div>
    );
}

export default TestExamples;
