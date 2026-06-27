const { test, expect } = require('@playwright/test');
const LoginPage = require('../pages/LoginPage');
const testData = require('../test-data/test_data.json');

const APP_URL = 'https://automationexercise.com';
const LOGIN_URL = `${APP_URL}/login`;

test.describe('Login - Valid Credentials', () => {
  testData.valid_data.forEach((data) => {
    test(data.description, async ({ page }) => {
      const loginPage = new LoginPage(page);
      await loginPage.navigateTo(LOGIN_URL);
      await loginPage.fillInputByIndex(0, data.username);
      await loginPage.fillInputByIndex(1, data.password);
      await loginPage.clickSubmit();
      await expect(page).not.toHaveURL(LOGIN_URL);
    });
  });
});

test.describe('Login - Invalid Credentials', () => {
  testData.invalid_data.forEach((data) => {
    test(data.description, async ({ page }) => {
      const loginPage = new LoginPage(page);
      await loginPage.navigateTo(LOGIN_URL);
      await loginPage.fillInputByIndex(0, data.username);
      await loginPage.fillInputByIndex(1, data.password);
      await loginPage.clickSubmit();
      await expect(page).toHaveURL(LOGIN_URL);
    });
  });
});

test.describe('Login - Edge Cases', () => {
  testData.edge_cases.forEach((data) => {
    test(data.description, async ({ page }) => {
      const loginPage = new LoginPage(page);
      await loginPage.navigateTo(LOGIN_URL);
      await loginPage.fillInputByIndex(0, data.username);
      await loginPage.fillInputByIndex(1, data.password);
      await loginPage.clickSubmit();
      await expect(page).toHaveURL(LOGIN_URL);
    });
  });
});
