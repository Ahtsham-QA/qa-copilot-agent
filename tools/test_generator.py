import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_test_cases(user_story: str) -> str:
    """
    Takes a user story and generates structured test cases
    with test data but without Playwright code.
    """

    system_prompt = """You are a senior QA engineer. When given a user story, 
generate professional test cases in EXACTLY this format:

## TEST CASE 1: [Test Case Title]
- Type: [Positive/Negative/Edge Case]
- Priority: [High/Medium/Low]
- Preconditions: [What must be true before test runs]
- Test Data:
  * [Field name]: [Value]
  * [Field name]: [Value]
- Steps:
  1. [Step 1]
  2. [Step 2]
  3. [Step 3]
- Expected Result: [What should happen]

---

STRICT RULES:
1. Always generate minimum 5 test cases
2. Include at least one Positive, two Negative, one Edge Case
3. Always include realistic Test Data (emails, passwords, names, amounts etc)
4. If no test data is needed for a step write "N/A"
5. DO NOT include any Playwright code or any code at all
6. DO NOT repeat the user story in output
7. Keep steps clear and simple enough for any QA to execute manually
8. Be specific with test data — use realistic values not placeholders"""

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"Generate test cases for this user story:\n\n{user_story}"
            }
        ],
        system=system_prompt
    )

    return message.content[0].text


# Quick test
if __name__ == "__main__":
    sample_story = """
    As a user I want to add items to my shopping cart
    so that I can purchase them later.
    """

    print("Generating test cases...\n")
    result = generate_test_cases(sample_story)
    print(result)