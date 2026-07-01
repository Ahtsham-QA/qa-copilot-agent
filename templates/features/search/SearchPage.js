class SearchPage {
  constructor(page) {
    this.page = page;
    this.searchInput = page.locator(
      'input[type="search"], input[name="search"], input[name="q"], input[placeholder*="search" i], input[placeholder*="find" i], input[placeholder*="type" i], #search, .search-input, #searchProduct, input[id*="search" i]'
    ).first();
    this.searchButton = page.locator(
      'button[type="submit"], button:has-text("Search"), button:has-text("Find"), [aria-label*="search" i], #searchBtn, button[id*="search" i]'
    ).first();
    this.searchResults = page.locator(
      '.results, .search-results, [class*="result"], [data-test*="result"], .product-list, .features_items, ul.results, #results'
    ).first();
    this.noResultsMessage = page.locator(
      '[class*="no-result"], [class*="empty"], .no-products'
    ).first();
  }

  async navigateTo(url) {
    await this.page.goto(url);
    await this.page.waitForLoadState('domcontentloaded');
  }

  async search(query) {
    await this.searchInput.waitFor({ state: 'visible', timeout: 15000 });
    await this.searchInput.fill(query);
    await this.searchButton.waitFor({ state: 'visible', timeout: 10000 });
    await this.searchButton.click();
    await this.page.waitForTimeout(2000);
  }

  async areResultsVisible() {
    try {
      await this.searchResults.waitFor({ state: 'visible', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  async isNoResultsVisible() {
    try {
      return await this.noResultsMessage.isVisible();
    } catch {
      return false;
    }
  }
}

module.exports = SearchPage;
