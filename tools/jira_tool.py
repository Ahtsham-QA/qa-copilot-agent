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


def build_jira_description(user_story: str, test_case_text: str) -> dict:
    """
    Builds a properly structured Jira ADF (Atlassian Document Format) description.
    Separates user story, test steps, and code into clean sections.
    """

    # Split into lines for processing
    lines = test_case_text.strip().split("\n")

    content_blocks = []

    # ── User Story Section ──
    content_blocks.append({
        "type": "heading",
        "attrs": {"level": 3},
        "content": [{"type": "text", "text": "User Story"}]
    })
    content_blocks.append({
        "type": "paragraph",
        "content": [{"type": "text", "text": user_story.strip()}]
    })

    # ── Test Case Details Section ──
    content_blocks.append({
        "type": "heading",
        "attrs": {"level": 3},
        "content": [{"type": "text", "text": "Test Case Details"}]
    })

    # Process lines — detect code blocks separately
    in_code_block = False
    code_lines = []
    paragraph_lines = []

    def flush_paragraph(blocks, lines):
        """Push accumulated paragraph lines as a block."""
        text = "\n".join(lines).strip()
        if text:
            blocks.append({
                "type": "paragraph",
                "content": [{"type": "text", "text": text}]
            })

    for line in lines:
        if line.strip().startswith("```"):
            if not in_code_block:
                # Flush any pending paragraph first
                flush_paragraph(content_blocks, paragraph_lines)
                paragraph_lines = []
                in_code_block = True
                code_lines = []
            else:
                # End of code block — flush it
                in_code_block = False
                content_blocks.append({
                    "type": "codeBlock",
                    "attrs": {"language": "javascript"},
                    "content": [{"type": "text", "text": "\n".join(code_lines)}]
                })
                code_lines = []
        elif in_code_block:
            code_lines.append(line)
        else:
            paragraph_lines.append(line)

    # Flush any remaining paragraph lines
    flush_paragraph(content_blocks, paragraph_lines)

    return {
        "type": "doc",
        "version": 1,
        "content": content_blocks
    }


def create_jira_ticket(summary: str, user_story: str, test_case_text: str, issue_type: str = "Task") -> dict:
    """
    Creates a Jira ticket with properly formatted description.
    """

    url = f"{JIRA_BASE_URL}/rest/api/3/issue"

    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": build_jira_description(user_story, test_case_text),
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
    Parses generated test cases and logs each one as a separate Jira ticket.
    """

    sections = test_cases_text.split("## TEST CASE")
    created_issues = []

    for section in sections:
        section = section.strip()
        if not section:
            continue

        # Extract title from first line
        lines = section.split("\n")
        first_line = lines[0].strip()

        if ":" in first_line:
            title = first_line.split(":", 1)[1].strip()
        else:
            title = first_line

        # Remove markdown bold from title if present
        title = title.replace("**", "").strip()

        summary = f"[QA] {title}"

        result = create_jira_ticket(
            summary=summary,
            user_story=user_story,
            test_case_text=section,
            issue_type="Task"
        )

        if result["success"]:
            created_issues.append(result["issue_key"])

    return created_issues