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
→ Use aria locators wherever possible:
   this.usernameInput = page.getByRole('textbox', {{ name: /username/i }})
   this.passwordInput = page.getByLabel(/password/i)
   this.submitButton = page.getByRole('button', {{ name: /login/i }})
   this.errorMessages = page.getByRole('alert')
→ Fall back to CSS only when aria not available
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

   async getErrorMessageByIndex(index) {{
     return await this.errorMessages.nth(index).textContent();
   }}

   async isErrorVisibleByIndex(index) {{
     return await this.errorMessages.nth(index).isVisible();
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
    Saves playwright tests.
    Uses templates for page classes.
    Only generates spec.js dynamically.
    """
    import shutil

    output_dir = "generated"
    pages_dir = os.path.join(output_dir, "pages")
    tests_dir = os.path.join(output_dir, "tests")

    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    saved_files = []

    # Copy template page classes (don't regenerate)
    template_dir = "templates"

    if os.path.exists(f"{template_dir}/LoginPage.js"):
        shutil.copy(
            f"{template_dir}/LoginPage.js",
            f"{pages_dir}/LoginPage.js"
        )
        print(f"  ✅ Saved: {pages_dir}/LoginPage.js (from template)")
        saved_files.append(f"{pages_dir}/LoginPage.js")

    if os.path.exists(f"{template_dir}/InventoryPage.js"):
        shutil.copy(
            f"{template_dir}/InventoryPage.js",
            f"{pages_dir}/InventoryPage.js"
        )
        print(f"  ✅ Saved: {pages_dir}/InventoryPage.js (from template)")
        saved_files.append(f"{pages_dir}/InventoryPage.js")

    # Use template spec.js (reads from JSON)
    if os.path.exists(f"{template_dir}/login.spec.js"):
        shutil.copy(
            f"{template_dir}/login.spec.js",
            f"{tests_dir}/login.spec.js"
        )
        print(f"  ✅ Saved: {tests_dir}/login.spec.js (from template)")
        saved_files.append(f"{tests_dir}/login.spec.js")

    return saved_files