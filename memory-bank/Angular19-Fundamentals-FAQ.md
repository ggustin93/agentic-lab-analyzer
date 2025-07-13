# Angular 19 Fundamentals & Best Practices FAQ

*Last Updated: July 12, 2025*

A comprehensive guide to Angular 19 fundamentals, state management strategies, and modern software practices for building production-ready applications.

## 📚 Table of Contents

- [Angular 19 Fundamentals \& Best Practices FAQ](#angular-19-fundamentals--best-practices-faq)
  - [📚 Table of Contents](#-table-of-contents)
  - [1. 🎓 Programming Fundamentals (OOP Concepts)](#1--programming-fundamentals-oop-concepts)
    - [1.1 Q: What are the basic OOP concepts in TypeScript?](#11-q-what-are-the-basic-oop-concepts-in-typescript)
    - [1.2 Q: What is the difference between class, instance, and variable instance?](#12-q-what-is-the-difference-between-class-instance-and-variable-instance)
    - [1.3 Q: What is inheritance vs composition in Angular?](#13-q-what-is-inheritance-vs-composition-in-angular)
  - [2. 🔄 Asynchronous Programming Patterns](#2--asynchronous-programming-patterns)
    - [2.1 Q: What is the difference between Promise, Observable, and Signals?](#21-q-what-is-the-difference-between-promise-observable-and-signals)
    - [2.2 Q: When should I use Promise vs Observable vs Signals?](#22-q-when-should-i-use-promise-vs-observable-vs-signals)
    - [2.3 Q: How to migrate from Promises to Observables to Signals?](#23-q-how-to-migrate-from-promises-to-observables-to-signals)
  - [3. 🚀 Angular 19 Core Concepts](#3--angular-19-core-concepts)
    - [3.1 Q: What are the key changes in Angular 19?](#31-q-what-are-the-key-changes-in-angular-19)
    - [3.2 Q: When should I use standalone components vs NgModules?](#32-q-when-should-i-use-standalone-components-vs-ngmodules)
    - [3.3 Q: How do signals compare to RxJS Observables?](#33-q-how-do-signals-compare-to-rxjs-observables)
    - [3.4 Q: What are standalone components and why use them?](#34-q-what-are-standalone-components-and-why-use-them)
  - [4. 🔄 State Management Deep Dive](#4--state-management-deep-dive)
    - [4.1 Q: What is a "store" and when do I need one?](#41-q-what-is-a-store-and-when-do-i-need-one)
    - [4.2 Q: Should I use NgRx or stick with Angular Signals?](#42-q-should-i-use-ngrx-or-stick-with-angular-signals)
    - [4.3 Q: What's the cleanest way to implement state management?](#43-q-whats-the-cleanest-way-to-implement-state-management)
  - [5. 🎯 Modern Software Practices](#5--modern-software-practices)
    - [5.1 Q: How do I structure my Angular project for scalability?](#51-q-how-do-i-structure-my-angular-project-for-scalability)
    - [5.2 Q: What are the performance best practices?](#52-q-what-are-the-performance-best-practices)
    - [5.3 Q: How should I handle TypeScript in Angular 19?](#53-q-how-should-i-handle-typescript-in-angular-19)
    - [5.4 Q: What's the best approach to testing in Angular 19?](#54-q-whats-the-best-approach-to-testing-in-angular-19)
  - [6. 🔄 State Management Comparison](#6--state-management-comparison)
    - [6.1 Q: When should I use NgRx vs Angular Signals vs RxJS?](#61-q-when-should-i-use-ngrx-vs-angular-signals-vs-rxjs)
  - [7. 📡 Component Communication](#7--component-communication)
    - [7.1 Q: What are all the ways to share data between components?](#71-q-what-are-all-the-ways-to-share-data-between-components)
  - [8. 🏗️ Application Architecture](#8-️-application-architecture)
    - [8.1 Q: What is Dependency Inversion and how do I implement it in Angular?](#81-q-what-is-dependency-inversion-and-how-do-i-implement-it-in-angular)
    - [8.2 Q: How do I manage variable scopes and lifecycles in Angular applications?](#82-q-how-do-i-manage-variable-scopes-and-lifecycles-in-angular-applications)
    - [8.3 Q: What's the difference between Observables and Signals, and when should I use each?](#83-q-whats-the-difference-between-observables-and-signals-and-when-should-i-use-each)
  - [9. 🌐 API Integration](#9--api-integration)
    - [9.1 Q: How do I handle RESTful APIs cleanly?](#91-q-how-do-i-handle-restful-apis-cleanly)
    - [9.2 Q: How do I implement WebSocket/SSE integration?](#92-q-how-do-i-implement-websocketsse-integration)
  - [10. 🏛️ Advanced Architecture](#10-️-advanced-architecture)
    - [10.1 Q: Should I use Hexagonal Architecture in Angular?](#101-q-should-i-use-hexagonal-architecture-in-angular)
    - [10.2 Q: How do I implement Domain-Driven Design patterns?](#102-q-how-do-i-implement-domain-driven-design-patterns)
  - [11. 🧪 Testing](#11--testing)
    - [11.1 Q: What's the modern approach to Angular testing?](#111-q-whats-the-modern-approach-to-angular-testing)
  - [12. 🎨 Styling and UI](#12--styling-and-ui)
    - [12.1 Q: Should I use separate SCSS files or inline styles?](#121-q-should-i-use-separate-scss-files-or-inline-styles)
  - [13. ⚡ Performance](#13--performance)
    - [13.1 Q: How do I optimize bundle size and loading?](#131-q-how-do-i-optimize-bundle-size-and-loading)
  - [14. 📋 Summary](#14--summary)
    - [14.1 ✅ Essential Angular 19 Practices](#141--essential-angular-19-practices)
    - [14.2 ✅ State Management Decision Tree](#142--state-management-decision-tree)
    - [14.3 ✅ Performance Checklist](#143--performance-checklist)
  - [15. 🔗 Related Files in This Codebase](#15--related-files-in-this-codebase)

---

## 1. 🎓 Programming Fundamentals (OOP Concepts)

### 1.1 Q: What are the basic OOP concepts in TypeScript?

**Classes**: Blueprints for creating objects with properties and methods.
**Objects/Instances**: Specific instances created from a class template.
**Encapsulation**: Hiding internal implementation details behind public interfaces.
**Inheritance**: Creating new classes based on existing ones.
**Polymorphism**: Objects of different types responding to the same interface.

```typescript
// 📚 Basic OOP concepts in Angular context
export class DocumentProcessor {
  // 🏠 Properties (instance variables)
  private documents: Document[] = [];  // 🔒 Private - encapsulated
  public isProcessing: boolean = false; // 🌐 Public - accessible

  // 🏗️ Constructor - initializes instance
  constructor(private apiService: ApiService) {}

  // 🔧 Methods (instance functions)
  public processDocument(file: File): Promise<Document> {
    this.isProcessing = true;  // 📝 Modifying instance state
    return this.apiService.upload(file);
  }

  // 📊 Getter - computed property
  get documentCount(): number {
    return this.documents.length;
  }
}

// 📱 Usage - creating instances
const processor1 = new DocumentProcessor(apiService); // Instance 1
const processor2 = new DocumentProcessor(apiService); // Instance 2
// Each instance has its own state and memory space
```

### 1.2 Q: What is the difference between class, instance, and variable instance?

**Class**: The template/blueprint that defines structure and behavior.
**Instance**: A specific object created from a class (using `new`).
**Instance Variable**: Properties that belong to a specific instance.

```typescript
// 🏗️ CLASS - The blueprint (see src/app/services/document.store.ts)
export class DocumentStore {
  // 📦 Instance variables - each instance gets its own copy
  private state = signal<DocumentState>({  // 🎯 This belongs to each instance
    documents: {},
    loading: false
  });

  // 🔧 Instance methods - operate on instance variables
  addDocument(doc: Document): void {
    this.state.update(state => ({  // 'this' refers to current instance
      ...state,
      documents: { ...state.documents, [doc.id]: doc }
    }));
  }
}

// 📱 INSTANCES - Specific objects created from the class
const userStore = new DocumentStore();     // Instance 1 with its own state
const adminStore = new DocumentStore();    // Instance 2 with its own state

// 🔍 Each instance has independent state
userStore.addDocument(doc1);   // Only affects userStore's state
adminStore.addDocument(doc2);  // Only affects adminStore's state

/* 💡 Key Points for Junior Developers:
 * 1. CLASS = Recipe/Blueprint
 * 2. INSTANCE = Actual cake made from recipe
 * 3. INSTANCE VARIABLES = Ingredients in each specific cake
 * 4. You can make many cakes (instances) from one recipe (class)
 * 5. Each cake has its own ingredients (state) that don't affect other cakes
 */
```

### 1.3 Q: What is inheritance vs composition in Angular?

**Inheritance**: "IS-A" relationship - extending base classes.
**Composition**: "HAS-A" relationship - combining objects (preferred in Angular).

```typescript
// 🔗 INHERITANCE Example (less common in modern Angular)
export abstract class BaseComponent {
  protected isLoading = signal(false);
  
  protected handleError(error: Error): void {
    console.error('Component error:', error);
  }
}

export class DocumentComponent extends BaseComponent {
  // 🧬 Inherits isLoading and handleError
  processDocument(): void {
    this.isLoading.set(true);  // Using inherited property
    // ... processing logic
  }
}

// 🧩 COMPOSITION Example (preferred in Angular - see our services)
export class DocumentAnalysisService {
  // 🤝 HAS-A relationships through dependency injection
  constructor(
    private apiService: DocumentApiService,     // HAS-A API service
    private store: DocumentStore,               // HAS-A store
    private logger: LoggingService              // HAS-A logger
  ) {}

  // 🎯 Delegates to composed services
  uploadDocument(file: File): Observable<string> {
    return this.apiService.uploadDocument(file)  // Delegates to API service
      .pipe(
        tap(response => this.store.addDocument(response)), // Uses store
        catchError(error => this.logger.logError(error))  // Uses logger
      );
  }
}

/* 🎯 Why Composition > Inheritance in Angular:
 * 1. More flexible - can change behavior at runtime
 * 2. Better testability - can mock individual services
 * 3. Follows Dependency Injection patterns
 * 4. Avoids inheritance hierarchy problems
 * 5. Easier to understand and maintain
 */
```

## 2. 🔄 Asynchronous Programming Patterns

### 2.1 Q: What is the difference between Promise, Observable, and Signals?

**Promise**: Single future value, eager execution, not cancellable.
**Observable**: Stream of values over time, lazy execution, cancellable.
**Signals**: Reactive state containers, synchronous, automatically tracked dependencies.

```typescript
// 🎯 PROMISE - Single value, executes immediately
async function uploadWithPromise(file: File): Promise<Document> {
  // ⚡ Executes immediately when called
  const response = await fetch('/api/upload', {
    method: 'POST',
    body: file
  });
  return response.json(); // 🎯 Single value returned
}

// Usage
const documentPromise = uploadWithPromise(file); // 🚀 Already executing!
documentPromise.then(doc => console.log(doc));   // 📥 Gets single result

// 🌊 OBSERVABLE - Stream of values, lazy execution
function uploadWithObservable(file: File): Observable<UploadProgress> {
  return new Observable(observer => {
    // 😴 Only executes when subscribed
    const xhr = new XMLHttpRequest();
    
    xhr.upload.onprogress = (event) => {
      // 📊 Multiple values over time
      observer.next({ progress: (event.loaded / event.total) * 100 });
    };
    
    xhr.onload = () => {
      observer.next({ progress: 100, document: xhr.response });
      observer.complete(); // 🏁 Stream ends
    };
    
    xhr.open('POST', '/api/upload');
    xhr.send(file);
    
    // 🛑 Cleanup function for cancellation
    return () => xhr.abort();
  });
}

// Usage
const uploadSub = uploadWithObservable(file)
  .subscribe(progress => console.log(progress)); // 📊 Multiple values
// uploadSub.unsubscribe(); // 🛑 Can cancel

// ⚡ SIGNALS - Reactive state, synchronous (see src/app/services/document.store.ts)
export class DocumentStore {
  private uploadProgress = signal(0);        // 🎯 Current state
  private uploadedDoc = signal<Document | null>(null);
  
  // 🧮 Computed signal - automatically updates
  readonly uploadStatus = computed(() => {
    const progress = this.uploadProgress();
    if (progress === 0) return 'Not started';
    if (progress === 100) return 'Complete';
    return `Uploading: ${progress}%`;
  });
  
  // 🔄 Update methods
  setProgress(progress: number): void {
    this.uploadProgress.set(progress); // 🔄 Immediately updates, triggers UI
  }
}

/* 📊 Comparison Table:
 * 
 * | Feature     | Promise | Observable | Signals |
 * |-------------|---------|------------|---------|
 * | Values      | Single  | Multiple   | Current |
 * | Execution   | Eager   | Lazy       | Sync    |
 * | Cancellable | No      | Yes        | N/A     |
 * | Caching     | Yes     | No*        | Yes     |
 * | UI Updates  | Manual  | Manual     | Auto    |
 * | Error Handling | .catch() | catchError() | try/catch |
 */
```

### 2.2 Q: When should I use Promise vs Observable vs Signals?

**Use Promises for**:
- Simple async operations (one-time API calls)
- Working with fetch() or async/await
- Converting to other patterns

**Use Observables for**:
- Stream data (WebSocket, SSE, progress tracking)
- Complex async flows with operators
- Cancellable operations
- HTTP requests with HttpClient

**Use Signals for**:
- Component state management
- Reactive UI updates
- Computed derived state
- Replacing simple RxJS patterns

```typescript
// 🎯 WHEN TO USE PROMISES - Simple API calls
export class AuthService {
  // ✅ Good for: One-time login
  async login(credentials: LoginData): Promise<User> {
    const response = await fetch('/api/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    });
    return response.json(); // Single result
  }
}

// 🌊 WHEN TO USE OBSERVABLES - Streaming/Complex operations (document-analysis.service.ts)
export class DocumentAnalysisService {
  // ✅ Good for: Real-time progress tracking
  trackDocumentAnalysis(docId: string): Observable<AnalysisUpdate> {
    return new Observable(observer => {
      const eventSource = new EventSource(`/api/documents/${docId}/stream`);
      
      eventSource.onmessage = event => {
        observer.next(JSON.parse(event.data)); // 📊 Multiple values over time
      };
      
      eventSource.onerror = error => observer.error(error);
      
      return () => eventSource.close(); // 🛑 Cleanup
    });
  }
  
  // ✅ Good for: HTTP requests with operators
  uploadWithProgress(file: File): Observable<UploadEvent> {
    return this.http.post('/api/upload', file, {
      reportProgress: true,
      observe: 'events'
    }).pipe(
      filter(event => event.type === HttpEventType.UploadProgress),
      map(event => ({ progress: event.loaded / event.total * 100 })),
      catchError(error => of({ error: error.message }))
    );
  }
}

// ⚡ WHEN TO USE SIGNALS - State management (document.store.ts)
export class DocumentStore {
  // ✅ Good for: Reactive component state
  private documents = signal<Document[]>([]);
  private filter = signal<string>('');
  
  // 🧮 Computed signals for derived state
  readonly filteredDocuments = computed(() => {
    const docs = this.documents();
    const filterText = this.filter();
    return docs.filter(doc => 
      doc.filename.toLowerCase().includes(filterText.toLowerCase())
    );
  });
  
  // ✅ Good for: Simple state updates
  addDocument(doc: Document): void {
    this.documents.update(docs => [...docs, doc]); // 🔄 UI auto-updates
  }
  
  setFilter(filter: string): void {
    this.filter.set(filter); // 🔄 filteredDocuments auto-recalculates
  }
}

/* 🎯 Decision Tree:
 * 
 * Need real-time data? → Observable
 * ↓
 * Need to cancel operations? → Observable  
 * ↓
 * Need complex async operators? → Observable
 * ↓
 * Managing component state? → Signals
 * ↓
 * Need reactive derived values? → Signals
 * ↓
 * Simple one-time async call? → Promise
 */
```

### 2.3 Q: How to migrate from Promises to Observables to Signals?

**Migration Path**: Promise → Observable → Signal (where appropriate)

```typescript
// 🔄 MIGRATION EXAMPLE: Document Upload Feature

// 📝 STEP 1: Promise-based (legacy approach)
class DocumentServiceV1 {
  private documents: Document[] = []; // ❌ Manual state management
  
  async uploadDocument(file: File): Promise<Document> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      });
      
      const document = await response.json();
      this.documents.push(document); // ❌ Manual array update
      
      // ❌ Manual notification needed
      this.notifyDocumentAdded(document);
      
      return document;
    } catch (error) {
      console.error('Upload failed:', error);
      throw error;
    }
  }
}

// 🌊 STEP 2: Observable-based (better async handling)
class DocumentServiceV2 {
  private documentsSubject = new BehaviorSubject<Document[]>([]);
  public documents$ = this.documentsSubject.asObservable();
  
  uploadDocument(file: File): Observable<Document> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.http.post<Document>('/api/upload', formData).pipe(
      tap(document => {
        // ✅ Side effect in stream
        const currentDocs = this.documentsSubject.value;
        this.documentsSubject.next([...currentDocs, document]);
      }),
      catchError(error => {
        console.error('Upload failed:', error);
        return throwError(() => error);
      })
    );
  }
}

// ⚡ STEP 3: Signal-based (modern Angular 19 - see document.store.ts)
@Injectable({ providedIn: 'root' })
export class DocumentServiceV3 {
  private readonly http = inject(HttpClient);
  
  // 🎯 Signal-based state
  private documents = signal<Document[]>([]);
  private uploadProgress = signal<number>(0);
  private isUploading = signal<boolean>(false);
  
  // 🧮 Computed signals for derived state
  readonly documentsCount = computed(() => this.documents().length);
  readonly hasDocuments = computed(() => this.documents().length > 0);
  readonly uploadStatus = computed(() => {
    if (!this.isUploading()) return 'idle';
    const progress = this.uploadProgress();
    return progress === 100 ? 'complete' : `uploading ${progress}%`;
  });
  
  // 📖 Read-only accessors
  readonly documentsSignal = this.documents.asReadonly();
  readonly isUploadingSignal = this.isUploading.asReadonly();
  
  // 🚀 Upload with progress tracking
  uploadDocument(file: File): Observable<Document> {
    this.isUploading.set(true);
    this.uploadProgress.set(0);
    
    const formData = new FormData();
    formData.append('file', file);
    
    return this.http.post<Document>('/api/upload', formData, {
      reportProgress: true,
      observe: 'events'
    }).pipe(
      tap(event => {
        if (event.type === HttpEventType.UploadProgress && event.total) {
          // 📊 Update progress signal
          const progress = Math.round(100 * event.loaded / event.total);
          this.uploadProgress.set(progress);
        } else if (event.type === HttpEventType.Response) {
          // ✅ Upload complete - update documents
          this.documents.update(docs => [...docs, event.body!]);
          this.uploadProgress.set(100);
        }
      }),
      filter(event => event.type === HttpEventType.Response),
      map(event => event.body!),
      finalize(() => {
        this.isUploading.set(false);
        // Reset progress after delay for UI feedback
        setTimeout(() => this.uploadProgress.set(0), 1000);
      }),
      catchError(error => {
        console.error('Upload failed:', error);
        this.isUploading.set(false);
        this.uploadProgress.set(0);
        return throwError(() => error);
      })
    );
  }
}

// 📱 COMPONENT USAGE - Automatic reactivity
@Component({
  template: `
    <div>
      <!-- ⚡ Automatic UI updates from signals -->
      <p>Documents: {{ documentService.documentsCount() }}</p>
      <p>Status: {{ documentService.uploadStatus() }}</p>
      
      @if (documentService.isUploadingSignal()) {
        <progress [value]="uploadProgress()" max="100"></progress>
      }
      
      <!-- 📋 List automatically updates when documents change -->
      <ul>
        @for (doc of documentService.documentsSignal(); track doc.id) {
          <li>{{ doc.filename }}</li>
        }
      </ul>
    </div>
  `
})
export class DocumentListComponent {
  constructor(protected documentService: DocumentServiceV3) {}
}

/* 🎯 Migration Benefits:
 * 
 * Promise → Observable:
 * ✅ Better error handling with operators
 * ✅ Cancellation support
 * ✅ Progress tracking capabilities
 * ✅ Composable with other streams
 * 
 * Observable → Signals:
 * ✅ Automatic change detection
 * ✅ Simpler mental model
 * ✅ No subscription management
 * ✅ Better performance
 * ✅ Computed derived state
 */
```

## 3. 🚀 Angular 19 Core Concepts

### 3.1 Q: What are the key changes in Angular 19?

**Standalone Components by Default**: Angular 19 embraces standalone components as the primary architecture pattern, eliminating the need for NgModules in most cases.

**Signals-First Approach**: Native signals replace many RxJS patterns for state management and change detection.

**Zoneless Change Detection**: Optional zoneless mode improves performance by reducing Zone.js overhead.

**Enhanced Developer Experience**: Better TypeScript integration, improved debugging, and streamlined APIs.

```typescript
// Modern Angular 19 component (see src/app/components/upload-zone/upload-zone.component.ts)
@Component({
  standalone: true,  // 🚀 No NgModules needed! Direct imports in component
  selector: 'app-user-profile',
  imports: [CommonModule, ReactiveFormsModule], // 📦 Direct dependency imports
  template: `
    <div class="profile-card">
      <h2>{{ user().name }}</h2>  <!-- 🔄 Signal automatically triggers change detection -->
      <p>{{ computedBio() }}</p>   <!-- 💡 Computed signal updates when dependencies change -->
    </div>
  `
})
export class UserProfileComponent {
  // 📥 Signal inputs - type-safe, reactive, no @Input() decorator needed
  user = input.required<User>();  // ✅ Required input, throws error if not provided
  bio = input<string>('');        // ⭐ Optional input with default value
  
  // 🧮 Computed signals automatically recalculate when dependencies change
  computedBio = computed(() => 
    this.bio() || `${this.user().name} has no bio yet.`
  );
}

/* 🎯 Key Benefits for Junior Developers:
 * 1. No complex lifecycle methods - signals handle reactivity
 * 2. Type safety prevents runtime errors
 * 3. Automatic change detection optimization
 * 4. Clear dependency tracking through computed signals
 */
```

### 3.2 Q: When should I use standalone components vs NgModules?

**Use Standalone Components** (recommended for new projects):
- Simplified architecture with less boilerplate
- Better tree-shaking and lazy loading
- Clearer dependencies through the `imports` array
- Easier testing and reusability

**Use NgModules** only when:
- Working with legacy codebases
- Need complex feature module organization
- Using libraries that haven't adopted standalone pattern

```typescript
// ✅ Standalone Component (Recommended)
@Component({
  selector: 'app-document-viewer',
  standalone: true,
  imports: [CommonModule, MatButtonModule, DocumentListComponent], // Direct imports
  template: `...`
})
export class DocumentViewerComponent {}

// ❌ NgModule-based (Legacy)
@NgModule({
  declarations: [DocumentViewerComponent, DocumentListComponent],
  imports: [CommonModule, MatButtonModule],
  exports: [DocumentViewerComponent]
})
export class DocumentModule {}
```

### 3.3 Q: How do signals compare to RxJS Observables?

**Signals**: Synchronous reactive state containers, automatically tracked dependencies, zoneless-ready.

**Observables**: Asynchronous streams, rich operator ecosystem, complex async flows.

```typescript
// 🎯 SIGNALS - State management (see document.store.ts)
export class DocumentStore {
  private state = signal<DocumentState>({
    documents: [],
    loading: false
  });

  // Computed signals automatically track dependencies
  readonly documentCount = computed(() => this.state().documents.length);
  
  // Simple mutations
  addDocument(doc: Document): void {
    this.state.update(state => ({
      ...state,
      documents: [...state.documents, doc]
    }));
  }
}

// 🌊 OBSERVABLES - Async operations
export class DocumentApiService {
  uploadDocument(file: File): Observable<Document> {
    return this.http.post<Document>('/api/documents', file).pipe(
      retry(3),
      timeout(30000),
      catchError(error => throwError(() => error))
    );
  }
}
```

### 3.4 Q: What are standalone components and why use them?

**Standalone Components** eliminate NgModules for individual components, making them self-contained and easier to manage.

**Benefits**: Simplified architecture, better tree-shaking, clearer dependencies, easier lazy loading.

```typescript
// Standalone component with direct imports
@Component({
  selector: 'app-upload-zone',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule], // Direct imports
  templateUrl: './upload-zone.component.html'
})
export class UploadZoneComponent {
  // Component logic...
}

// Lazy loading standalone components
const routes: Routes = [
  {
    path: 'documents',
    loadComponent: () => import('./documents/document-list.component')
      .then(m => m.DocumentListComponent)
  }
];
```

## 4. 🔄 State Management Deep Dive

### 4.1 Q: What is a "store" and when do I need one?

A **store** is a centralized state container that manages application data and provides reactive access to components.

**Use a store when**:
- State is shared between multiple components
- State needs to persist across route changes
- Complex state transformations are needed
- You need undo/redo functionality

```typescript
// Signal-based state management (see src/app/services/document.store.ts)
@Injectable({ providedIn: 'root' })  // 🌐 Available throughout entire app
export class DocumentStore {
  // 🏪 Single source of truth - all state in one signal
  private state = signal<DocumentState>({
    documents: {},      // 📁 Record<string, Document> for O(1) lookup by ID
    loading: false,     // 🔄 Global loading state
    error: null        // ❌ Error state management
  });

  // 🧮 Computed selectors - automatically update when state changes
  readonly documents = computed(() => 
    Object.values(this.state().documents)  // 📊 Convert object to array for templates
  );
  readonly isLoading = computed(() => this.state().loading);
  
  // 🔄 State mutations - use update() for immutable updates
  addDocument(document: Document): void {
    this.state.update(state => ({
      ...state,  // 📋 Spread existing state
      documents: { 
        ...state.documents,           // 📋 Spread existing documents
        [document.id]: document       // ➕ Add/update document by ID
      }
    }));
  }
  
  // 🎯 Always prefer update() over set() for partial state changes
  setError(error: string | null): void {
    this.state.update(state => ({ ...state, error }));
  }
}

/* 💡 Junior Developer Notes:
 * - state.update() preserves existing state (immutable)
 * - computed() automatically tracks dependencies
 * - Use Record<string, T> for efficient ID-based lookups
 * - Signals eliminate manual change detection and subscriptions
 */
```

### 4.2 Q: Should I use NgRx or stick with Angular Signals?

**Use Angular Signals for**:
- Most applications (recommended starting point)
- Simple to moderate state complexity
- Teams new to state management
- Rapid prototyping

**Use NgRx when**:
- Complex state with many interdependencies
- Need time-travel debugging
- Large teams requiring strict patterns
- Advanced features like entity management

```typescript
// Simple signal-based approach
@Injectable({ providedIn: 'root' })
export class SimpleDocumentStore {
  private documents = signal<Document[]>([]);
  
  readonly documentsCount = computed(() => this.documents().length);
  
  addDocument(doc: Document): void {
    this.documents.update(docs => [...docs, doc]);
  }
}

// When you might need NgRx
interface AppState {
  documents: DocumentState;
  users: UserState;
  notifications: NotificationState;
  router: RouterState;
  // ... many more slices
}
```

### 4.3 Q: What's the cleanest way to implement state management?

**Three-Tier Architecture**: Separate API calls, state management, and business logic into distinct layers.

```typescript
// 🏗️ THREE-TIER ARCHITECTURE (see src/app/services/ folder)

// 1. API Service - Pure HTTP operations (src/app/services/document-api.service.ts)
@Injectable({ providedIn: 'root' })
export class DocumentApiService {
  constructor(private http: HttpClient) {}  // 🌐 Only HTTP concerns
  
  uploadDocument(file: File): Observable<UploadResponse> {
    const formData = new FormData();          // 📋 Prepare file for upload
    formData.append('file', file);
    return this.http.post<UploadResponse>('/api/documents', formData);
    // ✅ No state management - pure HTTP operation
  }
  
  // 📡 Server-Sent Events for real-time updates
  createDocumentStream(documentId: string): EventSource {
    return new EventSource(`/api/v1/documents/${documentId}/stream`);
  }
}

// 2. Store Service - State management (src/app/services/document.store.ts)
@Injectable({ providedIn: 'root' })
export class DocumentStore {
  private state = signal<DocumentState>(initialState);  // 🏪 Central state
  
  // 🧮 Computed selectors for components
  readonly documents = computed(() => Object.values(this.state().documents));
  readonly isUploading = computed(() => this.state().loading.upload);
  
  // 🔄 State mutations - ONLY data operations
  addDocument(document: Document): void {
    this.state.update(state => ({
      ...state,
      documents: { ...state.documents, [document.id]: document }
    }));
  }
}

// 3. Business Logic Service - Orchestration (src/app/services/document-analysis.service.ts)
@Injectable({ providedIn: 'root' })
export class DocumentAnalysisService {
  // 💉 Modern dependency injection using inject()
  private readonly apiService = inject(DocumentApiService);
  private readonly store = inject(DocumentStore);
  
  // 🎯 Orchestrates complete workflows
  uploadDocument(file: File): Observable<string> {
    this.store.setUploadLoading(true);  // 🔄 Update UI state
    
    return this.apiService.uploadDocument(file).pipe(
      tap((response: UploadResponse) => {
        // 📄 Create pending document for immediate UI feedback
        const pendingDocument = this.createPendingDocument(response);
        this.store.addDocument(pendingDocument);
        
        // 📡 Start real-time tracking via SSE
        this.connectToSSE(response.document_id);
      }),
      catchError(this.handleWorkflowError('Upload')),  // ❌ Centralized error handling
      finalize(() => this.store.setUploadLoading(false)),  // 🏁 Always cleanup
      map(response => response.document_id)  // 🎯 Return just the ID
    );
  }
}

/* 🎓 Architecture Benefits for Junior Developers:
 * 1. SEPARATION OF CONCERNS: Each service has ONE responsibility
 * 2. TESTABILITY: Easy to mock individual layers
 * 3. MAINTAINABILITY: Changes isolated to specific layers
 * 4. REUSABILITY: API service can be used by multiple business services
 * 5. SCALABILITY: Easy to add new business logic without touching API/state
 */
```

## 5. 🎯 Modern Software Practices

### 5.1 Q: How do I structure my Angular project for scalability?

**Feature-First Organization**: Group files by feature rather than by type.

**Core/Shared/Feature Structure**: Organize code into logical modules with clear dependencies.

```typescript
src/
├── app/
│   ├── core/                    // Singleton services, guards
│   │   ├── services/
│   │   └── interceptors/
│   ├── shared/                  // Reusable components, directives
│   │   ├── components/
│   │   └── pipes/
│   ├── features/                // Feature modules
│   │   ├── documents/
│   │   │   ├── components/
│   │   │   ├── services/
│   │   │   └── models/
│   │   └── auth/
│   └── layout/                  // App shell components
```

### 5.2 Q: What are the performance best practices?

**Change Detection Optimization** (see src/app/components/data-table/data-table.component.ts):

```typescript
@Component({
  selector: 'app-data-table',
  changeDetection: ChangeDetectionStrategy.OnPush, // 🚀 ESSENTIAL for performance!
  standalone: true  // 📦 Standalone components are faster
})
export class DataTableComponent {
  // 📥 Signal inputs automatically optimize change detection
  data = input.required<HealthMarker[]>(); // ✅ Type-safe required input
  
  // 🧮 Computed signals only recalculate when dependencies change
  readonly filteredData = computed(() => {
    const allData = this.data();  // 📊 Read current data
    const filterActive = this.showOnlyOutOfRange();
    
    if (!filterActive) return allData;
    
    // 🔍 Filter logic only runs when data or filter changes
    return allData.filter(item => {
      const status = this.getValueStatus(item);
      return status === 'borderline' || status === 'abnormal';
    });
  });
  
  // 🔄 Local state with signals
  readonly showOnlyOutOfRange = signal(false);
  
  // 🎯 Method to toggle filter - triggers computed recalculation
  toggleFilter(): void {
    this.showOnlyOutOfRange.set(!this.showOnlyOutOfRange());
  }
}

/* 💡 Performance Tips for Junior Developers:
 * 1. OnPush + Signals = Minimal change detection cycles
 * 2. computed() creates efficient dependency graphs
 * 3. Signals only notify when values actually change
 * 4. No manual subscription management needed
 * 5. Automatic cleanup when component is destroyed
 */
```

**Lazy Loading and Code Splitting**:

```typescript
// Lazy load feature modules
const routes: Routes = [
  {
    path: 'documents',
    loadComponent: () => import('./features/documents/document-list.component')
  },
  {
    path: 'analysis',
    loadChildren: () => import('./features/analysis/analysis.routes')
  }
];
```

### 5.3 Q: How should I handle TypeScript in Angular 19?

**Strong Typing Patterns** (see src/app/models/document.model.ts):

```typescript
// 📋 Use interfaces for data contracts - clear structure expectations
export interface HealthDocument {
  readonly id: string;           // 🔑 Immutable ID
  readonly filename: string;     // 📄 Original filename
  readonly status: DocumentStatus; // 🔄 Current processing state
  readonly uploaded_at: string;  // ⏰ ISO timestamp
  readonly analysis?: AnalysisResult; // ❓ Optional - available when complete
  
  // 📊 Progress tracking fields
  readonly progress?: number;              // 0-100 percentage
  readonly processing_stage?: ProcessingStage; // Current pipeline stage
  readonly error_message?: string;         // Error details if failed
}

// 🎯 Use type unions for finite states - prevents invalid states
export type DocumentStatus = 
  | 'uploading'    // 📤 File being uploaded
  | 'processing'   // 🔄 In analysis pipeline
  | 'complete'     // ✅ Successfully processed
  | 'error';       // ❌ Processing failed

// 🔄 Processing stages for medical document pipeline
export type ProcessingStage = 
  | 'ocr_extraction'  // 📄 Text extraction from PDF/image
  | 'ai_analysis'     // 🤖 AI parsing health data
  | 'saving_results'  // 💾 Persisting to database
  | 'complete';       // ✅ All stages finished

// 🔬 Health marker data structure
export interface HealthMarker {
  readonly marker: string;          // e.g., "Hemoglobin"
  readonly value: string;           // e.g., "14.2"
  readonly unit?: string;           // e.g., "g/dL"
  readonly reference_range?: string; // e.g., "12.0-15.5"
  readonly status?: 'normal' | 'high' | 'low'; // Clinical assessment
}

// 🛠️ Use mapped types for transformations - type-safe modifications
export type CreateDocumentRequest = Omit<HealthDocument, 'id' | 'status' | 'uploaded_at'>;
export type UpdateDocumentRequest = Partial<Pick<HealthDocument, 'status' | 'progress' | 'error_message'>>;

// 🌐 Use generic constraints for reusable API patterns
export interface ApiResponse<T> {
  data: T;                           // 📊 Response payload
  status: 'success' | 'error';      // 🎯 Operation result
  message?: string;                  // ℹ️ Optional details
  timestamp?: string;                // ⏰ Response time
}

// 🔒 Use const assertions for immutable data
export const PROCESSING_STAGES = [
  'ocr_extraction',
  'ai_analysis', 
  'saving_results',
  'complete'
] as const;

// 🎯 Type guards for runtime validation
export function isDocumentStatus(value: string): value is DocumentStatus {
  return ['uploading', 'processing', 'complete', 'error'].includes(value);
}

export function isValidHealthMarker(obj: unknown): obj is HealthMarker {
  return typeof obj === 'object' && 
         obj !== null &&
         typeof (obj as HealthMarker).marker === 'string' &&
         typeof (obj as HealthMarker).value === 'string';
}

/* 💡 TypeScript Best Practices for Junior Developers:
 * 1. readonly fields prevent accidental mutations
 * 2. Union types catch invalid state combinations at compile time
 * 3. Optional fields (?) vs undefined - be explicit about expectations
 * 4. Mapped types (Omit, Pick, Partial) create type-safe variations
 * 5. Type guards enable safe runtime type checking
 * 6. const assertions create immutable, strictly typed arrays
 * 7. Generic constraints make reusable, type-safe utilities
 */
```

### 5.4 Q: What's the best approach to testing in Angular 19?

**Signal Testing** (see src/app/services/document-analysis.service.spec.ts):

```typescript
describe('DocumentStore', () => {
  let store: DocumentStore;

  beforeEach(() => {
    store = new DocumentStore();  // 🏪 Fresh store for each test
  });

  it('should add document and update computed values', () => {
    // 📋 Arrange - Create test data
    const document = createMockDocument();
    
    // 🎬 Act - Perform the operation
    store.addDocument(document);
    
    // ✅ Assert - Verify state changes
    expect(store.documents()).toContain(document);    // 📊 Array includes document
    expect(store.documentCount()).toBe(1);            // 🔢 Count updated
    expect(store.processingCount()).toBe(0);          // 🔄 No processing docs
  });
  
  it('should handle document status transitions', () => {
    // 📋 Create document in processing state
    const processingDoc = createMockDocument({ 
      status: DocumentStatus.PROCESSING 
    });
    store.addDocument(processingDoc);
    
    // ✅ Verify initial computed state
    expect(store.processingCount()).toBe(1);
    expect(store.completedCount()).toBe(0);
    
    // 🎬 Update to completed status
    store.updateDocument(processingDoc.id, { 
      status: DocumentStatus.COMPLETE 
    });
    
    // ✅ Verify computed signals updated automatically
    expect(store.processingCount()).toBe(0);  // 📉 Processing count decreased
    expect(store.completedCount()).toBe(1);   // 📈 Completed count increased
  });
  
  it('should filter documents by status correctly', () => {
    // 📋 Add documents with different statuses
    const docs = [
      createMockDocument({ status: DocumentStatus.PROCESSING }),
      createMockDocument({ status: DocumentStatus.COMPLETE }),
      createMockDocument({ status: DocumentStatus.ERROR })
    ];
    docs.forEach(doc => store.addDocument(doc));
    
    // ✅ Verify filtering computed signals
    expect(store.pendingDocuments()).toHaveLength(1);
    expect(store.completedDocuments()).toHaveLength(1);
    expect(store.failedDocuments()).toHaveLength(1);
  });
});

// 🔧 Test utilities for consistent mock data
function createMockDocument(overrides: Partial<HealthDocument> = {}): HealthDocument {
  return {
    id: crypto.randomUUID(),
    filename: 'test-document.pdf',
    uploaded_at: new Date().toISOString(),
    status: DocumentStatus.PROCESSING,
    progress: 0,
    processing_stage: 'ocr_extraction',
    ...overrides  // 🎯 Allow test-specific customization
  };
}

/* 🎓 Signal Testing Best Practices for Junior Developers:
 * 1. Test computed signals by verifying they update when dependencies change
 * 2. Use descriptive test data factories (createMockDocument)
 * 3. Test state transitions, not just individual operations
 * 4. Signals eliminate the need for async testing in most cases
 * 5. Focus on testing behavior, not implementation details
 * 6. Use overrides pattern for flexible test data creation
 */
```

## 6. 🔄 State Management Comparison

### 6.1 Q: When should I use NgRx vs Angular Signals vs RxJS?

Choose based on your application's complexity and team needs:

**🔵 Angular Signals** (Recommended for Modern Apps):
- Simple to moderate state complexity
- Team new to state management
- Rapid development and prototyping
- Better performance out of the box

**🟡 RxJS** (For Complex Async Operations):
- Complex async flows and data transformations
- Heavy integration with external APIs
- Need advanced operators (debounce, switchMap, etc.)
- Existing RxJS expertise in team

**🟠 NgRx** (For Enterprise Applications):
- Large, complex applications
- Multiple teams working on same codebase
- Need for time-travel debugging
- Strict architectural patterns required

```typescript
// 🔵 ANGULAR SIGNALS - Simple, Modern Approach
@Injectable({ providedIn: 'root' })
export class SimpleDocumentStore {
  private documents = signal<Document[]>([]);
  private loading = signal(false);
  
  readonly documentCount = computed(() => this.documents().length);
  readonly isEmpty = computed(() => this.documents().length === 0);
  
  addDocument(doc: Document): void {
    this.documents.update(docs => [...docs, doc]);
  }
  
  setLoading(loading: boolean): void {
    this.loading.set(loading);
  }
}

// 🟡 RXJS - Complex Async Operations
@Injectable({ providedIn: 'root' })
export class RxJSDocumentService {
  private documentsSubject = new BehaviorSubject<Document[]>([]);
  public documents$ = this.documentsSubject.asObservable();
  
  uploadWithProgress(file: File): Observable<UploadEvent> {
    return this.http.post('/api/upload', file, { reportProgress: true })
      .pipe(
        debounceTime(100),
        distinctUntilChanged(),
        switchMap(response => this.processDocument(response)),
        catchError(error => this.handleError(error)),
        tap(event => this.updateProgress(event))
      );
  }
}

// 🟠 NGRX - Enterprise State Management
@Injectable()
export class DocumentEffects {
  uploadDocument$ = createEffect(() =>
    this.actions$.pipe(
      ofType(DocumentActions.uploadDocument),
      switchMap(action =>
        this.documentService.upload(action.file).pipe(
          map(result => DocumentActions.uploadSuccess({ document: result })),
          catchError(error => of(DocumentActions.uploadFailure({ error })))
        )
      )
    )
  );
}
```

## 7. 📡 Component Communication

### 7.1 Q: What are all the ways to share data between components?

Modern Angular 19 provides several communication patterns:

**1. 📥 Parent → Child: Signal Inputs** (Recommended):

```typescript
// Parent component
@Component({
  template: `
    <app-document-card 
      [document]="selectedDocument()" 
      [isHighlighted]="isSelected()" />
  `
})
export class DocumentListComponent {
  selectedDocument = signal<Document | null>(null);
  isSelected = computed(() => this.selectedDocument() !== null);
}

// Child component  
@Component({
  selector: 'app-document-card'
})
export class DocumentCardComponent {
  document = input.required<Document>();  // ✅ Type-safe, reactive
  isHighlighted = input<boolean>(false);  // Optional with default
  
  // Computed properties based on inputs
  cardClasses = computed(() => [
    'document-card',
    this.isHighlighted() && 'highlighted'
  ].filter(Boolean).join(' '));
}
```

**2. 📤 Child → Parent: Output Events**:

```typescript
// Child component
@Component({
  selector: 'app-upload-zone',
  template: `
    <input type="file" (change)="onFileSelected($event)" />
  `
})
export class UploadZoneComponent {
  @Output() fileSelected = new EventEmitter<File>();
  
  onFileSelected(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) {
      this.fileSelected.emit(file);
    }
  }
}

// Parent component
@Component({
  template: `
    <app-upload-zone (fileSelected)="handleFileUpload($event)" />
  `
})
export class DocumentPageComponent {
  handleFileUpload(file: File): void {
    this.documentService.uploadDocument(file);
  }
}
```

**3. 🏪 Service-Based Communication** (Signal Stores):

```typescript
// Shared service
@Injectable({ providedIn: 'root' })
export class DocumentStore {
  private selectedId = signal<string | null>(null);
  private documents = signal<Document[]>([]);
  
  readonly selectedDocument = computed(() => {
    const id = this.selectedId();
    return id ? this.documents().find(doc => doc.id === id) || null : null;
  });
  
  selectDocument(id: string | null): void {
    this.selectedId.set(id);
  }
}

// Component A
export class DocumentListComponent {
  constructor(private store: DocumentStore) {}
  
  onDocumentClick(doc: Document): void {
    this.store.selectDocument(doc.id);
  }
}

// Component B  
export class DocumentDetailComponent {
  constructor(private store: DocumentStore) {}
  
  selectedDocument = this.store.selectedDocument;
}
```

## 8. 🏗️ Application Architecture

### 8.1 Q: What is Dependency Inversion and how do I implement it in Angular?

**Dependency Inversion Principle**: High-level modules shouldn't depend on low-level modules. Both should depend on abstractions.

```typescript
// ❌ BAD: Direct dependency on concrete implementation
export class DocumentService {
  constructor(private http: HttpClient) {}
  
  uploadDocument(file: File): Observable<Document> {
    // Tightly coupled to HttpClient
    return this.http.post<Document>('/api/documents', file);
  }
}

// ✅ GOOD: Depend on abstraction
export abstract class DocumentApiInterface {
  abstract uploadDocument(file: File): Observable<Document>;
  abstract getDocument(id: string): Observable<Document>;
}

export class HttpDocumentApi implements DocumentApiInterface {
  constructor(private http: HttpClient) {}
  
  uploadDocument(file: File): Observable<Document> {
    return this.http.post<Document>('/api/documents', file);
  }
  
  getDocument(id: string): Observable<Document> {
    return this.http.get<Document>(`/api/documents/${id}`);
  }
}

export class DocumentService {
  constructor(private api: DocumentApiInterface) {} // Depends on abstraction
  
  processDocument(file: File): Observable<Document> {
    return this.api.uploadDocument(file);
  }
}

// Dependency injection configuration
@Injectable({
  providedIn: 'root',
  useClass: HttpDocumentApi  // Can be swapped for testing
})
export class DocumentApiInterface {}
```

### 8.2 Q: How do I manage variable scopes and lifecycles in Angular applications?

Understanding scope and lifecycle prevents memory leaks and improves performance:

```typescript
// 🎯 COMPONENT SCOPE - Lives with component instance
@Component({})
export class DocumentComponent implements OnInit, OnDestroy {
  // 🏠 Component instance variables
  private subscription: Subscription = new Subscription();
  private documents = signal<Document[]>([]);  // Cleaned up automatically
  
  ngOnInit(): void {
    // 📡 Component-scoped subscriptions
    this.subscription.add(
      this.documentService.getDocuments().subscribe(docs => {
        this.documents.set(docs);
      })
    );
  }
  
  ngOnDestroy(): void {
    // 🧹 Manual cleanup for observables
    this.subscription.unsubscribe();
    // Signals clean up automatically
  }
}

// 🌐 SERVICE SCOPE - Singleton, lives for app lifetime
@Injectable({ providedIn: 'root' })
export class DocumentStore {
  // 🌍 App-wide state - persists across route changes
  private documents = signal<Document[]>([]);
  
  // No ngOnDestroy needed - lives for app lifetime
}

// 🔄 LOCAL SCOPE - Function/method scope
export class UploadService {
  uploadDocument(file: File): Observable<Document> {
    // 📍 Local variables - garbage collected when function ends
    const formData = new FormData();
    const uploadStartTime = Date.now();
    
    return this.http.post('/api/upload', formData).pipe(
      tap(response => {
        // 📊 Local scope access
        const duration = Date.now() - uploadStartTime;
        console.log(`Upload took ${duration}ms`);
      })
    );
  }
}
```

### 8.3 Q: What's the difference between Observables and Signals, and when should I use each?

**Observables**: Asynchronous streams over time, lazy evaluation, rich operators.
**Signals**: Synchronous reactive state, automatic dependency tracking, simpler mental model.

```typescript
// 🌊 OBSERVABLES - For async operations and streams
export class DocumentApiService {
  // ✅ Perfect for: HTTP requests
  getDocuments(): Observable<Document[]> {
    return this.http.get<Document[]>('/api/documents').pipe(
      retry(3),
      timeout(5000),
      catchError(error => of([]))
    );
  }
  
  // ✅ Perfect for: Real-time streams
  watchDocumentProgress(id: string): Observable<Progress> {
    return new Observable(observer => {
      const eventSource = new EventSource(`/api/documents/${id}/progress`);
      eventSource.onmessage = event => observer.next(JSON.parse(event.data));
      return () => eventSource.close();
    });
  }
  
  // ✅ Perfect for: Complex async workflows
  uploadWithRetry(file: File): Observable<Document> {
    return this.uploadDocument(file).pipe(
      retryWhen(errors => 
        errors.pipe(
          delay(1000),
          take(3)
        )
      ),
      switchMap(result => this.pollForCompletion(result.id)),
      shareReplay(1)
    );
  }
}

// ⚡ SIGNALS - For state management and reactive UI
export class DocumentStore {
  // ✅ Perfect for: Component state
  private documents = signal<Document[]>([]);
  private filter = signal<string>('');
  private sortBy = signal<'name' | 'date'>('name');
  
  // ✅ Perfect for: Computed derived state
  readonly filteredDocuments = computed(() => {
    const docs = this.documents();
    const filterText = this.filter().toLowerCase();
    const sortField = this.sortBy();
    
    return docs
      .filter(doc => doc.name.toLowerCase().includes(filterText))
      .sort((a, b) => a[sortField].localeCompare(b[sortField]));
  });
  
  // ✅ Perfect for: Simple state updates
  setFilter(filter: string): void {
    this.filter.set(filter); // UI updates automatically
  }
  
  addDocument(doc: Document): void {
    this.documents.update(docs => [...docs, doc]);
  }
}

// 🤝 HYBRID APPROACH - Combine both for optimal results
export class DocumentService {
  private store = inject(DocumentStore);
  private api = inject(DocumentApiService);
  
  // Observable for async operation → Signal for state management
  uploadDocument(file: File): Observable<string> {
    return this.api.uploadDocument(file).pipe(
      tap(document => {
        // Update signal-based store with Observable result
        this.store.addDocument(document);
      }),
      map(document => document.id)
    );
  }
  
  // Signal for reactive queries
  searchDocuments(query: string): void {
    this.store.setFilter(query); // Immediate UI update via signals
    
    // Background refresh via Observable
    this.api.searchDocuments(query).subscribe(results => {
      this.store.setDocuments(results);
    });
  }
}

/* 🎯 Decision Matrix:
 * 
 * Use Observables for:
 * ✅ HTTP requests and API calls
 * ✅ Event streams (WebSocket, SSE)
 * ✅ Complex async operations with operators
 * ✅ Time-based operations (debounce, throttle)
 * ✅ Cancellable operations
 * 
 * Use Signals for:
 * ✅ Component state management
 * ✅ Reactive computed values
 * ✅ UI updates and change detection
 * ✅ Simple synchronous transformations
 * ✅ Cross-component state sharing
 */
```

## 9. 🌐 API Integration

### 9.1 Q: How do I handle RESTful APIs cleanly?

Structure API calls with proper error handling, typing, and separation of concerns:

```typescript
// Clean API service with strong typing
@Injectable({ providedIn: 'root' })
export class DocumentApiService {
  private readonly baseUrl = '/api/v1/documents';
  
  constructor(private http: HttpClient) {}
  
  // GET /api/v1/documents
  getDocuments(): Observable<Document[]> {
    return this.http.get<Document[]>(this.baseUrl).pipe(
      catchError(this.handleError<Document[]>('getDocuments', []))
    );
  }
  
  // POST /api/v1/documents
  createDocument(file: File): Observable<Document> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.http.post<Document>(this.baseUrl, formData).pipe(
      catchError(this.handleError<Document>('createDocument'))
    );
  }
  
  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {
      console.error(`${operation} failed:`, error);
      return of(result as T);
    };
  }
}
```

### 9.2 Q: How do I implement WebSocket/SSE integration?

**Server-Sent Events (SSE) Service** (see src/app/services/document-analysis.service.ts):

```typescript
@Injectable({ providedIn: 'root' })
export class DocumentAnalysisService {
  private readonly store = inject(DocumentStore);  // 💉 Modern injection
  private eventSource: EventSource | null = null;  // 📡 Track connection

  // 🔌 Establish SSE connection for real-time updates
  private connectToSSE(documentId: string): void {
    console.log('🔌 Establishing SSE connection for:', documentId);
    
    // 🧹 Clean up any existing connection
    this.disconnectSSE();
    
    // 📊 Update connection status in store
    this.store.setConnectionStatus('connecting');

    try {
      // 📡 Create EventSource connection
      this.eventSource = new EventSource(`/api/v1/documents/${documentId}/stream`);
      
      // ✅ Handle successful connection
      this.eventSource.onopen = () => {
        console.log('✅ SSE connection established');
        this.store.setConnectionStatus('connected');
      };

      // 📩 Handle incoming real-time messages
      this.eventSource.onmessage = (event: MessageEvent) => {
        try {
          const data: AnalysisResultResponse = JSON.parse(event.data);
          console.log('📡 SSE message received:', data);

          // 🔄 Update document state with latest progress
          this.store.updateDocument(documentId, {
            status: data.status,
            progress: data.progress,                    // 📊 Real-time progress
            processing_stage: data.processing_stage,   // 🎯 Current stage
            processed_at: data.processed_at,
            raw_text: data.raw_text,                   // 📄 OCR results
            extracted_data: data.extracted_data,       // 🔬 Parsed health data
            ai_insights: data.ai_insights,             // 🤖 AI analysis
            error_message: data.error_message
          });

          // 🎯 Close connection when processing completes
          if (data.status === 'complete' || data.status === 'error') {
            console.log('🎯 Document processing completed:', data.status);
            this.disconnectSSE();
          }
        } catch (error) {
          console.error('🚨 Error parsing SSE message:', error);
        }
      };

      // ❌ Handle connection errors
      this.eventSource.onerror = (error: Event) => {
        console.error('❌ SSE connection error:', error);
        this.store.setConnectionStatus('disconnected');
      };

    } catch (error) {
      console.error('🚨 Failed to establish SSE connection:', error);
      this.store.setConnectionStatus('disconnected');
    }
  }
  
  // 🔌 Safely close SSE connection
  private disconnectSSE(): void {
    if (this.eventSource) {
      console.log('🔌 Closing SSE connection');
      this.eventSource.close();
      this.eventSource = null;
      this.store.setConnectionStatus('disconnected');
    }
  }
}

/* 🎓 SSE Learning Points for Junior Developers:
 * 1. EventSource provides one-way server-to-client communication
 * 2. Perfect for progress updates, notifications, live data
 * 3. Automatic reconnection on connection drops
 * 4. More efficient than polling for real-time updates
 * 5. Always clean up connections to prevent memory leaks
 * 6. Handle errors gracefully with fallback strategies
 */
```

## 10. 🏛️ Advanced Architecture

### 10.1 Q: Should I use Hexagonal Architecture in Angular?

**Hexagonal Architecture** (Ports and Adapters) can be beneficial for complex applications with multiple external dependencies.

```typescript
// Core domain (business logic)
export interface DocumentRepository {
  save(document: Document): Promise<void>;
  findById(id: string): Promise<Document | null>;
}

export interface DocumentProcessor {
  process(file: File): Promise<Document>;
}

// Application service (use cases)
export class DocumentService {
  constructor(
    private repository: DocumentRepository,
    private processor: DocumentProcessor
  ) {}
  
  async uploadAndProcess(file: File): Promise<Document> {
    const document = await this.processor.process(file);
    await this.repository.save(document);
    return document;
  }
}

// Infrastructure adapters
export class HttpDocumentRepository implements DocumentRepository {
  async save(document: Document): Promise<void> {
    await this.http.post('/api/documents', document).toPromise();
  }
  
  async findById(id: string): Promise<Document | null> {
    return this.http.get<Document>(`/api/documents/${id}`).toPromise();
  }
}
```

### 10.2 Q: How do I implement Domain-Driven Design patterns?

**Domain-Driven Design** helps organize complex business logic:

```typescript
// Value Objects
export class DocumentId {
  constructor(private readonly value: string) {
    if (!value || value.trim().length === 0) {
      throw new Error('DocumentId cannot be empty');
    }
  }
  
  toString(): string {
    return this.value;
  }
  
  equals(other: DocumentId): boolean {
    return this.value === other.value;
  }
}

// Entities
export class Document {
  constructor(
    private readonly id: DocumentId,
    private filename: string,
    private status: DocumentStatus = DocumentStatus.PENDING
  ) {}
  
  // Domain methods
  markAsProcessing(): void {
    if (this.status !== DocumentStatus.PENDING) {
      throw new Error('Can only process pending documents');
    }
    this.status = DocumentStatus.PROCESSING;
  }
  
  complete(analysis: AnalysisResult): void {
    if (this.status !== DocumentStatus.PROCESSING) {
      throw new Error('Can only complete processing documents');
    }
    this.analysis = analysis;
    this.status = DocumentStatus.COMPLETE;
  }
}

// Domain Services
export class DocumentDomainService {
  canProcess(document: Document, user: User): boolean {
    return user.hasPermission('PROCESS_DOCUMENTS') && 
           document.getStatus() === DocumentStatus.PENDING;
  }
}
```

## 11. 🧪 Testing

### 11.1 Q: What's the modern approach to Angular testing?

Focus on behavior over implementation, use signal-friendly testing patterns:

```typescript
describe('DocumentStore', () => {
  let store: DocumentStore;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    store = TestBed.inject(DocumentStore);
  });

  describe('document management', () => {
    it('should add document and update counts', () => {
      const document = createMockDocument();
      
      store.addDocument(document);
      
      expect(store.documents()).toContain(document);
      expect(store.documentCount()).toBe(1);
    });

    it('should filter documents by status', () => {
      const pendingDoc = createMockDocument({ status: 'pending' });
      const completeDoc = createMockDocument({ status: 'complete' });
      
      store.addDocument(pendingDoc);
      store.addDocument(completeDoc);
      
      expect(store.pendingDocuments()).toEqual([pendingDoc]);
      expect(store.completedDocuments()).toEqual([completeDoc]);
    });
  });
});

// Component testing with signals
describe('DocumentListComponent', () => {
  let component: DocumentListComponent;
  let mockStore: jasmine.SpyObj<DocumentStore>;

  beforeEach(() => {
    const storeSpy = jasmine.createSpyObj('DocumentStore', ['addDocument'], {
      documents: signal([]),
      documentCount: signal(0)
    });

    TestBed.configureTestingModule({
      imports: [DocumentListComponent],
      providers: [
        { provide: DocumentStore, useValue: storeSpy }
      ]
    });

    mockStore = TestBed.inject(DocumentStore) as jasmine.SpyObj<DocumentStore>;
    component = TestBed.createComponent(DocumentListComponent).componentInstance;
  });

  it('should display document count from store', () => {
    mockStore.documentCount.set(5);
    
    expect(component.displayCount()).toBe('5 documents');
  });
});
```

## 12. 🎨 Styling and UI

### 12.1 Q: Should I use separate SCSS files or inline styles?

**Use separate SCSS files for**:
- Complex component styles
- Shared mixins and variables
- Better IDE support and syntax highlighting

**Use inline styles for**:
- Simple components with minimal styling
- Dynamic styles based on component state
- Better component encapsulation

```typescript
// Separate SCSS file approach
@Component({
  selector: 'app-document-card',
  templateUrl: './document-card.component.html',
  styleUrls: ['./document-card.component.scss']  // External styles
})
export class DocumentCardComponent {
  status = input.required<DocumentStatus>();
}

// Inline styles approach
@Component({
  selector: 'app-status-badge',
  template: `
    <span [class]="badgeClasses()">
      {{ status() }}
    </span>
  `,
  styles: [`
    .badge {
      padding: 0.25rem 0.5rem;
      border-radius: 0.375rem;
      font-size: 0.875rem;
      font-weight: 500;
    }
    .success { background-color: #dcfce7; color: #166534; }
    .error { background-color: #fecaca; color: #991b1b; }
  `]
})
export class StatusBadgeComponent {
  status = input.required<'success' | 'error' | 'pending'>();
  
  badgeClasses = computed(() => [
    'badge',
    this.status()
  ].join(' '));
}
```

## 13. ⚡ Performance

### 13.1 Q: How do I optimize bundle size and loading?

**Lazy Loading and Code Splitting**:

```typescript
// Lazy load feature modules
const routes: Routes = [
  {
    path: 'documents',
    loadComponent: () => import('./features/documents/document-list.component')
      .then(m => m.DocumentListComponent)
  },
  {
    path: 'analysis',
    loadChildren: () => import('./features/analysis/analysis.routes')
      .then(m => m.analysisRoutes)
  }
];

// Tree-shaking optimizations
// ❌ Don't import entire libraries
import * as _ from 'lodash';

// ✅ Import only what you need
import { debounce } from 'lodash-es';

// Bundle analysis
// ng build --stats-json
// npx webpack-bundle-analyzer dist/stats.json
```

## 14. 📋 Summary

### 14.1 ✅ Essential Angular 19 Practices

- [ ] Use standalone components by default *(see upload-zone.component.ts)*
- [ ] Implement signal-based state management *(see document.store.ts)*
- [ ] Apply OnPush change detection strategy *(see data-table.component.ts)*
- [ ] Structure with feature-first organization *(see src/app/ structure)*
- [ ] Use typed reactive forms *(see models/document.model.ts)*
- [ ] Implement proper error handling *(see document-analysis.service.ts)*
- [ ] Add comprehensive testing *(see document-analysis.service.spec.ts)*
- [ ] Configure strict TypeScript mode *(see tsconfig.json)*
- [ ] Use lazy loading for routes *(see app routing)*
- [ ] Implement proper API layer separation *(see services/ folder)*

### 14.2 ✅ State Management Decision Tree

1. **Local component state** → Use signals
2. **Service-level state** → Use signal-based stores
3. **Complex global state** → Consider NgRx
4. **Simple global state** → Use signal-based stores with dependency injection

### 14.3 ✅ Performance Checklist

- [ ] OnPush change detection
- [ ] Lazy loading routes
- [ ] Virtual scrolling for large lists
- [ ] Proper bundle splitting
- [ ] Optimized imports (no barrel imports for large libs)
- [ ] Image optimization and lazy loading

## 15. 🔗 Related Files in This Codebase

**Key Implementation References:**
- `src/app/components/upload-zone/upload-zone.component.ts` - Complete file upload with signals
- `src/app/components/data-table/data-table.component.ts` - Advanced computed signals and filtering
- `src/app/services/document.store.ts` - Signal-based state management store
- `src/app/services/document-analysis.service.ts` - Business logic with SSE integration
- `src/app/services/document-api.service.ts` - Pure HTTP API service
- `src/app/models/document.model.ts` - TypeScript interfaces and types
- `backend/main.py` - FastAPI backend with SSE endpoints
- `backend/services/document_processor.py` - Agent-based document processing

**Architecture Documentation:**
- `memory-bank/systemPatterns.md` - System architecture patterns
- `memory-bank/techContext.md` - Technical decisions and context
- `CLAUDE.md` - Development guidance and commands

This FAQ provides a foundation for building production-ready Angular 19 applications with modern practices, clean architecture, and optimal performance, using real examples from this health document analyzer codebase.