# agent.py
import os
import sys
from dotenv import load_dotenv
from tools.test_generator import generate_test_cases
from tools.jira_tool import log_test_cases_to_jira
from tools.playwright_gen import (
    generate_playwright_tests,
    save_playwright_tests
)
from tools.data_generator import (
    generate_test_data,
    save_test_data
)
from tools.markdown_export import export_to_markdown

load_dotenv()

BANNER = """
╔══════════════════════════════════════════════════════════╗
║           🤖 QA COPILOT AGENT v2.0                      ║
║     AI-Powered Test Case Generator + Jira Logger        ║
║     Built by: Ahtsham Ijaz | github.com/Ahtsham-QA     ║
╚══════════════════════════════════════════════════════════╝
"""


def get_user_story() -> str:
    """
    Gets user story from command line or interactive prompt
    """
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])

    print("\nPaste your user story below.")
    print("When done, press Enter twice:\n")

    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)

    return "\n".join(lines).strip()


def get_app_url() -> str:
    """
    Gets target application URL
    """
    print("\n🌐 Enter app URL to test")
    print("(Press Enter to skip — uses SauceDemo):\n")
    url = input().strip()
    return url if url else "..."


def get_app_credentials():
    """
    Gets test credentials from user
    Works for any application
    """
    print("\n" + "="*60)
    print("🔐 TEST CREDENTIALS SETUP")
    print("="*60)
    print("Enter credentials for your application.\n")

    valid_username = input(
        "✅ Valid username/email: "
    ).strip()

    valid_password = input(
        "✅ Valid password: "
    ).strip()

    print("\nFor negative tests:")
    
    invalid_username = input(
        "❌ Invalid username/email: "
    ).strip() or "wrong_user@test.com"

    invalid_password = input(
        "❌ Invalid password: "
    ).strip() or "WrongPass123"

    locked_username = input(
        "🔒 Locked/blocked username (or Enter to skip): "
    ).strip() or None

    print("="*60)

    return {
        "valid": {
            "username": valid_username,
            "password": valid_password,
            "description": "Valid credentials"
        },
        "invalid": {
            "username": invalid_username,
            "password": invalid_password,
            "description": "Invalid credentials"
        },
        "locked": {
            "username": locked_username,
            "password": valid_password,
            "description": "Locked account"
        } if locked_username else None
    }


def run_agent(user_story: str, url: str, credentials: dict):
    """
    Main agent pipeline v2.0:
    1. Generate test cases
    2. Generate Playwright tests
    3. Save Playwright tests
    4. Log to Jira
    5. Export markdown report
    6. Print summary
    """

    # STEP 1 — Generate Test Cases
    print("\n" + "="*60)
    print("📋 STEP 1: Generating test cases...")
    print("="*60)
    test_cases = generate_test_cases(user_story)
    print(test_cases)

    # STEP 2 — Generate Playwright Tests
    print("\n" + "="*60)
    print("🎭 STEP 2: Generating Playwright tests...")
    print("="*60)
    playwright_tests = generate_playwright_tests(
        user_story, 
        test_cases,
        url
    )
    print(playwright_tests)

    # STEP 3 — Save Playwright Tests
    print("\n" + "="*60)
    print("💾 STEP 3: Saving Playwright tests...")
    print("="*60)
    playwright_files = save_playwright_tests(playwright_tests)

     
    # STEP 3.5 — Generate Test Data
    print("\n" + "="*60)
    print("📊 STEP 3.5: Generating test data...")
    print("="*60)
    test_data = generate_test_data(
        user_story,
        test_cases,
        credentials  # NEW - pass credentials
    )
    data_file = save_test_data(test_data)
    print(f"  ✅ Test data: {data_file}")

    # STEP 4 — Log to Jira
    print("\n" + "="*60)
    print("🎯 STEP 4: Creating Jira tickets...")
    print("="*60)
    created_issues = log_test_cases_to_jira(
        user_story, 
        test_cases
    )

    # STEP 5 — Export Markdown Report
    print("\n" + "="*60)
    print("📄 STEP 5: Exporting markdown report...")
    print("="*60)
    report_file = export_to_markdown(
        user_story=user_story,
        test_cases=test_cases,
        playwright_tests=playwright_tests,
        jira_tickets=created_issues
    )

    
    # STEP 6 — Summary
    print("\n" + "="*60)
    print("✅ COMPLETE — SUMMARY")
    print("="*60)
    print(f"  ✔ Test cases generated  : {len(created_issues)}")
    for f in playwright_files:
        print(f"  ✔ Saved: {f}")
        print(f"  ✔ Test data saved       : {data_file}")
    print(f"  ✔ Jira tickets created  : {len(created_issues)}")
    if created_issues:
        print(f"  ✔ Ticket IDs           : {', '.join(created_issues)}")
        jira_url = os.getenv("JIRA_BASE_URL")
        print(f"  🔗 View board          : {jira_url}/jira/software/projects/SCRUM/boards")
    print(f"  ✔ Report saved         : {report_file}")
    print("="*60 + "\n")


if __name__ == "__main__":
    print(BANNER)

    user_story = get_user_story()
    if not user_story:
        print("❌ No user story provided. Exiting.")
        sys.exit(1)

    url = get_app_url()
    credentials = get_app_credentials()
    run_agent(user_story, url, credentials)