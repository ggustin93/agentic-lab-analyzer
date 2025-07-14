import { Injectable, signal, computed } from '@angular/core';

/**
 * Toast Notification Service
 * 
 * Simple toast notification system using Angular 19 signals.
 * Provides success, error, warning, and info toast notifications.
 * 
 * Features:
 * - Signal-based reactive state management
 * - Auto-dismiss functionality
 * - Multiple toast types with different styles
 * - Queue management for multiple toasts
 * - Accessible toast notifications
 */

export interface Toast {
  id: string;
  message: string;
  type: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  dismissible?: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ToastService {
  
  private readonly _toasts = signal<Toast[]>([]);
  private toastCounter = 0;
  
  /**
   * Active toasts signal
   */
  readonly toasts = computed(() => this._toasts());
  
  /**
   * Show a success toast
   */
  success(message: string, duration: number = 4000): void {
    this.addToast({
      id: this.generateId(),
      message,
      type: 'success',
      duration,
      dismissible: true
    });
  }
  
  /**
   * Show an error toast
   */
  error(message: string, duration: number = 6000): void {
    this.addToast({
      id: this.generateId(),
      message,
      type: 'error',
      duration,
      dismissible: true
    });
  }
  
  /**
   * Show a warning toast
   */
  warning(message: string, duration: number = 5000): void {
    this.addToast({
      id: this.generateId(),
      message,
      type: 'warning',
      duration,
      dismissible: true
    });
  }
  
  /**
   * Show an info toast
   */
  info(message: string, duration: number = 4000): void {
    this.addToast({
      id: this.generateId(),
      message,
      type: 'info',
      duration,
      dismissible: true
    });
  }
  
  /**
   * Dismiss a specific toast
   */
  dismiss(toastId: string): void {
    this._toasts.update(toasts => toasts.filter(t => t.id !== toastId));
  }
  
  /**
   * Clear all toasts
   */
  clear(): void {
    this._toasts.set([]);
  }
  
  /**
   * Add a toast to the queue
   */
  private addToast(toast: Toast): void {
    this._toasts.update(toasts => [...toasts, toast]);
    
    // Auto-dismiss if duration is set
    if (toast.duration && toast.duration > 0) {
      setTimeout(() => this.dismiss(toast.id), toast.duration);
    }
  }
  
  /**
   * Generate unique toast ID
   */
  private generateId(): string {
    return `toast-${++this.toastCounter}-${Date.now()}`;
  }
}