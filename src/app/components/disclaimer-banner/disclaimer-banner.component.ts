import { Component, ChangeDetectionStrategy } from '@angular/core';

/**
 * Medical disclaimer banner component for health-related applications
 * 
 * Key architectural decisions:
 * - Standalone component for better modularity and tree-shaking
 * - OnPush strategy for optimal performance (no data changes expected)
 * - Pure Tailwind CSS for consistent design system integration
 * - Semantic HTML with proper accessibility attributes
 * - No external dependencies - self-contained warning icon
 */
@Component({
  selector: 'app-disclaimer-banner',
  standalone: true,
  template: `
    <div 
      class="disclaimer-banner bg-amber-50 border border-amber-200 rounded-lg p-4"
      role="alert"
      aria-labelledby="disclaimer-title">
      <div class="flex items-start space-x-3">
        <!-- Warning icon with proper ARIA attributes -->
        <div class="flex-shrink-0" aria-hidden="true">
          <svg 
            class="w-6 h-6 text-amber-600" 
            fill="currentColor" 
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg">
            <path 
              fill-rule="evenodd" 
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" 
              clip-rule="evenodd"/>
          </svg>
        </div>
        
        <!-- Content with semantic structure -->
        <div class="flex-1">
          <h3 
            id="disclaimer-title"
            class="text-sm font-semibold text-amber-800 mb-2">
            Important Medical Disclaimer
          </h3>
          <p class="text-sm text-amber-700 leading-relaxed">
            <strong>This is not medical advice.</strong> The information provided is for educational purposes only. 
            Always consult a qualified healthcare professional regarding any health concerns or before making any 
            decisions related to your health or treatment.
          </p>
        </div>
      </div>
    </div>
  `,
  styles: [`
    /* Component-specific styles for enhanced UX */
    .disclaimer-banner {
      /* Smooth transitions for dynamic showing/hiding */
      transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
    }
    
    /* Focus management for accessibility */
    .disclaimer-banner:focus-within {
      @apply ring-2 ring-amber-500 ring-offset-2;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
      .disclaimer-banner {
        @apply border-2 border-amber-600;
      }
    }
    
    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
      .disclaimer-banner {
        transition: none;
      }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DisclaimerBannerComponent {
  /**
   * Static component with no dynamic state
   * OnPush strategy is optimal as content never changes
   * Component serves as a pure presentational element
   */
}