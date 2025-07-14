import { Injectable } from '@angular/core';
import { RangeParseResult } from '../models/lab-marker.model';

/**
 * 📊 Reference Range Parser Service
 * Specialized service for parsing and validating clinical reference ranges
 */
@Injectable({
  providedIn: 'root'
})
export class ReferenceRangeParserService {
  
  private readonly NORMALIZATION_PATTERNS = [
    { pattern: /\s+/g, replacement: ' ' },
    { pattern: /[^\w\s\-.,;:()]/g, replacement: '' },
    { pattern: /^(le|la|les|du|de|des)\s+/i, replacement: '' }
  ] as const;

  /**
   * Parse a reference range string into structured data
   */
  parseReferenceRange(range: string): RangeParseResult {
    const cleanRange = this.cleanReferenceRange(range);
    
    // Range pattern (e.g., "13.0 - 18.0")
    let match = cleanRange.match(/^(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)$/);
    if (match) {
      return {
        success: true,
        min: parseFloat(match[1]),
        max: parseFloat(match[2]),
        type: 'range',
        originalRange: range
      };
    }

    // Less than pattern (e.g., "< 100")
    match = cleanRange.match(/^[<≤]\s*(\d+(?:\.\d+)?)$/);
    if (match) {
      return {
        success: true,
        max: parseFloat(match[1]),
        type: 'less_than',
        originalRange: range
      };
    }

    // Greater than pattern (e.g., "> 40")
    match = cleanRange.match(/^[>≥]\s*(\d+(?:\.\d+)?)$/);
    if (match) {
      return {
        success: true,
        min: parseFloat(match[1]),
        type: 'greater_than',
        originalRange: range
      };
    }

    // Single value pattern (e.g., "100")
    match = cleanRange.match(/^(\d+(?:\.\d+)?)$/);
    if (match) {
      return {
        success: true,
        min: parseFloat(match[1]),
        max: parseFloat(match[1]),
        type: 'single_value',
        originalRange: range
      };
    }

    return {
      success: false,
      type: 'invalid',
      originalRange: range
    };
  }

  /**
   * Validate if a reference range is properly formatted
   */
  isReferenceRangeValid(range: string): boolean {
    if (!range || range.trim() === '') {
      return false;
    }
    
    const parseResult = this.parseReferenceRange(range);
    return parseResult.success && parseResult.type !== 'invalid';
  }

  /**
   * Clean reference range string by removing LaTeX and special characters
   */
  private cleanReferenceRange(range: string): string {
    return range
      .replace(/\$/g, '')
      .replace(/\\[a-zA-Z]+/g, '')
      .replace(/[{}]/g, '')
      .trim();
  }

  /**
   * Normalize marker name for consistent matching
   */
  normalizeMarkerName(name: string): string {
    if (!name) return '';
    
    let normalized = name.toLowerCase().trim();
    
    // Apply normalization patterns
    for (const { pattern, replacement } of this.NORMALIZATION_PATTERNS) {
      normalized = normalized.replace(pattern, replacement);
    }
    
    return normalized.trim();
  }
}