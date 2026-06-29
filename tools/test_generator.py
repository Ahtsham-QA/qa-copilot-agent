import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_test_cases(
    user_story: str,
    credentials: dict = None  # ADD THIS
) -> str:

    # Build credentials context
    cred_info = ""
    if credentials:
        cred_info = f"""
REAL CREDENTIALS TO USE IN TEST CASES:
Valid username: {credentials['valid']['username']}
Valid password: {credentials['valid']['password']}
Invalid username: {credentials['invalid']['username']}
Invalid password: {credentials['invalid']['password']}

RULES:
→ Use ONLY these credentials in test data
→ Never invent fake emails
→ Never invent fake passwords
→ Maximum 4 test cases total
→ 1 positive, 2 negative, 1 edge case
"""

    system_prompt = f"""You are a senior QA engineer.
{cred_info}
When given a user story generate professional
test cases in EXACTLY this format:

## TEST CASE 1: [Test Case Title]
- Type: [Positive/Negative/Edge Case]
- Priority: [High/Medium/Low]
- Preconditions: [What must be true]
- Test Data:
  * Username: [use provided credentials]
  * Password: [use provided credentials]
- Steps:
  1. [Step 1]
  2. [Step 2]
- Expected Result: [What should happen]

---

STRICT RULES:
1. Maximum 4 test cases only
2. 1 Positive, 2 Negative, 1 Edge Case
3. Use ONLY provided credentials
4. Never invent fake emails
5. Never use placeholder@example.com
6. Steps must be clear and executable
7. No Playwright code"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
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