class LoginPage {
  constructor(page) {
    this.page = page;
    this.inputs = page.locator('input:visible');
    this.usernameInput = this.inputs.nth(0);
    this.passwordInput = this.inputs.nth(1);
    this.submitButton = page.locator('button[type="submit"]');
    this.errorMessages = page.locator('.oxd-alert-content, .oxd-input-field-error-message').first();
  }

  async navigateTo(url) {
    await this.page.goto(url);
    await this.page.waitForLoadState('domcontentloaded');
  }

  async fillInputByIndex(index, value) {
    await this.inputs.nth(index).waitFor({ state: 'visible', timeout: 10000 });
    await this.inputs.nth(index).fill(value);
  }

  async clickSubmit() {
    await this.submitButton.waitFor({ state: 'visible', timeout: 10000 });
    await this.submitButton.click();
  }

  async getErrorMessageByIndex(index) {
    return await this.errorMessages.textContent();
  }

  async isErrorVisibleByIndex(index) {
    return await this.errorMessages.isVisible();
  }
}

module.exports = LoginPage;
