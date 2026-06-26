```javascript
const { test, expect } = require('@playwright/test');

// Page Object Model for SauceDemo Login Page
class LoginPage {
  constructor(page) {
    this.page = page;
    this.usernameInput = page.locator('[data-test="username"]');
    this.passwordInput = page.locator('[data-test="password"]');
    this.loginButton = page.locator('[data-test="login-button"]');
    this.errorMessage = page.locator('[data-test="error"]');
  }

  async navigate() {
    await this.page.goto('https://www.saucedemo.com');
  }

  async enterUsername(username) {
    await this.usernameInput.fill(username);
  }

  async enterPassword(password) {
    await this.passwordInput.fill(password);
  }

  async clickLoginButton() {
    await this.loginButton.click();
  }

  async login(username, password) {
    await this.enterUsername(username);
    await this.enterPassword(password);
    await this.clickLoginButton();
  }

  async getErrorMessage() {
    return await this.errorMessage.textContent();
  }
}

// Page Object Model for SauceDemo Inventory/Dashboard Page
class InventoryPage {
  constructor(page) {
    this.page = page;
    this.inventoryContainer = page.locator('[data-test="inventory-container"]');
    this.appLogo = page.locator('.app_logo');
    this.shoppingCartLink = page.locator('[data-test="shopping-cart-link"]');
  }

  async isLoaded() {
    return await this.inventoryContainer.isVisible();
  }
}

test.describe('SauceDemo Login Tests', () => {
  let loginPage;
  let inventoryPage;

  // Note: SauceDemo uses predefined usernames (not email addresses).
  // The valid credentials for this site are username: 'standard_user', password: 'secret_sauce'.
  // The test cases below adapt the user story to the actual SauceDemo application behavior.

  beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    inventoryPage = new InventoryPage(page);
    // Navigate to the login page before each test
    await loginPage.navigate();
  });

  // TEST CASE 1: Successful Login with Valid Credentials
  // Verifies that a user with valid credentials can log in and is redirected to the inventory page
  test('TC01 - Successful Login with Valid Credentials', async ({ page }) => {
    // SauceDemo uses predefined usernames; mapping valid credentials to site-specific ones
    const validUsername = 'standard_user';
    const validPassword = 'secret_sauce';

    // Enter valid username and password, then click login
    await loginPage.login(validUsername, validPassword);

    // Assert user is redirected to the inventory/dashboard page
    await expect(page).toHaveURL('https://www.saucedemo.com/inventory.html');

    // Assert that the inventory container is visible (dashboard loaded)
    await expect(inventoryPage.inventoryContainer).toBeVisible();

    // Assert the app logo is visible indicating successful login
    await expect(inventoryPage.appLogo).toBeVisible();

    // Assert the shopping cart icon is visible
    await expect(inventoryPage.shoppingCartLink).toBeVisible();
  });

  // TEST CASE 2: Login Fails with Incorrect Password
  // Verifies that login is rejected when an incorrect password is provided
  test('TC02 - Login Fails with Incorrect Password', async ({ page }) => {
    const username = 'standard_user';
    const wrongPassword = 'WrongPass@999';

    // Enter valid username but wrong password, then click login
    await loginPage.login(username, wrongPassword);

    // Assert user remains on the login page
    await expect(page).toHaveURL('https://www.saucedemo.com/');

    // Assert error message is visible
    await expect(loginPage.errorMessage).toBeVisible();

    // Assert the error message contains relevant text about invalid credentials
    const errorText = await loginPage.getErrorMessage();
    expect(errorText).toContain('Username and password do not match');
  });

  // TEST CASE 3: Login Fails with Unregistered/Invalid Username
  // Verifies that login is rejected when a username that does not exist is used
  test('TC03 - Login Fails with Unregistered Username', async ({ page }) => {
    const unregisteredUsername = 'ghost.user@outlook.com';
    const password = 'SecurePass@123';

    // Enter unregistered username and a password, then click login
    await loginPage.login(unregisteredUsername, password);

    // Assert user remains on the login page
    await expect(page).toHaveURL('https://www.saucedemo.com/');

    // Assert error message is visible
    await expect(loginPage.errorMessage).toBeVisible();

    // Assert the error message indicates the credentials are not recognized
    const errorText = await loginPage.getErrorMessage();
    expect(errorText).toContain('Username and password do not match');
  });

  // TEST CASE 4: Login Fails with Empty Credentials
  // Verifies that validation errors are shown when both fields are left empty
  test('TC04 - Login Fails with Empty Credentials', async ({ page }) => {
    // Leave both fields empty and click the login button
    await loginPage.clickLoginButton();

    // Assert user remains on the login page
    await expect(page).toHaveURL('https://www.saucedemo.com/');

    // Assert error message is visible
    await expect(loginPage.errorMessage).toBeVisible();

    // Assert the error message indicates username is required
    const errorText = await loginPage.getErrorMessage();
    expect(errorText).toContain('Username is required');

    // Assert the inventory page is NOT loaded (login was not attempted)
    await expect(inventoryPage.inventoryContainer).not.toBeVisible();
  });

  // TEST CASE 5: Login with Password Case Sensitivity Check
  // Verifies that the password field is case-sensitive
  test('TC05 - Login Fails with Wrong Password Case', async ({ page }) => {
    const username = 'standard_user';
    // Using lowercase version of the correct password 'secret_sauce'
    const wrongCasePassword = 'SECRET_SAUCE';

    // Enter valid username but wrong-case password, then click login
    await loginPage.login(username, wrongCasePassword);

    // Assert user remains on the login page (password is case-sensitive)
    await expect(page).toHaveURL('https://www.saucedemo.com/');

    // Assert error message is visible confirming case-sensitive rejection
    await expect(loginPage.errorMessage).toBeVisible();

    // Assert the error message confirms credentials mismatch
    const errorText = await loginPage.getErrorMessage();
    expect(errorText).toContain('Username and password do not match');
  });

  // TEST CASE 6: Login with Leading and Trailing Spaces in Username
  // Verifies that the app handles leading/trailing spaces in the username field
  test('TC06 - Login with Leading and Trailing Spaces in Username', async ({ page }) => {
    // Username with leading and trailing spaces
    const usernameWithSpaces = '  standard_user  ';
    const validPassword = 'secret_sauce';

    // Enter username with spaces and valid password
    await loginPage.enterUsername(usernameWithSpaces);
    await loginPage.enterPassword(validPassword);
    await loginPage.clickLoginButton();

    // The application may or may not trim spaces
    // Check if it either logs in successfully (trimmed spaces) or shows an error (not trimmed)
    const currentUrl = page.url();

    if (currentUrl.includes('inventory.html')) {
      // Application trimmed the spaces and logged in successfully
      await expect(inventoryPage.inventoryContainer).toBeVisible();
      console.log('Application trimmed leading/trailing spaces and logged in successfully.');
    } else {
      // Application did NOT trim spaces — it should show a clear validation/error message
      await expect(page).toHaveURL('https://www.saucedemo.com/');
      await expect(loginPage.errorMessage).toBeVisible();

      const errorText = await loginPage.getErrorMessage();
      // Ensure there is meaningful feedback and not a silent failure
      expect(errorText.length).toBeGreaterThan(0);
      console.log(`Application rejected spaces with error: ${errorText}`);
    }
  });

  // TEST CASE 7: Login Page Masks Password Input
  // Verifies that the password field masks input characters for security
  test('TC07 - Login Page Masks Password Input', async ({ page }) => {
    const password = 'SecurePass@123';

    // Click on the password field and type the password
    await loginPage.passwordInput.click();
    await loginPage.passwordInput.fill(password);

    // Assert that the input type is 'password', which ensures characters are masked
    const inputType = await loginPage.passwordInput.getAttribute('type');
    expect(inputType).toBe('password');

    // Assert the password value is not exposed as plain text in the DOM attribute
    const inputValue = await loginPage.passwordInput.inputValue();
    // The value should match what was typed, but the type='password' ensures it's visually masked
    expect(inputValue).toBe(password);

    // Double-check: the field should NOT have type="text" which would expose the password
    expect(inputType).not.toBe('text');
  });
});
```