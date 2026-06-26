
const { expect } = require('@playwright/test');

class LoginPage {
  constructor(page) {
    this.page = page;
    this.url = 'https://www.saucedemo.com';
    this.usernameInput = '[data-test="username"]';
    this.passwordInput = '[data-test="password"]';
    this.loginButton = '[data-test="login-button"]';
    this.errorMessage = '[data-test="error"]';
    this.inventoryContainer = '[data-test="inventory-container"]';
  }

  async navigate() {
    await this.page.goto(this.url);
  }

  async fillUsername(username) {
    await this.page.fill(this.usernameInput, username);
  }

  async fillPassword(password) {
    await this.page.fill(this.passwordInput, password);
  }

  async clickLogin() {
    await this.page.click(this.loginButton);
  }

  async login(username, password) {
    await this.fillUsername(username);
    await this.fillPassword(password);
    await this.clickLogin();
  }

  async getErrorMessage() {
    return await this.page.textContent(this.errorMessage);
  }

  async assertLoggedIn() {
    await expect(this.page).toHaveURL(/inventory/);
    await expect(this.page.locator(this.inventoryContainer)).toBeVisible();
  }

  async assertErrorVisible(expectedText) {
    await expect(this.page.locator(this.errorMessage)).toBeVisible();
    if (expectedText) {
      await expect(this.page.locator(this.errorMessage)).toContainText(expectedText);
    }
  }
}

module.exports = LoginPage;
