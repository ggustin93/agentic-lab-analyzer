import { Component, ChangeDetectionStrategy, computed, input } from '@angular/core';
import { marked } from 'marked';
import * as katex from 'katex';

/**
 * AI Insights Component - Clean Angular 19 Implementation
 * 
 * Renders AI-generated medical insights with LaTeX formula support
 * Key optimizations:
 * - Removed unnecessary dependencies and effects
 * - Single computed signal for reactive processing
 * - Clean separation of LaTeX and markdown processing
 * - OnPush strategy with automatic signal change detection
 * - Pure functions for better testability
 */
@Component({
  selector: 'app-ai-insights',
  standalone: true,
  templateUrl: './ai-insights.component.html',
  styleUrl: './ai-insights.component.scss',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AiInsightsComponent {
  /**
   * Medical insights input - automatically triggers recomputation
   * Signal provides reactive updates without manual change detection
   */
  readonly insights = input('');

  /**
   * Computed signal for processed insights
   * Automatically recalculates when insights() changes
   * Memoized for performance - only processes when input actually changes
   */
  readonly processedInsights = computed(() => 
    this.processMarkdownWithLatex(this.insights())
  );

  /**
   * Processes markdown text with embedded LaTeX formulas
   * Optimized workflow: protect LaTeX → process markdown → render LaTeX
   */
  private processMarkdownWithLatex(text: string): string {
    if (!text) return '';
    
    // Step 1: Extract and protect LaTeX expressions
    const { processedText, latexExpressions } = this.extractLatexExpressions(text);
    
    // Step 2: Process markdown on protected text
    const markdownProcessed = this.processMarkdown(processedText);
    
    // Step 3: Restore and render LaTeX expressions
    return this.renderLatexExpressions(markdownProcessed, latexExpressions);
  }

  /**
   * Extracts LaTeX expressions and replaces them with placeholders
   * Returns both the protected text and extracted expressions map
   */
  private extractLatexExpressions(text: string): {
    processedText: string;
    latexExpressions: Map<string, string>;
  } {
    const latexExpressions = new Map<string, string>();
    let counter = 0;

    // Define LaTeX patterns with their types
    const patterns = [
      { regex: /\$\$([\s\S]+?)\$\$/g, type: 'block' },
      { regex: /\$([^\n$]+?)\$/g, type: 'inline' },
      // Special medical unit patterns
      { regex: /\$10\^{\\wedge}3\\mathrm{mm}\^{3}\$/g, type: 'inline' },
      { regex: /\$\\mu\\mathrm{g}\/\\mathrm{dL}\$/g, type: 'inline' },
      { regex: /\$\\mu\\mathrm{g}\/\\mathrm{L}\$/g, type: 'inline' },
    ];

    let processedText = text;
    
    patterns.forEach(({ regex, type }) => {
      processedText = processedText.replace(regex, (match) => {
        const placeholder = `__LATEX_${type.toUpperCase()}_${counter++}__`;
        latexExpressions.set(placeholder, match);
        return placeholder;
      });
    });

    return { processedText, latexExpressions };
  }

  /**
   * Renders LaTeX expressions back into the processed text
   */
  private renderLatexExpressions(text: string, latexExpressions: Map<string, string>): string {
    let result = text;

    latexExpressions.forEach((latexMatch, placeholder) => {
      try {
        const { formula, isBlock } = this.parseLatexExpression(latexMatch);
        const rendered = katex.renderToString(formula, {
          displayMode: isBlock,
          throwOnError: false,
          strict: false,
        });
        result = result.replace(placeholder, rendered);
      } catch (error) {
        console.warn(`LaTeX rendering failed for: ${latexMatch}`, error);
        // Graceful fallback to original expression
        result = result.replace(placeholder, latexMatch);
      }
    });

    return result;
  }

  /**
   * Parses LaTeX expression to extract formula and determine display mode
   */
  private parseLatexExpression(latexMatch: string): { formula: string; isBlock: boolean } {
    const isBlock = latexMatch.startsWith('$$') && latexMatch.endsWith('$$');
    const formula = isBlock 
      ? latexMatch.slice(2, -2)  // Remove $$ delimiters
      : latexMatch.slice(1, -1); // Remove $ delimiters
    
    return { formula, isBlock };
  }

  /**
   * Processes markdown using marked library with fallback
   */
  private processMarkdown(text: string): string {
    try {
      return marked.parse(text, {
        gfm: true,        // GitHub Flavored Markdown
        breaks: true,     // Convert line breaks to <br>
      }) as string;
    } catch (error) {
      console.warn('Marked library failed, using fallback:', error);
      return this.simpleMarkdownFallback(text);
    }
  }

  /**
   * Simple markdown fallback for essential formatting
   * Handles headers, emphasis, and lists when marked library fails
   */
  private simpleMarkdownFallback(text: string): string {
    return text
      // Headers
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      // Emphasis
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      // Lists
      .replace(/^\* (.*)$/gim, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      // Paragraphs
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(.*)$/gim, '<p>$1</p>')
      // Cleanup
      .replace(/<p><\/p>/g, '')
      .replace(/<p>(<h[1-6]>)/g, '$1')
      .replace(/(<\/h[1-6]>)<\/p>/g, '$1')
      .replace(/<p>(<ul>)/g, '$1')
      .replace(/(<\/ul>)<\/p>/g, '$1');
  }
}