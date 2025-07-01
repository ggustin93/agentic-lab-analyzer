export interface HealthDocument {
  id: string;
  title: string;
  filename: string;
  uploadedAt: Date;
  status: DocumentStatus;
  extractedData?: ExtractedHealthData[];
  aiInsights?: string;
  rawText?: string;
  errorMessage?: string;
}

export interface ExtractedHealthData {
  marker: string;
  value: string;
  unit?: string;
  referenceRange?: string;
}

export enum DocumentStatus {
  PROCESSING = 'processing',
  COMPLETE = 'complete',
  ERROR = 'error'
}

export interface UploadResponse {
  documentId: string;
  message: string;
}

export interface AnalysisResult {
  documentId: string;
  extractedData: ExtractedHealthData[];
  aiInsights: string;
  rawText: string;
  status: string;
  filename: string;
  uploadedAt: string;
  errorMessage?: string;
  processedAt?: string;
}