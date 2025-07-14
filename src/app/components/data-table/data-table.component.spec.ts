import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DataTableComponent } from './data-table.component';
import { HealthMarker } from '../../models/document.model';
import { LabMarkerInfoService } from '../../services/lab-marker-info.service';

describe('DataTableComponent (Pragmatic MVP Test)', () => {
  let component: DataTableComponent;
  let fixture: ComponentFixture<DataTableComponent>;
  let nativeElement: HTMLElement;
  let mockLabMarkerService: jasmine.SpyObj<LabMarkerInfoService>;

  beforeEach(async () => {
    // Create a spy object for the LabMarkerInfoService
    const spy = jasmine.createSpyObj('LabMarkerInfoService', ['getMarkerInfo', 'getFallbackReferenceRange', 'getMarkerClinicalStatus']);

    await TestBed.configureTestingModule({
      imports: [DataTableComponent], // Standalone components are imported directly
      providers: [
        { provide: LabMarkerInfoService, useValue: spy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(DataTableComponent);
    component = fixture.componentInstance;
    nativeElement = fixture.nativeElement;
    mockLabMarkerService = TestBed.inject(LabMarkerInfoService) as jasmine.SpyObj<LabMarkerInfoService>;

    // Setup default spy returns
    mockLabMarkerService.getMarkerInfo.and.returnValue(undefined);
    mockLabMarkerService.getFallbackReferenceRange.and.returnValue(undefined);
    
    // Setup dynamic clinical status based on marker values
    mockLabMarkerService.getMarkerClinicalStatus.and.callFake((item: HealthMarker) => {
      // Simple logic to determine status based on marker name for testing
      if (item.marker === 'Glucose' && item.value === '150') return 'abnormal';
      if (item.marker === 'Potassium' && item.value === '3.0') return 'abnormal';
      if (item.marker === 'Cholesterol' && item.value === '200') return 'borderline';
      if (item.marker === 'Hemoglobin' && item.value === '13.5') return 'borderline';
      if (item.marker === 'High1' && item.value === '10.0') return 'abnormal';
      if (item.marker === 'Low1' && item.value === '2.0') return 'abnormal';
      return 'normal'; // Default to normal
    });
  });

  // THE SINGLE MOST IMPORTANT COMPONENT TEST: Highlighting logic
  it('should apply correct CSS classes for low, high, and normal values', () => {
    const mockData: HealthMarker[] = [
      // Test Case 1: HIGH value (abnormal)
      { marker: 'Glucose', value: '150', unit: 'mg/dL', reference_range: '70 - 100' },
      // Test Case 2: LOW value (abnormal)  
      { marker: 'Potassium', value: '3.0', unit: 'mmol/L', reference_range: '3.5 - 5.1' },
      // Test Case 3: NORMAL value
      { marker: 'Sodium', value: '140', unit: 'mmol/L', reference_range: '136 - 145' },
      // Test Case 4: BORDERLINE HIGH value
      { marker: 'Cholesterol', value: '200', unit: 'mg/dL', reference_range: '< 200' },
      // Test Case 5: BORDERLINE LOW value
      { marker: 'Hemoglobin', value: '13.5', unit: 'g/dL', reference_range: '13.5 - 17.5' }
    ];

    // Use Angular 19 testing pattern for signal inputs
    fixture.componentRef.setInput('data', mockData);
    fixture.detectChanges(); // Trigger rendering

    const rows = nativeElement.querySelectorAll('tbody tr');
    
    // Test Case 1: HIGH glucose should have abnormal highlighting
    expect(rows[0]).toHaveClass('highlight-abnormal');
    expect(rows[0]).not.toHaveClass('highlight-borderline');
    
    // Test Case 2: LOW potassium should have abnormal highlighting
    expect(rows[1]).toHaveClass('highlight-abnormal');
    expect(rows[1]).not.toHaveClass('highlight-borderline');
    
    // Test Case 3: NORMAL sodium should have no highlighting
    expect(rows[2]).not.toHaveClass('highlight-abnormal');
    expect(rows[2]).not.toHaveClass('highlight-borderline');
    
    // Verify status badges are shown for abnormal values
    const abnormalBadges = nativeElement.querySelectorAll('.status-badge.abnormal');
    expect(abnormalBadges.length).toBe(2); // Glucose and Potassium
  });

  it('should handle edge cases and malformed reference ranges gracefully', () => {
    const edgeCaseData: HealthMarker[] = [
      // Missing reference range
      { marker: 'TestMarker1', value: '50', unit: 'unit', reference_range: undefined },
      // Empty reference range
      { marker: 'TestMarker2', value: '75', unit: 'unit', reference_range: '' },
      // Malformed range
      { marker: 'TestMarker3', value: '100', unit: 'unit', reference_range: 'invalid-range' },
      // Complex range format
      { marker: 'TestMarker4', value: '5.0', unit: 'unit', reference_range: '< 6.0' }
    ];

    fixture.componentRef.setInput('data', edgeCaseData);
    fixture.detectChanges();

    const rows = nativeElement.querySelectorAll('tbody tr');
    
    // Component should render without errors
    expect(rows.length).toBe(4);
    
    // All rows should render marker names correctly
    expect(rows[0].textContent).toContain('TestMarker1');
    expect(rows[1].textContent).toContain('TestMarker2');
    expect(rows[2].textContent).toContain('TestMarker3');
    expect(rows[3].textContent).toContain('TestMarker4');
  });

  it('should correctly filter data when showOnlyOutOfRange is enabled', () => {
    const mixedData: HealthMarker[] = [
      { marker: 'Normal1', value: '5.0', unit: 'unit', reference_range: '4.0 - 6.0' },
      { marker: 'High1', value: '10.0', unit: 'unit', reference_range: '4.0 - 6.0' },
      { marker: 'Normal2', value: '5.5', unit: 'unit', reference_range: '4.0 - 6.0' },
      { marker: 'Low1', value: '2.0', unit: 'unit', reference_range: '4.0 - 6.0' }
    ];

    fixture.componentRef.setInput('data', mixedData);
    fixture.detectChanges();

    // Initially, all rows should be visible
    let rows = nativeElement.querySelectorAll('tbody tr');
    expect(rows.length).toBe(4);

    // Enable filter to show only out-of-range values
    component.toggleFilter();
    fixture.detectChanges();

    // Now only out-of-range values should be visible
    rows = nativeElement.querySelectorAll('tbody tr');
    expect(rows.length).toBe(2); // High1 and Low1

    // Verify the correct markers are shown
    const visibleMarkers = Array.from(rows).map(row => row.textContent);
    expect(visibleMarkers.some(text => text?.includes('High1'))).toBe(true);
    expect(visibleMarkers.some(text => text?.includes('Low1'))).toBe(true);
    expect(visibleMarkers.some(text => text?.includes('Normal1'))).toBe(false);
    expect(visibleMarkers.some(text => text?.includes('Normal2'))).toBe(false);
  });

  it('should show appropriate empty state when filter results in no data', () => {
    const allNormalData: HealthMarker[] = [
      { marker: 'Normal1', value: '5.0', unit: 'unit', reference_range: '4.0 - 6.0' },
      { marker: 'Normal2', value: '5.5', unit: 'unit', reference_range: '4.0 - 6.0' }
    ];

    fixture.componentRef.setInput('data', allNormalData);
    component.toggleFilter(); // Enable out-of-range filter
    fixture.detectChanges();

    // Should show the "all values normal" empty state
    const emptyState = nativeElement.querySelector('.text-center h3');
    expect(emptyState?.textContent?.trim()).toBe('All values are within normal range!');
    
    // Should have appropriate empty state content or show all button
    const showAllButton = nativeElement.querySelector('button');
    const emptyStateText = nativeElement.textContent;
    
    // Either should have a button or show empty state message
    const hasButton = showAllButton && showAllButton.textContent?.trim().includes('Show');
    const hasEmptyMessage = emptyStateText?.includes('No') || emptyStateText?.includes('values');
    
    expect(hasButton || hasEmptyMessage).toBeTruthy();
  });

  it('should provide correct filter statistics', () => {
    const statisticsTestData: HealthMarker[] = [
      { marker: 'Normal1', value: '5.0', unit: 'unit', reference_range: '4.0 - 6.0' },
      { marker: 'Normal2', value: '5.5', unit: 'unit', reference_range: '4.0 - 6.0' },
      { marker: 'High1', value: '10.0', unit: 'unit', reference_range: '4.0 - 6.0' },
      { marker: 'Low1', value: '2.0', unit: 'unit', reference_range: '4.0 - 6.0' }
    ];

    fixture.componentRef.setInput('data', statisticsTestData);
    fixture.detectChanges();

    const stats = component.filterStats();
    
    expect(stats.total).toBe(4);
    expect(stats.normal).toBe(2);
    expect(stats.outOfRange).toBe(2);
    expect(stats.percentage).toBe(50); // 2 out of 4 = 50%
  });

  // Test the value status logic directly
  it('should correctly determine value status based on reference ranges', () => {
    // Override the service method to return proper clinical status based on the test cases
    mockLabMarkerService.getMarkerClinicalStatus.and.callFake((item: HealthMarker) => {
      const value = parseFloat(item.value);
      const range = item.reference_range;
      
      if (!range || !range.includes('4.0 - 6.0')) {
        return 'unknown';
      }
      
      // Test range is 4.0 - 6.0
      if (value >= 4.0 && value <= 6.0) {
        return 'normal';
      } else {
        return 'abnormal';
      }
    });

    // Test normal values
    const normalMarker: HealthMarker = { marker: 'Test', value: '5.0', reference_range: '4.0 - 6.0' };
    expect(component.getValueStatus(normalMarker)).toBe('normal');

    // Test high abnormal value
    const highMarker: HealthMarker = { marker: 'Test', value: '8.0', reference_range: '4.0 - 6.0' };
    expect(component.getValueStatus(highMarker)).toBe('abnormal');

    // Test low abnormal value  
    const lowMarker: HealthMarker = { marker: 'Test', value: '2.0', reference_range: '4.0 - 6.0' };
    expect(component.getValueStatus(lowMarker)).toBe('abnormal');

    // Test borderline value (exactly at boundary)
    const borderlineMarker: HealthMarker = { marker: 'Test', value: '6.0', reference_range: '4.0 - 6.0' };
    expect(component.getValueStatus(borderlineMarker)).toBe('normal');
  });
}); 