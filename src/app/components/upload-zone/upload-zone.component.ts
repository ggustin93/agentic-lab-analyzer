import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-upload-zone',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div 
      class="upload-zone"
      [class.dragover]="isDragOver"
      (dragover)="onDragOver($event)"
      (dragleave)="onDragLeave($event)"
      (drop)="onDrop($event)"
      (click)="fileInput.click()">
      
      <div class="flex flex-col items-center space-y-4">
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
      
      <input 
        #fileInput
        type="file" 
        class="hidden" 
        accept=".pdf,.png,.jpg,.jpeg"
        (change)="onFileSelected($event)">
    </div>
  `
})
export class UploadZoneComponent {
  @Output() fileSelected = new EventEmitter<File>();
  
  isDragOver = false;

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
}