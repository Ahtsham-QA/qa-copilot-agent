import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

FALLBACK_DATA = {
    "valid_data": [
        {
            "username": "standard_user",
            "password": "secret_sauce",
            "description": "Valid login with correct credentials",
            "expected_title": "Products"
        }
    ],
    "invalid_data": [
        {
            "username": "wrong_user",
            "password": "wrong_pass",
            "description": "Invalid credentials",
            "expected_error": "Username and password do not match"
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
            "username": "locked_out_user",
            "password": "secret_sauce",
            "description": "Locked out user",
            "expected": "failure"
        }
    ]
}


def generate_test_data(
    user_story: str,
    test_cases: str
) -> dict:
    """
    Generates structured test data as JSON.
    Falls back to safe default if JSON is invalid.
    """

    system_prompt = """You are a QA test data specialist.
Generate test data as valid JSON only.
No explanation. No markdown. Just JSON.

STRICT LIMITS:
→ Maximum 3 items in valid_data array
→ Maximum 3 items in invalid_data array
→ Maximum 2 items in edge_cases array
→ Keep all strings short and simple
→ Must be 100% complete valid JSON
→ Never leave strings unterminated
→ Never truncate output"""

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
Short strings only.
Must be complete valid JSON.
Return ONLY JSON. Nothing else."""
            }
        ],
        system=system_prompt
    )

    response_text = message.content[0].text

    # Clean markdown
    response_text = response_text.replace(
        "```json", ""
    ).replace("```", "").strip()

    # Try parsing JSON
    try:
        data = json.loads(response_text)
        print("  ✅ Test data generated successfully")
        return data

    except json.JSONDecodeError as e:
        print(f"  ⚠️ JSON truncated: {e}")
        print("  → Using fallback test data")
        return FALLBACK_DATA


def save_test_data(
    data: dict,
    filename: str = "test_data.json"
) -> str:
    """
    Saves test data to JSON file.
    """
    output_dir = "generated/test-data"
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"  ✅ Test data saved: {filepath}")
    return filepath


if __name__ == "__main__":
    sample_story = "user can add items to cart"
    sample_cases = "TC01: add single item, TC02: add multiple items"

    data = generate_test_data(sample_story, sample_cases)
    save_test_data(data)
    print(json.dumps(data, indent=2))