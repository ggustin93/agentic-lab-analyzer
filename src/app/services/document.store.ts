import { Injectable, signal, computed } from '@angular/core';
import { HealthDocument, DocumentStatus } from '../models/document.model';

/**
 * Document State Interface
 * 
 * Defines the complete state structure for document management.
 * Separates loading states, error handling, and document collections.
 */
export interface DocumentState {
  /** Collection of all documents indexed by ID */
  documents: Record<string, HealthDocument>;
  /** Currently selected document ID for detailed view */
  selectedDocumentId: string | null;
  /** Global loading states for different operations */
  loading: {
    upload: boolean;
    analysis: boolean;
    list: boolean;
  };
  /** Error state management */
  error: string | null;
  /** SSE connection status */
  connectionStatus: 'connected' | 'disconnected' | 'connecting';
}

/**
 * Document Store Service
 * 
 * Centralized state management for document-related operations using Angular 19 signals.
 * Provides reactive state management with computed selectors and state mutations.
 * 
 * Features:
 * - Signal-based reactive state management
 * - Computed selectors for derived state
 * - Immutable state updates
 * - Type-safe state operations
 * - Separation of concerns (state only, no business logic)
 * 
 * @example
 * ```typescript
 * // Inject the store
 * private documentStore = inject(DocumentStore);
 * 
 * // Read state
 * const documents = this.documentStore.documents();
 * const isLoading = this.documentStore.isUploading();
 * 
 * // Update state
 * this.documentStore.addDocument(newDocument);
 * this.documentStore.setUploadLoading(true);
 * ```
 */
@Injectable({
  providedIn: 'root'
})
export class DocumentStore {
  
  /**
   * Core State Signal
   * 
   * The single source of truth for all document-related state.
   * Uses Angular's signal for reactive updates throughout the application.
   */
  private readonly state = signal<DocumentState>({
    documents: {},
    selectedDocumentId: null,
    loading: {
      upload: false,
      analysis: false,
      list: false
    },
    error: null,
    connectionStatus: 'disconnected'
  });

  // ===========================================
  // COMPUTED SELECTORS
  // ===========================================
  
  /**
   * Documents Collection
   * 
   * Computed selector that returns all documents as an array.
   * Automatically updates when documents are added, removed, or modified.
   */
  readonly documents = computed(() => 
    Object.values(this.state().documents)
  );

  /**
   * Documents by Status
   * 
   * Computed selectors for documents filtered by their processing status.
   * Useful for displaying different document states in the UI.
   */
  readonly pendingDocuments = computed(() => 
    this.documents().filter(doc => doc.status === DocumentStatus.PROCESSING)
  );

  readonly completedDocuments = computed(() => 
    this.documents().filter(doc => doc.status === DocumentStatus.COMPLETE)
  );

  readonly failedDocuments = computed(() => 
    this.documents().filter(doc => doc.status === DocumentStatus.ERROR)
  );

  /**
   * Selected Document
   * 
   * Computed selector for the currently selected document.
   * Returns null if no document is selected or if the selected document doesn't exist.
   */
  readonly selectedDocument = computed(() => {
    const selectedId = this.state().selectedDocumentId;
    return selectedId ? this.state().documents[selectedId] || null : null;
  });

  /**
   * Loading States
   * 
   * Computed selectors for various loading states throughout the application.
   */
  readonly isUploading = computed(() => this.state().loading.upload);
  readonly isAnalyzing = computed(() => this.state().loading.analysis);
  readonly isLoadingList = computed(() => this.state().loading.list);
  readonly isAnyLoading = computed(() => 
    Object.values(this.state().loading).some(loading => loading)
  );

  /**
   * Error State
   * 
   * Computed selector for current error state.
   */
  readonly error = computed(() => this.state().error);

  /**
   * Connection Status
   * 
   * Computed selector for SSE connection status.
   */
  readonly connectionStatus = computed(() => this.state().connectionStatus);

  /**
   * Document Count Statistics
   * 
   * Computed selectors for document statistics and counts.
   */
  readonly documentCount = computed(() => this.documents().length);
  readonly processingCount = computed(() => this.pendingDocuments().length);
  readonly completedCount = computed(() => this.completedDocuments().length);
  readonly failedCount = computed(() => this.failedDocuments().length);

  // ===========================================
  // STATE MUTATIONS
  // ===========================================

  /**
   * Document Management Actions
   */

  /**
   * Add Document
   * 
   * Adds a new document to the state or updates an existing one.
   * 
   * @param document - Document to add or update
   */
  addDocument(document: HealthDocument): void {
    this.state.update(state => ({
      ...state,
      documents: {
        ...state.documents,
        [document.id]: document
      }
    }));
  }

  /**
   * Update Document
   * 
   * Updates an existing document with partial data.
   * 
   * @param documentId - ID of document to update
   * @param updates - Partial document data to merge
   */
  updateDocument(documentId: string, updates: Partial<HealthDocument>): void {
    this.state.update(state => {
      const existingDocument = state.documents[documentId];
      if (!existingDocument) {
        console.warn(`Document ${documentId} not found for update`);
        return state;
      }

      return {
        ...state,
        documents: {
          ...state.documents,
          [documentId]: {
            ...existingDocument,
            ...updates
          }
        }
      };
    });
  }

  /**
   * Remove Document
   * 
   * Removes a document from the state.
   * 
   * @param documentId - ID of document to remove
   */
  removeDocument(documentId: string): void {
    this.state.update(state => {
      // Create new documents object without the specified document
      const remainingDocuments = Object.fromEntries(
        Object.entries(state.documents).filter(([id]) => id !== documentId)
      );
      
      return {
        ...state,
        documents: remainingDocuments,
        selectedDocumentId: state.selectedDocumentId === documentId 
          ? null 
          : state.selectedDocumentId
      };
    });
  }

  /**
   * Set Documents
   * 
   * Replaces the entire documents collection (useful for initial load).
   * 
   * @param documents - Array of documents to set
   */
  setDocuments(documents: HealthDocument[]): void {
    const documentsRecord = documents.reduce((acc, doc) => {
      acc[doc.id] = doc;
      return acc;
    }, {} as Record<string, HealthDocument>);

    this.state.update(state => ({
      ...state,
      documents: documentsRecord
    }));
  }

  /**
   * Selection Management
   */

  /**
   * Select Document
   * 
   * Sets the currently selected document.
   * 
   * @param documentId - ID of document to select, or null to clear selection
   */
  selectDocument(documentId: string | null): void {
    this.state.update(state => ({
      ...state,
      selectedDocumentId: documentId
    }));
  }

  /**
   * Loading State Management
   */

  /**
   * Set Upload Loading
   * 
   * Sets the upload loading state.
   * 
   * @param loading - Loading state
   */
  setUploadLoading(loading: boolean): void {
    this.state.update(state => ({
      ...state,
      loading: {
        ...state.loading,
        upload: loading
      }
    }));
  }

  /**
   * Set Analysis Loading
   * 
   * Sets the analysis loading state.
   * 
   * @param loading - Loading state
   */
  setAnalysisLoading(loading: boolean): void {
    this.state.update(state => ({
      ...state,
      loading: {
        ...state.loading,
        analysis: loading
      }
    }));
  }

  /**
   * Set List Loading
   * 
   * Sets the list loading state.
   * 
   * @param loading - Loading state
   */
  setListLoading(loading: boolean): void {
    this.state.update(state => ({
      ...state,
      loading: {
        ...state.loading,
        list: loading
      }
    }));
  }

  /**
   * Error Management
   */

  /**
   * Set Error
   * 
   * Sets the current error state.
   * 
   * @param error - Error message or null to clear
   */
  setError(error: string | null): void {
    this.state.update(state => ({
      ...state,
      error
    }));
  }

  /**
   * Clear Error
   * 
   * Clears the current error state.
   */
  clearError(): void {
    this.setError(null);
  }

  /**
   * Connection Status Management
   */

  /**
   * Set Connection Status
   * 
   * Updates the SSE connection status.
   * 
   * @param status - Connection status
   */
  setConnectionStatus(status: 'connected' | 'disconnected' | 'connecting'): void {
    this.state.update(state => ({
      ...state,
      connectionStatus: status
    }));
  }

  /**
   * Reset State
   * 
   * Resets the entire state to initial values.
   * Useful for cleanup or when switching contexts.
   */
  reset(): void {
    this.state.set({
      documents: {},
      selectedDocumentId: null,
      loading: {
        upload: false,
        analysis: false,
        list: false
      },
      error: null,
      connectionStatus: 'disconnected'
    });
  }

  // ===========================================
  // DEBUGGING UTILITIES
  // ===========================================

  /**
   * Get State Snapshot
   * 
   * Returns a snapshot of the current state for debugging purposes.
   * 
   * @returns Current state snapshot
   */
  getStateSnapshot(): DocumentState {
    return { ...this.state() };
  }

  /**
   * Log State
   * 
   * Logs the current state to console for debugging.
   */
  logState(): void {
    console.log('📊 Document Store State:', this.getStateSnapshot());
  }
}
