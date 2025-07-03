import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { DocumentAnalysisService } from './document-analysis.service';
import { DocumentStatus, UploadResponse, AnalysisResultResponse, HealthDocument } from '../models/document.model';

describe('DocumentAnalysisService (Pragmatic MVP Test)', () => {
  let service: DocumentAnalysisService;
  let httpMock: HttpTestingController;
  const API_BASE_URL = 'http://localhost:8000/api/v1';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [DocumentAnalysisService],
    });
    service = TestBed.inject(DocumentAnalysisService);
    httpMock = TestBed.inject(HttpTestingController);

    // Mock initial document load to isolate our tests
    const req = httpMock.expectOne(`${API_BASE_URL}/documents`);
    req.flush([]);
  });

  afterEach(() => {
    httpMock.verify(); // Ensure no outstanding HTTP requests
  });

  // THE SINGLE MOST IMPORTANT TEST: The full lifecycle of a document
  it('should correctly handle the full lifecycle of a document: upload, update via SSE, and deletion', (done) => {
    const mockFile = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const mockUploadResponse: UploadResponse = { document_id: 'doc-123', filename: 'test.pdf' };
    
    // --- 1. UPLOAD ---
    service.uploadDocument(mockFile).subscribe({
      next: (response) => {
        expect(response).toEqual(mockUploadResponse);
        
        // Assert: Document is now in "processing" state
        const docs = service.documents();
        expect(docs.length).toBe(1);
        expect(docs[0].id).toBe('doc-123');
        expect(docs[0].status).toBe(DocumentStatus.PROCESSING);
        expect(docs[0].filename).toBe('test.pdf');
        
        // --- 2. SSE UPDATE ---
        // We simulate an SSE message by calling the private update method.
        // This is a pragmatic shortcut to avoid complex EventSource mocking.
        const mockSseUpdate: AnalysisResultResponse = {
          document_id: 'doc-123',
          filename: 'test.pdf',
          status: DocumentStatus.COMPLETE,
          uploaded_at: new Date().toISOString(),
          progress: 100,
          processing_stage: 'complete',
          extracted_data: [{ marker: 'Hemoglobin', value: '14.5', unit: 'g/dL', reference_range: '13.5 - 17.5' }],
          ai_insights: '# Analysis Report\n\nLooks good overall.',
          processed_at: new Date().toISOString()
        };
        
        // Use 'as any' to access the private methods for this test.
        // First map the response to a document, then update the state
        const mappedDocument = (service as any).mapResponseToDocument(mockSseUpdate);
        (service as any).updateDocumentInState(mappedDocument);
        
        // Assert: Document is now "complete" with all data
        const updatedDocs = service.documents();
        expect(updatedDocs[0].status).toBe(DocumentStatus.COMPLETE);
        expect(updatedDocs[0].progress).toBe(100);
        expect(updatedDocs[0].ai_insights).toBe('# Analysis Report\n\nLooks good overall.');
        expect(updatedDocs[0].extracted_data?.length).toBe(1);
        expect(updatedDocs[0].extracted_data?.[0].marker).toBe('Hemoglobin');
        
        // --- 3. DELETION ---
        service.deleteDocument('doc-123').subscribe({
          next: (success) => {
            expect(success).toBe(true);
            
            // Assert: The document list is now empty
            const finalDocs = service.documents();
            expect(finalDocs.length).toBe(0);
            
            done();
          }
        });
        
        const deleteReq = httpMock.expectOne(`${API_BASE_URL}/documents/doc-123`);
        deleteReq.flush({});
      }
    });

    const uploadReq = httpMock.expectOne(`${API_BASE_URL}/documents/upload`);
    expect(uploadReq.request.method).toBe('POST');
    expect(uploadReq.request.body).toBeInstanceOf(FormData);
    uploadReq.flush(mockUploadResponse);
  });

  // Additional critical test: Error handling
  it('should handle upload errors gracefully', () => {
    const mockFile = new File([''], 'test.pdf', { type: 'application/pdf' });
    
    service.uploadDocument(mockFile).subscribe({
      next: () => fail('should have failed'),
      error: (error) => {
        expect(error.message).toContain('Upload failed');
        
        // Ensure no documents were added to state on error
        const docs = service.documents();
        expect(docs.length).toBe(0);
      }
    });

    const req = httpMock.expectOne(`${API_BASE_URL}/documents/upload`);
    req.flush({ message: 'Upload failed' }, { status: 500, statusText: 'Server Error' });
  });

  // Signal-based state management test
  it('should provide correct computed state signals', () => {
    // Add a mix of document statuses
    const mockDocuments: HealthDocument[] = [
      {
        id: '1',
        filename: 'processing.pdf',
        uploaded_at: new Date().toISOString(),
        status: DocumentStatus.PROCESSING
      },
      {
        id: '2',
        filename: 'complete.pdf',
        uploaded_at: new Date().toISOString(),
        status: DocumentStatus.COMPLETE,
        processed_at: new Date().toISOString()
      },
      {
        id: '3',
        filename: 'error.pdf',
        uploaded_at: new Date().toISOString(),
        status: DocumentStatus.ERROR,
        error_message: 'Processing failed'
      }
    ];

    service.loadInitialDocuments();
    const req = httpMock.expectOne(`${API_BASE_URL}/documents`);
    req.flush(mockDocuments);

    // Test computed signals
    expect(service.documentCount()).toBe(3);
    expect(service.processingDocuments().length).toBe(1);
    expect(service.completedDocuments().length).toBe(1);
    expect(service.hasProcessingDocuments()).toBe(true);
    
    expect(service.processingDocuments()[0].filename).toBe('processing.pdf');
    expect(service.completedDocuments()[0].filename).toBe('complete.pdf');
  });
}); 