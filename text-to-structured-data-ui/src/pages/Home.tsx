import React, { useState } from 'react';
import DragDropUpload from '../components/DragDropUpload';
import ProcessViewer from '../components/ProcessViewer';
import StatusDashboard from '../components/StatusDashboard';

const Home: React.FC = () => {
    const [rawText, setRawText] = useState<string>('');
    const [jsonData, setJsonData] = useState<any>(null);
    const [loading, setLoading] = useState<boolean>(false);

    return (
        <div className="min-h-screen bg-gray-900 text-white p-8">
            <div className="max-w-7xl mx-auto">
                <h1 className="text-4xl font-bold mb-8 text-center">Text to Structured Data</h1>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                    <DragDropUpload onUpload={setRawText} setLoading={setLoading} setJsonData={setJsonData} />
                    <StatusDashboard data={jsonData} />
                </div>

                {rawText && jsonData && (
                    <ProcessViewer rawText={rawText} jsonData={jsonData} />
                )}

                {loading && (
                    <div className="text-center text-gray-400 mt-8">
                        <p>Procesando archivo...</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default Home;