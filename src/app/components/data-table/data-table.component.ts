import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HealthMarker } from '../../models/document.model';
import { MathFormulaComponent } from '../math-formula/math-formula.component';
import { LabMarkerInfoService, LabMarkerInfo } from '../../services/lab-marker-info.service';
import { TooltipDirective } from '../../directives/tooltip.directive';

@Component({
  selector: 'app-data-table',
  standalone: true,
  imports: [CommonModule, MathFormulaComponent, TooltipDirective],
  template: `
    <div class="bg-white shadow-sm rounded-lg overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">Extracted Data</h3>
      </div>
      
      <div class="overflow-x-auto">
        <table class="data-table">
          <thead>
            <tr>
              <th>Marker</th>
              <th>Value</th>
              <th>Unit</th>
              <th>Reference Range</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let item of data" 
                [class.highlight-low]="getValueStatus(item) === 'watch'"
                [class.highlight-high]="getValueStatus(item) === 'high'"
                [style.background-color]="getRowBackgroundColor(item)">
              <td class="relative">
                <div class="flex items-center space-x-2">
                  <span>{{ item.marker }}</span>
                  <svg *ngIf="getMarkerInfo(item.marker)" 
                       class="w-4 h-4 text-blue-500 cursor-help" 
                       fill="currentColor" 
                       viewBox="0 0 20 20"
                       [appTooltip]="getTooltipContent(item.marker)"
                       theme="medical"
                       placement="top"
                       [maxWidth]="350">
                    <path fill-rule="evenodd" 
                          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" 
                          clip-rule="evenodd" />
                  </svg>
                </div>
              </td>
              <td [style.color]="getValueColor(item)" 
                  [style.font-weight]="getValueWeight(item)">
                <div class="flex items-center space-x-2">
                  <span>{{ item.value }}</span>
                  <span *ngIf="getValueStatus(item) === 'watch'" 
                        class="status-badge low">
                    LOW
                  </span>
                  <span *ngIf="getValueStatus(item) === 'high'" 
                        class="status-badge high">
                    HIGH
                  </span>
                </div>
              </td>
              <td>
                <app-math-formula [expression]="item.unit"></app-math-formula>
              </td>
              <td>
                <div class="flex items-center space-x-2">
                  <span>{{ getDisplayReferenceRange(item) }}</span>
                  <span *ngIf="isUsingFallbackRange(item)" 
                        class="status-badge standard"
                        title="Using medical standard range (OCR extraction failed for this marker)">
                    STANDARD
                  </span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DataTableComponent {
  @Input() set data(value: HealthMarker[]) {
    this._data = value || [];
    console.log('Data table received:', this._data);
  }

  get data(): HealthMarker[] {
    return this._data;
  }

  private _data: HealthMarker[] = [];

  constructor(private labMarkerService: LabMarkerInfoService) {}

  getMarkerInfo(markerName: string): LabMarkerInfo | null {
    return this.labMarkerService.getMarkerInfo(markerName);
  }

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

  getDisplayReferenceRange(item: HealthMarker): string {
    // FIXED: Prioritize OCR ranges for display, only use fallback if truly not recognized
    const ocrRange = item.reference_range || '';
    
    // If we have a valid OCR range, always use it for display
    if (ocrRange && !this.labMarkerService.isReferenceRangeIncomplete(ocrRange)) {
      return ocrRange;
    }
    
    // Only if OCR truly failed, then show fallback range
    const fallback = this.labMarkerService.getFallbackReferenceRange(item.marker || '');
    if (fallback) {
      return fallback;
    }
    
    // Last resort: show whatever OCR gave us or N/A
    return ocrRange || 'N/A';
  }

  isUsingFallbackRange(item: HealthMarker): boolean {
    const ocrRange = item.reference_range || '';
    return this.labMarkerService.isReferenceRangeIncomplete(ocrRange) &&
           !!this.labMarkerService.getFallbackReferenceRange(item.marker || '');
  }

  // NEW: Get the range to use for value comparison (OCR only!)
  private getComparisonReferenceRange(item: HealthMarker): string | null {
    // FIXED: Only use OCR ranges for out-of-range comparison
    // Never use fallback ranges for highlighting - only what OCR actually extracted
    const ocrRange = item.reference_range || '';
    
    // If OCR range is missing or clearly invalid, don't highlight anything
    if (!ocrRange || this.labMarkerService.isReferenceRangeIncomplete(ocrRange)) {
      return null;
    }
    
    return ocrRange;
  }

  getValueColor(item: HealthMarker): string {
    const status = this.getValueStatus(item);
    switch (status) {
      case 'watch': return '#f59e0b'; // amber-500
      case 'high': return '#dc2626';  // red-600
      default: return '#16a34a';      // green-600
    }
  }

  getValueWeight(item: HealthMarker): string {
    const status = this.getValueStatus(item);
    return status !== 'normal' ? 'bold' : 'normal';
  }

  getRowBackgroundColor(item: HealthMarker): string {
    const status = this.getValueStatus(item);
    switch (status) {
      case 'watch': return '#fef3c7'; // amber-100
      case 'high': return '#fee2e2';  // red-100
      default: return 'transparent';
    }
  }

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