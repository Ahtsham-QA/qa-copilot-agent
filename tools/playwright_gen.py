import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def clean_code(text: str) -> str:
    """
    Removes markdown backticks from generated code.
    """
    text = text.strip()
    if text.startswith("```javascript"):
        text = text[len("```javascript"):].strip()
    elif text.startswith("```"):
        text = text[3:].strip()
    if text.endswith("```"):
        text = text[:-3].strip()
    return text


def generate_page_class(
    class_name: str,
    url: str
) -> str:
    """
    Generates ONE page class at a time.
    Focused call = complete output always.
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""Generate a Playwright Page Object class.

Class name: {class_name}
App URL: {url}

Rules:
→ CommonJS module.exports syntax
→ constructor(page) with this.page = page
→ Use getByRole selectors:
   this.usernameInput = page.getByRole('textbox').first()
   this.passwordInput = page.locator('input[type="password"]')
   this.submitButton = page.getByRole('button').first()
   this.errorMessages = page.locator('[data-test="error"], .error, [class*="error"], [role="alert"]')
→ No individual item methods
→ Maximum 10 selectors total
→ Maximum 8 methods total
→ No markdown backticks
→ No ``` in output
→ Pure JavaScript only
→ Never use .clear() before .fill()
→ Always include these exact methods:

   async navigateTo(url) {{
     await this.page.goto(url);
     await this.page.waitForLoadState('networkidle');
   }}

   async fillInputByIndex(index, value) {{
     if (index === 0) {{
       await this.usernameInput.waitFor({{ state: 'visible' }});
       await this.usernameInput.fill(value);
     }} else {{
       await this.passwordInput.waitFor({{ state: 'visible' }});
       await this.passwordInput.fill(value);
     }}
   }}

   async clickSubmit() {{
     await this.submitButton.waitFor({{ state: 'visible' }});
     await this.submitButton.click();
   }}

→ Works on ANY web application
→ Last line: module.exports = {class_name};

Return ONLY the JavaScript class.
Nothing else."""
            }
        ]
    )
    return clean_code(message.content[0].text)


def generate_spec_file(
    user_story: str,
    test_cases: str,
    url: str
) -> str:
    """
    Generates spec.js file separately.
    Reads from test_data.json.
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"""Generate Playwright spec.js file.

URL: {url}
User Story: {user_story}
Test Cases: {test_cases}

Rules:
→ CommonJS require() syntax
→ Import LoginPage from '../pages/LoginPage'
→ Import InventoryPage from '../pages/InventoryPage'
→ Import testData from '../test-data/test_data.json'
→ Use testData.valid_data.forEach()
→ Use testData.invalid_data.forEach()
→ Maximum 3 tests per section
→ No markdown in output
→ No ``` backticks anywhere
→ Every test fully complete
→ Every bracket must close
→ Pure JavaScript only
→ First line must be require()
→ Test data fields:
   data.username
   data.password
   data.description
   data.expected_error
→ Use data.description for test names

URL RULES - CRITICAL:
→ ONLY ONE URL constant allowed:
   const APP_URL = '{url}';
→ NEVER create LOGIN_URL variable
→ NEVER append /login to any URL
→ URL provided is already the login URL
→ Use APP_URL for ALL navigateTo() calls
→ Use APP_URL for ALL toHaveURL() checks
→ Never modify APP_URL in any way
→ Never write '...' for URLs
→ Never write 'example.com'
→ Never hardcode any URL
→ Only use APP_URL throughout entire file

METHOD RULES - CRITICAL:
→ Never use enterEmail()
→ Never use enterUsername()
→ Never use enterPassword()
→ Never use clickLoginButton()
→ Never use getDashboardElement()
→ Never invent method names
→ Never hardcode credentials
→ Always use data.username
→ Always use data.password
→ Always use these methods ONLY:
   loginPage.navigateTo(APP_URL)
   loginPage.fillInputByIndex(0, data.username)
   loginPage.fillInputByIndex(1, data.password)
   loginPage.clickSubmit()
   loginPage.isErrorVisibleByIndex(0)
   loginPage.getErrorMessageByIndex(0)

METHOD RULES:
→ Use loginPage.clickLoginButton()
→ Use inventoryPage.inventoryContainer
→ Never use getDashboardElement()
→ Never invent method names

Return ONLY complete spec.js.
Nothing else."""
            }
        ]
    )
    return clean_code(message.content[0].text)

def generate_playwright_tests(
    user_story: str,
    test_cases: str,
    url: str = "https://www.saucedemo.com"
) -> dict:
    """
    Generates all files separately.
    One API call per file.
    No truncation issues.
    """
    print("  → Generating LoginPage.js...")
    login_page = generate_page_class("LoginPage", url)

    print("  → Generating InventoryPage.js...")
    inventory_page = generate_page_class("InventoryPage", url)

    print("  → Generating spec.js...")
    spec = generate_spec_file(user_story, test_cases, url)

    return {
        "LoginPage": login_page,
        "InventoryPage": inventory_page,
        "spec": spec
    }


def save_playwright_tests(content: dict) -> list:
    """
    Saves each file separately.
    Returns list of saved file paths.
    """
    output_dir = "generated"
    pages_dir = os.path.join(output_dir, "pages")
    tests_dir = os.path.join(output_dir, "tests")

    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    saved_files = []

    # Save LoginPage.js
    login_path = os.path.join(pages_dir, "LoginPage.js")
    with open(login_path, "w") as f:
        f.write(content["LoginPage"])
    print(f"  ✅ Saved: {login_path}")
    saved_files.append(login_path)

    # Save InventoryPage.js
    inventory_path = os.path.join(pages_dir, "InventoryPage.js")
    with open(inventory_path, "w") as f:
        f.write(content["InventoryPage"])
    print(f"  ✅ Saved: {inventory_path}")
    saved_files.append(inventory_path)

    # Save spec.js
    spec_path = os.path.join(tests_dir, "login.spec.js")
    with open(spec_path, "w") as f:
        f.write(content["spec"])
    print(f"  ✅ Saved: {spec_path}")
    saved_files.append(spec_path)

    return saved_files