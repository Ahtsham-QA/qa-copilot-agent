class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.getByRole('textbox').first();
    this.passwordInput = page.locator('input[type="password"]');
    this.submitButton = page.getByRole('button').first();
    this.errorMessages = page.locator(
      '[data-test="error"], .error, [class*="error"], [role="alert"]'
    );
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
    return await this.errorMessages.nth(index).textContent();
  }

  async isErrorVisibleByIndex(index) {
    return await this.errorMessages.nth(index).isVisible();
  }
}

module.exports = LoginPage;
