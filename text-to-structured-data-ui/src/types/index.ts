export interface FileUpload {
    name: string;
    type: string;
    size: number;
}

export interface ProcessedData {
    cliente: string;
    monto: number;
    fecha: string;
    tipo_solicitud: 'Sale' | 'Complaint' | 'Invoice';
}

export interface ValidationError {
    message: string;
    missingFields?: string[];
}