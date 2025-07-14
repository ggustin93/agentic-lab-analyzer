import { Component, ChangeDetectionStrategy, computed, input, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HealthMarker } from '../../models/document.model';
import { MathFormulaComponent } from '../math-formula/math-formula.component';
import { LabMarkerInfoService } from '../../services/lab-marker-info.service';
import { LabMarkerInfo, ClinicalStatus } from '../../models/lab-marker.model';
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
    
    // Show only borderline, abnormal, and critical values
    return allData.filter(item => {
      const status = this.getValueStatus(item);
      return status === 'borderline' || status === 'abnormal' || status === 'critical';
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
      return status === 'borderline' || status === 'abnormal' || status === 'critical';
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
  getMarkerInfo(markerName: string): LabMarkerInfo | undefined {
    return this.labMarkerService.getMarkerInfo(markerName) || undefined;
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
      case 'critical': return '#991b1b';   // red-800
      case 'abnormal': return '#dc2626';   // red-600
      case 'borderline': return '#f59e0b'; // amber-500 (yellow)
      case 'unknown': return '#6b7280';    // gray-500
      default: return '#16a34a';           // green-600 (normal)
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
   * Determine Value Status - Delegated to Service
   * 
   * The component now delegates the complex clinical logic to the LabMarkerInfoService.
   * This keeps the component clean and focused on presentation.
   * 
   * @param item - Health marker data
   * @returns Status of the value
   */
  getValueStatus(item: HealthMarker): ClinicalStatus {
    return this.labMarkerService.getMarkerClinicalStatus(item);
  }
}