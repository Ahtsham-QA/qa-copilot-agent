import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def generate_test_data(
    user_story: str,
    test_cases: str,
    credentials: dict = None
) -> dict:
    """
    Generates test data as JSON.
    Uses provided credentials if given.
    Falls back to safe defaults if JSON fails.
    """

    # Build credentials context
    cred_context = ""
    if credentials:
        cred_context = f"""
USE THESE EXACT CREDENTIALS:
→ Valid username: {credentials['valid']['username']}
→ Valid password: {credentials['valid']['password']}
→ Invalid username: {credentials['invalid']['username']}
→ Invalid password: {credentials['invalid']['password']}
"""
        if credentials.get('locked'):
            cred_context += f"→ Locked username: {credentials['locked']['username']}\n"

        cred_context += """
RULES FOR CREDENTIALS:
→ Use ONLY provided credentials
→ Never invent other usernames
→ Never generate email addresses
   unless provided credentials
   are email addresses
→ Use exact values provided
"""

    system_prompt = f"""You are a QA test data specialist.
Generate test data as valid JSON only.
No explanation. No markdown. Just JSON.

{cred_context}

STRICT RULES:
→ Maximum 3 items in valid_data
→ Maximum 3 items in invalid_data
→ Maximum 2 items in edge_cases
→ Keep descriptions short
→ Must be complete valid JSON
→ Never truncate mid-string

JSON Structure:
{{
  "valid_data": [
    {{
      "username": "...",
      "password": "...",
      "description": "...",
      "expected_title": "..."
    }}
  ],
  "invalid_data": [
    {{
      "username": "...",
      "password": "...",
      "description": "...",
      "expected_error": "..."
    }}
  ],
  "edge_cases": [
    {{
      "username": "...",
      "password": "...",
      "description": "...",
      "expected": "failure"
    }}
  ]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": f"""Generate test data JSON for:

User Story: {user_story}
Test Cases: {test_cases}

Maximum 3 items per array.
Must be complete valid JSON.
Return ONLY JSON. Nothing else."""
            }
        ],
        system=system_prompt
    )

    response_text = message.content[0].text
    response_text = response_text.replace(
        "```json", ""
    ).replace("```", "").strip()

    try:
        data = json.loads(response_text)
        print("  ✅ Test data generated successfully")
        return data

    except json.JSONDecodeError as e:
        print(f"  ⚠️ JSON parse error: {e}")
        print("  → Using fallback test data")

        # Build fallback from provided credentials
        username = credentials['valid']['username'] \
            if credentials else "test_user"
        password = credentials['valid']['password'] \
            if credentials else "Test@123"
        inv_username = credentials['invalid']['username'] \
            if credentials else "wrong_user"
        inv_password = credentials['invalid']['password'] \
            if credentials else "WrongPass"

        return {
            "valid_data": [
                {
                    "username": username,
                    "password": password,
                    "description": "Valid credentials",
                    "expected_title": "Dashboard"
                }
            ],
            "invalid_data": [
                {
                    "username": inv_username,
                    "password": inv_password,
                    "description": "Invalid credentials",
                    "expected_error": "Invalid username or password"
                },
                {
                    "username": "",
                    "password": "",
                    "description": "Empty fields",
                    "expected_error": "Username is required"
                }
            ],
            "edge_cases": [
                {
                    "username": username,
                    "password": password.upper(),
                    "description": "Wrong password case",
                    "expected": "failure"
                }
            ]
        }


def save_test_data(
    data: dict,
    filename: str = "test_data.json"
) -> str:
    """
    Saves test data to JSON file
    """
    output_dir = "generated/test-data"
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"  ✅ Test data saved: {filepath}")
    return filepath