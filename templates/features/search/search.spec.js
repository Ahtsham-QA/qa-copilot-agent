const { test, expect } = require('@playwright/test');
const SearchPage = require('../pages/SearchPage');
const testData = require('../test-data/test_data.json');

const APP_URL = process.env.APP_URL || 'https://example.com';

test.describe('Search - Valid Queries', () => {
  testData.valid_data.forEach((data) => {
    test(data.description, async ({ page }) => {
      const searchPage = new SearchPage(page);
      await searchPage.navigateTo(APP_URL);
      await searchPage.search(data.query);
      await page.waitForTimeout(1000);
      const hasResults = await searchPage.areResultsVisible();
      expect(hasResults).toBeTruthy();
    });
  });
});

test.describe('Search - No Results', () => {
  testData.invalid_data.forEach((data) => {
    test(data.description, async ({ page }) => {
      const searchPage = new SearchPage(page);
      await searchPage.navigateTo(APP_URL);
      await searchPage.search(data.query);
      await page.waitForTimeout(1000);
      await expect(page).toHaveURL(new RegExp(APP_URL.replace('https://', '')));
    });
  });
});

test.describe('Search - Edge Cases', () => {
  testData.edge_cases.forEach((data) => {
    test(data.description, async ({ page }) => {
      const searchPage = new SearchPage(page);
      await searchPage.navigateTo(APP_URL);
      await searchPage.search(data.query);
      await page.waitForTimeout(1000);
      await expect(page).toHaveURL(new RegExp(APP_URL.replace('https://', '')));
    });
  });
});
