const { test, expect } = require('@playwright/test');
const LoginPage = require('../pages/LoginPage');
const InventoryPage = require('../pages/InventoryPage');
const testData = require('../test-data/test_data.json');

test.describe('Login Tests', () => {

  testData.valid_data.forEach((data) => {
    test(`Valid Login: ${data.description}`, 
    async ({ page }) => {
      const loginPage = new LoginPage(page);
      const inventoryPage = new InventoryPage(page);
      await loginPage.navigate();
      await loginPage.login(
        data.username, 
        data.password
      );
      await expect(page).toHaveURL(
        'https://www.saucedemo.com/inventory.html'
      );
      await expect(
        inventoryPage.inventoryContainer
      ).toBeVisible();
    });
  });

  testData.invalid_data.forEach((data) => {
    test(`Invalid Login: ${data.description}`, 
    async ({ page }) => {
      const loginPage = new LoginPage(page);
      await loginPage.navigate();
      await loginPage.login(
        data.username, 
        data.password
      );
      await expect(page).toHaveURL(
        'https://www.saucedemo.com/'
      );
      await expect(
        loginPage.errorMessage
      ).toBeVisible();
    });
  });

});