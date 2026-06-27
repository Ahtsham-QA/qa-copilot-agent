class LoginPage {
  constructor(page) {
    this.page = page;
    this.inputs = page.locator('input:visible');
    this.submitButton = page.locator(
      'button[type="submit"], input[type="submit"]'
    ).first();
    this.errorMessages = page.locator(
      '[class*="error"], [class*="alert"], .alert-danger'
    );
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
}

module.exports = LoginPage;
