class InventoryPage {
  constructor(page) {
    this.page = page;
    this.inventoryContainer = page.locator('.inventory_list').first();
    this.pageTitle = page.locator('.title').first();
    this.cartBadge = page.locator('.shopping_cart_badge').first();
  }

  async isLoaded() {
    await this.inventoryContainer.waitFor({ state: 'visible' });
    return true;
  }
}

module.exports = InventoryPage;
