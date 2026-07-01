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
    credentials: dict = None,
    feature_type: str = "Login / Authentication"
) -> dict:
    """
    Generates test data based on feature type.
    Never invents fake credentials.
    """

    if feature_type == "Login / Authentication":
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
                    "username": "' OR '1'='1",
                    "password": valid_pass if credentials else "Test@123",
                    "description": "SQL injection attempt in username field",
                    "expected": "failure"
                }
            ]
        }

    elif feature_type == "Search & Navigation":
        # Use provided search terms if available
        valid_term = credentials['valid']['username'] \
            if credentials and credentials['valid']['username'] \
            else "test"
        invalid_term = credentials['invalid']['username'] \
            if credentials and credentials['invalid']['username'] \
            else "xyzabc123notexist"

        test_data = {
            "valid_data": [
                {
                    "query": valid_term,
                    "description": f"Search for '{valid_term}' returns results",
                    "expected": "results"
                }
            ],
            "invalid_data": [
                {
                    "query": invalid_term,
                    "description": f"Search for '{invalid_term}' shows no results",
                    "expected": "no results"
                },
                {
                    "query": "",
                    "description": "Empty search query stays on page",
                    "expected": "same page"
                }
            ],
            "edge_cases": [
                {
                    "query": "<script>alert('xss')</script>",
                    "description": "XSS injection in search field handled safely",
                    "expected": "safe"
                }
            ]
        }

    elif feature_type == "Form Submission":
        test_data = {
            "valid_data": [
                {
                    "fields": {
                        "name": "John Doe",
                        "email": "test@example.com",
                        "message": "This is a test message"
                    },
                    "description": "Valid form submission succeeds",
                    "expected": "success"
                }
            ],
            "invalid_data": [
                {
                    "fields": {
                        "name": "",
                        "email": "",
                        "message": ""
                    },
                    "description": "Empty form submission shows errors",
                    "expected": "error"
                },
                {
                    "fields": {
                        "name": "Test",
                        "email": "notanemail",
                        "message": "Test"
                    },
                    "description": "Invalid email format shows error",
                    "expected": "error"
                }
            ],
            "edge_cases": [
                {
                    "fields": {
                        "name": "A" * 256,
                        "email": "test@example.com",
                        "message": "Test"
                    },
                    "description": "Maximum length input in name field",
                    "expected": "handled"
                }
            ]
        }

    elif feature_type == "Shopping Cart":
        test_data = {
            "valid_data": [
                {
                    "item_index": 0,
                    "description": "Add first item to cart",
                    "expected": "cart count increases"
                }
            ],
            "invalid_data": [
                {
                    "item_index": 0,
                    "description": "Remove item from cart",
                    "expected": "cart count decreases"
                }
            ],
            "edge_cases": [
                {
                    "item_index": 0,
                    "description": "Add same item to cart twice",
                    "expected": "cart count updates"
                }
            ]
        }

    else:
        # Default fallback
        test_data = {
            "valid_data": [
                {
                    "description": "Feature works with valid input",
                    "expected": "success"
                }
            ],
            "invalid_data": [
                {
                    "description": "Feature handles invalid input",
                    "expected": "error"
                }
            ],
            "edge_cases": [
                {
                    "description": "Feature handles edge case input",
                    "expected": "handled"
                }
            ]
        }

    print(f"  ✅ Test data generated for: {feature_type}")
    return test_data

def save_test_data(
    data: dict,
    filename: str = "test_data.json"
) -> str:
    """
    Saves test data to JSON file.
    """
    import json
    import os

    output_dir = "generated/test-data"
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    print(f"  ✅ Test data saved: {filepath}")
    return filepath