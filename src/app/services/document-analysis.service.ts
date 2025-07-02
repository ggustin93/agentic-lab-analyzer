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
      this.updateDocumentInState(result);
      if (result.status === DocumentStatus.COMPLETE || result.status === DocumentStatus.ERROR) {
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
      };
      const newDocs = [...currentDocs];
      newDocs[index] = updatedDoc;
      this.documentsSubject.next(newDocs);
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
    // First check if we already have the document in our state
    const existingDoc = this.documentsSubject.value.find(doc => doc.id === documentId);
    if (existingDoc) {
      return of(existingDoc);
    }
    
    // If not, try to fetch it from the API
    return this.http.get<AnalysisResultResponse>(`${this.API_BASE_URL}/documents/${documentId}`).pipe(
      map(result => ({
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
      })),
      catchError(error => {
        console.error(`Error fetching document ${documentId}:`, error);
        return of(null);
      })
    );
  }

  private handleError(error: HttpErrorResponse): Observable<never> {
    console.error('An error occurred:', error.message);
    return throwError(() => new Error('Something bad happened; please try again later.'));
  }
}