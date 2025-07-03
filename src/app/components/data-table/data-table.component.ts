import { Component, ChangeDetectionStrategy, computed, input, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HealthMarker } from '../../models/document.model';
import { MathFormulaComponent } from '../math-formula/math-formula.component';
import { LabMarkerInfoService, LabMarkerInfo } from '../../services/lab-marker-info.service';
import { TooltipDirective } from '../../directives/tooltip.directive';

/**
 * Data Table Component - Angular 19 Modernized
 * 
 * Displays extracted health marker data in a structured table format.
 * Demonstrates Angular 19 best practices:
 * - Signal-based inputs using input() instead of @Input() decorator
 * - New control flow (@for, @if) instead of structural directives
 * - inject() function for dependency injection
 * - Computed signals for derived state and complex calculations
 * - OnPush change detection for optimal performance
 * - Pure OCR-first data display philosophy (no fallback contamination)
 */
@Component({
  selector: 'app-data-table',
  standalone: true,
  imports: [CommonModule, MathFormulaComponent, TooltipDirective],
  templateUrl: './data-table.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DataTableComponent {
  /**
   * Modern Angular 19 Signal Input
   * 
   * Using input() signal instead of @Input() decorator:
   * - Automatic change detection integration
   * - Better type safety and inference
   * - Reactive programming patterns
   * - No need for complex setter/getter logic
   */
  readonly data = input<HealthMarker[]>([]);

  /**
   * Dependency Injection using inject() Function
   * 
   * Modern Angular pattern that:
   * - Enables better tree-shaking
   * - Works in functional contexts
   * - Improves testability  
   * - Cleaner than constructor injection
   */
  private readonly labMarkerService = inject(LabMarkerInfoService);

  /**
   * Computed Signal for Data Validation
   * 
   * Provides a computed property that automatically updates when data changes.
   * Used for debugging and ensuring data integrity.
   */
  readonly dataLength = computed(() => {
    const currentData = this.data();
    console.log('Data table received:', currentData);
    return currentData.length;
  });

  /**
   * Get Lab Marker Information
   * 
   * Pure function that retrieves marker metadata from the service.
   * Used for tooltips and additional context.
   * 
   * @param markerName - Name of the health marker
   * @returns Marker information or null if not found
   */
  getMarkerInfo(markerName: string): LabMarkerInfo | null {
    return this.labMarkerService.getMarkerInfo(markerName);
  }

  /**
   * Generate Tooltip Content
   * 
   * Creates rich HTML tooltip content with medical information.
   * Includes clinical significance, interpretations, and standard ranges.
   * 
   * @param markerName - Name of the health marker
   * @returns HTML string for tooltip display
   */
  getTooltipContent(markerName: string): string {
    const info = this.getMarkerInfo(markerName);
    if (!info) return '';

    const fallbackRange = this.labMarkerService.getFallbackReferenceRange(markerName);
    
    return `
      <div class="medical-tooltip">
        <h4>${info.name}</h4>
        <div class="description">${info.description}</div>
        
        <div class="clinical-info">
          <strong>Clinical Significance</strong>
          <p>${info.clinicalSignificance}</p>
        </div>
        
        ${info.lowMeaning ? `
          <div class="clinical-info">
            <strong>Low Levels</strong>
            <p>${info.lowMeaning}</p>
          </div>
        ` : ''}
        
        ${info.highMeaning ? `
          <div class="clinical-info">
            <strong>High Levels</strong>
            <p>${info.highMeaning}</p>
          </div>
        ` : ''}
        
        ${fallbackRange ? `
          <div class="range-info">
            <span class="range-icon"></span>Standard Range: ${fallbackRange}
            <span class="badge standard">STANDARD</span>
          </div>
        ` : ''}
      </div>
    `;
  }

  /**
   * Get Display Reference Range - Pure OCR Strategy
   * 
   * CRITICAL PRINCIPLE: Shows ONLY what was extracted by OCR.
   * Never contaminates display with fallback ranges to maintain data integrity.
   * This ensures users see exactly what the system detected from documents.
   * 
   * @param item - Health marker data
   * @returns OCR-extracted reference range or empty string
   */
  getDisplayReferenceRange(item: HealthMarker): string {
    // ONLY show what was actually extracted by OCR - NEVER fallback ranges in the table
    const ocrRange = item.reference_range || '';
    
    // Return exactly what OCR extracted, or empty if nothing was extracted
    return ocrRange || '';
  }

  /**
   * Get Comparison Reference Range - OCR Only for Highlighting
   * 
   * CRITICAL PRINCIPLE: Uses ONLY OCR ranges for out-of-range comparison.
   * Fallback ranges are never used for highlighting to prevent false positives.
   * 
   * @param item - Health marker data
   * @returns OCR reference range for comparison or null if unavailable
   */
  private getComparisonReferenceRange(item: HealthMarker): string | null {
    // ONLY use OCR ranges for out-of-range comparison
    // Use whatever OCR extracted, even if it seems incomplete
    const ocrRange = item.reference_range || '';
    
    // Only skip completely empty ranges
    if (!ocrRange || ocrRange.trim() === '') {
      return null;
    }
    
    return ocrRange.trim();
  }

  /**
   * Get Value Color Based on Status
   * 
   * Returns appropriate color for health marker values:
   * - Amber for low/watch values
   * - Red for high values  
   * - Green for normal values
   * 
   * @param item - Health marker data
   * @returns CSS color value
   */
  getValueColor(item: HealthMarker): string {
    const status = this.getValueStatus(item);
    switch (status) {
      case 'watch': return '#f59e0b'; // amber-500
      case 'high': return '#dc2626';  // red-600
      default: return '#16a34a';      // green-600
    }
  }

  /**
   * Get Value Font Weight Based on Status
   * 
   * Makes abnormal values bold for better visual emphasis.
   * 
   * @param item - Health marker data
   * @returns CSS font-weight value
   */
  getValueWeight(item: HealthMarker): string {
    const status = this.getValueStatus(item);
    return status !== 'normal' ? 'bold' : 'normal';
  }

  /**
   * Get Row Background Color Based on Status
   * 
   * Provides subtle background highlighting for abnormal values.
   * 
   * @param item - Health marker data
   * @returns CSS background-color value
   */
  getRowBackgroundColor(item: HealthMarker): string {
    const status = this.getValueStatus(item);
    switch (status) {
      case 'watch': return '#fef3c7'; // amber-100
      case 'high': return '#fee2e2';  // red-100
      default: return 'transparent';
    }
  }

  /**
   * Determine Value Status - Advanced Range Analysis
   * 
   * CRITICAL PRINCIPLE: Only uses OCR-extracted ranges for comparison.
   * Implements sophisticated range parsing for various formats:
   * - Standard ranges: "70.0 - 100.0"
   * - Upper bounds: "<100", "< 100"  
   * - Lower bounds: ">40", "> 40"
   * - Malformed ranges: "<6 - 6.0" (treated as upper bound)
   * 
   * @param item - Health marker data
   * @returns Status classification: 'normal' | 'watch' | 'high'
   */
  getValueStatus(item: HealthMarker): 'normal' | 'watch' | 'high' {
    // FIXED: Only use OCR ranges for out-of-range comparison
    const comparisonRange = this.getComparisonReferenceRange(item);
    
    // If no valid OCR range or no value, don't highlight
    if (!comparisonRange || !item.value) {
      return 'normal';
    }

    const value = parseFloat(item.value);
    if (isNaN(value)) {
      return 'normal';
    }

    console.log(`Checking value ${value} against OCR range "${comparisonRange}" for marker "${item.marker}"`);

    // Skip ranges that are incomplete or contain descriptive text
    if (comparisonRange.includes('...') || 
        comparisonRange.includes('depending') || 
        comparisonRange.includes('for males') || 
        comparisonRange.includes('for females')) {
      console.log('Result: Skipping complex/incomplete range');
      return 'normal';
    }

    // Case 1: Standard range like "70.0 - 100.0" or "75 - 200"
    let match = comparisonRange.match(/^(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$/);
    if (match) {
      const min = parseFloat(match[1]);
      const max = parseFloat(match[2]);
      console.log(`Standard range: ${min} - ${max}, value: ${value}`);
      if (value < min) {
        console.log('Result: Watch (low)');
        return 'watch';
      }
      if (value > max) {
        console.log('Result: High');
        return 'high';
      }
      console.log('Result: Normal');
      return 'normal';
    }

    // Case 2: Less than like "<100" or "< 100"
    match = comparisonRange.match(/^<\s*(\d+(?:\.\d+)?)$/);
    if (match) {
      const max = parseFloat(match[1]);
      console.log(`Upper bound only: < ${max}, value: ${value}`);
      if (value >= max) {
        console.log('Result: High');
        return 'high';
      }
      console.log('Result: Normal');
      return 'normal';
    }

    // Case 3: Greater than like ">40" or "> 40"
    match = comparisonRange.match(/^>\s*(\d+(?:\.\d+)?)$/);
    if (match) {
      const min = parseFloat(match[1]);
      console.log(`Lower bound only: > ${min}, value: ${value}`);
      if (value <= min) {
        console.log('Result: Watch (low)');
        return 'watch';
      }
      console.log('Result: Normal');
      return 'normal';
    }

    // Case 4: Complex ranges like "<6 - 6.0" (malformed, treat as upper bound)
    match = comparisonRange.match(/^<\s*(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$/);
    if (match) {
      const max = parseFloat(match[2]);
      console.log(`Malformed range treated as upper bound: < ${max}, value: ${value}`);
      if (value >= max) {
        console.log('Result: High');
        return 'high';
      }
      console.log('Result: Normal');
      return 'normal';
    }

    console.log('Result: No pattern matched, returning normal');
    return 'normal';
  }
}