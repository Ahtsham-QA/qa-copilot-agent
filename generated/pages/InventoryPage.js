class InventoryPage {
  constructor(page) {
    this.page = page;
    this.inventoryContainer = page.locator('.inventory_list');
    this.pageTitle = page.locator('.title');
    this.cartBadge = page.locator('.shopping_cart_badge');
    this.cartLink = page.locator('.shopping_cart_link');
  }

  async isLoaded() {
    return await this.inventoryContainer.isVisible();
  }
}

module.exports = InventoryPage;
