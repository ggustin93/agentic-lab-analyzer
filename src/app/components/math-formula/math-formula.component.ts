import { 
  Component, 
  input, 
  viewChild, 
  effect, 
  ChangeDetectionStrategy, 
  ElementRef 
} from '@angular/core';
import * as katex from 'katex';

/**
 * Modern Angular 19 component for rendering KaTeX mathematical expressions
 * 
 * Key architectural decisions:
 * - Uses signals for optimal change detection and reactivity
 * - OnPush strategy reduces unnecessary render cycles
 * - Standalone component for better tree-shaking and modularity
 * - Graceful error handling preserves UX when LaTeX syntax is invalid
 */
@Component({
  selector: 'app-math-formula',
  standalone: true,
  template: `<span #container class="math-formula"></span>`,
  styles: [`
    :host {
      display: inline-block;
      line-height: 1;
    }
    
    /* Error state provides visual feedback for invalid expressions */
    .math-formula.error {
      color: #dc3545;
      font-family: monospace;
      padding: 0.125rem 0.25rem;
      background-color: #f8f9fa;
      border-radius: 0.25rem;
      border: 1px solid #dee2e6;
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MathFormulaComponent {
  /**
   * Mathematical expression to render using LaTeX syntax
   * Transform function ensures data consistency and handles edge cases
   */
  readonly expression = input('', {
    transform: (value: string | undefined | null) => value?.trim() || ''
  });

  /**
   * Signal-based ViewChild provides type safety and eliminates null checks
   * Required ensures the container always exists when accessed
   */
  private readonly container = viewChild.required<ElementRef<HTMLSpanElement>>('container');

  constructor() {
    /**
     * Effect automatically tracks expression signal changes
     * More efficient than ngOnChanges as it only monitors specific dependencies
     * Runs automatically when expression updates, providing reactive rendering
     */
    effect(() => this.renderExpression());
  }

  /**
   * Renders mathematical expression using KaTeX library
   * Implements defensive programming with fallback for rendering errors
   */
  private renderExpression(): void {
    const element = this.container().nativeElement;
    // Strip LaTeX delimiters ($) for compatibility with KaTeX render method
    const cleanExpression = this.expression().replace(/\$/g, '');
    
    // Reset previous error state for clean rendering
    element.classList.remove('error');
    
    // Handle empty expressions efficiently
    if (!cleanExpression) {
      element.textContent = '';
      return;
    }

    try {
      // KaTeX configuration optimized for inline mathematical expressions
      katex.render(cleanExpression, element, {
        throwOnError: false,  // Prevents crashes on invalid syntax
        displayMode: false,   // Inline mode for better text flow integration
        output: 'html',       // HTML output for better performance than MathML
        strict: false,        // Allow LaTeX extensions for broader compatibility
      });
    } catch (error) {
      /**
       * Graceful degradation strategy:
       * 1. Log error for debugging without breaking user experience
       * 2. Display original expression as plain text
       * 3. Apply error styling to indicate rendering failure
       */
      console.warn('KaTeX rendering failed:', error);
      element.textContent = cleanExpression;
      element.classList.add('error');
    }
  }
}