import { Component, Input, ChangeDetectionStrategy, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MarkdownModule } from 'ngx-markdown';
import * as katex from 'katex';
import { marked } from 'marked';

@Component({
  selector: 'app-ai-insights',
  standalone: true,
  imports: [CommonModule, MarkdownModule],
  template: `
    <div class="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200 bg-blue-50">
        <div class="flex items-center space-x-3">
          <div class="p-2 bg-blue-100 rounded-lg">
            <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900">Medical Analysis Report</h3>
        </div>
      </div>
      
      <div class="px-6 py-6">
        <div class="medical-report" [innerHTML]="processedInsights"></div>
      </div>
    </div>
  `,
  styles: [`
    :host ::ng-deep .katex-display {
      margin: 1.5em 0;
      overflow-x: auto;
      overflow-y: hidden;
      text-align: center;
    }
    :host ::ng-deep .katex {
      font-size: 1.1em;
    }
    
    /* Enhanced Medical Report Styling */
    :host ::ng-deep .medical-report h1 {
      color: #1e40af;
      font-size: 1.75rem;
      font-weight: 700;
      margin: 2rem 0 1.5rem 0;
      padding-bottom: 0.75rem;
      border-bottom: 2px solid #e0e7ff;
      display: flex;
      align-items: center;
      position: relative;
    }
    
    :host ::ng-deep .medical-report h1:before {
      content: "";
      display: inline-block;
      width: 20px;
      height: 20px;
      margin-right: 0.75rem;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23059669'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z'/%3E%3C/svg%3E");
      background-size: contain;
      background-repeat: no-repeat;
      flex-shrink: 0;
    }
    
    :host ::ng-deep .medical-report h2 {
      color: #1e40af;
      font-size: 1.5rem;
      font-weight: 600;
      margin: 2rem 0 1rem 0;
      display: flex;
      align-items: center;
      position: relative;
    }
    
    :host ::ng-deep .medical-report h2:before {
      content: "";
      display: inline-block;
      width: 18px;
      height: 18px;
      margin-right: 0.75rem;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%232563eb'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z'/%3E%3C/svg%3E");
      background-size: contain;
      background-repeat: no-repeat;
      flex-shrink: 0;
    }
    
    :host ::ng-deep .medical-report h3 {
      color: #3730a3;
      font-size: 1.25rem;
      font-weight: 600;
      margin: 1.5rem 0 0.75rem 0;
      display: flex;
      align-items: center;
      position: relative;
    }
    
    :host ::ng-deep .medical-report h3:before {
      content: "";
      display: inline-block;
      width: 16px;
      height: 16px;
      margin-right: 0.75rem;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236366f1'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z'/%3E%3C/svg%3E");
      background-size: contain;
      background-repeat: no-repeat;
      flex-shrink: 0;
    }
    
    :host ::ng-deep .medical-report p {
      color: #374151;
      line-height: 1.7;
      margin: 1rem 0;
      font-size: 0.95rem;
    }
    
    :host ::ng-deep .medical-report ul {
      margin: 1.5rem 0;
      padding-left: 0;
      list-style: none;
      space-y: 0.75rem;
    }
    
    :host ::ng-deep .medical-report li {
      background: #fafafa;
      margin: 0.75rem 0;
      padding: 1rem 1.25rem;
      border-radius: 0.5rem;
      position: relative;
      box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.06);
      transition: all 0.2s ease;
      line-height: 1.6;
      font-size: 0.95rem;
      color: #374151;
      border: 1px solid #f3f4f6;
    }
    
    :host ::ng-deep .medical-report li:hover {
      background: #f5f5f5;
      box-shadow: 0 2px 6px 0 rgba(0, 0, 0, 0.08);
      transform: translateY(-1px);
    }
    
    :host ::ng-deep .medical-report li:before {
      content: "•";
      position: absolute;
      left: 0.75rem;
      top: 1rem;
      color: #6b7280;
      font-weight: 600;
      font-size: 1rem;
    }
    
    :host ::ng-deep .medical-report strong {
      color: #1f2937;
      font-weight: 600;
    }
    
    :host ::ng-deep .medical-report em {
      color: #6366f1;
      font-style: italic;
    }
    
    /* Medical value highlighting - subtle background variations */
    :host ::ng-deep .medical-report li:contains("Normal") {
      background: #f0fdf4;
      border-color: #dcfce7;
    }
    
    :host ::ng-deep .medical-report li:contains("elevated") {
      background: #fef2f2;
      border-color: #fecaca;
    }
    
    :host ::ng-deep .medical-report li:contains("slightly elevated") {
      background: #fffbeb;
      border-color: #fed7aa;
    }
    
    /* Disclaimer styling */
    :host ::ng-deep .medical-report .disclaimer,
    :host ::ng-deep .medical-report p:last-child {
      background: #fef3c7;
      border: 1px solid #f59e0b;
      border-radius: 0.5rem;
      padding: 1rem 1rem 1rem 3rem;
      margin-top: 2rem;
      font-size: 0.875rem;
      color: #92400e;
      position: relative;
      line-height: 1.5;
    }
    
    :host ::ng-deep .medical-report .disclaimer:before,
    :host ::ng-deep .medical-report p:last-child:before {
      content: "";
      position: absolute;
      left: 1rem;
      top: 1rem;
      width: 18px;
      height: 18px;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%23d97706'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z'/%3E%3C/svg%3E");
      background-size: contain;
      background-repeat: no-repeat;
    }
    
    /* Responsive adjustments */
    @media (max-width: 640px) {
      :host ::ng-deep .medical-report h1 {
        font-size: 1.5rem;
      }
      
      :host ::ng-deep .medical-report h2 {
        font-size: 1.25rem;
      }
      
      :host ::ng-deep .medical-report h3 {
        font-size: 1.1rem;
      }
      
      :host ::ng-deep .medical-report li {
        padding: 0.75rem 1rem 0.75rem 1.25rem;
      }
    }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AiInsightsComponent implements OnChanges {
  @Input() insights: string = '';
  processedInsights: string = '';

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['insights']) {
      this.processedInsights = this.processMarkdownWithLatex(this.insights || '');
    }
  }

  processMarkdownWithLatex(text: string): string {
    if (!text) return '';
    
    // First, protect LaTeX blocks from markdown processing
    const placeholders: { [key: string]: string } = {};
    let counter = 0;
    
    // Process block LaTeX formulas ($$formula$$)
    text = text.replace(/\$\$([\s\S]+?)\$\$/g, (match, formula) => {
      const placeholder = `__LATEX_BLOCK_${counter++}__`;
      placeholders[placeholder] = match;
      return placeholder;
    });
    
    // Process special LaTeX formulas with \mathrm{mm}^{3} pattern
    text = text.replace(/\$10\^{\\wedge}3\\mathrm{mm}\^{3}\$/g, (match) => {
      const placeholder = `__LATEX_SPECIAL_${counter++}__`;
      placeholders[placeholder] = match;
      return placeholder;
    });
    
    // Process special LaTeX formulas with \mu\mathrm{g} pattern
    text = text.replace(/\$\\mu\\mathrm{g}\/\\mathrm{dL}\$/g, (match) => {
      const placeholder = `__LATEX_SPECIAL_${counter++}__`;
      placeholders[placeholder] = match;
      return placeholder;
    });
    
    // Process special LaTeX formulas with \mu\mathrm{g} pattern
    text = text.replace(/\$\\mu\\mathrm{g}\/\\mathrm{L}\$/g, (match) => {
      const placeholder = `__LATEX_SPECIAL_${counter++}__`;
      placeholders[placeholder] = match;
      return placeholder;
    });
    
    // Process inline LaTeX formulas ($formula$)
    text = text.replace(/\$([^\n$]+?)\$/g, (match, formula) => {
      const placeholder = `__LATEX_INLINE_${counter++}__`;
      placeholders[placeholder] = match;
      return placeholder;
    });
    
    // Process markdown (you can use a library like marked here)
    // For now, we'll just do some basic processing
    text = this.processMarkdown(text);

    // Restore LaTeX formulas and render them
    for (const placeholder in placeholders) {
      const latexMatch = placeholders[placeholder];
      
      if (latexMatch.startsWith('$$') && latexMatch.endsWith('$$')) {
        // Block formula
        const formula = latexMatch.slice(2, -2);
        try {
          const rendered = katex.renderToString(formula, { displayMode: true });
          text = text.replace(placeholder, rendered);
        } catch (e) {
          console.warn('Failed to render LaTeX block:', formula, e);
          text = text.replace(placeholder, latexMatch);
        }
      } else if (latexMatch.startsWith('$') && latexMatch.endsWith('$')) {
        // Inline formula
        const formula = latexMatch.slice(1, -1);
        try {
          const rendered = katex.renderToString(formula, { displayMode: false });
          text = text.replace(placeholder, rendered);
        } catch (e) {
          console.warn('Failed to render LaTeX inline:', formula, e);
          text = text.replace(placeholder, latexMatch);
        }
      }
    }
    
    return text;
  }

  private processMarkdown(text: string): string {
    try {
      // Use marked library for better markdown processing
      const result = marked.parse(text, {
        gfm: true,
        breaks: true
      });
      return typeof result === 'string' ? result : String(result);
    } catch (e) {
      console.warn('Marked library failed, falling back to simple processing:', e);
      return this.simpleMarkdownFallback(text);
    }
  }

  private simpleMarkdownFallback(text: string): string {
    return text
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/^\* (.*)$/gim, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(.*)$/gim, '<p>$1</p>')
      .replace(/<p><\/p>/g, '')
      .replace(/<p>(<h[1-6]>)/g, '$1')
      .replace(/(<\/h[1-6]>)<\/p>/g, '$1')
      .replace(/<p>(<ul>)/g, '$1')
      .replace(/(<\/ul>)<\/p>/g, '$1');
  }
}