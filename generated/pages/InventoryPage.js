
const { expect } = require('@playwright/test');

class InventoryPage {
  constructor(page) {
    this.page = page;
    this.url = 'https://www.saucedemo.com/inventory.html';
    this.inventoryContainer = '[data-test="inventory-container"]';
    this.inventoryItems = '.inventory_item';
    this.inventoryItemName = '.inventory_item_name';
    this.inventoryItemPrice = '.inventory_item_price';
    this.inventoryItemDesc = '.inventory_item_desc';
    this.addToCartButton = '[data-test^="add-to-cart"]';
    this.removeButton = '[data-test^="remove"]';
    this.cartBadge = '.shopping_cart_badge';
    this.cartLink = '.shopping_cart_link';
    this.sortDropdown = '[data-test="product-sort-container"]';
    this.pageTitle = '.title';
    this.burgerMenu = '#react-burger-menu-btn';
    this.logoutLink = '#logout_sidebar_link';
    this.resetAppLink = '#reset_sidebar_link';
  }

  async navigate() {
    await this.page.goto(this.url);
  }

  async getInventoryItems() {
    return this.page.locator(this.inventoryItems);
  }

  async getItemCount() {
    return this.page.locator(this.inventoryItems).count();
  }

  async addItemToCartByIndex(index) {
    const buttons = this.page.locator(this.addToCartButton);
    await buttons.nth(index).click();
  }

  async addItemToCartByName(name) {
    const formattedName = name.toLowerCase().replace(/\s+/g, '-').replace(/[()]/g, '');
    await this.page.locator(`[data-test="add-to-cart-${formattedName}"]`).click();
  }

  async removeItemByName(name) {
    const formattedName = name.toLowerCase().replace(/\s+/g, '-').replace(/[()]/g, '');
    await this.page.locator(`[data-test="remove-${formattedName}"]`).click();
  }

  async getCartBadgeCount() {
    const badge = this.page.locator(this.cartBadge);
    const visible = await badge.isVisible();
    if (!visible) return 0;
    return parseInt(await badge.textContent(), 10);
  }

  async goToCart() {
    await this.page.locator(this.cartLink).click();
  }

  async sortBy(option) {
    await this.page.locator(this.sortDropdown).selectOption(option);
  }

  async getItemNames() {
    return this.page.locator(this.inventoryItemName).allTextContents();
  }

  async getItemPrices() {
    const priceTexts = await this.page.locator(this.inventoryItemPrice).allTextContents();
    return priceTexts.map(p => parseFloat(p.replace('$', '')));
  }

  async openBurgerMenu() {
    await this.page.locator(this.burgerMenu).click();
  }

  async logout() {
    await this.openBurgerMenu();
    await this.page.locator(this.logoutLink).click();
  }

  async resetApp() {
    await this.openBurgerMenu();
    await this.page.locator(this.resetAppLink).click();
  }

  async assertPageLoaded() {
    await expect(this.page.locator(this.pageTitle)).toHaveText('Products');
    await expect(this.page.locator(this.inventoryContainer)).toBeVisible();
  }

  async assertCartBadge(expectedCount) {
    if (expectedCount === 0) {
      await expect(this.page.locator(this.cartBadge)).not.toBeVisible();
    } else {
      await expect(this.page.locator(this.cartBadge)).toHaveText(String(expectedCount));
    }
  }
}

module.exports = InventoryPage;
