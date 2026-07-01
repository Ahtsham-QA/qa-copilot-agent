const { test, expect } = require('@playwright/test');
const CartPage = require('../pages/CartPage');
const testData = require('../test-data/test_data.json');

const APP_URL = process.env.APP_URL || 'https://example.com';

test.describe('Cart - Add Items', () => {
  testData.valid_data.forEach((data) => {
    test(data.description, async ({ page }) => {
      const cartPage = new CartPage(page);
      await cartPage.navigateTo(APP_URL);
      await cartPage.addItemByIndex(data.item_index || 0);
      await page.waitForTimeout(1000);
      const count = await cartPage.getCartCount();
      expect(parseInt(count) || 0).toBeGreaterThan(0);
    });
  });
});

test.describe('Cart - Remove Items', () => {
  testData.invalid_data.forEach((data) => {
    test(data.description, async ({ page }) => {
      const cartPage = new CartPage(page);
      await cartPage.navigateTo(APP_URL);
      await cartPage.addItemByIndex(0);
      await cartPage.openCart();
      await cartPage.removeItemByIndex(0);
      await page.waitForTimeout(1000);
      const itemCount = await cartPage.getCartItemCount();
      expect(itemCount).toBe(0);
    });
  });
});

test.describe('Cart - Edge Cases', () => {
  testData.edge_cases.forEach((data) => {
    test(data.description, async ({ page }) => {
      const cartPage = new CartPage(page);
      await cartPage.navigateTo(APP_URL);
      await cartPage.addItemByIndex(0);
      await cartPage.addItemByIndex(0);
      await page.waitForTimeout(1000);
      const count = await cartPage.getCartCount();
      expect(parseInt(count) || 0).toBeGreaterThan(0);
    });
  });
});
