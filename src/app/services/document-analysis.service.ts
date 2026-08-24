import { Injectable, inject } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError, tap, map } from 'rxjs/operators';
import { HealthDocument, DocumentStatus, UploadResponse, AnalysisResultResponse } from '../models/document.model';
import { DocumentApiService } from './document-api.service';
import { DocumentStore } from './document.store';
import { ToastService } from './toast.service';

/**
 * Orchestrates the document analysis workflow.
 *
 * Coordinates the other two layers of the architecture: DocumentStore
 * (signal-based state) and DocumentApiService (HTTP). This service owns the
 * business logic — upload lifecycle, SSE tracking, deletion, retry — and is
 * the single writer of workflow state into the store.
 */
@Injectable({
  providedIn: 'root'
})
export class DocumentAnalysisService {

  private readonly apiService = inject(DocumentApiService);
  private readonly store = inject(DocumentStore);
  private readonly toastService = inject(ToastService);

  // Reactive state, re-exposed from the store for component convenience
  readonly documents = this.store.documents;
  readonly pendingDocuments = this.store.pendingDocuments;
  readonly completedDocuments = this.store.completedDocuments;
  readonly failedDocuments = this.store.failedDocuments;
  readonly selectedDocument = this.store.selectedDocument;
  readonly isUploading = this.store.isUploading;
  readonly isAnalyzing = this.store.isAnalyzing;
  readonly isLoadingList = this.store.isLoadingList;
  readonly isAnyLoading = this.store.isAnyLoading;
  readonly error = this.store.error;
  readonly connectionStatus = this.store.connectionStatus;
  readonly documentCount = this.store.documentCount;
  readonly processingCount = this.store.processingCount;
  readonly completedCount = this.store.completedCount;
  readonly failedCount = this.store.failedCount;

  /**
   * One EventSource per tracked document, so several uploads can stream
   * progress concurrently without cutting each other off.
   */
  private readonly eventSources = new Map<string, EventSource>();

  /**
   * Uploads a file and starts real-time tracking of its processing.
   * Returns the backend document ID.
   */
  uploadDocument(file: File): Observable<string> {
    this.store.clearError();
    this.store.setUploadLoading(true);

    return this.apiService.uploadDocument(file).pipe(
      tap((response: UploadResponse) => {
        this.store.addDocument(this.createPendingDocument(response));
        this.connectToSSE(response.document_id);
        this.store.setUploadLoading(false);
      }),
      catchError(this.handleWorkflowError('Upload')),
      map(response => response.document_id)
    );
  }

  /** Fetches all documents into the store. */
  loadDocuments(): Observable<HealthDocument[]> {
    this.store.setListLoading(true);
    this.store.clearError();

    return this.apiService.getDocuments().pipe(
      tap((documents: HealthDocument[]) => {
        this.store.setDocuments(documents);
        this.store.setListLoading(false);
      }),
      catchError(this.handleWorkflowError('Load Documents'))
    );
  }

  /** Fetches the full analysis for one document and merges it into the store. */
  getAnalysisResults(documentId: string): Observable<AnalysisResultResponse> {
    if (!this.isValidDocumentId(documentId)) {
      this.store.setError('Invalid document ID provided');
      return throwError(() => new Error('Invalid document ID: Cannot fetch analysis results'));
    }

    this.store.setAnalysisLoading(true);
    this.store.clearError();

    return this.apiService.getDocument(documentId).pipe(
      tap((analysis: AnalysisResultResponse) => {
        this.store.addDocument(this.mapAnalysisToDocument(analysis));
        this.store.setAnalysisLoading(false);
      }),
      catchError(this.handleWorkflowError('Get Analysis'))
    );
  }

  selectDocument(documentId: string | null): void {
    this.store.selectDocument(documentId);
  }

  /** Deletes a document in the backend, then mirrors the change locally. */
  removeDocument(documentId: string): void {
    if (!this.isValidDocumentId(documentId)) {
      this.toastService.error('Cannot delete document: Invalid document ID', 5000);
      return;
    }

    const documentName = this.store.documents().find(d => d.id === documentId)?.filename || 'Document';

    this.apiService.deleteDocument(documentId).subscribe({
      next: () => {
        this.toastService.success(`${documentName} has been successfully deleted.`, 4000);
        this.disconnectSSE(documentId);
        this.store.removeDocument(documentId);
        if (this.store.selectedDocument()?.id === documentId) {
          this.store.selectDocument(null);
        }
        // Re-sync with the backend so the list reflects the database
        this.loadDocuments().subscribe({
          error: () => {
            this.toastService.warning('Document deleted but failed to refresh list. Please refresh the page.', 6000);
          }
        });
      },
      error: (error) => {
        this.toastService.error(`Failed to delete ${documentName}: ${error.message || 'Unknown error'}`, 6000);
        this.store.setError(`Failed to delete document: ${error.message || 'Unknown error'}`);
      }
    });
  }

  /** Restarts backend processing for a stuck or failed document. */
  retryDocumentProcessing(documentId: string): void {
    this.store.clearError();

    this.apiService.retryDocumentProcessing(documentId).subscribe({
      next: () => {
        this.store.updateDocument(documentId, {
          status: DocumentStatus.PROCESSING,
          progress: 0,
          processing_stage: 'ocr_extraction',
          error_message: undefined
        });
        this.disconnectSSE(documentId);
        this.connectToSSE(documentId);
      },
      error: (error) => {
        this.store.setError(`Failed to retry processing: ${error.message || 'Unknown error'}`);
      }
    });
  }

  /**
   * Documents still at 0% progress after 5 minutes are considered stuck
   * (the backend pipeline is fire-and-forget, so a crashed worker leaves
   * the document in "processing" forever — see ADR-002).
   */
  getStuckDocuments(): string[] {
    const now = new Date();
    const stuckThresholdMs = 5 * 60 * 1000;

    return this.documents()
      .filter(doc => {
        if (doc.status !== DocumentStatus.PROCESSING) return false;
        const timeDiff = now.getTime() - new Date(doc.uploaded_at).getTime();
        return timeDiff > stuckThresholdMs && (doc.progress === 0 || doc.progress === undefined);
      })
      .map(doc => doc.id);
  }

  private connectToSSE(documentId: string): void {
    this.disconnectSSE(documentId);
    this.store.setConnectionStatus('connecting');

    try {
      const eventSource = this.apiService.createDocumentStream(documentId);
      this.eventSources.set(documentId, eventSource);

      eventSource.onopen = () => this.store.setConnectionStatus('connected');
      eventSource.onmessage = (event: MessageEvent) => this.handleSSEMessage(event, documentId);
      eventSource.onerror = () => {
        this.store.setConnectionStatus('disconnected');
      };
    } catch {
      this.store.setConnectionStatus('disconnected');
      this.store.setError('Failed to establish real-time connection');
    }
  }

  private handleSSEMessage(event: MessageEvent, documentId: string): void {
    try {
      const data: AnalysisResultResponse = JSON.parse(event.data);

      this.store.updateDocument(documentId, {
        status: data.status,
        progress: data.progress,
        processing_stage: data.processing_stage,
        processed_at: data.processed_at,
        raw_text: data.raw_text,
        extracted_data: data.extracted_data,
        ai_insights: data.ai_insights,
        error_message: data.error_message
      });

      if (data.status === DocumentStatus.COMPLETE || data.status === DocumentStatus.ERROR) {
        this.disconnectSSE(documentId);
      }
    } catch {
      this.store.setError('Failed to process real-time update');
    }
  }

  private disconnectSSE(documentId?: string): void {
    if (documentId) {
      this.eventSources.get(documentId)?.close();
      this.eventSources.delete(documentId);
    } else {
      this.eventSources.forEach(source => source.close());
      this.eventSources.clear();
    }
    if (this.eventSources.size === 0) {
      this.store.setConnectionStatus('disconnected');
    }
  }

  private createPendingDocument(response: UploadResponse): HealthDocument {
    return {
      id: response.document_id,
      filename: response.filename,
      uploaded_at: new Date().toISOString(),
      status: DocumentStatus.PROCESSING,
      progress: 0,
      processing_stage: 'ocr_extraction'
    };
  }

  /** Single owner of the API-response → HealthDocument mapping. */
  mapAnalysisToDocument(analysis: AnalysisResultResponse): HealthDocument {
    return {
      id: analysis.document_id,
      filename: analysis.filename,
      uploaded_at: analysis.uploaded_at,
      status: analysis.status,
      processed_at: analysis.processed_at,
      public_url: analysis.public_url,
      raw_text: analysis.raw_text,
      extracted_data: analysis.extracted_data || [],
      ai_insights: analysis.ai_insights,
      error_message: analysis.error_message,
      progress: analysis.progress,
      processing_stage: analysis.processing_stage,
    };
  }

  private isValidDocumentId(documentId: string): boolean {
    return !!documentId && documentId !== 'undefined' && documentId !== 'null' && documentId.trim() !== '';
  }

  private handleWorkflowError = (operation: string) => (error: unknown): Observable<never> => {
    const message = error instanceof Error ? error.message : `${operation} failed unexpectedly`;

    this.store.setError(message);
    this.store.setUploadLoading(false);
    this.store.setAnalysisLoading(false);
    this.store.setListLoading(false);
    this.disconnectSSE();

    return throwError(() => new Error(message));
  };
}
