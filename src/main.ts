import { Component } from '@angular/core';
import { bootstrapApplication } from '@angular/platform-browser';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideMarkdown } from 'ngx-markdown';
import { RouterOutlet } from '@angular/router';
import { DashboardComponent } from './app/pages/dashboard/dashboard.component';
import { AnalysisComponent } from './app/pages/analysis/analysis.component';

@Component({
  selector: 'app-root',
  standalone: true,  // ← AJOUTEZ CECI
  template: '<router-outlet></router-outlet>',
  imports: [RouterOutlet]
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
    provideMarkdown()
  ]
});