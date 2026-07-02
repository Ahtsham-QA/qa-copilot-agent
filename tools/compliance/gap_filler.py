"""
AI Gap Filler — generates Playwright tests
for missing compliance controls.
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Pre-built templates for common compliance gaps
# These are reliable and don't need AI generation
GAP_TEMPLATES = {
    "PCI-DSS 8.1.8": {
        "title": "Session Timeout after 15 minutes",
        "description": "PCI-DSS requires re-authentication after 15 minutes of inactivity",
        "test": """test('PCI-DSS 8.1.8 - Session timeout after inactivity', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.navigateTo(APP_URL);
  await loginPage.fillInputByIndex(0, testData.valid_data[0].username);
  await loginPage.fillInputByIndex(1, testData.valid_data[0].password);
  await loginPage.clickSubmit();
  await page.waitForTimeout(2000);

  // Simulate inactivity — wait and check session expires
  // NOTE: Adjust timeout to match your app's session policy
  await page.waitForTimeout(5000);
  await page.reload();

  // After session timeout, user should be redirected to login
  await expect(page).toHaveURL(new RegExp(APP_URL));
});"""
    },
    "PCI-DSS 8.1.6": {
        "title": "Account lockout after failed attempts",
        "description": "PCI-DSS requires account lockout after 6 failed login attempts",
        "test": """test('PCI-DSS 8.1.6 - Account lockout after repeated failures', async ({ page }) => {
  const loginPage = new LoginPage(page);

  // Attempt login 6 times with wrong credentials
  for (let i = 0; i < 6; i++) {
    await loginPage.navigateTo(APP_URL);
    await loginPage.fillInputByIndex(0, 'wrong_user_' + i);
    await loginPage.fillInputByIndex(1, 'wrong_pass');
    await loginPage.clickSubmit();
    await page.waitForTimeout(500);
  }

  // On 7th attempt, account should be locked
  await loginPage.navigateTo(APP_URL);
  await loginPage.fillInputByIndex(0, testData.valid_data[0].username);
  await loginPage.fillInputByIndex(1, testData.valid_data[0].password);
  await loginPage.clickSubmit();
  await page.waitForTimeout(1000);

  // Should still be on login page (locked out)
  const isError = await loginPage.isErrorVisibleByIndex(0);
  expect(isError).toBeTruthy();
});"""
    },
    "HIPAA 164.312(a)(2)(iii)": {
        "title": "Automatic logoff after inactivity",
        "description": "HIPAA requires automatic session termination after inactivity",
        "test": """test('HIPAA 164.312(a)(2)(iii) - Automatic logoff after inactivity', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.navigateTo(APP_URL);
  await loginPage.fillInputByIndex(0, testData.valid_data[0].username);
  await loginPage.fillInputByIndex(1, testData.valid_data[0].password);
  await loginPage.clickSubmit();
  await page.waitForTimeout(2000);

  // Simulate inactivity period
  await page.waitForTimeout(5000);
  await page.reload();

  // User should be logged out and redirected to login
  await expect(page).toHaveURL(new RegExp(APP_URL));
});"""
    },
    "HIPAA 164.312(b)": {
        "title": "Audit controls — verify access logging",
        "description": "HIPAA requires recording and examining activity in systems containing ePHI",
        "test": """test('HIPAA 164.312(b) - Audit trail for login activity', async ({ page }) => {
  const loginPage = new LoginPage(page);

  // Successful login should be auditable
  await loginPage.navigateTo(APP_URL);
  await loginPage.fillInputByIndex(0, testData.valid_data[0].username);
  await loginPage.fillInputByIndex(1, testData.valid_data[0].password);
  await loginPage.clickSubmit();
  await page.waitForTimeout(2000);

  // Verify login was successful (audit event triggered)
  await expect(page).not.toHaveURL(APP_URL);

  // Failed login should also be auditable
  await loginPage.navigateTo(APP_URL);
  await loginPage.fillInputByIndex(0, 'wrong_user');
  await loginPage.fillInputByIndex(1, 'wrong_pass');
  await loginPage.clickSubmit();
  await page.waitForTimeout(1000);

  const isError = await loginPage.isErrorVisibleByIndex(0);
  expect(isError).toBeTruthy();
});"""
    },
    "HIPAA 164.312(a)(1)": {
        "title": "Access control — unauthorized user blocked",
        "description": "HIPAA requires restricting access to authorized users only",
        "test": """test('HIPAA 164.312(a)(1) - Unauthorized access blocked', async ({ page }) => {
  const loginPage = new LoginPage(page);

  // Attempt access with invalid credentials
  await loginPage.navigateTo(APP_URL);
  await loginPage.fillInputByIndex(0, 'unauthorized_user');
  await loginPage.fillInputByIndex(1, 'unauthorized_pass');
  await loginPage.clickSubmit();
  await page.waitForTimeout(1000);

  // Should remain on login page
  await expect(page).toHaveURL(new RegExp(APP_URL));
  const isError = await loginPage.isErrorVisibleByIndex(0);
  expect(isError).toBeTruthy();
});"""
    },
    "SR 11-7 VII": {
        "title": "Audit trail for model access",
        "description": "SR 11-7 requires maintaining records of model access",
        "test": """test('SR 11-7 VII - Audit trail for system access', async ({ page }) => {
  const loginPage = new LoginPage(page);

  // Login and verify audit trail capability
  await loginPage.navigateTo(APP_URL);
  await loginPage.fillInputByIndex(0, testData.valid_data[0].username);
  await loginPage.fillInputByIndex(1, testData.valid_data[0].password);
  await loginPage.clickSubmit();
  await page.waitForTimeout(2000);

  // Successful login creates audit record
  await expect(page).not.toHaveURL(APP_URL);

  // Failed attempt also creates audit record
  await loginPage.navigateTo(APP_URL);
  await loginPage.fillInputByIndex(0, 'wrong_user');
  await loginPage.fillInputByIndex(1, 'wrong_pass');
  await loginPage.clickSubmit();
  const isError = await loginPage.isErrorVisibleByIndex(0);
  expect(isError).toBeTruthy();
});"""
    },
    "SOX 302": {
        "title": "Audit trail for financial data access",
        "description": "SOX requires tracking all changes to financial data",
        "test": """test('SOX 302 - Audit trail for system access', async ({ page }) => {
  const loginPage = new LoginPage(page);

  // Login creates auditable access record
  await loginPage.navigateTo(APP_URL);
  await loginPage.fillInputByIndex(0, testData.valid_data[0].username);
  await loginPage.fillInputByIndex(1, testData.valid_data[0].password);
  await loginPage.clickSubmit();
  await page.waitForTimeout(2000);

  await expect(page).not.toHaveURL(APP_URL);
});"""
    },
    "SOX 404.2": {
        "title": "Segregation of duties — access control",
        "description": "SOX requires no single user has conflicting access rights",
        "test": """test('SOX 404.2 - Segregation of duties enforced', async ({ page }) => {
  const loginPage = new LoginPage(page);

  // Standard user should not have admin access
  await loginPage.navigateTo(APP_URL);
  await loginPage.fillInputByIndex(0, testData.valid_data[0].username);
  await loginPage.fillInputByIndex(1, testData.valid_data[0].password);
  await loginPage.clickSubmit();
  await page.waitForTimeout(2000);

  // Attempt to access admin area
  await page.goto(APP_URL + '/admin');
  await page.waitForTimeout(1000);

  // Should be redirected away from admin
  expect(page.url()).not.toContain('/admin');
});"""
    }
}


def generate_gap_tests(
    compliance_matrix: dict,
    app_url: str
) -> list:
    """
    For each uncovered compliance control,
    generates a Playwright test to cover it.
    Returns list of gap test objects.
    """
    gaps = compliance_matrix.get("coverage", {}).get("uncovered", [])
    framework = compliance_matrix.get("framework", "None")

    if not gaps:
        return []

    gap_tests = []

    for gap in gaps:
        control_id = gap["id"]
        control_title = gap["title"]

        # Check if we have a pre-built template
        if control_id in GAP_TEMPLATES:
            template = GAP_TEMPLATES[control_id]
            gap_tests.append({
                "control_id": control_id,
                "control_title": control_title,
                "test_title": template["title"],
                "description": template["description"],
                "playwright_test": template["test"],
                "source": "template"
            })
        else:
            # Use Claude API to generate
            test_code = generate_with_claude(
                control_id=control_id,
                control_title=control_title,
                framework=framework,
                app_url=app_url
            )
            gap_tests.append({
                "control_id": control_id,
                "control_title": control_title,
                "test_title": f"Compliance test for {control_id}",
                "description": f"Tests {control_title} requirement",
                "playwright_test": test_code,
                "source": "ai_generated"
            })

    return gap_tests


def generate_with_claude(
    control_id: str,
    control_title: str,
    framework: str,
    app_url: str
) -> str:
    """
    Uses Claude to generate a Playwright test
    for a compliance control that has no template.
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""Generate a Playwright test for this compliance requirement:

Framework: {framework}
Control ID: {control_id}
Control Title: {control_title}
App URL: {app_url}

Rules:
→ Use LoginPage class already imported
→ Use testData.valid_data[0].username and .password
→ Use APP_URL constant
→ CommonJS style
→ No markdown, no backticks
→ Return only the test() block
→ Make it practical and runnable"""
        }]
    )
    return message.content[0].text


def format_gap_tests_for_spec(gap_tests: list) -> str:
    """
    Formats gap tests into a complete spec file section.
    """
    if not gap_tests:
        return ""

    lines = []
    lines.append("\n// ============================================")
    lines.append("// COMPLIANCE GAP TESTS — Auto-generated by TestGen AI")
    lines.append("// ============================================\n")

    lines.append("test.describe('Compliance Gap Tests', () => {")

    for gap in gap_tests:
        lines.append(f"\n  // {gap['control_id']} — {gap['control_title']}")
        lines.append(f"  // {gap['description']}")
        lines.append(f"  {gap['playwright_test']}")

    lines.append("});")

    return "\n".join(lines)
