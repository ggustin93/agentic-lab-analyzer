/**
 * 📋 Document List Component - Angular 19 Expert Implementation
 * 
 * Advanced document management interface with real-time status tracking.
 * Demonstrates expert-level Angular 19 patterns and medical UX design.
 * 
 * Features:
 * - Signal-based reactive architecture
 * - Real-time processing status visualization
 * - 4-stage progress tracking with animations
 * - Separated template and SCSS files
 * - Expert-level accessibility support
 * - Type-safe document status management
 * - Responsive design with micro-interactions
 * 
 * @author Angular Expert Team
 * @version 2.0.0 - Angular 19 Modernization
 */

import { 
  Component, 
  output,
  input, 
  computed, 
  effect,
  ChangeDetectionStrategy 
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { HealthDocument, DocumentStatus } from '../../models/document.model';

/**
 * 🏥 Processing Stage Type Definition
 * 
 * Represents the 4-stage medical document processing pipeline:
 * 1. ocr_extraction - OCR text extraction from uploaded document
 * 2. ai_analysis - AI analysis of extracted health data  
 * 3. saving_results - Persisting analysis results to database
 * 4. complete - Processing finished successfully
 */
type ProcessingStage = 'ocr_extraction' | 'ai_analysis' | 'saving_results' | 'complete' | undefined;

@Component({
  selector: 'app-document-list',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './document-list.component.html',
  styleUrl: './document-list.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    'class': 'block',
    'role': 'region',
    'aria-label': 'Document analysis list'
  }
})
export class DocumentListComponent {
  
  // ===== 📤 Component Outputs (Angular 19) =====
  /**
   * Emits document ID when user requests deletion.
   * Parent component handles the actual deletion logic.
   */
  readonly deleteDocument = output<string>();
  
  // ===== 📥 Signal-Based Inputs (Angular 19) =====
  /**
   * 📋 Documents Array Signal
   * Array of health documents to display in the list.
   * Updates automatically trigger reactive re-renders.
   */
  readonly documents = input<HealthDocument[]>([]);
  
  // ===== 📊 Public Constants for Template =====
  /**
   * DocumentStatus enum exposure for template usage.
   * Enables type-safe status comparisons in Angular templates.
   */
  readonly DocumentStatus = DocumentStatus;
  
  // ===== 💡 Computed Signals for Derived State =====
  /**
   * 🔄 Processing Documents Count
   * Computes number of documents currently being processed.
   * Used for debugging and potential progress indicators.
   */
  readonly processingDocumentsCount = computed(() => {
    return this.documents().filter(doc => doc.status === DocumentStatus.PROCESSING).length;
  });
  
  /**
   * ✅ Completed Documents Count  
   * Computes number of successfully processed documents.
   * Could be used for analytics or dashboard statistics.
   */
  readonly completedDocumentsCount = computed(() => {
    return this.documents().filter(doc => doc.status === DocumentStatus.COMPLETE).length;
  });
  
  /**
   * 📈 Overall Processing Progress
   * Computes average progress across all processing documents.
   * Useful for global progress indicators.
   */
  readonly overallProgress = computed(() => {
    const processingDocs = this.documents().filter(doc => 
      doc.status === DocumentStatus.PROCESSING && doc.progress !== undefined
    );
    
    if (processingDocs.length === 0) return 0;
    
    const totalProgress = processingDocs.reduce((sum, doc) => sum + (doc.progress || 0), 0);
    return Math.round(totalProgress / processingDocs.length);
  });
  
  // ===== 🔄 Reactive Effects (Angular 19) =====
  /**
   * 📊 Processing Progress Logger Effect
   * Logs real-time processing updates for debugging.
   * Demonstrates effect() usage for reactive side effects.
   */
  private readonly progressLoggingEffect = effect(() => {
    const processingDocs = this.documents().filter(doc => doc.status === DocumentStatus.PROCESSING);
    
    processingDocs.forEach(doc => {
      console.log(`🔄 DOCUMENT LIST - Progress Update: ${doc.filename} - ${doc.progress}% (${doc.processing_stage})`);
    });
    
    // Enhanced analytics logging
    if (processingDocs.length > 0) {
      console.log(`📊 DOCUMENT LIST - Overall Progress: ${this.overallProgress()}% (${processingDocs.length} documents processing)`);
    }
  });
  
  // ===== 🕒 Date & Time Utilities =====
  
  /**
   * 📅 Relative Time Formatter
   * 
   * Converts ISO date strings to human-readable relative time.
   * Provides user-friendly temporal context for document timestamps.
   * 
   * @param dateString - ISO date string from document metadata
   * @returns Human-readable relative time string
   */
  getRelativeTime(dateString: string): string {
    if (!dateString) return 'Unknown date';
    
    try {
      const date = new Date(dateString);
      
      // Validate date parsing
      if (isNaN(date.getTime())) {
        console.warn(`📅 DOCUMENT LIST - Invalid date format: ${dateString}`);
        return 'Invalid date';
      }
      
      const now = new Date();
      const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
      
      // Comprehensive relative time logic
      if (diffInMinutes < 1) return 'Just now';
      if (diffInMinutes < 60) return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
      
      const diffInHours = Math.floor(diffInMinutes / 60);
      if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
      
      const diffInDays = Math.floor(diffInHours / 24);
      if (diffInDays < 7) return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
      
      const diffInWeeks = Math.floor(diffInDays / 7);
      if (diffInWeeks < 4) return `${diffInWeeks} week${diffInWeeks > 1 ? 's' : ''} ago`;
      
      // For older documents, show formatted date
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      console.error('📅 DOCUMENT LIST - Date parsing error:', dateString, error);
      return 'Invalid date';
    }
  }
  
  // ===== 🎬 Event Handlers =====
  
  /**
   * 🗑️ Document Deletion Handler
   * 
   * Handles document deletion requests with user confirmation.
   * Emits deletion event to parent component for actual processing.
   * 
   * @param documentId - Unique identifier of document to delete
   */
  onDeleteDocument(documentId: string): void {
    console.log(`🗑️ DOCUMENT LIST - Delete requested for document: ${documentId}`);
    
    const confirmMessage = 'Are you sure you want to delete this document analysis? This action cannot be undone.';
    
    if (confirm(confirmMessage)) {
      console.log(`✅ DOCUMENT LIST - Deletion confirmed, emitting to parent`);
      this.deleteDocument.emit(documentId);
    } else {
      console.log(`❌ DOCUMENT LIST - Deletion cancelled by user`);
    }
  }
  
  // ===== 🎨 UI State Computed Methods =====
  
  /**
   * 📝 Processing Stage Text Generator
   * 
   * Generates user-friendly text for each processing stage.
   * Provides clear communication about current system activity.
   * 
   * @param document - HealthDocument with processing information
   * @returns Human-readable stage description
   */
  processingStageText(document: HealthDocument): string {
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
        console.warn(`🚨 DOCUMENT LIST - Unknown processing stage: ${document.processing_stage}`);
        return 'Processing...';
    }
  }
  
  /**
   * 🎨 Processing Stage Color Classes
   * 
   * Generates CSS classes for stage-specific color coding.
   * Creates visually consistent stage-to-color mapping.
   * 
   * @param document - HealthDocument with processing information
   * @returns CSS class string for stage styling
   */
  processingStageColor(document: HealthDocument): string {
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
  
  /**
   * 📊 Progress Bar Color Classes
   * 
   * Generates CSS classes for progress bar color coordination.
   * Matches progress bar colors to processing stages.
   * 
   * @param document - HealthDocument with processing information
   * @returns CSS class string for progress bar styling
   */
  progressBarColor(document: HealthDocument): string {
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
  
  /**
   * 🔢 Current Stage Number Calculator
   * 
   * Maps processing stages to numerical values for UI indicators.
   * Enables progressive stage visualization in the interface.
   * 
   * @param document - HealthDocument with processing information
   * @returns Stage number (1-4) for progress visualization
   */
  currentStageNumber(document: HealthDocument): number {
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

/**
 * 📚 Component Usage Example:
 * 
 * ```html
 * <app-document-list
 *   [documents]="healthDocuments()"
 *   (deleteDocument)="handleDocumentDeletion($event)">
 * </app-document-list>
 * ```
 * 
 * 🏗️ Architecture Notes:
 * 
 * This component demonstrates Angular 19 excellence:
 * - Signal-based inputs for optimal change detection
 * - Output signals for type-safe event emission
 * - Computed signals for derived state management
 * - Effects for reactive side effects and logging
 * - Separated template and styles for maintainability
 * - Expert-level accessibility with ARIA attributes
 * - Type-safe processing stage management
 * - Comprehensive error handling and validation
 * - Real-time progress visualization with animations
 * - Responsive design with micro-interactions
 * - Medical UX patterns for healthcare applications
 */