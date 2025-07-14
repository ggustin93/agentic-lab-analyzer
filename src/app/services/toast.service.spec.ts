import { TestBed } from '@angular/core/testing';
import { ToastService } from './toast.service';

describe('ToastService', () => {
  let service: ToastService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ToastService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should add success toast', () => {
    service.success('Test message');
    
    const toasts = service.toasts();
    expect(toasts.length).toBe(1);
    expect(toasts[0].message).toBe('Test message');
    expect(toasts[0].type).toBe('success');
    expect(toasts[0].dismissible).toBe(true);
  });

  it('should add error toast', () => {
    service.error('Error message');
    
    const toasts = service.toasts();
    expect(toasts.length).toBe(1);
    expect(toasts[0].message).toBe('Error message');
    expect(toasts[0].type).toBe('error');
  });

  it('should add warning toast', () => {
    service.warning('Warning message');
    
    const toasts = service.toasts();
    expect(toasts.length).toBe(1);
    expect(toasts[0].message).toBe('Warning message');
    expect(toasts[0].type).toBe('warning');
  });

  it('should add info toast', () => {
    service.info('Info message');
    
    const toasts = service.toasts();
    expect(toasts.length).toBe(1);
    expect(toasts[0].message).toBe('Info message');
    expect(toasts[0].type).toBe('info');
  });

  it('should dismiss toast by id', () => {
    service.success('Test message');
    const toasts = service.toasts();
    const toastId = toasts[0].id;
    
    service.dismiss(toastId);
    
    expect(service.toasts().length).toBe(0);
  });

  it('should clear all toasts', () => {
    service.success('Test message 1');
    service.error('Test message 2');
    service.warning('Test message 3');
    
    expect(service.toasts().length).toBe(3);
    
    service.clear();
    
    expect(service.toasts().length).toBe(0);
  });

  it('should handle multiple toasts', () => {
    service.success('Success message');
    service.error('Error message');
    service.warning('Warning message');
    
    const toasts = service.toasts();
    expect(toasts.length).toBe(3);
    
    // Check that each toast has unique ID
    const ids = toasts.map(t => t.id);
    const uniqueIds = [...new Set(ids)];
    expect(uniqueIds.length).toBe(3);
  });

  it('should auto-dismiss toasts after duration', (done) => {
    service.success('Test message', 100); // 100ms duration
    
    expect(service.toasts().length).toBe(1);
    
    setTimeout(() => {
      expect(service.toasts().length).toBe(0);
      done();
    }, 150);
  });

  it('should not auto-dismiss if duration is 0', (done) => {
    service.success('Test message', 0); // No auto-dismiss
    
    expect(service.toasts().length).toBe(1);
    
    setTimeout(() => {
      expect(service.toasts().length).toBe(1);
      done();
    }, 100);
  });
});