class LoginPage {
  constructor(page) {
    this.page = page;
    this.inputs = page.locator('input:visible');
    this.submitButton = page.locator('[type="submit"]');
    this.errorMessages = page.locator('[data-test*="error"]');
    this.errorIcons = page.locator('.error-message-container');
    this.formContainer = page.locator('form');
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
    return await this.errorMessages.nth(index).innerText();
  }

  async isErrorVisibleByIndex(index) {
    return await this.errorMessages.nth(index).isVisible();
  }

  async getInputCount() {
    return await this.inputs.count();
  }

  async getPageTitle() {
    return await this.page.title();
  }
}

module.exports = LoginPage;