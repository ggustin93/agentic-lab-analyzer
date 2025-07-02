export enum DocumentStatus {
  PROCESSING = 'processing',
  COMPLETE = 'complete',
  ERROR = 'error',
}

export interface HealthMarker {
  readonly marker: string;
  readonly value: string;
  readonly unit?: string;
  readonly reference_range?: string;
}

export interface HealthDocument {
  readonly id: string;
  readonly filename: string;
  readonly uploaded_at: string;
  readonly status: DocumentStatus;
  readonly processed_at?: string;
  readonly raw_text?: string;
  readonly extracted_data?: HealthMarker[];
  readonly ai_insights?: string;
  readonly error_message?: string;
  readonly progress?: number;
  readonly processing_stage?: 'ocr_extraction' | 'ai_analysis' | 'saving_results' | 'complete';
}

// Wrapper class that provides camelCase accessors for snake_case properties
export class DocumentViewModel {
  constructor(private document: HealthDocument) {
    console.log('Creating DocumentViewModel with document:', document);
  }

  get id(): string { return this.document.id; }
  get filename(): string { return this.document.filename; }
  get status(): DocumentStatus { return this.document.status; }
  
  // CamelCase accessors for snake_case properties
  get title(): string { return this.document.filename; }
  get uploadedAt(): string { return this.document.uploaded_at; }
  get processedAt(): string | undefined { return this.document.processed_at; }
  get rawText(): string | undefined { return this.document.raw_text; }
  get extractedData(): HealthMarker[] | undefined { 
    console.log('Getting extractedData:', this.document.extracted_data);
    return this.document.extracted_data; 
  }
  get aiInsights(): string | undefined { return this.document.ai_insights; }
  get errorMessage(): string | undefined { return this.document.error_message; }
  get progress(): number | undefined { return this.document.progress; }
  get processingStage(): string | undefined { return this.document.processing_stage; }
  
  // Helper method to get stage-specific progress message
  get progressMessage(): string {
    if (!this.processingStage) return 'Processing...';
    
    switch (this.processingStage) {
      case 'ocr_extraction':
        return 'Extracting text from document...';
      case 'ai_analysis':
        return 'Analyzing health data...';
      case 'saving_results':
        return 'Finalizing results...';
      case 'complete':
        return 'Processing complete';
      default:
        return 'Processing...';
    }
  }
}

export interface UploadResponse {
  readonly document_id: string;
  readonly filename: string;
}

// This should match the JSON from the backend stream
export interface AnalysisResultResponse {
  readonly document_id: string;
  readonly status: DocumentStatus;
  readonly filename: string;
  readonly uploaded_at: string;
  readonly raw_text?: string;
  readonly extracted_data?: any[]; // The backend sends snake_case
  readonly ai_insights?: string;
  readonly error_message?: string;
  readonly processed_at?: string;
  readonly progress?: number;
  readonly processing_stage?: 'ocr_extraction' | 'ai_analysis' | 'saving_results' | 'complete';
}