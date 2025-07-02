import { Component, Input, OnChanges, SimpleChanges, ElementRef, ViewChild, ChangeDetectionStrategy } from '@angular/core';
import * as katex from 'katex';

@Component({
  selector: 'app-math-formula',
  standalone: true,
  imports: [],
  template: `<span #container></span>`,
  styles: [
    `
      :host {
        display: inline-block;
      }
    `,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MathFormulaComponent implements OnChanges {
  @Input() expression: string | undefined | null = '';
  @ViewChild('container', { static: true }) container!: ElementRef;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['expression']) {
      this.render();
    }
  }

  private render(): void {
    const expressionToRender = this.expression?.replace(/\$/g, '') || '';
    if (this.container) {
      try {
        katex.render(expressionToRender, this.container.nativeElement, {
          throwOnError: false,
          displayMode: false,
        });
      } catch (e) {
        console.error('Error rendering KaTeX expression:', e);
        this.container.nativeElement.textContent = this.expression;
      }
    }
  }
} 