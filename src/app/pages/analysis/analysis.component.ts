import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule, NavigationEnd } from '@angular/router';
import { Subject, takeUntil, switchMap, map, of, filter } from 'rxjs';
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
                class="text-gray-400 hover:text-gray-600 transition-colors duration-150 p-1 rounded-md hover:bg-gray-100">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
              </button>
              <div class="flex items-center space-x-2">
                <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                </svg>
                <h1 class="text-xl font-semibold text-gray-900">Analysis Results</h1>
              </div>
            </div>
            <div class="text-sm text-gray-500 font-medium bg-gray-100 px-3 py-1 rounded-md">
              {{ document?.title }}
            </div>
          </div>
        </div>
      </header>

      <!-- Loading State -->
      <div *ngIf="!document" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="text-center">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
            <svg class="w-8 h-8 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <h2 class="text-lg font-medium text-gray-900 mb-2">Processing Analysis</h2>
          <p class="text-gray-600">Please wait while we analyze your document...</p>
        </div>
      </div>

      <!-- Document Not Found -->
      <div *ngIf="document === null" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="text-center">
          <div class="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
            <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
          </div>
          <h2 class="text-xl font-semibold text-gray-900 mb-2">Document Not Found</h2>
          <p class="text-gray-600 mb-6">The requested document analysis could not be found.</p>
          <button routerLink="/" class="btn-primary">
            Return to Dashboard
          </button>
        </div>
      </div>

      <!-- Processing State -->
      <div *ngIf="document && document.status === DocumentStatus.PROCESSING" 
           class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
          <div class="text-center">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4">
              <svg class="w-8 h-8 text-blue-600 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <h2 class="text-xl font-semibold text-gray-900 mb-2">Processing Your Document</h2>
            <p class="text-gray-600 mb-6">{{ document.progressMessage }}</p>
            
            <!-- Progress Bar -->
            <div class="w-full max-w-md mx-auto">
              <div class="flex justify-between items-center mb-2">
                <span class="text-sm text-gray-600">Progress</span>
                <span class="text-sm text-gray-900 font-medium">{{ document.progress || 0 }}%</span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                     [style.width]="(document.progress || 0) + '%'"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Error State -->
      <div *ngIf="document && document.status === DocumentStatus.ERROR" 
           class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div class="bg-white rounded-lg shadow-sm border border-red-200 p-8">
          <div class="text-center">
            <div class="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-4">
              <svg class="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
              </svg>
            </div>
            <h2 class="text-xl font-semibold text-gray-900 mb-2">Processing Error</h2>
            <p class="text-gray-600 mb-6">
              {{ document.errorMessage || 'An error occurred while processing your document.' }}
            </p>
            <button routerLink="/" class="btn-primary">
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>

      <!-- Analysis Results -->
      <main *ngIf="document && document.status === DocumentStatus.COMPLETE" 
            class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <!-- Disclaimer Banner -->
        <app-disclaimer-banner></app-disclaimer-banner>

        <!-- View Toggle -->
        <div class="mb-8 flex justify-center">
          <div class="inline-flex bg-white rounded-lg border border-gray-200 shadow-sm p-1">
            <button
              (click)="setView('data')"
              [ngClass]="{
                'bg-blue-600 text-white shadow-sm': currentView === 'data',
                'text-gray-600 hover:text-gray-900 hover:bg-gray-50': currentView !== 'data'
              }"
              class="flex items-center px-4 py-3 text-sm font-medium rounded-md transition-all duration-200 ease-in-out min-w-[140px] justify-center"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2H9a2 2 0 00-2 2v10z"/>
              </svg>
              Lab Data
            </button>
            <button
              (click)="setView('insights')"
              [ngClass]="{
                'bg-blue-600 text-white shadow-sm': currentView === 'insights',
                'text-gray-600 hover:text-gray-900 hover:bg-gray-50': currentView !== 'insights'
              }"
              class="flex items-center px-4 py-3 text-sm font-medium rounded-md transition-all duration-200 ease-in-out min-w-[140px] justify-center"
            >
              <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
              Medical Insights
            </button>
          </div>
        </div>

        <!-- Content Views -->
        <div class="space-y-6">
          <!-- Extracted Data View -->
          <div *ngIf="currentView === 'data'">
            <app-data-table [data]="document.extractedData || []"></app-data-table>
          </div>

          <!-- AI Insights View -->
          <div *ngIf="currentView === 'insights'">
            <app-ai-insights [insights]="document.aiInsights || ''"></app-ai-insights>
          </div>
        </div>

        <!-- Raw Data Section -->
        <div class="mt-8">
          <div class="bg-white rounded-lg border border-gray-200 shadow-sm">
            <div class="px-6 py-4 border-b border-gray-200">
              <button 
                (click)="showRawData = !showRawData"
                class="flex items-center justify-between w-full text-left">
                <div class="flex items-center space-x-2">
                  <svg class="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/>
                  </svg>
                  <h3 class="text-lg font-medium text-gray-900">Raw Extracted Text</h3>
                </div>
                <svg class="w-5 h-5 text-gray-400 transition-transform duration-200" 
                     [class.rotate-180]="showRawData"
                     fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
            </div>
            
            <div *ngIf="showRawData" class="px-6 py-4">
              <div class="bg-gray-50 border border-gray-200 rounded-md p-4">
                <pre class="text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed overflow-x-auto">{{ document.rawText }}</pre>
              </div>
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
  currentView: 'data' | 'insights' = 'data';
  DocumentStatus = DocumentStatus;
  private destroy$ = new Subject<void>();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private documentService: DocumentAnalysisService
  ) {
    // Listen for router navigation events to handle direct navigation between analysis pages
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd),
      takeUntil(this.destroy$)
    ).subscribe(() => {
      // This will trigger when navigating between analysis pages
      // The paramMap subscription in ngOnInit will handle the actual data loading
    });
  }

  ngOnInit(): void {
    // Reset the document to undefined when initializing to show loading state
    this.document = undefined;
    
    // Use paramMap instead of params to react to all route parameter changes
    this.route.paramMap
      .pipe(
        takeUntil(this.destroy$),
        switchMap(params => {
          // Reset document to undefined on each navigation to show loading state
          this.document = undefined;
          
          const id = params.get('id');
          if (!id) {
            return of(null);
          }
          
          console.log('Fetching document with ID:', id);
          return this.documentService.getDocument(id);
        }),
        map(doc => {
          console.log('Document data received:', doc);
          return doc ? new DocumentViewModel(doc) : null;
        })
      )
      .subscribe({
        next: (document) => {
          console.log('Document view model:', document);
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

  setView(view: 'data' | 'insights'): void {
    this.currentView = view;
  }
}