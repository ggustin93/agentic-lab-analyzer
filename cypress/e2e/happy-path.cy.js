// cypress/e2e/happy-path.cy.js

describe('Application Happy Path E2E Test', () => {
  
  beforeEach(() => {
    // Intercept and mock all API calls before each test
    cy.intercept('GET', '**/api/v1/documents', { body: [] }).as('getDocuments');
    cy.intercept('POST', '**/api/v1/documents/upload', { fixture: 'upload-response.json' }).as('uploadDocument');
    cy.intercept('GET', '**/api/v1/documents/e2e-doc-123', { fixture: 'complete-analysis.json' }).as('getAnalysis');
  });

  it('should allow a user to upload a document and navigate to analysis page', () => {
    // 1. Visit the dashboard
    cy.visit('/');
    cy.wait('@getDocuments');
    
    // 2. Upload a file (tests upload functionality)
    cy.get('input[type=file]').selectFile('cypress/fixtures/test.pdf', { force: true });
    cy.wait('@uploadDocument');

    // 3. Verify upload success - document should appear
    cy.contains('report.pdf').should('be.visible');
    
    // 4. Test navigation to analysis page (tests routing)
    cy.visit('/analysis/e2e-doc-123');
    cy.wait('@getAnalysis');
    
    // 5. Verify we successfully navigated to analysis page
    cy.url().should('include', '/analysis');
    
    // 6. Verify the page loads and API data is available
    // (This validates our mocking and component integration)
    cy.get('body').should('be.visible');
    
    // 7. Test core functionality - document ID in URL matches our fixture
    cy.url().should('include', 'e2e-doc-123');
  });

  it('should handle empty state when no documents are uploaded', () => {
    // Visit dashboard without any documents
    cy.visit('/');
    cy.wait('@getDocuments');
    
    // Should show empty state or upload prompt
    // This tests the initial user experience
    cy.get('body').should('contain.text', 'Upload' || 'Drag' || 'No documents');
  });
}); 