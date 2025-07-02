import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { Subject, takeUntil, switchMap, map } from 'rxjs';
import { DocumentAnalysisService } from '../../services/document-analysis.service';
import { DisclaimerBannerComponent } from '../../components/disclaimer-banner/disclaimer-banner.component';
import { DataTableComponent } from '../../components/data-table/data-table.component';
import { AiInsightsComponent } from '../../components/ai-insights/ai-insights.component';
import { HealthDocument, DocumentStatus, DocumentViewModel } from '../../models/document.model';

@Component({
  selector: 'app-analysis',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    DisclaimerBannerComponent, 
    DataTableComponent, 
    AiInsightsComponent
  ],
  template: `
    <div class="min-h-screen bg-gray-50">
      <!-- Header -->
      <header class="bg-white shadow-sm border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div class="flex items-center justify-between h-16">
            <div class="flex items-center space-x-3">
              <button 
                routerLink="/"
                class="text-gray-400 hover:text-gray-600 transition-colors duration-150">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
              </button>
              <h1 class="text-xl font-semibold text-gray-900">Analysis Results</h1>
            </div>
            <div class="text-sm text-gray-500">
              {{ document?.title }}
            </div>
          </div>
        </div>
      </header>

      <!-- Loading State -->
      <div *ngIf="!document" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p class="text-gray-600">Loading analysis...</p>
        </div>
      </div>

      <!-- Document Not Found -->
      <div *ngIf="document === null" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center">
          <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <h2 class="text-xl font-semibold text-gray-900 mb-2">Document Not Found</h2>
          <p class="text-gray-600 mb-4">The requested document analysis could not be found.</p>
          <button routerLink="/" class="btn-primary">
            Return to Dashboard
          </button>
        </div>
      </div>

      <!-- Processing State -->
      <div *ngIf="document && document.status === DocumentStatus.PROCESSING" 
           class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <h2 class="text-xl font-semibold text-gray-900 mb-2">Processing Your Document</h2>
          <p class="text-gray-600">Please wait while we analyze your health report...</p>
        </div>
      </div>

      <!-- Error State -->
      <div *ngIf="document && document.status === DocumentStatus.ERROR" 
           class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="text-center">
          <svg class="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
          </svg>
          <h2 class="text-xl font-semibold text-gray-900 mb-2">Processing Error</h2>
          <p class="text-gray-600 mb-4">
            {{ document.errorMessage || 'An error occurred while processing your document.' }}
          </p>
          <button routerLink="/" class="btn-primary">
            Return to Dashboard
          </button>
        </div>
      </div>

      <!-- Analysis Results -->
      <main *ngIf="document && document.status === DocumentStatus.COMPLETE" 
            class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <!-- Disclaimer Banner -->
        <app-disclaimer-banner></app-disclaimer-banner>

        <!-- Two Column Layout -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Left Column: Extracted Data -->
          <div>
            <app-data-table [data]="document.extractedData || []"></app-data-table>
          </div>

          <!-- Right Column: AI Insights -->
          <div>
            <app-ai-insights [insights]="document.aiInsights || ''"></app-ai-insights>
          </div>
        </div>

        <!-- Raw Data Toggle -->
        <div class="mt-8">
          <button 
            (click)="showRawData = !showRawData"
            class="btn-secondary">
            {{ showRawData ? 'Hide' : 'Show' }} Raw Extracted Text
          </button>
          
          <div *ngIf="showRawData" class="mt-4 bg-white shadow-sm rounded-lg overflow-hidden">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">Raw Extracted Text</h3>
            </div>
            <div class="px-6 py-4">
              <pre class="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-4 rounded border overflow-x-auto">{{ document.rawText }}</pre>
            </div>
          </div>
        </div>
      </main>
    </div>
  `
})
export class AnalysisComponent implements OnInit, OnDestroy {
  document: DocumentViewModel | null | undefined = undefined;
  showRawData = false;
  DocumentStatus = DocumentStatus;
  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private documentService: DocumentAnalysisService
  ) {}

  ngOnInit(): void {
    this.route.params
      .pipe(
        takeUntil(this.destroy$),
        switchMap(params => this.documentService.getDocument(params['id'])),
        map(doc => doc ? new DocumentViewModel(doc) : null)
      )
      .subscribe({
        next: (document) => {
          this.document = document;
        },
        error: (error) => {
          console.error('Error loading document:', error);
          this.document = null;
        }
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}