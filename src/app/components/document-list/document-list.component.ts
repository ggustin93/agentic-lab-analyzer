import { Component, Input, Output, EventEmitter, ChangeDetectionStrategy } from '@angular/core';
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
              <span [ngClass]="getStatusClass(document.status)">
                <span *ngIf="document.status === DocumentStatus.PROCESSING" class="flex items-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Processing...
                </span>
                <span *ngIf="document.status === DocumentStatus.COMPLETE" class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                  </svg>
                  Complete
                </span>
                <span *ngIf="document.status === DocumentStatus.ERROR" class="flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                  </svg>
                  Error
                </span>
              </span>
              
              <button *ngIf="document.status === DocumentStatus.COMPLETE"
                      [routerLink]="['/analysis', document.id]"
                      class="text-primary-600 hover:text-primary-800 text-sm font-medium">
                View Results
              </button>
              
              <button (click)="onDeleteDocument(document.id)"
                      class="text-gray-400 hover:text-red-600 transition-colors duration-150">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9zM4 5a2 2 0 012-2v1a1 1 0 001 1h6a1 1 0 001-1V3a2 2 0 012 2v6.5l1.5 1.5A2 2 0 0115 17H5a2 2 0 01-1.5-3.5L5 11.5V5zM5 11.5V17h10v-5.5l-1.5-1.5H6.5L5 11.5z" clip-rule="evenodd"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DocumentListComponent {
  @Input() documents: HealthDocument[] = [];
  @Output() deleteDocument = new EventEmitter<string>();
  
  readonly DocumentStatus = DocumentStatus;

  trackByDocumentId(index: number, document: HealthDocument): string {
    return document.id;
  }

  getStatusClass(status: DocumentStatus): string {
    switch (status) {
      case DocumentStatus.PROCESSING:
        return 'status-processing';
      case DocumentStatus.COMPLETE:
        return 'status-complete';
      case DocumentStatus.ERROR:
        return 'status-error';
      default:
        return '';
    }
  }

  getRelativeTime(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} minutes ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours} hours ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays} days ago`;
    
    return date.toLocaleDateString();
  }

  onDeleteDocument(documentId: string): void {
    if (confirm('Are you sure you want to delete this document analysis?')) {
      this.deleteDocument.emit(documentId);
    }
  }
}