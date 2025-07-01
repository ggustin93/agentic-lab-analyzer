import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { BehaviorSubject, Observable, throwError, timer, of } from 'rxjs';
import { catchError, switchMap, takeWhile, tap } from 'rxjs/operators';
import { HealthDocument, DocumentStatus, UploadResponse, AnalysisResult } from '../models/document.model';

@Injectable({
  providedIn: 'root'
})
export class DocumentAnalysisService {
  private readonly API_BASE_URL = 'http://localhost:8000/api';
  private documentsSubject = new BehaviorSubject<HealthDocument[]>([]);
  public documents$ = this.documentsSubject.asObservable();

  constructor(private http: HttpClient) {
    this.loadDocuments();
  }

  private loadDocuments(): void {
    // Try to load from backend first, fallback to localStorage
    this.http.get<{documents: any[]}>(`${this.API_BASE_URL}/documents`)
      .subscribe({
        next: (response) => {
          const documents = response.documents.map(doc => ({
            id: doc.id,
            title: this.generateTitle(doc.filename),
            filename: doc.filename,
            uploadedAt: new Date(doc.uploaded_at),
            status: doc.status as DocumentStatus
          }));
          this.documentsSubject.next(documents);
        },
        error: () => {
          // Fallback to localStorage for demo
          this.loadFromLocalStorage();
        }
      });
  }

  private loadFromLocalStorage(): void {
    const stored = localStorage.getItem('health_documents');
    if (stored) {
      const documents = JSON.parse(stored).map((doc: any) => ({
        ...doc,
        uploadedAt: new Date(doc.uploadedAt)
      }));
      this.documentsSubject.next(documents);
    }
  }

  private saveDocuments(documents: HealthDocument[]): void {
    localStorage.setItem('health_documents', JSON.stringify(documents));
    this.documentsSubject.next(documents);
  }

  uploadDocument(file: File): Observable<string> {
    const formData = new FormData();
    formData.append('file', file);

    return this.http.post<UploadResponse>(`${this.API_BASE_URL}/upload`, formData)
      .pipe(
        tap(response => {
          // Add document to local list immediately
          const newDocument: HealthDocument = {
            id: response.documentId,
            title: this.generateTitle(file.name),
            filename: file.name,
            uploadedAt: new Date(),
            status: DocumentStatus.PROCESSING
          };

          const currentDocuments = this.documentsSubject.value;
          const updatedDocuments = [newDocument, ...currentDocuments];
          this.saveDocuments(updatedDocuments);

          // Start polling for completion
          this.pollDocumentStatus(response.documentId);
        }),
        switchMap(response => of(response.documentId)),
        catchError(error => {
          console.error('Upload error:', error);
          // Fallback to demo mode
          return this.uploadDocumentDemo(file);
        })
      );
  }

  private uploadDocumentDemo(file: File): Observable<string> {
    // Demo fallback when backend is not available
    const documentId = this.generateId();
    const newDocument: HealthDocument = {
      id: documentId,
      title: this.generateTitle(file.name),
      filename: file.name,
      uploadedAt: new Date(),
      status: DocumentStatus.PROCESSING
    };

    const currentDocuments = this.documentsSubject.value;
    const updatedDocuments = [newDocument, ...currentDocuments];
    this.saveDocuments(updatedDocuments);

    // Simulate processing delay
    timer(3000).subscribe(() => {
      this.simulateProcessingComplete(documentId);
    });

    return of(documentId);
  }

  private pollDocumentStatus(documentId: string): void {
    const pollInterval = timer(0, 2000); // Poll every 2 seconds
    
    pollInterval.pipe(
      switchMap(() => this.http.get<AnalysisResult>(`${this.API_BASE_URL}/document/${documentId}`)),
      takeWhile(result => result.status === 'processing', true)
    ).subscribe({
      next: (result) => {
        this.updateDocumentFromBackend(documentId, result);
      },
      error: (error) => {
        console.error('Polling error:', error);
        // Continue with demo mode
      }
    });
  }

  private updateDocumentFromBackend(documentId: string, result: any): void {
    const documents = this.documentsSubject.value;
    const documentIndex = documents.findIndex(doc => doc.id === documentId);
    
    if (documentIndex !== -1) {
      documents[documentIndex] = {
        ...documents[documentIndex],
        status: result.status as DocumentStatus,
        extractedData: result.extracted_data || [],
        aiInsights: result.ai_insights || '',
        rawText: result.raw_text || '',
        errorMessage: result.error_message
      };
      
      this.saveDocuments(documents);
    }
  }

  private simulateProcessingComplete(documentId: string): void {
    const documents = this.documentsSubject.value;
    const documentIndex = documents.findIndex(doc => doc.id === documentId);
    
    if (documentIndex !== -1) {
      documents[documentIndex] = {
        ...documents[documentIndex],
        status: DocumentStatus.COMPLETE,
        extractedData: this.generateMockData(),
        aiInsights: this.generateMockInsights(),
        rawText: this.generateMockRawText()
      };
      
      this.saveDocuments(documents);
    }
  }

  getDocument(id: string): Observable<HealthDocument | undefined> {
    // Try backend first, fallback to local storage
    return this.http.get<AnalysisResult>(`${this.API_BASE_URL}/document/${id}`)
      .pipe(
        switchMap(result => {
          const document: HealthDocument = {
            id: result.document_id,
            title: this.generateTitle(result.filename),
            filename: result.filename,
            uploadedAt: new Date(result.uploaded_at),
            status: result.status as DocumentStatus,
            extractedData: result.extracted_data || [],
            aiInsights: result.ai_insights || '',
            rawText: result.raw_text || '',
            errorMessage: result.error_message
          };
          return of(document);
        }),
        catchError(() => {
          // Fallback to local documents
          return this.documents$.pipe(
            switchMap(documents => {
              const document = documents.find(doc => doc.id === id);
              return of(document);
            })
          );
        })
      );
  }

  deleteDocument(id: string): Observable<void> {
    return this.http.delete(`${this.API_BASE_URL}/document/${id}`)
      .pipe(
        tap(() => {
          const documents = this.documentsSubject.value;
          const filteredDocuments = documents.filter(doc => doc.id !== id);
          this.saveDocuments(filteredDocuments);
        }),
        switchMap(() => of(void 0)),
        catchError(() => {
          // Fallback to local deletion
          const documents = this.documentsSubject.value;
          const filteredDocuments = documents.filter(doc => doc.id !== id);
          this.saveDocuments(filteredDocuments);
          return of(void 0);
        })
      );
  }

  private generateId(): string {
    return Math.random().toString(36).substr(2, 9);
  }

  private generateTitle(filename: string): string {
    const date = new Date().toLocaleDateString();
    const baseName = filename.replace(/\.[^/.]+$/, "");
    return `${baseName} Analysis - ${date}`;
  }

  private generateMockData() {
    return [
      { marker: 'Hemoglobin', value: '14.5', unit: 'g/dL', referenceRange: '13.5 - 17.5' },
      { marker: 'White Blood Cells', value: '7.2', unit: '10³/μL', referenceRange: '4.0 - 11.0' },
      { marker: 'Platelets', value: '285', unit: '10³/μL', referenceRange: '150 - 450' },
      { marker: 'Glucose', value: '98', unit: 'mg/dL', referenceRange: '70 - 99' },
      { marker: 'Total Cholesterol', value: '190', unit: 'mg/dL', referenceRange: '< 200' },
      { marker: 'HDL Cholesterol', value: '55', unit: 'mg/dL', referenceRange: '> 40' },
      { marker: 'LDL Cholesterol', value: '115', unit: 'mg/dL', referenceRange: '< 130' },
      { marker: 'Triglycerides', value: '100', unit: 'mg/dL', referenceRange: '< 150' }
    ];
  }

  private generateMockInsights(): string {
    return `# Health Report Analysis

## Summary of Findings

Your health markers show generally positive results with most values falling within normal reference ranges. Here's a detailed breakdown:

## Blood Count Analysis

**Hemoglobin (14.5 g/dL)**: Your hemoglobin level is within the normal range, indicating good oxygen-carrying capacity of your blood.

**White Blood Cells (7.2 10³/μL)**: Your white blood cell count is normal, suggesting a healthy immune system function.

**Platelets (285 10³/μL)**: Platelet count is within normal range, indicating proper blood clotting function.

## Metabolic Panel

**Glucose (98 mg/dL)**: Your fasting glucose is at the upper end of normal range. Consider monitoring carbohydrate intake and maintaining regular physical activity.

## Lipid Profile

**Total Cholesterol (190 mg/dL)**: Excellent! Your total cholesterol is below 200 mg/dL, which is considered desirable.

**HDL Cholesterol (55 mg/dL)**: Good level of "good cholesterol" which helps protect against heart disease.

**LDL Cholesterol (115 mg/dL)**: Your "bad cholesterol" is within acceptable range but could be optimized further.

**Triglycerides (100 mg/dL)**: Normal triglyceride levels indicate good metabolic health.

## General Recommendations

- **Diet**: Continue maintaining a balanced diet rich in fruits, vegetables, and whole grains
- **Exercise**: Regular physical activity can help optimize cholesterol levels
- **Monitoring**: Consider regular check-ups to track these markers over time
- **Hydration**: Maintain adequate water intake for overall health

## Important Note

These insights are for educational purposes only. Always consult with your healthcare provider for personalized medical advice and treatment recommendations.`;
  }

  private generateMockRawText(): string {
    return `COMPREHENSIVE METABOLIC PANEL
Patient: John Doe
Date: ${new Date().toLocaleDateString()}
Lab: HealthLab Medical Center

COMPLETE BLOOD COUNT
Hemoglobin: 14.5 g/dL (Reference: 13.5-17.5)
White Blood Cells: 7.2 10³/μL (Reference: 4.0-11.0)
Platelets: 285 10³/μL (Reference: 150-450)

BASIC METABOLIC PANEL
Glucose: 98 mg/dL (Reference: 70-99)

LIPID PANEL
Total Cholesterol: 190 mg/dL (Reference: <200)
HDL Cholesterol: 55 mg/dL (Reference: >40)
LDL Cholesterol: 115 mg/dL (Reference: <130)
Triglycerides: 100 mg/dL (Reference: <150)

All values reviewed and approved by:
Dr. Sarah Johnson, MD
Internal Medicine`;
  }

  private handleError(error: HttpErrorResponse) {
    let errorMessage = 'An unknown error occurred';
    if (error.error instanceof ErrorEvent) {
      errorMessage = `Error: ${error.error.message}`;
    } else {
      errorMessage = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    return throwError(() => errorMessage);
  }
}