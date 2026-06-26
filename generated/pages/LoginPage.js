// LoginPage.js - Page Object Model for the Sauce Demo Login Page

class LoginPage {
  constructor(page) {
    this.page = page;

    // Selectors using data-test attributes (preferred)
    this.usernameInput = page.locator('[data-test="username"]');
    this.passwordInput = page.locator('[data-test="password"]');
    this.loginButton = page.locator('[data-test="login-button"]');
    this.errorMessage = page.locator('[data-test="error"]');
    this.errorMessageContainer = page.locator('.error-message-container');
  }

  // Navigate to the login page
  async navigate() {
    await this.page.goto('https://www.saucedemo.com');
  }

  // Enter username in the username field
  async enterUsername(username) {
    await this.usernameInput.clear();
    await this.usernameInput.fill(username);
  }

  // Enter password in the password field
  async enterPassword(password) {
    await this.passwordInput.clear();
    await this.passwordInput.fill(password);
  }

  // Click the login button
  async clickLoginButton() {
    await this.loginButton.click();
  }

  // Complete login action with username and password
  async login(username, password) {
    await this.enterUsername(username);
    await this.enterPassword(password);
    await this.clickLoginButton();
  }

  // Get error message text
  async getErrorMessage() {
    return await this.errorMessage.textContent();
  }

  // Check if error message is visible
  async isErrorMessageVisible() {
    return await this.errorMessage.isVisible();
  }
}

module.exports = LoginPage;

