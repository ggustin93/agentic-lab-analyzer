import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MarkdownModule } from 'ngx-markdown';

@Component({
  selector: 'app-ai-insights',
  standalone: true,
  imports: [CommonModule, MarkdownModule],
  template: `
    <div class="bg-white shadow-sm rounded-lg overflow-hidden">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">AI-Generated Insights</h3>
      </div>
      
      <div class="px-6 py-4">
        <div class="markdown-content">
          <markdown [data]="insights"></markdown>
        </div>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AiInsightsComponent {
  @Input() insights: string = '';
}