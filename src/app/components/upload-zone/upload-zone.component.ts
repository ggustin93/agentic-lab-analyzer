import { Component, EventEmitter, Output, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-upload-zone',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div 
      class="upload-zone"
      [class.dragover]="isDragOver"
      [class.processing]="isUploading || progress !== undefined"
      (dragover)="onDragOver($event)"
      (dragleave)="onDragLeave($event)"
      (drop)="onDrop($event)"
      (click)="!isUploading && fileInput.click()">
      
      <!-- Normal upload state -->
      <div *ngIf="!isUploading && progress === undefined" class="flex flex-col items-center space-y-4">
        <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
        </svg>
        
        <div class="text-center">
          <h3 class="text-lg font-medium text-gray-900 mb-2">
            Drag & Drop Your Health Report Here
          </h3>
          <p class="text-gray-600 mb-4">
            Or click to select a file (PDF, PNG, JPG)
          </p>
          <button type="button" class="btn-primary">
            Select File
          </button>
        </div>
      </div>
      
      <!-- Progress state -->
      <div *ngIf="isUploading || progress !== undefined" class="flex flex-col items-center space-y-4">
        <div class="relative">
          <!-- Stage-specific icons and colors -->
          <div [ngSwitch]="processingStage" class="w-16 h-16 flex items-center justify-center rounded-full transition-all duration-500">
            <!-- OCR Extraction Stage -->
            <div *ngSwitchCase="'ocr_extraction'" class="bg-yellow-100 w-16 h-16 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
              </svg>
            </div>
            
            <!-- AI Analysis Stage -->
            <div *ngSwitchCase="'ai_analysis'" class="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
            </div>
            
            <!-- Saving Results Stage -->
            <div *ngSwitchCase="'saving_results'" class="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"/>
              </svg>
            </div>
            
            <!-- Complete Stage -->
            <div *ngSwitchCase="'complete'" class="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
            </div>
            
            <!-- Default/Unknown Stage -->
            <div *ngSwitchDefault class="bg-gray-100 w-16 h-16 rounded-full flex items-center justify-center">
              <svg class="w-8 h-8 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
              </svg>
            </div>
          </div>
          
          <!-- Processing spinner overlay - only show if not complete -->
          <div *ngIf="processingStage !== 'complete'" 
               class="absolute inset-0 flex items-center justify-center">
            <svg class="animate-spin h-6 w-6" [class]="getSpinnerColorClass()" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        </div>
        
        <div class="text-center w-full max-w-xs">
          <h3 class="text-lg font-medium mb-2" [class]="getTextColorClass()">
            {{ getProgressText() }}
          </h3>
          
          <!-- Enhanced Progress bar with stage-specific colors -->
          <div class="w-full bg-gray-200 rounded-full h-3 mb-2 shadow-inner">
            <div class="h-3 rounded-full transition-all duration-500 ease-out" 
                 [class]="getProgressBarColorClass()"
                 [style.width.%]="progress || 0"></div>
          </div>
          
          <div class="flex justify-between items-center">
            <p class="text-sm font-semibold" [class]="getTextColorClass()">
              {{ progress || 0 }}% complete
            </p>
            <p class="text-xs text-gray-500">
              Stage {{ getCurrentStageNumber() }}/4
            </p>
          </div>
          
          <!-- Stage indicator dots -->
          <div class="flex justify-center space-x-2 mt-3">
            <div class="w-2 h-2 rounded-full transition-all duration-300" 
                 [class]="getCurrentStageNumber() >= 1 ? 'bg-yellow-500' : 'bg-gray-300'"></div>
            <div class="w-2 h-2 rounded-full transition-all duration-300" 
                 [class]="getCurrentStageNumber() >= 2 ? 'bg-blue-500' : 'bg-gray-300'"></div>
            <div class="w-2 h-2 rounded-full transition-all duration-300" 
                 [class]="getCurrentStageNumber() >= 3 ? 'bg-purple-500' : 'bg-gray-300'"></div>
            <div class="w-2 h-2 rounded-full transition-all duration-300" 
                 [class]="getCurrentStageNumber() >= 4 ? 'bg-green-500' : 'bg-gray-300'"></div>
          </div>
        </div>
      </div>
      
      <input 
        #fileInput
        type="file" 
        class="hidden" 
        accept=".pdf,.png,.jpg,.jpeg"
        (change)="onFileSelected($event)">
    </div>
  `
})
export class UploadZoneComponent implements OnChanges {
  @Output() fileSelected = new EventEmitter<File>();
  @Input() isUploading = false;
  @Input() progress: number | undefined = undefined;
  @Input() processingStage: string | undefined = undefined;
  
  isDragOver = false;

  ngOnChanges(changes: SimpleChanges): void {
    // Enhanced logging for debugging progress updates
    if (changes['progress'] && changes['progress'].currentValue !== changes['progress'].previousValue) {
      console.log(`🎯 UPLOAD ZONE - Progress updated: ${changes['progress'].previousValue}% → ${changes['progress'].currentValue}%`);
    }
    
    if (changes['processingStage'] && changes['processingStage'].currentValue !== changes['processingStage'].previousValue) {
      console.log(`🔄 UPLOAD ZONE - Stage updated: "${changes['processingStage'].previousValue}" → "${changes['processingStage'].currentValue}"`);
    }
    
    // Log current state for debugging
    if (this.progress !== undefined || this.processingStage) {
      console.log(`📊 UPLOAD ZONE - Current state: ${this.progress}% | Stage: "${this.processingStage}"`);
    }
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = true;
  }

  onDragLeave(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;
  }

  onDrop(event: DragEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.isDragOver = false;

    const files = event.dataTransfer?.files;
    if (files && files.length > 0) {
      this.handleFile(files[0]);
    }
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      this.handleFile(input.files[0]);
    }
  }

  private handleFile(file: File): void {
    const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    
    if (!allowedTypes.includes(file.type)) {
      alert('Please select a valid file type (PDF, PNG, or JPG)');
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      alert('File size must be less than 10MB');
      return;
    }

    this.fileSelected.emit(file);
  }

  getProgressText(): string {
    if (!this.processingStage) {
      return this.isUploading ? 'Uploading...' : 'Processing...';
    }
    
    switch (this.processingStage) {
      case 'ocr_extraction':
        return 'Extracting text from document...';
      case 'ai_analysis':
        return 'Analyzing health data with AI...';
      case 'saving_results':
        return 'Finalizing results...';
      case 'complete':
        return 'Processing complete!';
      default:
        return 'Processing...';
    }
  }

  getTextColorClass(): string {
    switch (this.processingStage) {
      case 'ocr_extraction':
        return 'text-yellow-800';
      case 'ai_analysis':
        return 'text-blue-800';
      case 'saving_results':
        return 'text-purple-800';
      case 'complete':
        return 'text-green-800';
      default:
        return 'text-gray-800';
    }
  }

  getProgressBarColorClass(): string {
    switch (this.processingStage) {
      case 'ocr_extraction':
        return 'bg-gradient-to-r from-yellow-400 to-yellow-600';
      case 'ai_analysis':
        return 'bg-gradient-to-r from-blue-400 to-blue-600';
      case 'saving_results':
        return 'bg-gradient-to-r from-purple-400 to-purple-600';
      case 'complete':
        return 'bg-gradient-to-r from-green-400 to-green-600';
      default:
        return 'bg-gradient-to-r from-gray-400 to-gray-600';
    }
  }

  getSpinnerColorClass(): string {
    switch (this.processingStage) {
      case 'ocr_extraction':
        return 'text-yellow-600';
      case 'ai_analysis':
        return 'text-blue-600';
      case 'saving_results':
        return 'text-purple-600';
      default:
        return 'text-gray-600';
    }
  }

  getCurrentStageNumber(): number {
    switch (this.processingStage) {
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