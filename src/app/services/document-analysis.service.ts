import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError, of } from 'rxjs';
import { catchError, tap, map } from 'rxjs/operators';
import { HealthDocument, DocumentStatus, UploadResponse, AnalysisResultResponse } from '../models/document.model';

@Injectable({ providedIn: 'root' })
export class DocumentAnalysisService {
  private readonly API_BASE_URL = 'http://localhost:8000/api/v1';
  private documentsSubject = new BehaviorSubject<HealthDocument[]>([]);
  public readonly documents$ = this.documentsSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadInitialDocuments();
  }

  loadInitialDocuments(): void {
    this.http.get<HealthDocument[]>(`${this.API_BASE_URL}/documents`).pipe(
      catchError(this.handleError)
    ).subscribe(documents => {
      this.documentsSubject.next(documents);
    });
  }

  uploadDocument(file: File): Observable<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<UploadResponse>(`${this.API_BASE_URL}/documents/upload`, formData).pipe(
      tap(response => {
        // Use the current time in ISO format for the upload date
        // The backend will update this with the correct value via SSE
        const newDoc: HealthDocument = {
          id: response.document_id,
          filename: response.filename,
          uploaded_at: new Date().toISOString(),
          status: DocumentStatus.PROCESSING,
        };
        this.documentsSubject.next([newDoc, ...this.documentsSubject.value]);
        this.streamDocumentStatus(response.document_id);
      }),
      catchError(this.handleError)
    );
  }

  private streamDocumentStatus(documentId: string): void {
    const eventSource = new EventSource(`${this.API_BASE_URL}/documents/${documentId}/stream`);

    eventSource.onmessage = (event) => {
      const result: AnalysisResultResponse = JSON.parse(event.data);
      console.log(`📡 SSE Update received for ${result.document_id}:`, {
        progress: result.progress,
        stage: result.processing_stage,
        status: result.status
      });
      this.updateDocumentInState(result);
      if (result.status === DocumentStatus.COMPLETE || result.status === DocumentStatus.ERROR) {
        console.log(`✅ SSE Stream closed for ${result.document_id} - Final status: ${result.status}`);
        eventSource.close();
      }
    };

    eventSource.onerror = (error) => {
      console.error('SSE Error:', error);
      this.updateDocumentStatusToError(documentId, 'Connection to analysis stream failed.');
      eventSource.close();
    };
  }

  private updateDocumentInState(result: AnalysisResultResponse): void {
    const currentDocs = this.documentsSubject.value;
    const index = currentDocs.findIndex(d => d.id === result.document_id);
    if (index !== -1) {
      const updatedDoc: HealthDocument = {
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
      const newDocs = [...currentDocs];
      newDocs[index] = updatedDoc;
      console.log(`🔄 State updated for ${result.document_id}: ${result.progress}% (${result.processing_stage})`);
      this.documentsSubject.next(newDocs);
    } else {
      console.warn(`⚠️ Document ${result.document_id} not found in current state for update`);
    }
  }

  private updateDocumentStatusToError(documentId: string, errorMessage: string): void {
    const currentDocs = this.documentsSubject.value;
    const index = currentDocs.findIndex(d => d.id === documentId);
    if (index !== -1) {
      const docToUpdate = currentDocs[index];
      const updatedDoc: HealthDocument = {
        ...docToUpdate,
        status: DocumentStatus.ERROR,
        error_message: errorMessage
      };
      const newDocs = [...currentDocs];
      newDocs[index] = updatedDoc;
      this.documentsSubject.next(newDocs);
    }
  }

  getDocument(documentId: string): Observable<HealthDocument | null> {
    console.log(`Getting document ${documentId}`);
    
    // Always fetch from API for analysis view to ensure fresh data
    // This prevents stale data when navigating between different analyses
    console.log(`Fetching document ${documentId} from API`);
    return this.http.get<AnalysisResultResponse>(`${this.API_BASE_URL}/documents/${documentId}`).pipe(
      tap(result => console.log(`API response for document ${documentId}:`, result)),
      map(result => {
        const document: HealthDocument = {
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
          processing_stage: result.processing_stage
        };
        
        // Update the document in our state as well
        this.updateDocumentInState({
          document_id: document.id,
          filename: document.filename,
          uploaded_at: document.uploaded_at,
          status: document.status,
          processed_at: document.processed_at,
          raw_text: document.raw_text,
          extracted_data: document.extracted_data,
          ai_insights: document.ai_insights,
          error_message: document.error_message,
          progress: document.progress,
          processing_stage: document.processing_stage
        });
        
        console.log(`Mapped document ${documentId}:`, document);
        return document;
      }),
      catchError(error => {
        console.error(`Error fetching document ${documentId}:`, error);
        return of(null);
      })
    );
  }

  deleteDocument(documentId: string): Observable<any> {
    return this.http.delete(`${this.API_BASE_URL}/documents/${documentId}`).pipe(
      tap(() => {
        // Remove the document from the local state
        const currentDocs = this.documentsSubject.value;
        const filteredDocs = currentDocs.filter(doc => doc.id !== documentId);
        this.documentsSubject.next(filteredDocs);
      }),
      catchError(this.handleError)
    );
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    console.error('An error occurred:', error.message);
    return throwError(() => new Error('Something bad happened; please try again later.'));
  }
}