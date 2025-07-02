import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-disclaimer-banner',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="disclaimer-banner">
      <div class="flex items-start space-x-3">
        <div class="flex-shrink-0">
          <svg class="w-6 h-6 text-warning-500" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
          </svg>
        </div>
        <div class="flex-1">
          <h3 class="text-sm font-medium text-warning-800 mb-1">
            Important Medical Disclaimer
          </h3>
          <p class="text-sm text-warning-700">
            <strong>This is not medical advice.</strong> The information provided is for educational purposes only. 
            Always consult a qualified healthcare professional regarding any health concerns or before making any 
            decisions related to your health or treatment.
          </p>
        </div>
      </div>
    </div>
  `
})
export class DisclaimerBannerComponent {}