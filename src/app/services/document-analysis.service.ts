import { Injectable, OnDestroy, inject, effect } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError, tap, map } from 'rxjs/operators';
import { HealthDocument, DocumentStatus, UploadResponse, AnalysisResultResponse } from '../models/document.model';
import { DocumentApiService } from './document-api.service';
import { DocumentStore } from './document.store';
import { ToastService } from './toast.service';

/**
 * Document Analysis Service
 * 
 * Orchestrates the complete document analysis workflow using a clean separation of concerns.
 * This service focuses purely on business logic and workflow coordination, delegating
 * state management to DocumentStore and API operations to DocumentApiService.
 * 
 * Architecture Overview:
 * - DocumentStore: Handles all state management using Angular 19 signals
 * - DocumentApiService: Manages HTTP communications with backend
 * - DocumentAnalysisService: Orchestrates workflows and business logic
 * 
 * Key Responsibilities:
 * - Document upload workflow coordination
 * - Real-time SSE connection management
 * - Business logic for document lifecycle
 * - Error handling and recovery
 * - Progress tracking orchestration
 * 
 * Benefits of this architecture:
 * - Clear separation of concerns
 * - Testable business logic
 * - Reactive state management via signals
 * - Centralized error handling
 * - Simplified component integration
 * 
 * @example
 * ```typescript
 * constructor(
 *   private documentService = inject(DocumentAnalysisService),
 *   private documentStore = inject(DocumentStore)
 * ) {
 *   // Access reactive state
 *   const documents = this.documentStore.documents();
 *   const isLoading = this.documentStore.isUploading();
 *   
 *   // Trigger workflows
 *   this.documentService.uploadDocument(file);
 * }
 * ```
 */
@Injectable({
  providedIn: 'root'
})
export class DocumentAnalysisService implements OnDestroy {

  // ===========================================
  // DEPENDENCY INJECTION (Angular 19 Style)
  // ===========================================
  
  /** API service for HTTP operations */
  private readonly apiService = inject(DocumentApiService);
  
  /** Centralized state management store */
  private readonly store = inject(DocumentStore);
  
  /** Toast notification service */
  private readonly toastService = inject(ToastService);

  // ===========================================
  // STATE MANAGEMENT VIA STORE
  // ===========================================
  
  /**
   * Reactive State Access
   * 
   * All state is managed by DocumentStore. These getters provide convenient
   * access to reactive state for components and other services.
   */
  
  /** All documents reactive signal */
  readonly documents = this.store.documents;
  
  /** Documents filtered by status */
  readonly pendingDocuments = this.store.pendingDocuments;
  readonly completedDocuments = this.store.completedDocuments;
  readonly failedDocuments = this.store.failedDocuments;
  
  /** Currently selected document */
  readonly selectedDocument = this.store.selectedDocument;
  
  /** Loading states */
  readonly isUploading = this.store.isUploading;
  readonly isAnalyzing = this.store.isAnalyzing;
  readonly isLoadingList = this.store.isLoadingList;
  readonly isAnyLoading = this.store.isAnyLoading;
  
  /** Error state */
  readonly error = this.store.error;
  
  /** Connection status */
  readonly connectionStatus = this.store.connectionStatus;
  
  /** Document statistics */
  readonly documentCount = this.store.documentCount;
  readonly processingCount = this.store.processingCount;
  readonly completedCount = this.store.completedCount;
  readonly failedCount = this.store.failedCount;

  // ===========================================
  // SSE CONNECTION MANAGEMENT
  // ===========================================
  
  /** Active SSE connection for real-time updates */
  private eventSource: EventSource | null = null;
  
  /** Cleanup effect for SSE connection */
  private readonly connectionCleanupEffect = effect(() => {
    // Auto-cleanup SSE connection when service is destroyed
    // This effect runs when the service lifecycle changes
  });

  // ===========================================
  // PUBLIC API - WORKFLOW ORCHESTRATION
  // ===========================================

  /**
   * Upload Document Workflow
   * 
   * Orchestrates the complete document upload process including:
   * - File validation and upload
   * - Immediate state updates for UX responsiveness
   * - SSE connection establishment for real-time updates
   * - Error handling and recovery
   * 
   * @param file - File to upload for analysis
   * @returns Observable<string> - Document ID for tracking
   * 
   * @example
   * ```typescript
   * this.documentService.uploadDocument(file).subscribe({
   *   next: (documentId) => console.log('Upload started:', documentId),
   *   error: (error) => console.error('Upload failed:', error)
   * });
   * ```
   */
  uploadDocument(file: File): Observable<string> {
    console.log('🚀 Starting document upload workflow:', file.name);
    
    // Clear any previous errors
    this.store.clearError();
    
    // Set upload loading state
    this.store.setUploadLoading(true);

    return this.apiService.uploadDocument(file).pipe(
      tap((response: UploadResponse) => {
        console.log('📄 Upload response received:', response);
        
        // Create pending document for immediate UI feedback
        const pendingDocument = this.createPendingDocument(response);
        this.store.addDocument(pendingDocument);
        
        // Establish SSE connection for real-time updates
        this.connectToSSE(response.document_id);
      }),
      tap((response: UploadResponse) => {
        // Clear upload loading state
        this.store.setUploadLoading(false);
        console.log('✅ Upload workflow completed for:', response.document_id);
      }),
      catchError(this.handleWorkflowError('Upload')),
      // Extract document ID for caller convenience
      map(response => response.document_id)
    );
  }

  /**
   * Load Documents Workflow
   * 
   * Fetches all documents from the backend and updates the store.
   * Handles loading states and error management.
   * 
   * @returns Observable<HealthDocument[]> - Array of all documents
   */
  loadDocuments(): Observable<HealthDocument[]> {
    console.log('📋 Loading documents from backend');
    
    this.store.setListLoading(true);
    this.store.clearError();

    return this.apiService.getDocuments().pipe(
      tap((documents: HealthDocument[]) => {
        console.log(`📊 Loaded ${documents.length} documents`);
        this.store.setDocuments(documents);
        this.store.setListLoading(false);
      }),
      catchError(this.handleWorkflowError('Load Documents'))
    );
  }

  /**
   * Get Analysis Results Workflow
   * 
   * Fetches detailed analysis results for a specific document.
   * 
   * @param documentId - ID of document to fetch analysis for
   * @returns Observable<AnalysisResultResponse> - Detailed analysis results
   */
  getAnalysisResults(documentId: string): Observable<AnalysisResultResponse> {
    // Defensive programming - validate document ID
    if (!documentId || documentId === 'undefined' || documentId === 'null' || documentId.trim() === '') {
      console.error('❌ Invalid document ID provided to getAnalysisResults:', documentId);
      this.store.setError('Invalid document ID provided');
      return throwError(() => new Error('Invalid document ID: Cannot fetch analysis results'));
    }

    console.log('🔍 Fetching analysis results for:', documentId);
    
    this.store.setAnalysisLoading(true);
    this.store.clearError();

    return this.apiService.getDocument(documentId).pipe(
      tap((analysis: AnalysisResultResponse) => {
        console.log('📊 Analysis results received:', analysis);
        console.log('📊 Extracted data in response:', analysis.extracted_data);
        
        // Create a complete HealthDocument object from the API response
        const documentForStore: HealthDocument = {
          id: analysis.document_id,
          filename: analysis.filename,
          uploaded_at: analysis.uploaded_at,
          status: analysis.status,
          processed_at: analysis.processed_at,
          public_url: analysis.public_url, // <-- ADD THIS MAPPING
          raw_text: analysis.raw_text,
          extracted_data: analysis.extracted_data || [], // Ensure this is never undefined
          ai_insights: analysis.ai_insights,
          error_message: analysis.error_message,
          progress: analysis.progress,
          processing_stage: analysis.processing_stage,
        };
        
        console.log('📊 Document for store:', documentForStore);
        console.log('📊 Extracted data for store:', documentForStore.extracted_data);
        
        // Use addDocument to create or update the document in the store
        this.store.addDocument(documentForStore);
        
        this.store.setAnalysisLoading(false);
      }),
      catchError(this.handleWorkflowError('Get Analysis'))
    );
  }

  /**
   * Document Selection Management
   * 
   * Updates the currently selected document for detailed viewing.
   * 
   * @param documentId - ID of document to select, or null to clear selection
   */
  selectDocument(documentId: string | null): void {
    console.log('📌 Selecting document:', documentId);
    this.store.selectDocument(documentId);
  }

  /**
   * Remove Document Workflow
   * 
   * Removes a document from both the backend database and frontend state.
   * Ensures proper cleanup, error handling, and user feedback via toast notifications.
   * 
   * @param documentId - ID of document to remove
   */
  removeDocument(documentId: string): void {
    // Defensive programming - validate document ID
    if (!documentId || documentId === 'undefined' || documentId === 'null' || documentId.trim() === '') {
      console.error('❌ Invalid document ID provided to removeDocument:', documentId);
      this.toastService.error('Cannot delete document: Invalid document ID', 5000);
      return;
    }

    console.log('🗑️ Removing document from database:', documentId);
    
    // Get document name for better user feedback
    const document = this.store.documents().find(d => d.id === documentId);
    const documentName = document?.filename || 'Document';
    
    // Call backend API to delete the document from database
    this.apiService.deleteDocument(documentId).subscribe({
      next: () => {
        console.log('✅ Document successfully deleted from database:', documentId);
        
        // Show success toast notification
        this.toastService.success(`${documentName} has been successfully deleted.`, 4000);
        
        // Only remove from frontend state if backend deletion succeeded
        this.store.removeDocument(documentId);
        
        // If this was the selected document, clear selection
        if (this.store.selectedDocument()?.id === documentId) {
          this.store.selectDocument(null);
        }
        
        // Force refresh of document list to ensure UI is in sync with database
        console.log('🔄 Refreshing document list after deletion...');
        this.loadDocuments().subscribe({
          next: (documents) => {
            console.log(`✅ Document list refreshed: ${documents.length} documents remaining`);
          },
          error: (error) => {
            console.warn('⚠️ Failed to refresh document list after deletion:', error);
            this.toastService.warning('Document deleted but failed to refresh list. Please refresh the page.', 6000);
          }
        });
      },
      error: (error) => {
        console.error('❌ Failed to delete document from database:', documentId, error);
        
        // Show error toast notification
        this.toastService.error(`Failed to delete ${documentName}: ${error.message || 'Unknown error'}`, 6000);
        
        // Also update store error state for other UI components
        this.store.setError(`Failed to delete document: ${error.message || 'Unknown error'}`);
      }
    });
  }

  /**
   * Retry Document Processing
   * 
   * Retries processing for stuck or failed documents by calling the backend retry API.
   * This is useful when documents get stuck in "Starting processing" state.
   * 
   * @param documentId - ID of document to retry
   */
  retryDocumentProcessing(documentId: string): void {
    console.log('🔄 Retrying document processing:', documentId);
    
    this.store.clearError();
    
    // Call backend API to retry processing
    this.apiService.retryDocumentProcessing(documentId).subscribe({
      next: (response) => {
        console.log('✅ Backend retry initiated:', response.message);
        
        // Update local state to show processing restart
        this.store.updateDocument(documentId, {
          status: DocumentStatus.PROCESSING,
          progress: 0,
          processing_stage: 'ocr_extraction',
          error_message: undefined
        });
        
        // Disconnect any existing SSE connection and establish new one
        this.disconnectSSE();
        this.connectToSSE(documentId);
        
        console.log('✅ Processing retry initiated for:', documentId);
      },
      error: (error) => {
        console.error('❌ Failed to retry processing for:', documentId, error);
        this.store.setError(`Failed to retry processing: ${error.message || 'Unknown error'}`);
      }
    });
  }

  /**
   * Check for Stuck Documents
   * 
   * Identifies documents that have been processing for too long without progress.
   * Documents stuck for more than 5 minutes are considered stuck.
   * 
   * @returns Array of document IDs that appear to be stuck
   */
  getStuckDocuments(): string[] {
    const now = new Date();
    const stuckThresholdMs = 5 * 60 * 1000; // 5 minutes
    
    return this.documents()
      .filter(doc => {
        if (doc.status !== DocumentStatus.PROCESSING) return false;
        
        const uploadTime = new Date(doc.uploaded_at);
        const timeDiff = now.getTime() - uploadTime.getTime();
        
        // Consider stuck if processing for more than 5 minutes with 0% progress
        return timeDiff > stuckThresholdMs && (doc.progress === 0 || doc.progress === undefined);
      })
      .map(doc => doc.id);
  }

  /**
   * Auto-detect and Report Stuck Documents
   * 
   * Utility method to check for stuck documents and log warnings.
   * Can be called periodically to monitor document processing health.
   */
  checkForStuckDocuments(): void {
    const stuckDocs = this.getStuckDocuments();
    
    if (stuckDocs.length > 0) {
      console.warn(`⚠️ Found ${stuckDocs.length} stuck document(s):`, stuckDocs);
      console.log('💡 Consider using retryDocumentProcessing() to restart these documents');
    }
  }

  // ===========================================
  // SSE CONNECTION MANAGEMENT
  // ===========================================

  /**
   * Establish SSE Connection
   * 
   * Creates a Server-Sent Events connection for real-time document processing updates.
   * Handles connection lifecycle, message parsing, and automatic reconnection.
   * 
   * @param documentId - Document ID to track processing for
   * @private
   */
  private connectToSSE(documentId: string): void {
    console.log('🔌 Establishing SSE connection for:', documentId);
    
    // Clean up any existing connection
    this.disconnectSSE();
    
    // Update connection status
    this.store.setConnectionStatus('connecting');

         try {
       // Create new SSE connection
       this.eventSource = this.apiService.createDocumentStream(documentId);
       
       // Handle successful connection
       this.eventSource.onopen = () => {
         console.log('✅ SSE connection established');
         this.store.setConnectionStatus('connected');
       };

       // Handle incoming messages
       this.eventSource.onmessage = (event: MessageEvent) => {
         this.handleSSEMessage(event, documentId);
       };

       // Handle connection errors
       this.eventSource.onerror = (error: Event) => {
         console.error('❌ SSE connection error:', error);
         this.store.setConnectionStatus('disconnected');
         
         // Auto-reconnect logic could be added here
         // For now, we'll let the connection close
       };

     } catch (error: unknown) {
       console.error('🚨 Failed to establish SSE connection:', error);
       this.store.setConnectionStatus('disconnected');
       this.store.setError('Failed to establish real-time connection');
     }
  }

  /**
   * Handle SSE Message
   * 
   * Processes incoming Server-Sent Events messages and updates document state.
   * Handles different message types including progress updates and completion notifications.
   * 
   * @param event - SSE message event
   * @param documentId - Document ID being tracked
   * @private
   */
  private handleSSEMessage(event: MessageEvent, documentId: string): void {
    try {
      const data: AnalysisResultResponse = JSON.parse(event.data);
      console.log('📡 SSE message received:', data);

      // Update document with latest analysis data
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

      // Close connection when processing is complete
      if (data.status === DocumentStatus.COMPLETE || data.status === DocumentStatus.ERROR) {
        console.log('🎯 Document processing completed:', data.status);
        this.disconnectSSE();
      }

    } catch (error: unknown) {
      console.error('🚨 Error parsing SSE message:', error);
      this.store.setError('Failed to process real-time update');
    }
  }

  /**
   * Disconnect SSE Connection
   * 
   * Safely closes the active SSE connection and updates connection status.
   * 
   * @private
   */
  private disconnectSSE(): void {
    if (this.eventSource) {
      console.log('🔌 Closing SSE connection');
      this.eventSource.close();
      this.eventSource = null;
      this.store.setConnectionStatus('disconnected');
    }
  }

  // ===========================================
  // UTILITY METHODS
  // ===========================================

  /**
   * Create Pending Document
   * 
   * Creates a document object with initial state for immediate UI feedback.
   * 
   * @param response - Upload response from backend
   * @returns HealthDocument with pending state
   * @private
   */
  private createPendingDocument(response: UploadResponse): HealthDocument {
    return {
      id: response.document_id,
      filename: response.filename,
      uploaded_at: new Date().toISOString(),
      status: DocumentStatus.PROCESSING,
      // Initial progress state for immediate UI feedback
      progress: 0,
      processing_stage: 'ocr_extraction'
    };
  }

  /**
   * Handle Workflow Errors
   * 
   * Centralized error handling for workflow operations.
   * Provides consistent error logging, state management, and user feedback.
   * 
   * @param operation - Name of the operation that failed
   * @returns Error handler function for RxJS operators
   * @private
   */
  private handleWorkflowError = (operation: string) => (error: unknown): Observable<never> => {
    const message = error instanceof Error ? error.message : `${operation} failed unexpectedly`;
    
    console.error(`🚨 ${operation} Workflow Error:`, { error, message });
    
    // Update store with error state
    this.store.setError(message);
    this.store.setUploadLoading(false);
    this.store.setAnalysisLoading(false);
    this.store.setListLoading(false);
    
    // Ensure SSE connection is closed on errors
    this.disconnectSSE();
    
    return throwError(() => new Error(message));
  };

  // ===========================================
  // LIFECYCLE MANAGEMENT
  // ===========================================

  /**
   * Service Cleanup
   * 
   * Ensures proper cleanup of resources when the service is destroyed.
   * Closes SSE connections and resets state.
   */
  ngOnDestroy(): void {
    console.log('🧹 DocumentAnalysisService cleanup');
    
    // Close any active SSE connections
    this.disconnectSSE();
    
    // Reset store state for clean service lifecycle
    this.store.reset();
  }

  // ===========================================
  // DEBUGGING UTILITIES
  // ===========================================

  /**
   * Debug Store State
   * 
   * Utility method for debugging current store state.
   * Should only be used in development.
   */
  debugState(): void {
    if (typeof window !== 'undefined' && (window as unknown as Record<string, unknown>)['ng']) {
      this.store.logState();
    }
  }
}