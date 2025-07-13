# Tech Context: Lab Insight Engine

## 1. Frontend

- **Framework:** Angular 19.0.0 (avec TypeScript 5.8.2) **+ Bonnes pratiques modernes**
- **State Management:** **Migration RxJS → Signals pour une meilleure performance et réactivité**
- **Styling:** Tailwind CSS **avec custom stage-specific color classes et animations pour progress tracking**
- **Real-time Communication:** Server-Sent Events (SSE) via native `EventSource` API **enhanced avec progress percentage et processing stage updates pour 4-stage visual feedback (OCR → AI Analysis → Saving → Complete)**
- **Progress System:** **NEW: Comprehensive stage-based progress tracking avec color-coded visual indicators, animated spinners, et dynamic progress bars qui update en real-time**
- **Testing:** Jasmine et Karma pour unit tests.

### 🚀 **Angular 19 Best Practices - STANDARDS APPLIQUÉS**

#### **1. Modern Control Flow (Angular 17+)**
```typescript
// ✅ NOUVELLE SYNTAXE - Appliquée partout
@if (!isUploading && progress === undefined) {
  <div>Upload content...</div>
}
@for (document of documents; track document.id) {
  <div>{{ document.filename }}</div>
}

// ❌ ANCIENNE SYNTAXE - À supprimer
*ngIf="condition"
*ngFor="let item of items; trackBy: trackFn"
```

#### **2. Signals pour State Management**
```typescript
// ✅ APPROCHE MODERNE - Performance optimale
private documentsSignal = signal<HealthDocument[]>([]);
public readonly documents = this.documentsSignal.asReadonly();
private progressSignal = signal<number | undefined>(undefined);
public readonly progress = this.progressSignal.asReadonly();

// ❌ ANCIENNE APPROCHE - Remplacée
private documentsSubject = new BehaviorSubject<HealthDocument[]>([]);
public readonly documents$ = this.documentsSubject.asObservable();
```

#### **3. inject() Function Pattern**
```typescript
// ✅ MODERNE - Plus testable et concis
private http = inject(HttpClient);
private router = inject(Router);

// ❌ ANCIEN - Constructor injection
constructor(private http: HttpClient, private router: Router) {}
```

#### **4. OnPush Change Detection**
```typescript
// ✅ PERFORMANCE - Appliqué partout où possible
@Component({
  changeDetection: ChangeDetectionStrategy.OnPush
})
```

#### **5. Standalone Components + Modern Bootstrap**
```typescript
// ✅ DÉJÀ APPLIQUÉ - Excellent !
@Component({
  standalone: true,
  imports: [CommonModule]
})

// main.ts - ✅ Bootstrap moderne déjà en place
bootstrapApplication(App, {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    provideMarkdown(),
  ],
});
```

#### **6. Enhanced TypeScript Configuration**
- **strict mode enabled** pour type safety maximale
- **exactOptionalPropertyTypes** pour precision des interfaces
- **noUncheckedIndexedAccess** pour array safety

#### **7. Modern Reactive Patterns**
```typescript
// ✅ Computed signals pour derived state
public readonly processingDocuments = computed(() => 
  this.documents().filter(doc => doc.status === DocumentStatus.PROCESSING)
);

// ✅ Effect pour side effects
constructor() {
  effect(() => {
    const docs = this.documents();
    console.log(`Documents updated: ${docs.length} total`);
  });
}
```

### **Migration Strategy - COMPLÈTEMENT APPLIQUÉE**
1. **✅ Phase 1:** Control Flow migration (*ngIf → @if, *ngFor → @for)
2. **✅ Phase 2:** Services migration (BehaviorSubject → signals)
3. **✅ Phase 3:** Components migration (inject() function)
4. **✅ Phase 4:** OnPush optimization partout où approprié
5. **✅ Phase 5:** Computed signals pour derived state

### **Composants Modernisés Angular 19**
- **✅ DocumentAnalysisService:** BehaviorSubject → signals, computed signals, effects
- **✅ DocumentListComponent:** Control flow (@if/@for), OnPush, track expressions
- **✅ UploadZoneComponent:** Control flow, OnPush, stage-specific conditionals
- **✅ DashboardComponent:** inject(), signals, computed(), effects, OnPush
- **⏳ Prochains:** ai-insights, data-table, analysis components

## 2. Backend

- **Framework:** FastAPI (Python)
- **Data Persistence:** Supabase (PostgreSQL)
- **AI/OCR Services:**
    - Mistral for OCR and data extraction.
    - Chute AI for generating insights (or another similar LLM).
- **Configuration:** Pydantic
- **Real-time Updates:** **Enhanced SSE implementation with progress tracking and stage information included in document processing responses**
- **Testing:** pytest

## 3. Development Environment

- **Containerization:** Docker & Docker Compose
- **Version Control:** Git & GitHub
- **CI/CD:** GitHub Actions
- **Development Scripts:** Organized in `scripts/` directory with utilities for:
  - Development environment startup (`dev-start.sh`)
  - Dependency management (`fix-dependencies.sh`, `check-deps.js`)
  - Docker resource management (`docker-cleanup.sh`, `docker-monitor.sh`)
  - Project validation and testing (`validate-setup.sh`, `test-docker.sh`)

## 4. Technical Constraints

- **File Size Limit:** The system is designed to handle file uploads up to 10MB.
- **File Types:** The system accepts `.pdf`, `.png`, and `.jpg` files.
- **Single-Tenant:** The MVP is designed for a single user/tenant.
- **Security:** API keys and database connection strings MUST be managed via environment variables and not be committed to source control.
- **Progress Updates:** **NEW: Real-time progress updates occur every 2 seconds during document processing with stage-specific visual feedback**

## 5. Tooling

- **Supabase MCP:** We have access to the Supabase MCP tools, allowing for direct programmatic interaction with Supabase services.
- **Progress Monitoring:** **NEW: Comprehensive logging system for tracking progress updates and debugging SSE communication throughout the processing pipeline** 