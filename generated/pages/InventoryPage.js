const { expect } = require('@playwright/test');

class InventoryPage {
  constructor(page) {
    this.page = page;
    this.inputs = page.locator('input:visible');
    this.addToCartButtons = page.locator('[data-test^="add-to-cart"]');
    this.removeButtons = page.locator('[data-test^="remove"]');
    this.inventoryItems = page.locator('.inventory_item');
    this.itemPrices = page.locator('.inventory_item_price');
    this.itemNames = page.locator('.inventory_item_name');
    this.sortDropdown = page.locator('[data-test="product_sort_container"]');
    this.cartIcon = page.locator('.shopping_cart_link');
    this.errorMessages = page.locator('[data-test="error"]');
    this.submitButton = page.locator('[type="submit"]');
  }

  async navigateTo(url) {
    await this.page.goto(url);
  }

  async fillInputByIndex(index, value) {
    await this.inputs.nth(index).fill(value);
  }

  async clickSubmit() {
    await this.submitButton.click();
  }

  async getErrorMessageByIndex(index) {
    return await this.errorMessages.nth(index).textContent();
  }

  async isErrorVisibleByIndex(index) {
    return await this.errorMessages.nth(index).isVisible();
  }

  async addItemByIndex(index) {
    await this.addToCartButtons.nth(index).click();
  }

  async removeItemByIndex(index) {
    await this.removeButtons.nth(index).click();
  }

  async sortItemsBy(value) {
    await this.sortDropdown.selectOption(value);
  }
}

module.exports = InventoryPage;