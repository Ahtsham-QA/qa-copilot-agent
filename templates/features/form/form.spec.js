const { test, expect } = require('@playwright/test');
const FormPage = require('../pages/FormPage');
const testData = require('../test-data/test_data.json');

const APP_URL = process.env.APP_URL || 'https://example.com';

test.describe('Form - Valid Submission', () => {
  testData.valid_data.forEach((data) => {
    test(data.description, async ({ page }) => {
      const formPage = new FormPage(page);
      await formPage.navigateTo(APP_URL);
      let index = 0;
      for (const value of Object.values(data.fields)) {
        await formPage.fillInputByIndex(index, value);
        index++;
      }
      await formPage.submitForm();
      await page.waitForTimeout(2000);
      const success = await formPage.isSuccessVisible();
      expect(success).toBeTruthy();
    });
  });
});

test.describe('Form - Invalid Submission', () => {
  testData.invalid_data.forEach((data) => {
    test(data.description, async ({ page }) => {
      const formPage = new FormPage(page);
      await formPage.navigateTo(APP_URL);
      if (data.fields) {
        let index = 0;
        for (const value of Object.values(data.fields)) {
          await formPage.fillInputByIndex(index, value);
          index++;
        }
      }
      await formPage.submitForm();
      await page.waitForTimeout(1000);
      const hasError = await formPage.isErrorVisible();
      expect(hasError).toBeTruthy();
    });
  });
});

test.describe('Form - Edge Cases', () => {
  testData.edge_cases.forEach((data) => {
    test(data.description, async ({ page }) => {
      const formPage = new FormPage(page);
      await formPage.navigateTo(APP_URL);
      if (data.fields) {
        let index = 0;
        for (const value of Object.values(data.fields)) {
          await formPage.fillInputByIndex(index, value);
          index++;
        }
      }
      await formPage.submitForm();
      await page.waitForTimeout(1000);
      await expect(page).toHaveURL(new RegExp(APP_URL.replace('https://', '')));
    });
  });
});
