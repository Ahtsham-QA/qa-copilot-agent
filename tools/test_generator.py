import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_test_cases(user_story: str) -> str:
    """
    Takes a user story and generates Playwright test cases using Claude.
    """

    system_prompt = """You are a senior QA automation engineer with expertise in Playwright.
When given a user story, you generate professional, structured test cases in this exact format:

TEST CASE 1: [Test Case Title]
- Type: [Positive/Negative/Edge Case]
- Priority: [High/Medium/Low]
- Preconditions: [What needs to be true before this test]
- Steps:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
- Expected Result: [What should happen]
- Playwright Code:
```javascript
test('[test title]', async ({ page }) => {
  // Your Playwright code here
});
```

Always generate at least 3 test cases per user story:
1. One happy path (positive)
2. One negative test
3. One edge case

Be specific, professional, and production-ready."""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"Generate Playwright test cases for this user story:\n\n{user_story}"
            }
        ],
        system=system_prompt
    )

    return message.content[0].text


# Quick test
if __name__ == "__main__":
    sample_story = """
    As a user, I want to log into the application using my email and password,
    so that I can access my dashboard securely.
    """

    print("Generating test cases...\n")
    result = generate_test_cases(sample_story)
    print(result)