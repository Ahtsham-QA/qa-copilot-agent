# tools/data_generator.py
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
    test_cases: str
) -> dict:
    """
    Generates structured test data
    as separate JSON file
    """

    system_prompt = """You are a senior QA engineer
specializing in test data management.

Generate test data as valid JSON only.
No explanation. No markdown. Just JSON.

Structure must be:
{
  "valid_data": [...],
  "invalid_data": [...],
  "edge_cases": [...]
}

Each item must have:
- All relevant field values
- expected outcome
- description of scenario

Use realistic data:
→ Real email formats
→ Real password patterns
→ Real names and addresses
→ Real phone numbers
→ Real amounts and dates"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""Generate test data JSON for:

User Story: {user_story}

Test Cases: {test_cases}

Return ONLY valid JSON. Nothing else."""
            }
        ],
        system=system_prompt
    )

    # Parse JSON response
    response_text = message.content[0].text
    
    # Clean any markdown if present
    response_text = response_text.replace(
        "```json", ""
    ).replace("```", "").strip()

    return json.loads(response_text)


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


if __name__ == "__main__":
    sample_story = "user can login"
    sample_cases = "TC01: valid login, TC02: invalid login"
    
    data = generate_test_data(sample_story, sample_cases)
    save_test_data(data)
    print(json.dumps(data, indent=2))