class InventoryPage {
  constructor(page) {
    this.page = page;
    this.productCards = page.locator('.product-image-wrapper');
    this.addToCartButtons = page.locator('[class*="add-to-cart"]');
    this.productTitles = page.locator('.productinfo h2');
    this.productPrices = page.locator('.productinfo h2').locator('..').locator('p');
    this.viewProductButtons = page.locator('a[href*="/product_details/"]');
    this.inputs = page.locator('input');
    this.submitButtons = page.locator('[type="submit"]');
    this.errorMessages = page.locator('.error-message, [class*="error"], .alert');
    this.formFields = page.locator('input, textarea, select');
    this.modalButtons = page.locator('.modal-footer button, .modal-body a');
  }

  async navigateTo(url) {
    await this.page.goto(url);
  }

  async addItemByIndex(index) {
    await this.productCards.nth(index).hover();
    await this.addToCartButtons.nth(index).click();
  }

  async viewProductByIndex(index) {
    await this.viewProductButtons.nth(index).click();
  }

  async fillInputByIndex(index, value) {
    await this.formFields.nth(index).fill(value);
  }

  async clickSubmit() {
    await this.submitButtons.first().click();
  }

  async getErrorMessageByIndex(index) {
    return await this.errorMessages.nth(index).textContent();
  }

  async isErrorVisibleByIndex(index) {
    return await this.errorMessages.nth(index).isVisible();
  }

  async clickModalButtonByIndex(index) {
    await this.modalButtons.nth(index).click();
  }
}

module.exports = InventoryPage;