import { Injectable, signal, computed, effect, inject, OnDestroy } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, of } from 'rxjs';
import { catchError, tap, map } from 'rxjs/operators';
import { HealthDocument, DocumentStatus, UploadResponse, AnalysisResultResponse } from '../models/document.model';

// Service configuration constants
const CONFIG = {
  API_BASE_URL: 'http://localhost:8000/api/v1',
  SSE_RETRY_DELAY: 1000,
  MAX_SSE_RETRIES: 3
} as const;

@Injectable({ providedIn: 'root' })
export class DocumentAnalysisService implements OnDestroy {
  private readonly http = inject(HttpClient);
  
  // State management with Angular 19 signals
  private documentsSignal = signal<HealthDocument[]>([]);
  public readonly documents = this.documentsSignal.asReadonly();
  
  // SSE connection tracking for cleanup
  private activeConnections = new Map<string, EventSource>();
  
  // Computed state selectors
  public readonly processingDocuments = computed(() => 
    this.documents().filter(doc => doc.status === DocumentStatus.PROCESSING)
  );
  
  public readonly completedDocuments = computed(() => 
    this.documents().filter(doc => doc.status === DocumentStatus.COMPLETE)
  );
  
  public readonly documentCount = computed(() => this.documents().length);
  
  public readonly hasProcessingDocuments = computed(() => 
    this.processingDocuments().length > 0
  );

  constructor() {
    this.loadInitialDocuments();
    this.setupStateLogging();
  }

  ngOnDestroy(): void {
    this.closeAllConnections();
  }

  // === PUBLIC API ===

  loadInitialDocuments(): void {
    this.http.get<HealthDocument[]>(`${CONFIG.API_BASE_URL}/documents`)
      .pipe(catchError(this.handleError))
      .subscribe(documents => this.documentsSignal.set(documents));
  }

  uploadDocument(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<UploadResponse>(`${CONFIG.API_BASE_URL}/documents/upload`, formData).pipe(
      tap(response => {
        const newDoc = this.createPendingDocument(response);
        this.documentsSignal.update(docs => [newDoc, ...docs]);
        this.startDocumentStream(response.document_id);
      }),
      catchError(this.handleError)
    );
  }

  getDocument(documentId: string): Observable<HealthDocument | null> {
    return this.http.get<AnalysisResultResponse>(`${CONFIG.API_BASE_URL}/documents/${documentId}`).pipe(
      map(result => this.mapResponseToDocument(result)),
      tap(document => {
        if (document) {
          this.updateDocumentInState(document);
        }
      }),
      catchError(error => {
        console.error(`Error fetching document ${documentId}:`, error);
        return of(null);
      })
    );
  }

  deleteDocument(documentId: string): Observable<boolean> {
    return this.http.delete(`${CONFIG.API_BASE_URL}/documents/${documentId}`).pipe(
      tap(() => {
        this.closeConnection(documentId);
        this.documentsSignal.update(docs => docs.filter(doc => doc.id !== documentId));
      }),
      map(() => true),
      catchError(this.handleError)
    );
  }

  // === PRIVATE IMPLEMENTATION ===

  private setupStateLogging(): void {
    effect(() => {
      const { length: total } = this.documents();
      const { length: processing } = this.processingDocuments();
      console.log(`📊 Documents: ${total} total, ${processing} processing`);
    });
  }

  private createPendingDocument(response: UploadResponse): HealthDocument {
    return {
      id: response.document_id,
      filename: response.filename,
      uploaded_at: new Date().toISOString(),
      status: DocumentStatus.PROCESSING,
    };
  }

  private startDocumentStream(documentId: string): void {
    // Close existing connection if any
    this.closeConnection(documentId);
    
    const eventSource = new EventSource(`${CONFIG.API_BASE_URL}/documents/${documentId}/stream`);
    this.activeConnections.set(documentId, eventSource);

    eventSource.onmessage = (event) => {
      try {
        const result: AnalysisResultResponse = JSON.parse(event.data);
        this.handleStreamUpdate(result);
        
        if (this.isTerminalStatus(result.status)) {
          this.closeConnection(documentId);
        }
      } catch (error) {
        console.error(`SSE parsing error for ${documentId}:`, error);
        this.handleStreamError(documentId, 'Invalid response format');
      }
    };

    eventSource.onerror = () => {
      console.error(`SSE connection error for ${documentId}`);
      this.handleStreamError(documentId, 'Connection to analysis stream failed');
    };
  }

  private handleStreamUpdate(result: AnalysisResultResponse): void {
    console.log(`📡 SSE Update ${result.document_id}: ${result.progress}% (${result.processing_stage})`);
    
    const document = this.mapResponseToDocument(result);
    this.updateDocumentInState(document);
  }

  private handleStreamError(documentId: string, errorMessage: string): void {
    this.closeConnection(documentId);
    this.setDocumentError(documentId, errorMessage);
  }

  private mapResponseToDocument(result: AnalysisResultResponse): HealthDocument {
    return {
      id: result.document_id,
      filename: result.filename,
      uploaded_at: result.uploaded_at,
      status: result.status,
      processed_at: result.processed_at,
      raw_text: result.raw_text,
      extracted_data: result.extracted_data?.map(d => ({
        marker: d.marker,
        value: d.value,
        unit: d.unit,
        reference_range: d.reference_range
      })),
      ai_insights: result.ai_insights,
      error_message: result.error_message,
      progress: result.progress,
      processing_stage: result.processing_stage,
    };
  }

  private updateDocumentInState(document: HealthDocument): void {
    this.documentsSignal.update(docs => {
      const index = docs.findIndex(d => d.id === document.id);
      if (index === -1) {
        console.warn(`⚠️ Document ${document.id} not found in state`);
        return docs;
      }
      
      const updatedDocs = [...docs];
      updatedDocs[index] = document;
      return updatedDocs;
    });
  }

  private setDocumentError(documentId: string, errorMessage: string): void {
    this.documentsSignal.update(docs => {
      const index = docs.findIndex(d => d.id === documentId);
      if (index === -1) return docs;

      const updatedDocs = [...docs];
      updatedDocs[index] = {
        ...updatedDocs[index],
        status: DocumentStatus.ERROR,
        error_message: errorMessage
      };
      return updatedDocs;
    });
  }

  private closeConnection(documentId: string): void {
    const connection = this.activeConnections.get(documentId);
    if (connection) {
      connection.close();
      this.activeConnections.delete(documentId);
      console.log(`🔌 SSE connection closed for ${documentId}`);
    }
  }

  private closeAllConnections(): void {
    this.activeConnections.forEach((connection, documentId) => {
      connection.close();
      console.log(`🔌 SSE connection closed for ${documentId} (cleanup)`);
    });
    this.activeConnections.clear();
  }

  private isTerminalStatus(status: DocumentStatus): boolean {
    return status === DocumentStatus.COMPLETE || status === DocumentStatus.ERROR;
  }

  private handleError = (error: HttpErrorResponse): Observable<never> => {
    const message = error.error?.message || error.message || 'Unknown error occurred';
    console.error('API Error:', { status: error.status, message });
    return throwError(() => new Error(message));
  };
}