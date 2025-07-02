import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Observable } from 'rxjs';
import { DocumentAnalysisService } from '../../services/document-analysis.service';
import { UploadZoneComponent } from '../../components/upload-zone/upload-zone.component';
import { DocumentListComponent } from '../../components/document-list/document-list.component';
import { HealthDocument } from '../../models/document.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, UploadZoneComponent, DocumentListComponent],
  template: `
    <div class="min-h-screen bg-gray-50">
      <!-- Header -->
      <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center space-x-3">
              <svg class="w-8 h-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
              <h1 class="text-xl font-semibold text-gray-900">Health Document Analyzer</h1>
            </div>
            <div class="text-sm text-gray-500">
              Secure • Local • Private
            </div>
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="space-y-8">
          <!-- Upload Section -->
          <div class="max-w-2xl mx-auto">
            <div class="text-center mb-8">
              <h2 class="text-2xl font-bold text-gray-900 mb-2">
                Analyze Your Health Reports
              </h2>
              <p class="text-gray-600">
                Upload your health documents for AI-powered analysis and insights. 
                All processing happens locally on your device.
              </p>
            </div>
            
            <app-upload-zone 
              (fileSelected)="onFileSelected($event)"
              [class.opacity-50]="isUploading"
              [class.pointer-events-none]="isUploading">
            </app-upload-zone>
            
            <div *ngIf="isUploading" class="mt-4 text-center">
              <div class="inline-flex items-center space-x-2 text-primary-600">
                <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="text-sm font-medium">Uploading and processing...</span>
              </div>
            </div>
          </div>

          <!-- Document List -->
          <div class="max-w-4xl mx-auto">
            <app-document-list 
              [documents]="(documents$ | async) || []">
            </app-document-list>
          </div>
        </div>
      </main>
    </div>
  `
})
export class DashboardComponent {
  public readonly documents$: Observable<HealthDocument[]> = this.documentService.documents$;
  isUploading = false;

  constructor(private documentService: DocumentAnalysisService) {}

  onFileSelected(file: File): void {
    this.isUploading = true;
    
    this.documentService.uploadDocument(file)
      .subscribe({
        next: (response) => {
          console.log('Document upload initiated:', response);
          // The UI will update reactively via the stream
          this.isUploading = false;
        },
        error: (error) => {
          console.error('Upload failed:', error);
          this.isUploading = false;
          alert('Upload failed. Please try again.');
        }
      });
  }
}