import { 
  Component, 
  output,
  input, 
  computed, 
  ChangeDetectionStrategy 
} from '@angular/core';
import { RouterModule } from '@angular/router';
import { HealthDocument, DocumentStatus } from '../../models/document.model';

/**
 * Document List Component - Clean Angular 19 Implementation
 * 
 * Displays health documents with real-time processing status
 * Key features:
 * - Signal-based reactive architecture
 * - 4-stage progress tracking (OCR → AI Analysis → Saving → Complete)
 * - Type-safe document status management
 * - Clean separation of concerns
 */
@Component({
  selector: 'app-document-list',
  standalone: true,
  imports: [RouterModule],
  templateUrl: './document-list.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
  host: {
    'class': 'block',
    'role': 'region',
    'aria-label': 'Document analysis list'
  }
})
export class DocumentListComponent {
  
  /**
   * Emits document ID when user requests deletion
   */
  readonly deleteDocument = output<string>();
  
  /**
   * Health documents to display in the list
   */
  readonly documents = input<HealthDocument[]>([]);
  
  /**
   * Expose DocumentStatus enum for template usage
   */
  readonly DocumentStatus = DocumentStatus;
  
  /**
   * Count of documents currently being processed
   */
  readonly processingCount = computed(() => 
    this.documents().filter(doc => doc.status === DocumentStatus.PROCESSING).length
  );
  
  /**
   * Overall processing progress across all documents
   */
  readonly overallProgress = computed(() => {
    const processingDocs = this.documents().filter(doc => 
      doc.status === DocumentStatus.PROCESSING && doc.progress !== undefined
    );
    
    if (processingDocs.length === 0) return 0;
    
    const totalProgress = processingDocs.reduce((sum, doc) => sum + (doc.progress || 0), 0);
    return Math.round(totalProgress / processingDocs.length);
  });
  
  /**
   * Converts date strings to human-readable relative time
   */
  getRelativeTime(dateString: string): string {
    if (!dateString) return 'Unknown date';
    
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'Invalid date';
      
      const now = new Date();
      const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
      
      if (diffInMinutes < 1) return 'Just now';
      if (diffInMinutes < 60) return `${diffInMinutes} minute${diffInMinutes > 1 ? 's' : ''} ago`;
      
      const diffInHours = Math.floor(diffInMinutes / 60);
      if (diffInHours < 24) return `${diffInHours} hour${diffInHours > 1 ? 's' : ''} ago`;
      
      const diffInDays = Math.floor(diffInHours / 24);
      if (diffInDays < 7) return `${diffInDays} day${diffInDays > 1 ? 's' : ''} ago`;
      
      // For older documents, show formatted date
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      console.error('Date parsing error:', dateString, error);
      return 'Invalid date';
    }
  }
  
  /**
   * Handles document deletion with user confirmation
   */
  onDeleteDocument(documentId: string): void {
    const confirmMessage = 'Are you sure you want to delete this document analysis? This action cannot be undone.';
    
    if (confirm(confirmMessage)) {
      this.deleteDocument.emit(documentId);
    }
  }
  
  /**
   * Gets user-friendly text for processing stages
   */
  processingStageText(document: HealthDocument): string {
    if (!document.processing_stage) return 'Starting processing...';
    
    const stageTexts = {
      'ocr_extraction': 'Extracting text...',
      'ai_analysis': 'AI analyzing data...',
      'saving_results': 'Finalizing results...',
      'complete': 'Complete!'
    };
    
    return (document.processing_stage && stageTexts[document.processing_stage]) || 'Processing...';
  }
  
  /**
   * Gets CSS classes for stage-specific styling
   */
  processingStageColor(document: HealthDocument): string {
    const stageStyles = {
      'ocr_extraction': 'text-yellow-600 bg-yellow-50 border-yellow-200',
      'ai_analysis': 'text-blue-600 bg-blue-50 border-blue-200',
      'saving_results': 'text-purple-600 bg-purple-50 border-purple-200',
      'complete': 'text-green-600 bg-green-50 border-green-200'
    };
    
    return (document.processing_stage && stageStyles[document.processing_stage]) || 'text-gray-600 bg-gray-50 border-gray-200';
  }
  
  /**
   * Gets progress bar color classes
   */
  progressBarColor(document: HealthDocument): string {
    const colorMap = {
      'ocr_extraction': 'bg-yellow-500',
      'ai_analysis': 'bg-blue-500',
      'saving_results': 'bg-purple-500',
      'complete': 'bg-green-500'
    };
    
    return (document.processing_stage && colorMap[document.processing_stage]) || 'bg-gray-500';
  }
  
  /**
   * Gets current stage number for progress visualization
   */
  currentStageNumber(document: HealthDocument): number {
    const stageNumbers = {
      'ocr_extraction': 1,
      'ai_analysis': 2,
      'saving_results': 3,
      'complete': 4
    };
    
    return (document.processing_stage && stageNumbers[document.processing_stage]) || 0;
  }
}