// src/app/components/math-formula/math-formula.component.ts

import { 
  Component, 
  input, 
  viewChild, 
  effect, 
  ChangeDetectionStrategy, 
  ElementRef 
} from '@angular/core';
import * as katex from 'katex';

@Component({
  selector: 'app-math-formula',
  standalone: true,
  template: `<span #container class="math-formula"></span>`,
  styles: [`
    :host { display: inline-block; line-height: 1; }
    .math-formula.error { color: #dc2626; font-family: monospace; }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MathFormulaComponent {
  readonly expression = input('', {
    transform: (value: string | undefined | null) => value?.trim() || ''
  });

  private readonly container = viewChild.required<ElementRef<HTMLSpanElement>>('container');

  constructor() {
    effect(() => this.renderExpression());
  }

  private renderExpression(): void {
    const element = this.container().nativeElement;
    const rawExpression = this.expression();
    element.classList.remove('error');

    if (!rawExpression) {
      element.innerHTML = '';
      return;
    }

    // NEW: Intelligent normalization logic
    const { normalized, requiresLatex } = this.normalizeLatexString(rawExpression);

    if (requiresLatex) {
      try {
        katex.render(normalized, element, {
          throwOnError: false,
          displayMode: false,
          strict: false,
        });
      } catch (error) {
        console.warn('KaTeX rendering failed, falling back to plain text:', { rawExpression, error });
        element.textContent = rawExpression;
        element.classList.add('error');
      }
    } else {
      // If no LaTeX is needed, just render as plain text.
      element.textContent = normalized;
    }
  }

  /**
   * Normalizes an input string to be safely rendered by KaTeX.
   * - Ensures proper LaTeX delimiters ($...$).
   * - Decides if LaTeX rendering is even necessary.
   */
  private normalizeLatexString(expr: string): { normalized: string; requiresLatex: boolean } {
    if (!expr) {
      return { normalized: '', requiresLatex: false };
    }
    
    // Remove "mathrm" commands from AI, as they are often unnecessary and can cause issues.
    let cleanedExpr = expr.replace(/\\mathrm/g, '').replace(/[{}]/g, '');

    // Check if the expression contains characters that require LaTeX rendering.
    const latexChars = ['\\', '^', '_'];
    const needsLatex = latexChars.some(char => cleanedExpr.includes(char));

    if (!needsLatex) {
      // It's likely plain text, return as is.
      return { normalized: cleanedExpr, requiresLatex: false };
    }

    // It needs LaTeX, so ensure it is properly delimited.
    // Strip any existing dollars to prevent double-wrapping, then wrap it cleanly.
    cleanedExpr = cleanedExpr.replace(/\$/g, '');
    
    return {
      normalized: cleanedExpr, // Give KaTeX the pure expression without delimiters
      requiresLatex: true
    };
  }
}