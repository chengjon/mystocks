describe('MyStocks E2E Tests', () => {
  const baseUrl = Cypress.env('baseUrl') || 'http://localhost:3000';

  beforeEach(() => {
    cy.visit(baseUrl);
    // Wait for app to be ready
    cy.contains('MyStocks').should('be.visible');
  });

  /**
   * Test 1: Basic Navigation and Landing Page
   */
  it('should load the homepage successfully', () => {
    cy.title().should('include', 'MyStocks - 量化交易数据管理系统');
    cy.get('[data-testid="main-nav"]').should('be.visible');
  });

  /**
   * Test 2: Login Flow
   */
  it('should handle user login', () => {
    cy.get('[data-testid="login-button"]').click();
    cy.get('[data-testid="username-input"]').type('admin');
    cy.get('[data-testid="password-input"]').type('admin123');
    cy.get('[data-testid="submit-button"]').click();
    cy.url().should('include', '/dashboard');
  });

  /**
   * Test 3: Market Data Display
   */
  it('should display market data', () => {
    cy.get('[data-testid="market-data-section"]').should('be.visible');
    // Wait for data to load
    cy.get('[data-testid="stock-table"]').should('have.length.greaterThan', 0);
  });

  /**
   * Test 4: Responsive Design
   */
  context('Responsive Design', () => {
    const viewports = [
      { width: 1920, height: 1080 },  // Desktop
      { width: 1366, height: 768 },   // Tablet
      { width: 1280, height: 720 },   // Small Tablet
    ];

    viewports.forEach((viewport) => {
      it(`should render correctly on ${viewport.width}x${viewport.height}`, () => {
        cy.viewport(viewport.width, viewport.height);
        cy.get('[data-testid="main-layout"]').should('be.visible');
        cy.get('[data-testid="main-layout"]').should('have.css', 'width').and('have.css', 'height');
      });
    });
  });

  /**
   * Test 5: API Error Handling
   */
  it('should handle API errors gracefully', () => {
    // Mock API failure
    cy.intercept('GET', '**/api/market/**', { statusCode: 500 }).as('apiError');
    cy.get('[data-testid="refresh-button"]').click();
    cy.contains('Network Error').should('be.visible');
  });

  /**
   * Test 6: Performance Metrics
   */
  it('should load within performance budget', () => {
    const startTime = Date.now();
    cy.visit(baseUrl);
    cy.window().then((win) => {
      const loadTime = Date.now() - startTime;
      expect(loadTime).to.be.lessThan(3000); // 3 seconds budget
    });
  });
});
