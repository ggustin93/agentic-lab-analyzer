import { Component, ChangeDetectionStrategy, computed, input, inject, signal } from '@angular/core';
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
 * - Clinical filtering for out-of-range values
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
   * Filter State - Writable Signal
   * 
   * Controls whether to show all data or only out-of-range values.
   * Uses Angular 19 signal() for reactive state management.
   */
  readonly showOnlyOutOfRange = signal(false);

  /**
   * Filtered Data - Computed Signal
   * 
   * Automatically filters data based on the toggle state and clinical status.
   * Recomputes whenever data or filter state changes.
   */
  readonly filteredData = computed(() => {
    const allData = this.data();
    const filterActive = this.showOnlyOutOfRange();
    
    if (!filterActive) {
      return allData;
    }
    
    // Show only borderline and abnormal values
    return allData.filter(item => {
      const status = this.getValueStatus(item);
      return status === 'borderline' || status === 'abnormal';
    });
  });

  /**
   * Filter Statistics - Computed Signal
   * 
   * Provides statistics about normal vs out-of-range values.
   * Useful for displaying counts and percentages.
   */
  readonly filterStats = computed(() => {
    const allData = this.data();
    const totalCount = allData.length;
    
    if (totalCount === 0) {
      return { total: 0, outOfRange: 0, normal: 0, percentage: 0 };
    }
    
    const outOfRangeCount = allData.filter(item => {
      const status = this.getValueStatus(item);
      return status === 'borderline' || status === 'abnormal';
    }).length;
    
    const normalCount = totalCount - outOfRangeCount;
    const percentage = Math.round((outOfRangeCount / totalCount) * 100);
    
    return {
      total: totalCount,
      outOfRange: outOfRangeCount,
      normal: normalCount,
      percentage
    };
  });

  /**
   * Toggle Filter State
   * 
   * Switches between showing all data and only out-of-range values.
   * Uses signal.set() for reactive updates.
   */
  toggleFilter(): void {
    this.showOnlyOutOfRange.set(!this.showOnlyOutOfRange());
  }

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
   * Clean LaTeX Formatting from Text
   * 
   * Removes LaTeX delimiters and formatting that may interfere with display.
   * Common in OCR results from scientific documents.
   * 
   * @param text - Text that may contain LaTeX formatting
   * @returns Cleaned text without LaTeX delimiters
   */
  private cleanLatexFormatting(text: string): string {
    if (!text) return '';
    
    return text
      .replace(/\$/g, '')           // Remove LaTeX delimiters
      .replace(/\\[a-zA-Z]+/g, '')  // Remove LaTeX commands
      .replace(/[{}]/g, '')         // Remove LaTeX braces
      .trim();
  }

  /**
   * Get Display Reference Range - Pure OCR Strategy with LaTeX Cleanup
   * 
   * CRITICAL PRINCIPLE: Shows ONLY what was extracted by OCR.
   * Never contaminates display with fallback ranges to maintain data integrity.
   * This ensures users see exactly what the system detected from documents.
   * 
   * @param item - Health marker data
   * @returns OCR-extracted reference range cleaned of LaTeX formatting
   */
  getDisplayReferenceRange(item: HealthMarker): string {
    // ONLY show what was actually extracted by OCR - NEVER fallback ranges in the table
    const ocrRange = item.reference_range || '';
    
    // Clean LaTeX formatting for proper display
    return this.cleanLatexFormatting(ocrRange);
  }

  /**
   * Get Comparison Reference Range - OCR Only for Highlighting with LaTeX Cleanup
   * 
   * CRITICAL PRINCIPLE: Uses ONLY OCR ranges for out-of-range comparison.
   * Fallback ranges are never used for highlighting to prevent false positives.
   * 
   * @param item - Health marker data
   * @returns OCR reference range cleaned for comparison or null if unavailable
   */
  private getComparisonReferenceRange(item: HealthMarker): string | null {
    // ONLY use OCR ranges for out-of-range comparison
    const ocrRange = item.reference_range || '';
    
    // Only skip completely empty ranges
    if (!ocrRange || ocrRange.trim() === '') {
      return null;
    }
    
    // Clean LaTeX formatting before parsing
    const cleanedRange = this.cleanLatexFormatting(ocrRange);
    
    // Skip if cleaning resulted in empty string
    if (!cleanedRange || cleanedRange.trim() === '') {
      return null;
    }
    
    return cleanedRange.trim();
  }

  /**
   * Get Value Color Based on Status
   * 
   * Returns appropriate color for health marker values:
   * - Green for normal values (within range)
   * - Yellow for borderline values (within ±25% of range)
   * - Red for significantly abnormal values (>25% outside range)
   * 
   * @param item - Health marker data
   * @returns CSS color value
   */
  getValueColor(item: HealthMarker): string {
    const status = this.getValueStatus(item);
    switch (status) {
      case 'borderline': return '#f59e0b'; // amber-500 (yellow)
      case 'abnormal': return '#dc2626';   // red-600
      default: return '#16a34a';           // green-600
    }
  }

  /**
   * Get Value Font Weight Based on Status
   * 
   * Makes significantly abnormal values bold, borderline values medium weight.
   * 
   * @param item - Health marker data
   * @returns CSS font-weight value
   */
  getValueWeight(item: HealthMarker): string {
    const status = this.getValueStatus(item);
    switch (status) {
      case 'abnormal': return 'bold';
      case 'borderline': return '500';     // medium weight
      default: return 'normal';
    }
  }

  /**
   * Get Row Background Color Based on Status
   * 
   * Provides subtle background highlighting with 3-tier system.
   * 
   * @param item - Health marker data
   * @returns CSS background-color value
   */
  getRowBackgroundColor(item: HealthMarker): string {
    const status = this.getValueStatus(item);
    switch (status) {
      case 'borderline': return '#fef3c7'; // amber-100 (light yellow)
      case 'abnormal': return '#fee2e2';   // red-100
      default: return 'transparent';
    }
  }

  /**
   * Determine Value Status - Clinical 3-Tier System
   * 
   * CLINICAL PRINCIPLE: Implements medically appropriate thresholds:
   * - 'normal': Within reference range
   * - 'borderline': Within ±25% of range boundaries (often not clinically significant)
   * - 'abnormal': >25% outside range (clinically significant)
   * 
   * This approach recognizes that many lab values have "gray zones" where
   * slight deviations aren't concerning (especially for markers like eosinophils,
   * basophils, LUC where low values are often normal).
   * 
   * @param item - Health marker data
   * @returns Status: 'normal' | 'borderline' | 'abnormal'
   */
  getValueStatus(item: HealthMarker): 'normal' | 'borderline' | 'abnormal' {
    // Only use OCR ranges for out-of-range comparison
    const comparisonRange = this.getComparisonReferenceRange(item);
    
    // If no valid OCR range or no value, don't highlight
    if (!comparisonRange || !item.value) {
      return 'normal';
    }

    const value = parseFloat(item.value);
    if (isNaN(value)) {
      return 'normal';
    }

    console.log(`🔍 Clinical assessment: ${value} vs "${comparisonRange}" for ${item.marker}`);

    // Skip ranges with descriptive text or incomplete data
    if (comparisonRange.includes('...') || 
        comparisonRange.includes('depending') || 
        comparisonRange.includes('for males') || 
        comparisonRange.includes('for females') ||
        comparisonRange.includes('varies') ||
        comparisonRange.length < 2) {
      console.log('⏭️ Skipping complex/incomplete range');
      return 'normal';
    }

    // Case 1: Standard ranges with clinical thresholds
    // Handles: "70.0 - 100.0", "75-200", "3.50-5.10", "136 - 145"
    let match = comparisonRange.match(/^(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)$/);
    if (match) {
      const min = parseFloat(match[1]);
      const max = parseFloat(match[2]);
      const rangeSize = max - min;
      const tolerance = rangeSize * 0.25; // 25% tolerance
      
      console.log(`📊 Range: ${min}-${max}, tolerance: ±${tolerance.toFixed(2)}`);
      
      if (value >= min && value <= max) {
        console.log('🟢 NORMAL (within range)');
        return 'normal';
      }
      
      // Check if within 25% tolerance zone
      if (value < min) {
        const deviation = min - value;
        if (deviation <= tolerance) {
          console.log(`🟡 BORDERLINE LOW (${deviation.toFixed(2)} below, within 25% tolerance)`);
          return 'borderline';
        } else {
          console.log(`🔴 ABNORMAL LOW (${deviation.toFixed(2)} below, >25% tolerance)`);
          return 'abnormal';
        }
      }
      
      if (value > max) {
        const deviation = value - max;
        if (deviation <= tolerance) {
          console.log(`🟡 BORDERLINE HIGH (${deviation.toFixed(2)} above, within 25% tolerance)`);
          return 'borderline';
        } else {
          console.log(`🔴 ABNORMAL HIGH (${deviation.toFixed(2)} above, >25% tolerance)`);
          return 'abnormal';
        }
      }
    }

    // Case 2: Upper bounds with clinical thresholds
    // Handles: "<100", "< 100", "≤100", "<2.0"
    match = comparisonRange.match(/^[<≤]\s*(\d+(?:\.\d+)?)$/);
    if (match) {
      const max = parseFloat(match[1]);
      const tolerance = max * 0.25; // 25% of the upper bound
      
      console.log(`📊 Upper bound: <${max}, tolerance: ${tolerance.toFixed(2)}`);
      
      if (value < max) {
        console.log('🟢 NORMAL (below upper bound)');
        return 'normal';
      }
      
      const excess = value - max;
      if (excess <= tolerance) {
        console.log(`🟡 BORDERLINE HIGH (${excess.toFixed(2)} above bound, within 25%)`);
        return 'borderline';
      } else {
        console.log(`🔴 ABNORMAL HIGH (${excess.toFixed(2)} above bound, >25%)`);
        return 'abnormal';
      }
    }

    // Case 2b: Malformed OCR upper bounds - Handle patterns like "<6 - 6.0", "<2 - 2.0", "<0 - 0.50"
    // These should be interpreted as simple upper bounds: "<6", "<2", "<0.50"
    match = comparisonRange.match(/^<(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$/);
    if (match) {
      const firstNum = parseFloat(match[1]);
      const secondNum = parseFloat(match[2]);
      
      // Use the higher number as the actual upper bound (more clinically sensible)
      const actualMax = Math.max(firstNum, secondNum);
      const tolerance = actualMax * 0.25;
      
      console.log(`🔧 MALFORMED OCR: "${comparisonRange}" → Treating as <${actualMax}`);
      console.log(`📊 Corrected upper bound: <${actualMax}, tolerance: ${tolerance.toFixed(2)}`);
      
      if (value < actualMax) {
        console.log('🟢 NORMAL (below corrected upper bound)');
        return 'normal';
      }
      
      const excess = value - actualMax;
      if (excess <= tolerance) {
        console.log(`🟡 BORDERLINE HIGH (${excess.toFixed(2)} above bound, within 25%)`);
        return 'borderline';
      } else {
        console.log(`🔴 ABNORMAL HIGH (${excess.toFixed(2)} above bound, >25%)`);
        return 'abnormal';
      }
    }

    // Case 3: Lower bounds with clinical thresholds
    // Handles: ">40", "> 40", "≥40"
    match = comparisonRange.match(/^[>≥]\s*(\d+(?:\.\d+)?)$/);
    if (match) {
      const min = parseFloat(match[1]);
      const tolerance = min * 0.25; // 25% of the lower bound
      
      console.log(`📊 Lower bound: >${min}, tolerance: ${tolerance.toFixed(2)}`);
      
      if (value > min) {
        console.log('🟢 NORMAL (above lower bound)');
        return 'normal';
      }
      
      const deficit = min - value;
      if (deficit <= tolerance) {
        console.log(`🟡 BORDERLINE LOW (${deficit.toFixed(2)} below bound, within 25%)`);
        return 'borderline';
      } else {
        console.log(`🔴 ABNORMAL LOW (${deficit.toFixed(2)} below bound, >25%)`);
        return 'abnormal';
      }
    }

    // Case 4: Ranges with multiple bounds (treat as standard range)
    // Handles: "Normal: 65-100", "Ref: 3.5-5.0"
    match = comparisonRange.match(/(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)/);
    if (match) {
      const min = parseFloat(match[1]);
      const max = parseFloat(match[2]);
      const rangeSize = max - min;
      const tolerance = rangeSize * 0.25;
      
      console.log(`📊 Extracted range: ${min}-${max}, tolerance: ±${tolerance.toFixed(2)}`);
      
      if (value >= min && value <= max) {
        console.log('🟢 NORMAL (within range)');
        return 'normal';
      }
      
      if (value < min) {
        const deviation = min - value;
        return deviation <= tolerance ? 'borderline' : 'abnormal';
      }
      
      if (value > max) {
        const deviation = value - max;
        return deviation <= tolerance ? 'borderline' : 'abnormal';
      }
    }

    console.log('⚪ No pattern matched, returning NORMAL');
    return 'normal';
  }
}