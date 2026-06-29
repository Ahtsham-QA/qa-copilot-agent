class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('input[type="text"], input[type="email"], #user-name, #email, input[name="username"]').first();
    this.passwordInput = page.locator('input[type="password"]').first();
    this.submitButton = page.locator('button[type="submit"], input[type="submit"], #login-button, button:has-text("Login"), button:has-text("Sign in")').first();
    this.errorMessages = page.locator('[data-test="error"], .error, [class*="error"], [role="alert"], .alert-danger').first();
  }

  async navigateTo(url) {
    await this.page.goto(url);
    await this.page.waitForLoadState('networkidle');
  }

  async fillInputByIndex(index, value) {
    if (index === 0) {
      await this.usernameInput.waitFor({ state: 'visible' });
      await this.usernameInput.fill(value);
    } else {
      await this.passwordInput.waitFor({ state: 'visible' });
      await this.passwordInput.fill(value);
    }
  }

  async clickSubmit() {
    await this.submitButton.waitFor({ state: 'visible' });
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
