class FormPage {
  constructor(page) {
    this.page = page;
    this.inputs = page.locator('input:visible, textarea:visible');
    this.submitButton = page.locator(
      'button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Send")'
    ).first();
    this.successMessage = page.locator(
      '[class*="success"], [class*="confirm"], [role="alert"], :text("Thank you"), :text("Success"), :text("submitted")'
    ).first();
    this.errorMessages = page.locator(
      '[class*="error"], [class*="invalid"], [role="alert"]'
    );
  }

  async navigateTo(url) {
    await this.page.goto(url);
    await this.page.waitForLoadState('domcontentloaded');
  }

  async fillInputByIndex(index, value) {
    await this.inputs.nth(index).waitFor({ state: 'visible', timeout: 10000 });
    await this.inputs.nth(index).fill(value);
  }

  async submitForm() {
    await this.submitButton.waitFor({ state: 'visible', timeout: 10000 });
    await this.submitButton.click();
  }

  async isSuccessVisible() {
    return await this.successMessage.isVisible();
  }

  async isErrorVisible() {
    return await this.errorMessages.first().isVisible();
  }

  async getErrorCount() {
    return await this.errorMessages.count();
  }
}

module.exports = FormPage;
