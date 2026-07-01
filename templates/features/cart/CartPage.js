class CartPage {
  constructor(page) {
    this.page = page;
    this.productItems = page.locator(
      '.product, .item, [class*="product"], [data-test*="item"], .card'
    );
    this.addToCartButtons = page.locator(
      'button:has-text("Add to cart"), button:has-text("Add to bag"), [data-test*="add-to-cart"], [class*="add-to-cart"]'
    );
    this.cartIcon = page.locator(
      '.cart, [class*="cart"], [aria-label*="cart" i], [data-test*="cart"]'
    ).first();
    this.cartCount = page.locator(
      '.cart-count, .cart-badge, [class*="cart-count"], [data-test*="cart-badge"]'
    ).first();
    this.removeButtons = page.locator(
      'button:has-text("Remove"), button:has-text("Delete"), [data-test*="remove"]'
    );
    this.cartItems = page.locator(
      '.cart-item, [class*="cart-item"], [data-test*="cart-item"]'
    );
  }

  async navigateTo(url) {
    await this.page.goto(url);
    await this.page.waitForLoadState('domcontentloaded');
  }

  async addItemByIndex(index) {
    await this.addToCartButtons.nth(index).waitFor({ state: 'visible', timeout: 10000 });
    await this.addToCartButtons.nth(index).click();
    await this.page.waitForTimeout(500);
  }

  async getCartCount() {
    try {
      return await this.cartCount.textContent();
    } catch {
      return "0";
    }
  }

  async openCart() {
    await this.cartIcon.waitFor({ state: 'visible', timeout: 10000 });
    await this.cartIcon.click();
    await this.page.waitForTimeout(1000);
  }

  async removeItemByIndex(index) {
    await this.removeButtons.nth(index).waitFor({ state: 'visible', timeout: 10000 });
    await this.removeButtons.nth(index).click();
    await this.page.waitForTimeout(500);
  }

  async getCartItemCount() {
    return await this.cartItems.count();
  }
}

module.exports = CartPage;
