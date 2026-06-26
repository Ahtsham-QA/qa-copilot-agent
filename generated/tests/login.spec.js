
const { test, expect } = require('@playwright/test');
const LoginPage = require('../pages/LoginPage');

test.describe('Add Items to Cart', () => {

  test.beforeEach(async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.navigate();
    await loginPage.login('standard_user', 'secret_sauce');
  });

  test('TC1: Add two items and verify cart count', 
  async ({ page }) => {
    const addButtons = page.locator('[data-test^="add-to-cart"]');
    
    await addButtons.first().click();
    await expect(
      page.locator('.shopping_cart_badge')
    ).toHaveText('1');
    
    await addButtons.first().click();
    await expect(
      page.locator('.shopping_cart_badge')
    ).toHaveText('2');
    
    await page.locator('.shopping_cart_link').click();
    await expect(page).toHaveURL(
      'https://www.saucedemo.com/cart.html'
    );
    await expect(
      page.locator('.cart_item')
    ).toHaveCount(2);
  });

  test('TC2: Verify correct items in cart', 
  async ({ page }) => {
    const addButtons = page.locator(
      '[data-test^="add-to-cart"]'
    );
    await addButtons.first().click();
    await addButtons.nth(1).click();
    await page.locator('.shopping_cart_link').click();
    await expect(
      page.locator('.cart_item')
    ).toHaveCount(2);
  });

  test('TC3: No login redirects to login page', 
  async ({ page }) => {
    await page.context().clearCookies();
    await page.goto(
      'https://www.saucedemo.com/inventory.html'
    );
    await expect(page).toHaveURL(
      'https://www.saucedemo.com/'
    );
  });

});