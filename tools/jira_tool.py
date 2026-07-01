import os
import requests
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def parse_test_case_sections(test_case_text: str) -> dict:
    """
    Parses a test case block into structured sections.
    Returns a dict with keys: type, priority, preconditions, 
    test_data, steps, expected_result
    """
    sections = {
        "type": "",
        "priority": "",
        "preconditions": "",
        "test_data": [],
        "steps": [],
        "expected_result": ""
    }

    current_section = None
    lines = test_case_text.split("\n")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("##"):
            continue

        # Detect sections
        if line.startswith("- Type:"):
            sections["type"] = line.replace("- Type:", "").strip()
        elif line.startswith("- Priority:"):
            sections["priority"] = line.replace("- Priority:", "").strip()
        elif line.startswith("- Preconditions:"):
            sections["preconditions"] = line.replace("- Preconditions:", "").strip()
            current_section = "preconditions"
        elif line.startswith("- Test Data:"):
            current_section = "test_data"
        elif line.startswith("- Steps:"):
            current_section = "steps"
        elif line.startswith("- Expected Result:"):
            sections["expected_result"] = line.replace("- Expected Result:", "").strip()
            current_section = "expected_result"
        elif current_section == "test_data" and line.startswith("*"):
            sections["test_data"].append(line.replace("*", "").strip())
        elif current_section == "steps" and line[0].isdigit():
            sections["steps"].append(line)
        elif current_section == "expected_result" and sections["expected_result"] == "":
            sections["expected_result"] = line

    return sections


def build_jira_description(sections: dict) -> dict:
    """
    Builds a clean Jira ADF description from parsed sections.
    No code blocks — only structured readable content.
    """

    content_blocks = []

    # ── Test Info Section ──
    content_blocks.append({
        "type": "heading",
        "attrs": {"level": 3},
        "content": [{"type": "text", "text": "Test Information"}]
    })
    content_blocks.append({
        "type": "paragraph",
        "content": [
            {"type": "text", "text": "Type: ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": sections["type"]}
        ]
    })
    content_blocks.append({
        "type": "paragraph",
        "content": [
            {"type": "text", "text": "Priority: ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": sections["priority"]}
        ]
    })

    # ── Preconditions ──
    if sections["preconditions"]:
        content_blocks.append({
            "type": "heading",
            "attrs": {"level": 3},
            "content": [{"type": "text", "text": "Preconditions"}]
        })
        content_blocks.append({
            "type": "paragraph",
            "content": [{"type": "text", "text": sections["preconditions"]}]
        })

    # ── Test Data ──
    if sections["test_data"]:
        content_blocks.append({
            "type": "heading",
            "attrs": {"level": 3},
            "content": [{"type": "text", "text": "Test Data"}]
        })
        test_data_items = []
        for item in sections["test_data"]:
            test_data_items.append({
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": item}]
                }]
            })
        content_blocks.append({
            "type": "bulletList",
            "content": test_data_items
        })

    # ── Steps ──
    if sections["steps"]:
        content_blocks.append({
            "type": "heading",
            "attrs": {"level": 3},
            "content": [{"type": "text", "text": "Test Steps"}]
        })
        step_items = []
        for step in sections["steps"]:
            step_items.append({
                "type": "listItem",
                "content": [{
                    "type": "paragraph",
                    "content": [{"type": "text", "text": step}]
                }]
            })
        content_blocks.append({
            "type": "orderedList",
            "content": step_items
        })

    # ── Expected Result ──
    if sections["expected_result"]:
        content_blocks.append({
            "type": "heading",
            "attrs": {"level": 3},
            "content": [{"type": "text", "text": "Expected Result"}]
        })
        content_blocks.append({
            "type": "paragraph",
            "content": [{"type": "text", "text": sections["expected_result"]}]
        })

    return {
        "type": "doc",
        "version": 1,
        "content": content_blocks
    }


def create_jira_ticket(summary: str, sections: dict, issue_type: str = "Task") -> dict:
    """
    Creates a clean Jira ticket with structured description.
    """

    url = f"{JIRA_BASE_URL}/rest/api/3/issue"

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": build_jira_description(sections),
            "issuetype": {"name": issue_type}
        }
    }

    response = requests.post(url, json=payload, headers=headers, auth=auth)

    if response.status_code == 201:
        issue_key = response.json().get("key")
        print(f"  ✅ Jira ticket created: {issue_key} — {summary}")
        return {"success": True, "issue_key": issue_key}
    else:
        print(f"  ❌ Failed: {response.status_code} - {response.text}")
        return {"success": False, "error": response.text}


def log_test_cases_to_jira(user_story: str, test_cases_text: str) -> list:
    """
    Parses generated test cases and logs each as a clean Jira ticket.
    """

    sections = test_cases_text.split("## TEST CASE")
    created_issues = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract title
        lines = section.split("\n")
        first_line = lines[0].strip()

        if ":" in first_line:
            title = first_line.split(":", 1)[1].strip()
        else:
            title = first_line

        title = title.replace("**", "").strip()
        summary = f"[QA] {title}"

        # Parse sections
        parsed = parse_test_case_sections(section)

        result = create_jira_ticket(
            summary=summary,
            sections=parsed,
            issue_type="Task"
        )

        if result["success"]:
            created_issues.append(result["issue_key"])

    return created_issues


# Quick test
if __name__ == "__main__":
    test_sections = {
        "type": "Positive",
        "priority": "High",
        "preconditions": "User must have an active account",
        "test_data": [
            "Email: testuser@example.com",
            "Password: SecurePass123!",
            "URL: /login"
        ],
        "steps": [
            "1. Navigate to login page",
            "2. Enter email and password",
            "3. Click Login button"
        ],
        "expected_result": "User is redirected to dashboard"
    }

    result = create_jira_ticket(
        summary="[QA] Smoke test ticket - clean format",
        sections=test_sections
    )
    print(result)

def create_bug_ticket(
    summary: str,
    failure_analysis: str,
    test_name: str,
    error_message: str,
    app_url: str,
    screenshot_path: str = None
) -> dict:
    """
    Creates a professional Jira BUG ticket
    with AI analysis, steps to reproduce,
    nature of bug and screenshot attachment.
    """

    # Determine bug nature from error
    if "timeout" in error_message.lower():
        bug_nature = "Performance / Timeout Issue"
        priority = "High"
    elif "selector" in error_message.lower() or \
         "locator" in error_message.lower():
        bug_nature = "UI Element Not Found"
        priority = "High"
    elif "url" in error_message.lower():
        bug_nature = "Navigation / Redirect Issue"
        priority = "Critical"
    elif "credentials" in error_message.lower() or \
         "login" in error_message.lower():
        bug_nature = "Authentication Failure"
        priority = "Critical"
    elif "assertion" in error_message.lower() or \
         "expect" in error_message.lower():
        bug_nature = "Functional Assertion Failure"
        priority = "High"
    else:
        bug_nature = "Automated Test Failure"
        priority = "Medium"

    content_blocks = [
        # AI Analysis Section
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "🤖 AI Failure Analysis"}]
        },
        {
            "type": "panel",
            "attrs": {"panelType": "warning"},
            "content": [{
                "type": "paragraph",
                "content": [{"type": "text", "text": failure_analysis}]
            }]
        } if False else {
            "type": "paragraph",
            "content": [{"type": "text", "text": failure_analysis}]
        },

        # Bug Nature
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "🔍 Nature of Bug"}]
        },
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Category: ",
                 "marks": [{"type": "strong"}]},
                {"type": "text", "text": bug_nature}
            ]
        },
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Severity: ",
                 "marks": [{"type": "strong"}]},
                {"type": "text", "text": priority}
            ]
        },
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Detected By: ",
                 "marks": [{"type": "strong"}]},
                {"type": "text", "text": "TestGen AI Automated Test Suite"}
            ]
        },

        # Test Details
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "📋 Test Information"}]
        },
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Test Name: ",
                 "marks": [{"type": "strong"}]},
                {"type": "text", "text": test_name}
            ]
        },
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Application URL: ",
                 "marks": [{"type": "strong"}]},
                {"type": "text", "text": app_url}
            ]
        },

        # Steps to Reproduce
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "🔄 Steps to Reproduce"}]
        },
        {
            "type": "orderedList",
            "content": [
                {
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text",
                                     "text": f"Navigate to: {app_url}"}]
                    }]
                },
                {
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text",
                                     "text": f"Execute test: {test_name}"}]
                    }]
                },
                {
                    "type": "listItem",
                    "content": [{
                        "type": "paragraph",
                        "content": [{"type": "text",
                                     "text": "Observe the failure as described above"}]
                    }]
                }
            ]
        },

        # Expected vs Actual
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "✅ Expected vs ❌ Actual"}]
        },
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Expected: ",
                 "marks": [{"type": "strong"}]},
                {"type": "text", "text": "Test should pass without errors"}
            ]
        },
        {
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Actual: ",
                 "marks": [{"type": "strong"}]},
                {"type": "text", "text": f"Test failed — {bug_nature}"}
            ]
        },

        # Raw Error
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "🔴 Raw Error Log"}]
        },
        {
            "type": "codeBlock",
            "attrs": {"language": "text"},
            "content": [{"type": "text", "text": error_message[:2000]}]
        },

        # Footer
        {
            "type": "rule"
        },
        {
            "type": "paragraph",
            "content": [
                {
                    "type": "text",
                    "text": "Auto-generated by TestGen AI Failure Analyzer | "
                            "Built by Ahtsham Ijaz",
                    "marks": [{"type": "em"}]
                }
            ]
        }
    ]

    url_endpoint = f"{JIRA_BASE_URL}/rest/api/3/issue"

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": f"[BUG] {test_name} — {bug_nature}",
            "description": {
                "type": "doc",
                "version": 1,
                "content": content_blocks
            },
            "issuetype": {"name": "Bug"},
            "priority": {"name": priority},
            "labels": ["testgen-ai", "automated-detection"]
        }
    }

    response = requests.post(
        url_endpoint,
        json=payload,
        headers=headers,
        auth=auth
    )

    if response.status_code == 201:
        issue_key = response.json().get("key")
        print(f"  🐛 Bug ticket created: {issue_key}")

        # Attach screenshot if available
        if screenshot_path and os.path.exists(screenshot_path):
            attach_screenshot(issue_key, screenshot_path)

        return {"success": True, "issue_key": issue_key}
    else:
        print(f"  ❌ Failed: {response.status_code} - {response.text}")
        return {"success": False, "error": response.text}


def attach_screenshot(issue_key: str, screenshot_path: str) -> bool:
    """
    Attaches screenshot to Jira ticket.
    """
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/attachments"

    attach_headers = {
        "X-Atlassian-Token": "no-check"
    }

    try:
        with open(screenshot_path, "rb") as f:
            response = requests.post(
                url,
                headers=attach_headers,
                auth=auth,
                files={"file": (
                    "failure-screenshot.png",
                    f,
                    "image/png"
                )}
            )

        if response.status_code == 200:
            print(f"  📸 Screenshot attached to {issue_key}")
            return True
        else:
            print(f"  ⚠️ Screenshot attach failed: {response.status_code}")
            return False

    except Exception as e:
        print(f"  ⚠️ Screenshot error: {str(e)}")
        return False