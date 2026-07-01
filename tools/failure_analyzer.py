import os
import json
import base64
import subprocess
import anthropic
from dotenv import load_dotenv
from tools.jira_tool import create_bug_ticket

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)


def run_playwright_tests(test_path: str = "generated") -> dict:
    """
    Runs only the most recently modified spec file.
    """
    tests_dir = os.path.join(test_path, "tests")

    spec_files = [
        f for f in os.listdir(tests_dir)
        if f.endswith('.spec.js')
        and 'debug' not in f
    ]

    if not spec_files:
        return {"error": "No spec files found"}

    latest_spec = max(
        spec_files,
        key=lambda f: os.path.getmtime(
            os.path.join(tests_dir, f)
        )
    )

    print(f"🎭 Running: {latest_spec}")

    result = subprocess.run(
        [
            "npx", "playwright", "test",
            f"tests/{latest_spec}",
            "--reporter=json",
            "--output=test-results"
        ],
        cwd=test_path,
        capture_output=True,
        text=True
    )

    try:
        results = json.loads(result.stdout)
    except json.JSONDecodeError:
        results = {"error": "Could not parse results"}

    return results


def encode_screenshot(screenshot_path: str) -> str:
    """
    Encodes screenshot to base64 for Claude Vision.
    """
    if os.path.exists(screenshot_path):
        with open(screenshot_path, "rb") as f:
            return base64.standard_b64encode(f.read()).decode("utf-8")
    return None


def analyze_failure_with_claude(
    test_name: str,
    error_message: str,
    screenshot_base64: str = None
) -> str:
    """
    Sends failure details to Claude.
    Returns plain English explanation.
    """
    print(f"  🤖 Analyzing failure: {test_name}")

    content = []

    if screenshot_base64:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": screenshot_base64
            }
        })

    content.append({
        "type": "text",
        "text": f"""You are a senior QA engineer analyzing a test failure.

Test Name: {test_name}

Error Message:
{error_message}

{"The screenshot above shows what the browser displayed when the test failed." if screenshot_base64 else "No screenshot available."}

Provide a concise plain English analysis (3-5 sentences max):
1. What failed and why
2. Most likely root cause
3. Suggested fix for the development team

Write as if explaining to a non-technical project manager.
Be specific, clear and actionable.
Do not use technical jargon without explanation."""
    })

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": content}]
    )

    return message.content[0].text


def find_screenshot(test_name: str, results_dir: str) -> str:
    """
    Finds screenshot for a failed test.
    """
    if not os.path.exists(results_dir):
        return None

    clean_name = test_name.replace(" ", "-").replace("/", "-")[:30]

    for folder in os.listdir(results_dir):
        if clean_name.lower() in folder.lower():
            screenshot = os.path.join(
                results_dir, folder, "test-failed-1.png"
            )
            if os.path.exists(screenshot):
                return screenshot

    return None


def analyze_and_log_failures(
    app_url: str,
    test_path: str = "generated",
    log_to_jira: bool = True
) -> dict:
    """
    Main function:
    1. Runs Playwright tests
    2. Finds all failures
    3. Analyzes each with Claude
    4. Creates Jira bug tickets
    5. Returns full report
    """
    results_dir = os.path.join(test_path, "test-results")

    raw_results = run_playwright_tests(test_path)

    if "error" in raw_results:
        return {"error": raw_results["error"]}

    failures = []
    passed = 0
    total = 0

    suites = raw_results.get("suites", [])

    def extract_tests(suite):
        nonlocal passed, total

        for spec in suite.get("specs", []):
            for test in spec.get("tests", []):
                total += 1
                status = test.get("status", "")

                error_msg = ""
                for result in test.get("results", []):
                    for error in result.get("errors", []):
                        error_msg += error.get("message", "") + "\n"

                if status in ["failed", "timedOut", "unexpected"]:
                    failures.append({
                        "name": spec.get("title", "Unknown Test"),
                        "error": error_msg.strip(),
                        "file": spec.get("file", "")
                    })
                else:
                    passed += 1

        for child in suite.get("suites", []):
            extract_tests(child)

    for suite in suites:
        extract_tests(suite)

    print(f"DEBUG: total={total} passed={passed} failures={len(failures)}")

    analysis_results = []
    bug_tickets = []

    for failure in failures:
        screenshot_path = find_screenshot(failure["name"], results_dir)
        screenshot_b64 = encode_screenshot(screenshot_path) \
            if screenshot_path else None

        analysis = analyze_failure_with_claude(
            test_name=failure["name"],
            error_message=failure["error"],
            screenshot_base64=screenshot_b64
        )

        analysis_results.append({
            "test": failure["name"],
            "error": failure["error"],
            "analysis": analysis,
            "screenshot": screenshot_path
        })

        if log_to_jira:
            bug = create_bug_ticket(
                summary=failure["name"],
                failure_analysis=analysis,
                test_name=failure["name"],
                error_message=failure["error"],
                app_url=app_url,
                screenshot_path=screenshot_path
            )
            if bug["success"]:
                bug_tickets.append(bug["issue_key"])

    return {
        "total": total,
        "passed": passed,
        "failed": len(failures),
        "failures": analysis_results,
        "bug_tickets": bug_tickets
    }


def format_report(analysis: dict) -> str:
    """
    Formats analysis into plain English report.
    """
    if "error" in analysis:
        return f"❌ Error running tests: {analysis['error']}"

    lines = []
    lines.append("=" * 50)
    lines.append("🤖 TestGen AI — Failure Analysis Report")
    lines.append("=" * 50)
    lines.append(
        f"\n📊 Summary: {analysis['passed']} passed, "
        f"{analysis['failed']} failed "
        f"out of {analysis['total']} total\n"
    )

    if analysis['failed'] == 0:
        lines.append("✅ All tests passing — no failures to analyze!")
        return "\n".join(lines)

    lines.append(
        f"🐛 Bug tickets created: "
        f"{', '.join(analysis['bug_tickets']) or 'None'}\n"
    )

    for i, failure in enumerate(analysis['failures'], 1):
        lines.append(f"{'─' * 40}")
        lines.append(f"❌ FAILURE {i}: {failure['test']}")
        lines.append(f"{'─' * 40}")
        lines.append(f"\n🤖 AI Analysis:")
        lines.append(failure['analysis'])
        if failure.get('screenshot'):
            lines.append(f"\n📸 Screenshot: {failure['screenshot']}")
        lines.append("")

    lines.append("=" * 50)
    lines.append("Generated by TestGen AI Failure Analyzer")
    lines.append("=" * 50)

    return "\n".join(lines)
