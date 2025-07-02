import { Component, Input, ChangeDetectionStrategy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HealthMarker } from '../../models/document.model';

@Component({
  selector: 'app-data-table',
  standalone: true,
  imports: [CommonModule],
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
            <tr *ngFor="let item of data">
              <td class="font-medium">{{ item.marker }}</td>
              <td>{{ item.value }}</td>
              <td>{{ item.unit || '-' }}</td>
              <td>{{ item.reference_range || '-' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class DataTableComponent {
  @Input() data: HealthMarker[] = [];
}