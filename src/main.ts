import 'zone.js';
import { Component } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { provideRouter, RouterOutlet } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideMarkdown } from 'ngx-markdown';

import { DashboardComponent } from './app/pages/dashboard/dashboard.component';
import { AnalysisComponent } from './app/pages/analysis/analysis.component';
import { ToastComponent } from './app/components/toast/toast.component';

@Component({
    selector: 'app-root',
    standalone: true,
    template: `
      <router-outlet></router-outlet>
      <app-toast></app-toast>
    `,
    imports: [RouterOutlet, ToastComponent]
})
export class App {}

const routes = [
    { path: '', component: DashboardComponent },
    { path: 'analysis/:id', component: AnalysisComponent },
    { path: '**', redirectTo: '' }
];

bootstrapApplication(App, {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    provideMarkdown(),
  ],
}).catch((err) => console.error(err));