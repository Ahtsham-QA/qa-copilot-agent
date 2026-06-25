import os
import sys
from dotenv import load_dotenv
from tools.test_generator import generate_test_cases
from tools.jira_tool import log_test_cases_to_jira

load_dotenv()

BANNER = """
╔══════════════════════════════════════════════════════════╗
║           🤖 QA COPILOT AGENT v1.0                      ║
║     AI-Powered Test Case Generator + Jira Logger        ║
║     Built by: Ahtsham Ijaz | github.com/Ahtsham-QA     ║
╚══════════════════════════════════════════════════════════╝
"""

def get_user_story() -> str:
    """
    Gets user story either from command line argument or interactive prompt.
    """
    # If passed as command line argument
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])

    # Otherwise prompt interactively
    print("\nPaste your user story below.")
    print("When done, press Enter twice:\n")

    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)

    return "\n".join(lines).strip()


def run_agent(user_story: str):
    """
    Main agent pipeline:
    1. Generate Playwright test cases from user story
    2. Log each test case as a Jira ticket
    3. Print summary
    """

    print("\n" + "="*60)
    print("📋 STEP 1: Generating test cases...")
    print("="*60)
    test_cases = generate_test_cases(user_story)
    print(test_cases)

    print("\n" + "="*60)
    print("🎯 STEP 2: Logging to Jira...")
    print("="*60)
    created_issues = log_test_cases_to_jira(user_story, test_cases)

    print("\n" + "="*60)
    print("✅ COMPLETE — SUMMARY")
    print("="*60)
    print(f"  ✔ Test cases generated : {len(created_issues)}")
    print(f"  ✔ Jira tickets created : {len(created_issues)}")
    if created_issues:
        print(f"  ✔ Ticket IDs          : {', '.join(created_issues)}")
        jira_url = os.getenv("JIRA_BASE_URL")
        print(f"  🔗 View board         : {jira_url}/jira/software/projects/SCRUM/boards")
    print("="*60 + "\n")


if __name__ == "__main__":
    print(BANNER)

    user_story = get_user_story()

    if not user_story:
        print("❌ No user story provided. Exiting.")
        sys.exit(1)

    run_agent(user_story)