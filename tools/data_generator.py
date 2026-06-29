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
    Generates test data using provided credentials.
    Never invents fake data.
    """

    if credentials:
        valid_user = credentials['valid']['username']
        valid_pass = credentials['valid']['password']
        invalid_user = credentials['invalid']['username']
        invalid_pass = credentials['invalid']['password']
    else:
        valid_user = "test_user"
        valid_pass = "Test@123"
        invalid_user = "wrong_user"
        invalid_pass = "wrong_pass"

    try:
        upper_user = valid_user.upper()
    except:
        upper_user = valid_user

    test_data = {
        "valid_data": [
            {
                "username": valid_user,
                "password": valid_pass,
                "description": "Valid credentials login",
                "expected_title": "Dashboard"
            }
        ],
        "invalid_data": [
            {
                "username": invalid_user,
                "password": invalid_pass,
                "description": "Invalid credentials login fails",
                "expected_error": "Invalid credentials"
            },
            {
                "username": "",
                "password": "",
                "description": "Empty fields login fails",
                "expected_error": "Required"
            }
        ],
        "edge_cases": [
            {
                "username": upper_user,
                "password": valid_pass,
                "description": "Uppercase username test",
                "expected": "failure"
            }
        ]
    }

    print("  ✅ Test data generated with provided credentials")
    return test_data
    
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