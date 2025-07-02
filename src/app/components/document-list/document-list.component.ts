import { Component, Input, Output, EventEmitter, OnChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HealthDocument, DocumentStatus } from '../../models/document.model';

@Component({
  selector: 'app-document-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="bg-white shadow-sm rounded-lg overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <h2 class="text-lg font-medium text-gray-900">Recent Analyses</h2>
      </div>
      
      <div *ngIf="documents.length === 0" class="px-6 py-8 text-center">
        <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <p class="text-gray-500">No documents analyzed yet</p>
        <p class="text-sm text-gray-400 mt-1">Upload your first health report to get started</p>
      </div>
      
      <div *ngIf="documents.length > 0" class="divide-y divide-gray-200">
        <div *ngFor="let document of documents; trackBy: trackByDocumentId" 
             class="px-6 py-4 hover:bg-gray-50 transition-colors duration-150">
          
          <div class="flex items-center justify-between">
            <div class="flex-1 min-w-0">
              <div class="flex items-center space-x-3">
                <div class="flex-shrink-0">
                  <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                  </svg>
                </div>
                
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-gray-900 truncate">
                    {{ document.filename }}
                  </p>
                  <p class="text-sm text-gray-500">
                    {{ getRelativeTime(document.uploaded_at) }}
                  </p>
                </div>
              </div>
            </div>
            
            <div class="flex items-center space-x-3">
              <!-- Processing Status with Enhanced Stage-Specific Display -->
              <div *ngIf="document.status === DocumentStatus.PROCESSING" class="flex flex-col items-end min-w-0">
                <!-- Stage badge with color coding -->
                <div class="flex items-center mb-2 px-2 py-1 rounded-full border" [class]="getProcessingStageColor(document)">
                  <!-- Stage-specific spinner icon -->
                  <svg *ngIf="document.processing_stage !== 'complete'" 
                       class="animate-spin -ml-1 mr-2 h-3 w-3" 
                       [class]="getProcessingStageColor(document).split(' ')[0]" 
                       fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <!-- Checkmark for complete -->
                  <svg *ngIf="document.processing_stage === 'complete'" 
                       class="mr-2 h-3 w-3 text-green-600" 
                       fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                  </svg>
                  <span class="text-xs font-medium">
                    {{ getProcessingStageText(document) }}
                  </span>
                </div>
                <!-- Enhanced Progress Bar with Stage Colors -->
                <div class="w-28 bg-gray-200 rounded-full h-2 mb-1 shadow-inner">
                  <div class="h-2 rounded-full transition-all duration-500 ease-out" 
                       [class]="getProgressBarColor(document)"
                       [style.width.%]="document.progress || 0"></div>
                </div>
                <span class="text-xs font-semibold" [class]="getProcessingStageColor(document).split(' ')[0]">
                  {{ document.progress || 0 }}% • Stage {{ getCurrentStageNumber(document) }}/4
                </span>
              </div>

              <!-- Complete Status -->
              <span *ngIf="document.status === DocumentStatus.COMPLETE" 
                    class="flex items-center text-green-600 bg-green-50 px-3 py-1 rounded-full text-sm font-medium">
                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                </svg>
                Complete
              </span>

              <!-- Error Status -->
              <span *ngIf="document.status === DocumentStatus.ERROR" 
                    class="flex items-center text-red-600 bg-red-50 px-3 py-1 rounded-full text-sm font-medium">
                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                Error
              </span>
              
              <button *ngIf="document.status === DocumentStatus.COMPLETE"
                      [routerLink]="['/analysis', document.id]"
                      class="text-primary-600 hover:text-primary-800 text-sm font-medium">
                View Results
              </button>
              
              <button (click)="onDeleteDocument(document.id)"
                      class="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-all duration-150"
                      title="Delete document">
                <!-- Hero Icons - Trash Can -->
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  // Removed OnPush to ensure progress updates are detected in real-time
})
export class DocumentListComponent implements OnChanges {
  @Input() documents: HealthDocument[] = [];
  @Output() deleteDocument = new EventEmitter<string>();
  
  readonly DocumentStatus = DocumentStatus;

  ngOnChanges(): void {
    // Log progress updates for debugging real-time functionality
    const processingDocs = this.documents.filter(doc => doc.status === DocumentStatus.PROCESSING);
    processingDocs.forEach(doc => {
      console.log(`🔄 Document List Update - ${doc.filename}: ${doc.progress}% (${doc.processing_stage})`);
    });
  }

  trackByDocumentId(index: number, document: HealthDocument): string {
    return document.id;
  }

  getRelativeTime(dateString: string): string {
    if (!dateString) return 'Unknown date';
    
    try {
      const date = new Date(dateString);
      
      // Check if date is valid
      if (isNaN(date.getTime())) {
        return 'Invalid date';
      }
      
      const now = new Date();
      const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
      
      if (diffInMinutes < 1) return 'Just now';
      if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
      
      const diffInHours = Math.floor(diffInMinutes / 60);
      if (diffInHours < 24) return `${diffInHours} hours ago`;
      
      const diffInDays = Math.floor(diffInHours / 24);
      if (diffInDays < 7) return `${diffInDays} days ago`;
      
      return date.toLocaleDateString();
    } catch (error) {
      console.error('Error parsing date:', dateString, error);
      return 'Invalid date';
    }
  }

  onDeleteDocument(documentId: string): void {
    if (confirm('Are you sure you want to delete this document analysis?')) {
      this.deleteDocument.emit(documentId);
    }
  }
  
  getProcessingStageText(document: HealthDocument): string {
    console.log(`📋 DOCUMENT LIST - Getting stage text for ${document.id}: Stage="${document.processing_stage}", Progress=${document.progress}%`);
    
    if (!document.processing_stage) return 'Starting processing...';
    
    switch (document.processing_stage) {
      case 'ocr_extraction':
        return 'Extracting text...';
      case 'ai_analysis':
        return 'AI analyzing data...';
      case 'saving_results':
        return 'Finalizing results...';
      case 'complete':
        return 'Complete!';
      default:
        return 'Processing...';
    }
  }

  getProcessingStageColor(document: HealthDocument): string {
    switch (document.processing_stage) {
      case 'ocr_extraction':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'ai_analysis':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'saving_results':
        return 'text-purple-600 bg-purple-50 border-purple-200';
      case 'complete':
        return 'text-green-600 bg-green-50 border-green-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  }

  getProgressBarColor(document: HealthDocument): string {
    switch (document.processing_stage) {
      case 'ocr_extraction':
        return 'bg-yellow-500';
      case 'ai_analysis':
        return 'bg-blue-500';
      case 'saving_results':
        return 'bg-purple-500';
      case 'complete':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  }

  getCurrentStageNumber(document: HealthDocument): number {
    switch (document.processing_stage) {
      case 'ocr_extraction':
        return 1;
      case 'ai_analysis':
        return 2;
      case 'saving_results':
        return 3;
      case 'complete':
        return 4;
      default:
        return 0;
    }
  }
}