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
              <!-- AI Doctor Robot Icon -->
              <div class="relative">
                <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <!-- Robot head/body -->
                  <rect x="6" y="6" width="12" height="10" rx="2" ry="2" stroke-width="2"/>
                  <!-- Eyes -->
                  <circle cx="9" cy="9" r="1" fill="currentColor"/>
                  <circle cx="15" cy="9" r="1" fill="currentColor"/>
                  <!-- Medical cross -->
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M12 11v2m-1-1h2"/>
                  <!-- Stethoscope around neck -->
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                        d="M8 4c0-1 1-2 2-2h4c1 0 2 1 2 2"/>
                  <!-- Antenna -->
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M12 6v-2"/>
                  <circle cx="12" cy="3" r="1" fill="currentColor"/>
                </svg>
                <!-- Medical pulse indicator -->
                <div class="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-pulse border-2 border-white"></div>
              </div>
              <div>
                <h1 class="text-xl font-bold text-gray-900 brand-text">DocBot AI</h1>
                <p class="text-xs text-blue-600 font-medium medical-text">Intelligent Health Analysis</p>
              </div>
            </div>
            <div class="flex items-center space-x-4">
              <div class="text-sm text-gray-500">
                <span class="flex items-center space-x-1">
                  <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd"/>
                  </svg>
                  <span>Secure</span>
                </span>
              </div>
              <!-- GitHub Link -->
              <a href="https://github.com/ggustin93/agentic-lab-analyzer" target="_blank" rel="noopener noreferrer" class="text-sm text-gray-500 hover:text-gray-700 transition-colors">
                <span class="flex items-center space-x-1">
                  <svg class="w-4 h-4 text-gray-700" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                  <span>Open-source</span>
                </span>
              </a>
              <div class="text-sm text-gray-500">
                <span class="flex items-center space-x-1">
                  <svg class="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M3.707 2.293a1 1 0 00-1.414 1.414l14 14a1 1 0 001.414-1.414l-1.473-1.473A10.014 10.014 0 0019.542 10C18.268 5.943 14.478 3 10 3a9.958 9.958 0 00-4.512 1.074l-1.78-1.781zm4.261 4.26l1.514 1.515a2.003 2.003 0 012.45 2.45l1.514 1.514a4 4 0 00-5.478-5.478z" clip-rule="evenodd"/>
                    <path d="M12.454 16.697L9.75 13.992a4 4 0 01-3.742-3.741L2.335 6.578A9.98 9.98 0 00.458 10c1.274 4.057 5.065 7 9.542 7 .847 0 1.669-.105 2.454-.303z"/>
                  </svg>
                  <span>Private</span>
                </span>
              </div>
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
              <div class="flex justify-center items-center mb-4">
                <div class="flex items-center space-x-2 text-blue-600">
                  <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M13 10V3L4 14h7v7l9-11h-7z"/>
                  </svg>
                  <span class="text-sm font-semibold tracking-wide uppercase medical-text">Powered by AI</span>
                </div>
              </div>
              <h2 class="text-3xl font-bold text-gray-900 mb-3 brand-text">
                Transform Your Health Data into Insights
              </h2>
              <p class="text-lg text-gray-600 max-w-xl mx-auto mb-2 medical-text">
                Upload medical reports and get instant AI-powered analysis with professional insights and recommendations.
              </p>
              <div class="flex justify-center items-center space-x-4 text-sm text-gray-500 mt-4">
                <span class="flex items-center space-x-1">
                  <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                  <span>Mistral OCR</span>
                </span>
                <span class="flex items-center space-x-1">
                  <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                  <span>Chutes.AI Analysis</span>
                </span>
                <span class="flex items-center space-x-1">
                  <svg class="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                  <span>PDF/Image Support</span>
                </span>
              </div>
              <p class="text-xs text-gray-400 mt-3">
                <span class="cursor-pointer text-blue-600 hover:underline font-medium">⚙️ Settings</span> 
                <span class="mx-2">•</span>
                <span>Coming soon: Local processing with docTR & Ollama</span>
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
              [documents]="(documents$ | async) || []"
              (deleteDocument)="onDeleteDocument($event)">
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

  onDeleteDocument(documentId: string): void {
    this.documentService.deleteDocument(documentId)
      .subscribe({
        next: (response) => {
          console.log('Document deleted successfully:', response);
        },
        error: (error) => {
          console.error('Delete failed:', error);
          alert('Failed to delete document. Please try again.');
        }
      });
  }
}