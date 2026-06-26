class InventoryPage {
  constructor(page) {
    this.page = page;
    this.inventoryContainer = page.locator('[data-test="inventory-container"]');
    this.pageTitle = page.locator('.title');
    this.shoppingCartLink = page.locator('[data-test="shopping-cart-link"]');
    this.appLogo = page.locator('.app_logo');
  }

  async isLoaded() {
    return await this.inventoryContainer.isVisible();
  }
}

module.exports = InventoryPage;