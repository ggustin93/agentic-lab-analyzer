import { Directive, ElementRef, Input, OnDestroy, OnInit } from '@angular/core';
import tippy, { Instance, Props } from 'tippy.js';

@Directive({
  selector: '[appTooltip]',
  standalone: true
})
export class TooltipDirective implements OnInit, OnDestroy {
  @Input('appTooltip') content: string = '';
  @Input() theme: 'light' | 'dark' | 'medical' = 'medical';
  @Input() placement: Props['placement'] = 'top';
  @Input() maxWidth: number = 300;
  @Input() allowHTML: boolean = true;

  private tippyInstance: Instance<Props> | null = null;

  constructor(private elementRef: ElementRef) {}

  ngOnInit() {
    this.initTooltip();
  }

  ngOnDestroy() {
    if (this.tippyInstance) {
      this.tippyInstance.destroy();
    }
  }

  private initTooltip() {
    if (!this.content) return;

    const instances = tippy(this.elementRef.nativeElement, {
      content: this.content,
      theme: this.theme,
      placement: this.placement,
      maxWidth: this.maxWidth,
      allowHTML: this.allowHTML,
      interactive: true,
      delay: [500, 200], // Show after 500ms, hide after 200ms
      duration: [200, 150], // Animation durations
      arrow: true,
      offset: [0, 8],
      zIndex: 10000,
      appendTo: () => document.body, // Prevent clipping
      // Professional medical styling
      onShow: (instance: Instance<Props>) => {
        if (this.theme === 'medical') {
          const tippyBox = instance.popper.querySelector('.tippy-box');
          if (tippyBox) {
            tippyBox.classList.add('medical-tooltip');
          }
        }
      }
    });

    // tippy returns an array, get the first instance
    this.tippyInstance = Array.isArray(instances) ? instances[0] : instances;
  }

  // Method to update content dynamically
  updateContent(newContent: string) {
    this.content = newContent;
    if (this.tippyInstance) {
      this.tippyInstance.setContent(newContent);
    }
  }
} 