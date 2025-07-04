import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { HealthDocument, UploadResponse, AnalysisResultResponse } from '../models/document.model';

/**
 * Service Configuration Constants
 * 
 * Centralized configuration for API endpoints and SSE settings.
 * Using const assertions for better TypeScript inference and immutability.
 */
const API_CONFIG = {
  /** Base URL for all backend API endpoints */
  BASE_URL: 'http://localhost:8000/api/v1',
  
  /** SSE connection retry configuration */
  SSE: {
    RETRY_DELAY: 1000,
    MAX_RETRIES: 3
  }
} as const;

/**
 * Document API Service
 * 
 * A dedicated service following Angular 19 best practices for handling all HTTP communication
 * with the backend API. This service is focused solely on API interactions and follows the
 * single responsibility principle by separating HTTP logic from state management.
 * 
 * Key Features:
 * - Pure HTTP operations without state management concerns
 * - Centralized error handling with proper error propagation
 * - Type-safe API interactions using TypeScript generics
 * - Modern Angular 19 dependency injection with inject() function
 * - Immutable configuration constants for better maintainability
 * 
 * @example
 * ```typescript
 * constructor(private apiService = inject(DocumentApiService)) {}
 * 
 * uploadFile(file: File) {
 *   this.apiService.uploadDocument(file).subscribe({
 *     next: (response) => console.log('Upload successful:', response),
 *     error: (error) => console.error('Upload failed:', error)
 *   });
 * }
 * ```
 */
@Injectable({ 
  providedIn: 'root' 
})
export class DocumentApiService {
  
  /**
   * HTTP Client Instance
   * 
   * Using Angular 19's inject() function pattern for better testability
   * and more modern dependency injection approach compared to constructor injection.
   */
  private readonly http = inject(HttpClient);

  // ===================================================================
  // PUBLIC API METHODS
  // ===================================================================

  /**
   * Retrieve All Documents
   * 
   * Fetches the complete list of documents from the backend.
   * This endpoint returns all documents with their current status and metadata.
   * 
   * @returns Observable<HealthDocument[]> Stream of document array
   * 
   * @example
   * ```typescript
   * this.apiService.getDocuments().subscribe({
   *   next: (docs) => console.log(`Loaded ${docs.length} documents`),
   *   error: (error) => this.handleError(error)
   * });
   * ```
   */
  getDocuments(): Observable<HealthDocument[]> {
    return this.http.get<HealthDocument[]>(`${API_CONFIG.BASE_URL}/documents`)
      .pipe(catchError(this.handleHttpError));
  }

  /**
   * Upload Document for Analysis
   * 
   * Uploads a file to the backend for OCR and AI analysis processing.
   * The server returns immediate response with document ID for tracking progress.
   * 
   * @param file - The file to upload (PDF, PNG, or JPG)
   * @returns Observable<UploadResponse> Upload confirmation with document ID
   * 
   * @example
   * ```typescript
   * const file = event.target.files[0];
   * this.apiService.uploadDocument(file).subscribe({
   *   next: (response) => this.startTracking(response.document_id),
   *   error: (error) => this.showUploadError(error)
   * });
   * ```
   */
  uploadDocument(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<UploadResponse>(`${API_CONFIG.BASE_URL}/documents/upload`, formData)
      .pipe(catchError(this.handleHttpError));
  }

  /**
   * Get Specific Document Details
   * 
   * Retrieves complete analysis results for a specific document by ID.
   * This includes extracted data, AI insights, and processing status.
   * 
   * @param documentId - Unique identifier for the document
   * @returns Observable<AnalysisResultResponse> Complete document analysis data
   * 
   * @example
   * ```typescript
   * this.apiService.getDocument('doc-123').subscribe({
   *   next: (result) => this.displayAnalysis(result),
   *   error: (error) => this.showNotFound(error)
   * });
   * ```
   */
  getDocument(documentId: string): Observable<AnalysisResultResponse> {
    return this.http.get<AnalysisResultResponse>(`${API_CONFIG.BASE_URL}/documents/${documentId}`)
      .pipe(catchError(this.handleHttpError));
  }

  /**
   * Delete Document
   * 
   * Permanently removes a document and all associated analysis data from the system.
   * This operation cannot be undone and will also clean up any stored files.
   * 
   * @param documentId - Unique identifier for the document to delete
   * @returns Observable<void> Completion signal
   * 
   * @example
   * ```typescript
   * this.apiService.deleteDocument('doc-123').subscribe({
   *   next: () => this.removeFromList('doc-123'),
   *   error: (error) => this.showDeleteError(error)
   * });
   * ```
   */
  deleteDocument(documentId: string): Observable<void> {
    return this.http.delete<void>(`${API_CONFIG.BASE_URL}/documents/${documentId}`)
      .pipe(catchError(this.handleHttpError));
  }

  /**
   * Retry Document Processing
   * 
   * Makes HTTP POST request to retry processing for stuck documents.
   * 
   * @param documentId - ID of document to retry
   * @returns Observable of retry response
   */
  retryDocumentProcessing(documentId: string): Observable<{message: string, document_id: string}> {
    return this.http.post<{message: string, document_id: string}>(`${API_CONFIG.BASE_URL}/documents/${documentId}/retry`, {})
      .pipe(catchError(this.handleHttpError));
  }

  /**
   * Create SSE Connection for Real-time Updates
   * 
   * Establishes a Server-Sent Events connection for real-time document processing updates.
   * This provides live progress tracking including percentage completion and processing stages.
   * 
   * Note: This method creates the EventSource but doesn't manage its lifecycle.
   * The calling service is responsible for closing the connection when appropriate.
   * 
   * @param documentId - Document ID to monitor
   * @returns EventSource instance for real-time updates
   * 
   * @example
   * ```typescript
   * const eventSource = this.apiService.createDocumentStream('doc-123');
   * eventSource.onmessage = (event) => {
   *   const update = JSON.parse(event.data);
   *   this.updateProgress(update.progress, update.processing_stage);
   * };
   * ```
   */
  createDocumentStream(documentId: string): EventSource {
    const streamUrl = `${API_CONFIG.BASE_URL}/documents/${documentId}/stream`;
    return new EventSource(streamUrl);
  }

  // ===================================================================
  // PRIVATE UTILITY METHODS
  // ===================================================================

  /**
   * Centralized HTTP Error Handler
   * 
   * Provides consistent error handling across all API calls with proper error transformation.
   * Extracts meaningful error messages from HTTP responses and converts them to user-friendly format.
   * 
   * @param error - HTTP error response from Angular's HttpClient
   * @returns Observable<never> Error stream for RxJS error handling
   * 
   * @private
   */
  private handleHttpError = (error: HttpErrorResponse): Observable<never> => {
    // Extract error message with fallback hierarchy for better UX
    const message = error.error?.message || 
                   error.error?.detail || 
                   error.message || 
                   'An unexpected error occurred while communicating with the server';
    
    // Log detailed error information for debugging (removed in production)
    console.error('🚨 API Error Details:', {
      status: error.status,
      statusText: error.statusText,
      message: message,
      url: error.url,
      timestamp: new Date().toISOString()
    });
    
    // Return user-friendly error for UI handling
    return throwError(() => new Error(message));
  };

  // ===================================================================
  // CONFIGURATION GETTERS (FOR TESTING/DEBUGGING)
  // ===================================================================

  /**
   * Get API Configuration
   * 
   * Exposes configuration for testing and debugging purposes.
   * Useful for unit tests that need to verify correct endpoint usage.
   * 
   * @returns Readonly configuration object
   * @internal
   */
  get config() {
    return API_CONFIG;
  }
} 