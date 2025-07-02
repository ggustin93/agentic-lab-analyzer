import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { DocumentAnalysisService } from './document-analysis.service';
import { DocumentStatus, UploadResponse } from '../models/document.model';

describe('DocumentAnalysisService', () => {
  let service: DocumentAnalysisService;
  let httpMock: HttpTestingController;
  const API_BASE_URL = 'http://localhost:8000/api/v1';

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [DocumentAnalysisService]
    });
    service = TestBed.inject(DocumentAnalysisService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
    // Expect the initial call to load documents
    const req = httpMock.expectOne(`${API_BASE_URL}/documents`);
    req.flush([]);
  });

  it('should load initial documents on startup', () => {
    const mockDocuments = [
      { id: '1', filename: 'test1.pdf', uploaded_at: new Date().toISOString(), status: DocumentStatus.COMPLETE },
      { id: '2', filename: 'test2.png', uploaded_at: new Date().toISOString(), status: DocumentStatus.ERROR }
    ];
    
    // The initial call is made in the constructor/beforeEach
    const req = httpMock.expectOne(`${API_BASE_URL}/documents`);
    expect(req.request.method).toBe('GET');
    req.flush(mockDocuments);

    service.documents$.subscribe(documents => {
      expect(documents.length).toBe(2);
      expect(documents[0].filename).toBe('test1.pdf');
    });
  });

  describe('#uploadDocument', () => {
    it('should handle successful upload', (done) => {
      const mockFile = new File([''], 'test.pdf', { type: 'application/pdf' });
      const mockResponse: UploadResponse = { document_id: 'new_id', filename: 'test.pdf' };
      
      // Spy on the private method to check if it's called
      spyOn(service as any, 'streamDocumentStatus').and.stub();

      service.uploadDocument(mockFile).subscribe(response => {
        expect(response).toEqual(mockResponse);
      });

      const req = httpMock.expectOne(`${API_BASE_URL}/documents/upload`);
      expect(req.request.method).toBe('POST');
      req.flush(mockResponse);

      service.documents$.subscribe(documents => {
        if (documents.length > 0) {
          const newDoc = documents.find(d => d.id === 'new_id');
          expect(newDoc).toBeTruthy();
          expect(newDoc?.status).toBe(DocumentStatus.PROCESSING);
          expect((service as any).streamDocumentStatus).toHaveBeenCalledWith('new_id');
          done();
        }
      });
    });

    it('should handle upload error', () => {
      const mockFile = new File([''], 'test.pdf', { type: 'application/pdf' });
      const errorMessage = 'Upload failed';

      service.uploadDocument(mockFile).subscribe({
        next: () => fail('should have failed'),
        error: (error) => {
          expect(error.message).toContain('Something bad happened');
        }
      });

      const req = httpMock.expectOne(`${API_BASE_URL}/documents/upload`);
      req.flush({ message: errorMessage }, { status: 500, statusText: 'Server Error' });
    });
  });
}); 