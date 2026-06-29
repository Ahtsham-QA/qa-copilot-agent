const { test, expect } = require('@playwright/test');
const LoginPage = require('../pages/LoginPage');
const InventoryPage = require('../pages/InventoryPage');
const testData = require('../test-data/test_data.json');

const APP_URL = 'https://www.saucedemo.com';

test.describe('Login - Valid Credentials', () => {
  testData.valid_data.forEach((data) => {
    test(data.description, async ({ page }) => {
      const loginPage = new LoginPage(page);
      const inventoryPage = new InventoryPage(page);
      await loginPage.navigateTo(APP_URL);
      await loginPage.fillInputByIndex(0, data.username);
      await loginPage.fillInputByIndex(1, data.password);
      await loginPage.clickSubmit();
      await expect(inventoryPage.inventoryContainer).toBeVisible();
    });
  });
});

test.describe('Login - Invalid Credentials', () => {
  testData.invalid_data.forEach((data) => {
    test(data.description, async ({ page }) => {
      const loginPage = new LoginPage(page);
      await loginPage.navigateTo(APP_URL);
      await loginPage.fillInputByIndex(0, data.username);
      await loginPage.fillInputByIndex(1, data.password);
      await loginPage.clickSubmit();
      await expect(page).toHaveURL(APP_URL);
    });
  });
});

test.describe('Login - Edge Cases', () => {
  testData.edge_cases.forEach((data) => {
    test(data.description, async ({ page }) => {
      const loginPage = new LoginPage(page);
      await loginPage.navigateTo(APP_URL);
      await loginPage.fillInputByIndex(0, data.username);
      await loginPage.fillInputByIndex(1, data.password);
      await loginPage.clickSubmit();
      await expect(page).toHaveURL(APP_URL);
    });
  });
});
