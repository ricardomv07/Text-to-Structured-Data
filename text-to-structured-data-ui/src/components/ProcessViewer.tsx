import React from 'react';
import { Code2 } from 'lucide-react';

interface ProcessViewerProps {
    rawText: string;
    jsonData: any;
}

const ProcessViewer: React.FC<ProcessViewerProps> = ({ rawText, jsonData }) => {
    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center mb-4">
                    <Code2 size={24} className="mr-2" />
                    <h3 className="text-xl font-bold">Texto Extraído</h3>
                </div>
                <pre className="bg-gray-900 p-4 rounded overflow-auto max-h-96 text-gray-300 text-sm">
                    {rawText || 'Esperando archivo...'}
                </pre>
            </div>

            <div className="bg-gray-800 rounded-lg p-6">
                <div className="flex items-center mb-4">
                    <Code2 size={24} className="mr-2" />
                    <h3 className="text-xl font-bold">JSON Estructurado</h3>
                </div>
                <pre className="bg-gray-900 p-4 rounded overflow-auto max-h-96 text-green-400 text-sm">
                    {jsonData ? JSON.stringify(jsonData, null, 2) : 'Esperando datos...'}
                </pre>
            </div>
        </div>
    );
};

export default ProcessViewer;