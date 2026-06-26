# tools/playwright_gen.py
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

def generate_playwright_tests(
    user_story: str, 
    test_cases: str,
    url: str = "https://www.saucedemo.com"
) -> str:
    """
    Takes user story + test cases and generates
    complete Playwright spec.js file
    """

    system_prompt = """You are a senior QA automation engineer
specializing in Playwright with JavaScript.

Generate THREE separate files:

FILE 1: pages/LoginPage.js
→ Class with constructor
→ Selectors as this.variables
→ Methods for actions only
→ module.exports at bottom

FILE 2: pages/InventoryPage.js  
→ Class with constructor
→ Selectors as this.variables
→ Methods for actions only
→ module.exports at bottom

FILE 3: tests/login.spec.js
→ Import from '../pages/LoginPage'
→ Import from '../pages/InventoryPage'
→ No classes inside spec file
→ Only test blocks
→ Use page objects only

STRICT RULES:
1. JavaScript not TypeScript
2. Use @playwright/test
3. Separate files clearly with:
   === FILE: pages/LoginPage.js ===
4. module.exports for each class
5. require() imports in spec file
6. No classes inside spec files
7. Real working code only
8. Use assertions with expect
9. Add comments explaining each test
10. Always complete every test fully,
11. Never leave expect() statements incomplete,
12. Every test must have closing }); bracket
13. Use /inventory\\.html/ not /inventory/ for URL checks,
14. Always escape dots in regex patterns,
15. Use toHaveURL(/inventory\\.html/) for redirects,
16. Valid usernames are:
- standard_user
- problem_user  
- performance_glitch_user
- locked_out_user
17. Password for all: secret_sauce
18. Never generate fake email addresses
    as usernames for SauceDemo.
19. data-test selectors preferred"""



    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
messages=[
    {
        "role": "user",
        "content": f"""Generate Playwright tests for:

URL: {url}

User Story:
{user_story}

Test Cases:
{test_cases}

CRITICAL REQUIREMENTS:
→ Import test data from JSON:
  const testData = require('../test-data/test_data.json');
→ Never hardcode any test values
→ Loop through valid_data array
→ Loop through invalid_data array  
→ Loop through edge_cases array
→ All usernames, passwords, expected
  results must come from JSON file
→ Every test fully complete
→ Every bracket must close
→ No incomplete expect() statements

EXAMPLE PATTERN:
const testData = require('../test-data/test_data.json');

testData.valid_data.forEach(data => {{
  test(`Valid: ${{data.description}}`,
  async ({{ page }}) => {{
    await loginPage.login(
      data.username,
      data.password
    );
    await expect(page).toHaveURL(/inventory\.html/);
  }});
}});

Return ONLY complete spec.js file.
No explanation. No markdown. Just code."""
    }
],
        system=system_prompt
    )

    return message.content[0].text


def save_playwright_tests(
    content: str,
    filename: str = "generated_tests.spec.js"
) -> list:
    """
    Saves generated Playwright tests
    Splits into separate files if POM detected
    """
    output_dir = "generated"
    pages_dir = os.path.join(output_dir, "pages")
    tests_dir = os.path.join(output_dir, "tests")
    
    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    saved_files = []

    # Split content by FILE markers
    if "=== FILE:" in content:
        sections = content.split("=== FILE:")
        
        for section in sections:
            if not section.strip():
                continue
                
            # Get filename from marker
            lines = section.strip().split("\n")
            file_path = lines[0].replace("===", "").strip()
            file_content = "\n".join(lines[1:]).strip()
            
            # Remove markdown code fences
            file_content = file_content.replace(
                "```javascript", ""
            ).replace("```", "").strip()
            
            # Save to correct folder
            full_path = os.path.join(output_dir, file_path)
            os.makedirs(
                os.path.dirname(full_path), 
                exist_ok=True
            )
            
            with open(full_path, "w") as f:
                f.write(file_content)
            
            saved_files.append(full_path)
            print(f"  ✅ Saved: {full_path}")
    
    else:
        # Single file fallback
        filepath = os.path.join(tests_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        saved_files.append(filepath)
        print(f"  ✅ Saved: {filepath}")

    return saved_files


if __name__ == "__main__":
    sample_story = "User can login with valid credentials"
    sample_tests = """
## TEST CASE 1: Valid Login
- Type: Positive
- Priority: High
- Steps:
  1. Navigate to login page
  2. Enter valid credentials
  3. Click login button
- Expected Result: User redirected to dashboard
    """
    
    result = generate_playwright_tests(
        sample_story, 
        sample_tests
    )
    save_playwright_tests(result)
    print(result)