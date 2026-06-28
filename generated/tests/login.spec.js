const { test, expect } = require('@playwright/test');
const LoginPage = require('../pages/LoginPage');
const InventoryPage = require('../pages/InventoryPage');
const testData = require('../test-data/test_data.json');

const APP_URL = 'https://www.saucedemo.com';
const LOGIN_URL = `${APP_URL}/login`;

test.describe('Positive Login Tests', () => {
  testData.valid_data.slice(0, 3).forEach((data) => {
    test(data.description, async ({ page }) => {
      const loginPage = new LoginPage(page);
      const inventoryPage = new InventoryPage(page);

      await loginPage.navigateTo(LOGIN_URL);
      await loginPage.fillInputByIndex(0, data.username);
      await loginPage.fillInputByIndex(1, data.password);
      await loginPage.clickSubmit();

      await expect(page).toHaveURL(new RegExp(APP_URL));
      await expect(inventoryPage.inventoryContainer).toBeVisible();
    });
  });
});

test.describe('Negative Login Tests', () => {
  testData.invalid_data.slice(0, 3).forEach((data) => {
    test(data.description, async ({ page }) => {
      const loginPage = new LoginPage(page);

      await loginPage.navigateTo(LOGIN_URL);
      await loginPage.fillInputByIndex(0, data.username);
      await loginPage.fillInputByIndex(1, data.password);
      await loginPage.clickSubmit();

      const isErrorVisible = await loginPage.isErrorVisibleByIndex(0);
      expect(isErrorVisible).toBe(true);

      const errorMessage = await loginPage.getErrorMessageByIndex(0);
      expect(errorMessage).toContain(data.expected_error);
    });
  });
});

test.describe('Edge Case Login Tests', () => {
  test('Password Field Masks Entered Characters', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.navigateTo(LOGIN_URL);
    await loginPage.fillInputByIndex(1, 'John@1234');

    const passwordInput = page.locator('input[type="password"]').nth(0);
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('Login Fails with SQL Injection in Email Field', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.navigateTo(LOGIN_URL);
    await loginPage.fillInputByIndex(0, "' OR '1'='1' --");
    await loginPage.fillInputByIndex(1, 'anypassword1');
    await loginPage.clickSubmit();

    const isErrorVisible = await loginPage.isErrorVisibleByIndex(0);
    expect(isErrorVisible).toBe(true);

    await expect(page).not.toHaveURL(new RegExp(`${APP_URL}/inventory`));
  });

  test('Login Fails After Multiple Consecutive Failed Attempts', async ({ page }) => {
    const loginPage = new LoginPage(page);

    await loginPage.navigateTo(LOGIN_URL);

    for (let i = 0; i < 5; i++) {
      await loginPage.fillInputByIndex(0, 'john.doe@gmail.com');
      await loginPage.fillInputByIndex(1, 'WrongPass@11');
      await loginPage.clickSubmit();
    }

    const isErrorVisible = await loginPage.isErrorVisibleByIndex(0);
    expect(isErrorVisible).toBe(true);

    const errorMessage = await loginPage.getErrorMessageByIndex(0);
    const isLockedOrRejected =
      errorMessage.toLowerCase().includes('locked') ||
      errorMessage.toLowerCase().includes('too many') ||
      errorMessage.toLowerCase().includes('epic sadface') ||
      errorMessage.toLowerCase().includes('sorry') ||
      errorMessage.toLowerCase().includes('invalid');

    expect(isLockedOrRejected).toBe(true);
  });
});