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
    sections = {
        "type": "",
        "priority": "",
        "preconditions": "",
        "test_data": [],
        "steps": [],
        "expected_result": "",
        "compliance": ""
    }

    current_section = None
    lines = test_case_text.split("\n")

    for line in lines:
        line = line.strip()
        if not line or line.startswith("##"):
            continue

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
    content_blocks = []

    # ── Test Info ──
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

    # ── Compliance Mapping ──
    if sections.get("compliance"):
        content_blocks.append({
            "type": "heading",
            "attrs": {"level": 3},
            "content": [{"type": "text", "text": "🏛️ Compliance Mapping"}]
        })
        content_blocks.append({
            "type": "paragraph",
            "content": [
                {"type": "text", "text": "Regulatory Control: ",
                 "marks": [{"type": "strong"}]},
                {"type": "text", "text": sections["compliance"]}
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

    # ── Footer ──
    content_blocks.append({"type": "rule"})
    content_blocks.append({
        "type": "paragraph",
        "content": [{
            "type": "text",
            "text": "Auto-generated by TestGen AI | Built by Ahtsham Ijaz",
            "marks": [{"type": "em"}]
        }]
    })

    return {
        "type": "doc",
        "version": 1,
        "content": content_blocks
    }


def create_jira_ticket(
    summary: str,
    sections: dict,
    issue_type: str = "Task"
) -> dict:
    url = f"{JIRA_BASE_URL}/rest/api/3/issue"

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": build_jira_description(sections),
            "issuetype": {"name": issue_type},
            "labels": ["testgen-ai"]
        }
    }

    response = requests.post(
        url, json=payload, headers=headers, auth=auth
    )

    if response.status_code == 201:
        issue_key = response.json().get("key")
        print(f"  ✅ Jira ticket created: {issue_key} — {summary}")
        return {"success": True, "issue_key": issue_key}
    else:
        print(f"  ❌ Failed: {response.status_code} - {response.text}")
        return {"success": False, "error": response.text}


def log_test_cases_to_jira(
    user_story: str,
    test_cases_text: str,
    compliance_framework: str = "None",
    compliance_matrix: dict = None
) -> list:
    """
    Parses generated test cases and logs each as a
    Jira ticket with optional compliance mapping.
    """
    sections = test_cases_text.split("## TEST CASE")
    created_issues = []

    # Build compliance lookup: test description → control
    control_lookup = {}
    if compliance_matrix and compliance_framework != "None":
        for mapping in compliance_matrix.get("mappings", []):
            if mapping["status"] == "Covered":
                control_lookup[
                    mapping["test"].lower()
                ] = mapping

    for section in sections:
        section = section.strip()
        if not section:
            continue

        lines = section.split("\n")
        first_line = lines[0].strip()

        if ":" in first_line:
            title = first_line.split(":", 1)[1].strip()
        else:
            title = first_line

        title = title.replace("**", "").strip()

        # Match compliance control to this test
        compliance_note = ""
        for key, mapping in control_lookup.items():
            if any(
                word in title.lower()
                for word in key.split()
                if len(word) > 4
            ):
                compliance_note = (
                    f"{compliance_framework}: "
                    f"{mapping['control_id']} — "
                    f"{mapping['control_title']}"
                )
                break

        # Build summary with compliance tag
        if compliance_note:
            summary = f"[QA][{compliance_framework}] {title}"
        else:
            summary = f"[QA] {title}"

        parsed = parse_test_case_sections(section)

        if compliance_note:
            parsed["compliance"] = compliance_note

        result = create_jira_ticket(
            summary=summary,
            sections=parsed,
            issue_type="Task"
        )

        if result["success"]:
            created_issues.append(result["issue_key"])

    return created_issues


def create_bug_ticket(
    summary: str,
    failure_analysis: str,
    test_name: str,
    error_message: str,
    app_url: str,
    screenshot_path: str = None
) -> dict:
    """
    Creates a professional Jira BUG ticket with AI analysis,
    steps to reproduce, nature of bug and screenshot.
    """
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
        {
            "type": "heading",
            "attrs": {"level": 2},
            "content": [{"type": "text", "text": "🤖 AI Failure Analysis"}]
        },
        {
            "type": "paragraph",
            "content": [{"type": "text", "text": failure_analysis}]
        },
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
        {"type": "rule"},
        {
            "type": "paragraph",
            "content": [{
                "type": "text",
                "text": "Auto-generated by TestGen AI Failure Analyzer | Built by Ahtsham Ijaz",
                "marks": [{"type": "em"}]
            }]
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
        if screenshot_path and os.path.exists(screenshot_path):
            attach_screenshot(issue_key, screenshot_path)
        return {"success": True, "issue_key": issue_key}
    else:
        print(f"  ❌ Failed: {response.status_code} - {response.text}")
        return {"success": False, "error": response.text}


def attach_screenshot(issue_key: str, screenshot_path: str) -> bool:
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/attachments"
    attach_headers = {"X-Atlassian-Token": "no-check"}

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
