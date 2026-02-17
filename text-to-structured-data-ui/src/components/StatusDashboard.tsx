import React from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';

interface StatusDashboardProps {
    data: any;
}

const StatusDashboard: React.FC<StatusDashboardProps> = ({ data }) => {
    if (!data) {
        return (
            <div className="bg-gray-800 rounded-lg p-6 flex items-center justify-center min-h-64">
                <AlertCircle className="mr-3" size={24} />
                <p className="text-gray-400">Carga un archivo para ver el estado</p>
            </div>
        );
    }

    return (
        <div className="bg-gray-800 rounded-lg p-6 space-y-4">
            <div className="flex items-center mb-6">
                <CheckCircle size={24} className="mr-2 text-green-500" />
                <h3 className="text-xl font-bold">Estado del Procesamiento</h3>
            </div>
            
            <div className="flex items-center justify-between p-4 bg-gray-900 rounded">
                <span className="text-gray-400">Cliente</span>
                <span className="font-semibold text-blue-400">{data.cliente || 'N/A'}</span>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-900 rounded">
                <span className="text-gray-400">Monto</span>
                <span className="font-semibold text-green-400">${data.monto || '0'}</span>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-900 rounded">
                <span className="text-gray-400">Tipo de Solicitud</span>
                <span className="font-semibold text-purple-400">{data.tipo_solicitud || 'N/A'}</span>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-900 rounded">
                <span className="text-gray-400">Fecha</span>
                <span className="font-semibold text-yellow-400">{data.fecha || 'N/A'}</span>
            </div>
        </div>
    );
};

export default StatusDashboard;