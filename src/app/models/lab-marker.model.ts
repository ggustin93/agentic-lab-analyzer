/**
 * 🧬 Lab Marker Models
 * Type definitions for clinical laboratory markers and analysis
 */

export interface LabMarkerInfo {
  name: string;
  description: string;
  clinicalSignificance: string;
  fallbackReferenceRange: string;
  unit: string;
  category: string;
  lowMeaning?: string;
  highMeaning?: string;
  alternativeNames?: string[];
  priority?: 'high' | 'medium' | 'low';
  criticalValues?: {
    criticalLow?: number;
    criticalHigh?: number;
  };
}

export interface MarkerCategory {
  name: string;
  description: string;
  priority: number;
  color: string;
}

export type ClinicalStatus = 'normal' | 'borderline' | 'abnormal' | 'critical' | 'unknown';

export interface RangeParseResult {
  success: boolean;
  min?: number;
  max?: number;
  type: 'range' | 'less_than' | 'greater_than' | 'single_value' | 'invalid';
  originalRange: string;
}

export interface StatusCalculationResult {
  status: ClinicalStatus;
  deviation?: number;
  deviationType?: 'below' | 'above';
  confidence: 'high' | 'medium' | 'low';
}

export interface MarkerAnalysisResult {
  marker: string;
  value: string;
  unit: string;
  referenceRange: string;
  status: ClinicalStatus;
  confidence: 'high' | 'medium' | 'low';
  deviation?: number;
  deviationType?: 'below' | 'above';
  markerInfo?: LabMarkerInfo;
}

export interface ConfigurationResult {
  success: boolean;
  error?: string;
}