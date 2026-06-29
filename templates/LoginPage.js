class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('#user-name, input[type="text"], input[type="email"]').first();
    this.passwordInput = page.locator('#password, input[type="password"]').first();
    this.submitButton = page.locator('#login-button, button[type="submit"], input[type="submit"]').first();
    this.errorMessages = page.locator('[data-test="error"], [role="alert"], .error').first();
  }

  async navigateTo(url) {
    await this.page.goto(url);
    await this.page.waitForLoadState('domcontentloaded');
  }

  async fillInputByIndex(index, value) {
    if (index === 0) {
      await this.usernameInput.waitFor({ state: 'visible', timeout: 10000 });
      await this.usernameInput.fill(value);
    } else {
      await this.passwordInput.waitFor({ state: 'visible', timeout: 10000 });
      await this.passwordInput.fill(value);
    }
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
