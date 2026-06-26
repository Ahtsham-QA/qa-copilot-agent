import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

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
→ CommonJS (require/module.exports)
→ constructor with page parameter
→ All selectors as this.variables
→ Methods for user actions
→ No markdown
→ No comments
→ Minimal comments only
→ No verbose explanations
→ Short but complete tests
→ Maximum 3 test scenarios
→ Never sacrifice completion
   for coverage
→ Better to have 3 complete
   tests than 6 incomplete
   → Maximum 3 items in valid_data
→ Maximum 3 items in invalid_data
→ Maximum 2 items in edge_cases
→ Keep descriptions short
→ Must be complete valid JSON
→ Never truncate mid-string
→ Return ONLY valid JSON
→ Pure JavaScript only
→ End with module.exports = {class_name};

Return ONLY the JavaScript class.
Nothing else."""
            }
        ]
    )
    return message.content[0].text


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
        max_tokens=2000,
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
→ Every test fully complete
→ Every bracket must close
→ Use string URL not regex
→ Pure JavaScript only

Return ONLY complete spec.js.
Nothing else."""
            }
        ]
    )
    return message.content[0].text


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