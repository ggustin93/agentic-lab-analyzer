import { Injectable, signal, computed, inject } from '@angular/core';
import { HealthMarker } from '../models/document.model';
import { 
  LabMarkerInfo, 
  MarkerCategory, 
  ClinicalStatus, 
  StatusCalculationResult, 
  RangeParseResult, 
  MarkerAnalysisResult,
  ConfigurationResult
} from '../models/lab-marker.model';
import { LAB_MARKER_CATEGORIES, LAB_MARKERS_DATABASE } from '../data/lab-markers.data';
import { ReferenceRangeParserService } from './reference-range-parser.service';

/**
 * 🧬 Lab Marker Information Service
 * Refactored service for managing clinical laboratory markers with enhanced 
 * separation of concerns and improved maintainability.
 */
@Injectable({
  providedIn: 'root'
})
export class LabMarkerInfoService {
  
  private readonly rangeParser = inject(ReferenceRangeParserService);
  
  // Signal-based reactive state for dynamic marker management
  private markersSignal = signal<Record<string, LabMarkerInfo>>(LAB_MARKERS_DATABASE);
  private categoriesSignal = signal<Record<string, MarkerCategory>>(LAB_MARKER_CATEGORIES);
  
  // Computed signals for reactive access
  public readonly markers = this.markersSignal.asReadonly();
  public readonly categories = this.categoriesSignal.asReadonly();
  public readonly markerNames = computed(() => Object.keys(this.markers()));
  public readonly categoryNames = computed(() => 
    Object.values(this.categories()).sort((a, b) => a.priority - b.priority).map(c => c.name)
  );

  // Configuration for clinical status determination
  private readonly CONFIG = {
    TOLERANCE_PERCENTAGE: 0.25,
    CRITICAL_DEVIATION_THRESHOLD: 2.0,
  } as const;

  /**
   * Enhanced marker retrieval with fuzzy matching and normalization
   */
  public getMarkerInfo(markerName: string): LabMarkerInfo | undefined {
    if (!markerName) return undefined;

    const normalizedName = this.rangeParser.normalizeMarkerName(markerName);
    const markers = this.markers();
    
    // Direct match
    if (markers[normalizedName]) {
      return markers[normalizedName];
    }

    // Fuzzy matching using alternative names
    for (const [, marker] of Object.entries(markers)) {
      if (marker.alternativeNames?.some(alt => 
        this.rangeParser.normalizeMarkerName(alt) === normalizedName
      )) {
        return marker;
      }
    }

    // Partial matching as fallback
    for (const [key, marker] of Object.entries(markers)) {
      if (key.includes(normalizedName) || normalizedName.includes(key)) {
        return marker;
      }
    }

    return undefined;
  }

  /**
   * Enhanced clinical status determination with confidence scoring
   */
  public getMarkerClinicalStatus(item: HealthMarker): ClinicalStatus {
    try {
      const result = this.calculateClinicalStatus(item);
      return result.status;
    } catch (error) {
      console.warn(`Error determining clinical status for ${item.marker}:`, error);
      return 'unknown';
    }
  }

  /**
   * Get detailed status calculation with confidence and deviation information
   */
  public getDetailedClinicalStatus(item: HealthMarker): StatusCalculationResult {
    return this.calculateClinicalStatus(item);
  }

  /**
   * Enhanced reference range validation using the parser service
   */
  public isReferenceRangeValid(range: string): boolean {
    return this.rangeParser.isReferenceRangeValid(range);
  }

  /**
   * Add or update a marker dynamically
   */
  public addOrUpdateMarker(key: string, marker: LabMarkerInfo): void {
    this.markersSignal.update(markers => ({
      ...markers,
      [this.rangeParser.normalizeMarkerName(key)]: marker
    }));
  }

  /**
   * Remove a marker
   */
  public removeMarker(key: string): boolean {
    const normalizedKey = this.rangeParser.normalizeMarkerName(key);
    const markers = this.markers();
    
    if (markers[normalizedKey]) {
      this.markersSignal.update(current => {
        const updated = { ...current };
        delete updated[normalizedKey];
        return updated;
      });
      return true;
    }
    return false;
  }

  /**
   * Get markers by category with enhanced filtering
   */
  public getMarkersByCategory(category: string): LabMarkerInfo[] {
    return Object.values(this.markers()).filter(marker => 
      marker.category === category
    ).sort((a, b) => {
      const priorityOrder = { 'high': 0, 'medium': 1, 'low': 2 };
      return (priorityOrder[a.priority || 'medium'] || 1) - (priorityOrder[b.priority || 'medium'] || 1);
    });
  }

  /**
   * Get comprehensive marker analysis result
   */
  public getMarkerAnalysis(item: HealthMarker): MarkerAnalysisResult {
    const markerInfo = this.getMarkerInfo(item.marker);
    const statusResult = this.getDetailedClinicalStatus(item);
    
    return {
      marker: item.marker,
      value: item.value,
      unit: item.unit || markerInfo?.unit || '',
      referenceRange: item.reference_range || markerInfo?.fallbackReferenceRange || '',
      status: statusResult.status,
      confidence: statusResult.confidence,
      deviation: statusResult.deviation,
      deviationType: statusResult.deviationType,
      markerInfo: markerInfo || undefined
    };
  }

  /**
   * Export current markers configuration
   */
  public exportConfiguration(): string {
    return JSON.stringify({
      markers: this.markers(),
      categories: this.categories(),
      timestamp: new Date().toISOString(),
      version: '1.0'
    }, null, 2);
  }

  /**
   * Import markers configuration with validation
   */
  public importConfiguration(configJson: string): ConfigurationResult {
    try {
      const config = JSON.parse(configJson);
      
      if (!config.markers || typeof config.markers !== 'object') {
        return { success: false, error: 'Invalid markers configuration' };
      }

      // Validate each marker
      for (const [key, marker] of Object.entries(config.markers)) {
        if (!this.validateMarkerStructure(marker as LabMarkerInfo)) {
          return { success: false, error: `Invalid marker structure for ${key}` };
        }
      }

      this.markersSignal.set(config.markers);
      
      if (config.categories) {
        this.categoriesSignal.set(config.categories);
      }

      return { success: true };
    } catch (error) {
      return { success: false, error: `Parse error: ${error}` };
    }
  }

  // Private helper methods

  private calculateClinicalStatus(item: HealthMarker): StatusCalculationResult {
    const comparisonRange = this.getComparisonReferenceRange(item);
    
    if (!comparisonRange || !item.value) {
      return { status: 'unknown', confidence: 'low' };
    }

    const value = parseFloat(item.value);
    if (isNaN(value)) {
      return { status: 'unknown', confidence: 'low' };
    }

    const parseResult = this.rangeParser.parseReferenceRange(comparisonRange);
    if (!parseResult.success) {
      return { status: 'unknown', confidence: 'low' };
    }

    // Check for critical values
    const markerInfo = this.getMarkerInfo(item.marker);
    if (markerInfo?.criticalValues) {
      const { criticalLow, criticalHigh } = markerInfo.criticalValues;
      if ((criticalLow && value <= criticalLow) || (criticalHigh && value >= criticalHigh)) {
        return { 
          status: 'critical', 
          confidence: 'high',
          deviation: this.calculateDeviation(value, parseResult),
          deviationType: criticalLow && value <= criticalLow ? 'below' : 'above'
        };
      }
    }

    return this.determineStatusFromRange(value, parseResult);
  }

  private determineStatusFromRange(value: number, parseResult: RangeParseResult): StatusCalculationResult {
    const tolerance = this.CONFIG.TOLERANCE_PERCENTAGE;

    switch (parseResult.type) {
      case 'range':
        if (parseResult.min !== undefined && parseResult.max !== undefined) {
          const rangeSize = parseResult.max - parseResult.min;
          const toleranceValue = rangeSize * tolerance;

          if (value >= parseResult.min && value <= parseResult.max) {
            return { status: 'normal', confidence: 'high' };
          }
          
          if (value < parseResult.min) {
            const deviation = parseResult.min - value;
            return {
              status: deviation <= toleranceValue ? 'borderline' : 'abnormal',
              confidence: 'high',
              deviation,
              deviationType: 'below'
            };
          }
          
          if (value > parseResult.max) {
            const deviation = value - parseResult.max;
            return {
              status: deviation <= toleranceValue ? 'borderline' : 'abnormal',
              confidence: 'high',
              deviation,
              deviationType: 'above'
            };
          }
        }
        break;

      case 'less_than':
        if (parseResult.max !== undefined) {
          const toleranceValue = parseResult.max * tolerance;
          if (value < parseResult.max) {
            return { status: 'normal', confidence: 'high' };
          }
          const deviation = value - parseResult.max;
          return {
            status: deviation <= toleranceValue ? 'borderline' : 'abnormal',
            confidence: 'high',
            deviation,
            deviationType: 'above'
          };
        }
        break;

      case 'greater_than':
        if (parseResult.min !== undefined) {
          const toleranceValue = parseResult.min * tolerance;
          if (value > parseResult.min) {
            return { status: 'normal', confidence: 'high' };
          }
          const deviation = parseResult.min - value;
          return {
            status: deviation <= toleranceValue ? 'borderline' : 'abnormal',
            confidence: 'high',
            deviation,
            deviationType: 'below'
          };
        }
        break;
    }

    return { status: 'unknown', confidence: 'low' };
  }

  private calculateDeviation(value: number, parseResult: RangeParseResult): number {
    switch (parseResult.type) {
      case 'range':
        if (parseResult.min !== undefined && parseResult.max !== undefined) {
          if (value < parseResult.min) return parseResult.min - value;
          if (value > parseResult.max) return value - parseResult.max;
        }
        break;
      case 'less_than':
        if (parseResult.max !== undefined && value > parseResult.max) {
          return value - parseResult.max;
        }
        break;
      case 'greater_than':
        if (parseResult.min !== undefined && value < parseResult.min) {
          return parseResult.min - value;
        }
        break;
    }
    return 0;
  }

  private getComparisonReferenceRange(item: HealthMarker): string | undefined {
    const ocrRange = item.reference_range || '';
    if (!ocrRange || ocrRange.trim() === '') {
      return undefined;
    }
    const cleanedRange = this.cleanReferenceRange(ocrRange);
    if (!cleanedRange || cleanedRange.trim() === '') {
      return undefined;
    }
    return cleanedRange.trim();
  }

  private cleanReferenceRange(range: string): string {
    return range
      .replace(/\$/g, '')
      .replace(/\\[a-zA-Z]+/g, '')
      .replace(/[{}]/g, '')
      .trim();
  }

  private validateMarkerStructure(marker: unknown): boolean {
    if (!marker || typeof marker !== 'object' || marker === null) {
      return false;
    }
    
    const m = marker as LabMarkerInfo;
    return (
      typeof m.name === 'string' &&
      typeof m.description === 'string' &&
      typeof m.clinicalSignificance === 'string' &&
      typeof m.fallbackReferenceRange === 'string' &&
      typeof m.unit === 'string' &&
      typeof m.category === 'string'
    );
  }

  // Legacy methods for backward compatibility
  public getAllMarkers(): Record<string, LabMarkerInfo> {
    return this.markers();
  }

  public getCategories(): string[] {
    return this.categoryNames();
  }

  public getFallbackReferenceRange(markerName: string): string | undefined {
    const info = this.getMarkerInfo(markerName);
    return info ? info.fallbackReferenceRange : undefined;
  }

  public isReferenceRangeIncomplete(range: string): boolean {
    return !this.isReferenceRangeValid(range);
  }
}