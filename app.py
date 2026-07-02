import streamlit as st
import os
import json
import re
import shutil
from dotenv import load_dotenv
from tools.test_generator import generate_test_cases
from tools.jira_tool import log_test_cases_to_jira
from tools.data_generator import (
    generate_test_data,
    save_test_data
)
from tools.markdown_export import export_to_markdown

load_dotenv()

st.set_page_config(
    page_title="TestGen AI",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 TestGen AI")
st.subheader("AI-Powered Universal Test Suite Generator")
st.markdown(
    "Built by **Ahtsham Ijaz** | "
    "Senior QA Lead & AI Consultant"
)
st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 App Configuration")
    app_url = st.text_input(
        "🌐 Application URL",
        placeholder="https://your-app.com"
    )

    app_profile = st.selectbox(
        "🎯 App Profile",
        [
            "Auto-detect (default)",
            "SauceDemo",
            "OrangeHRM",
            "Generic / Other App"
        ],
        help="Select a known app for guaranteed compatibility"
    )

    feature = st.text_area(
        "📝 Feature Description",
        placeholder="user can login with valid credentials",
        height=120
    )

    feature_type = st.selectbox(
        "🔧 Feature Type",
        [
            "Login / Authentication",
            "Search & Navigation",
            "Form Submission",
            "Shopping Cart"
        ],
        help="Select the type of feature you want to test"
    )

    compliance_framework = st.selectbox(
        "🏛️ Compliance Framework",
        [
            "None",
            "PCI-DSS",
            "HIPAA",
            "SR 11-7",
            "SOX"
        ],
        help="Select a regulatory framework to generate audit-ready traceability matrix"
    )

    login_path = st.text_input(
        "🔗 Login Page Path (optional)",
        placeholder="/login or /signin — leave blank if login is at root URL",
        help="Leave blank for apps like SauceDemo where login is at root URL"
    )
    success_url_contains = st.text_input(
        "✅ Success URL Contains (optional)",
        placeholder="inventory or dashboard",
        help="Text that appears in URL after successful login"
    )

with col2:
    if feature_type == "Login / Authentication":
        st.subheader("🔐 Test Credentials")
        valid_username = st.text_input(
            "✅ Valid Username/Email",
            placeholder="standard_user or email@example.com"
        )
        valid_password = st.text_input(
            "✅ Valid Password",
            placeholder="your password",
            type="password"
        )
        invalid_username = st.text_input(
            "❌ Invalid Username",
            placeholder="wrong_user",
            value="wrong_user"
        )
        invalid_password = st.text_input(
            "❌ Invalid Password",
            placeholder="wrong_pass",
            value="wrong_pass",
            type="password"
        )
    else:
        if feature_type == "Search & Navigation":
            st.subheader("🔍 Search Terms")
            valid_search = st.text_input(
                "✅ Valid Search Term",
                placeholder="e.g. laptop, shirt, John",
                help="Something that exists on your app"
            )
            invalid_search = st.text_input(
                "❌ Invalid Search Term",
                placeholder="e.g. xyznotexist123",
                value="xyznotexist123",
                help="Something that won't return results"
            )
            valid_username = valid_search
            invalid_username = invalid_search
            valid_password = ""
            invalid_password = ""

        elif feature_type == "Form Submission":
            st.subheader("📝 Form Data")
            form_name = st.text_input(
                "👤 Name Field Value",
                placeholder="e.g. John Doe",
                value="John Doe"
            )
            form_email = st.text_input(
                "📧 Email Field Value",
                placeholder="e.g. test@example.com",
                value="test@example.com"
            )
            form_message = st.text_input(
                "💬 Message Field Value",
                placeholder="e.g. This is a test message",
                value="This is a test message"
            )
            valid_username = form_name
            valid_password = form_email
            invalid_username = form_message
            invalid_password = ""

        elif feature_type == "Shopping Cart":
            st.subheader("🛒 Cart Settings")
            st.info(
                "Agent will test adding, removing, "
                "and updating cart items automatically."
            )
            valid_username = ""
            valid_password = ""
            invalid_username = ""
            invalid_password = ""

        else:
            st.subheader("ℹ️ Feature Info")
            st.info(
                f"✅ Test data will be generated "
                f"automatically for **{feature_type}**."
            )
            valid_username = ""
            valid_password = ""
            invalid_username = ""
            invalid_password = ""

st.markdown("---")

st.subheader("🌐 Browser Options")
col_b1, col_b2, col_b3 = st.columns(3)
with col_b1:
    run_chrome = st.checkbox("Chrome", value=True)
with col_b2:
    run_firefox = st.checkbox("Firefox", value=False)
with col_b3:
    run_safari = st.checkbox("Safari", value=False)

st.subheader("⚙️ Options")
col3, col4, col5 = st.columns(3)
with col3:
    gen_playwright = st.checkbox("🎭 Playwright Tests", value=True)
with col4:
    gen_jira = st.checkbox("🎫 Jira Tickets", value=True)
with col5:
    gen_report = st.checkbox("📄 Markdown Report", value=True)

st.markdown("---")


# ============================================================
# Helper functions
# ============================================================

def get_profile_folder(app_profile: str, app_url: str) -> str:
    if app_profile == "SauceDemo":
        return "saucedemo"
    elif app_profile == "OrangeHRM":
        return "orangehrm"
    elif app_profile == "Generic / Other App":
        return "default"
    else:
        if "saucedemo" in app_url.lower():
            return "saucedemo"
        elif "orangehrm" in app_url.lower():
            return "orangehrm"
        else:
            return "default"


def copy_templates(
    actual_login_url: str,
    app_profile: str,
    app_url: str,
    feature_type: str = "Login / Authentication"
) -> list:

    feature_folder_map = {
        "Login / Authentication": "login",
        "Search & Navigation": "search",
        "Form Submission": "form",
        "Shopping Cart": "cart"
    }
    feature_folder = feature_folder_map.get(feature_type, "login")

    if feature_type == "Login / Authentication":
        profile_folder = get_profile_folder(app_profile, app_url)
        template_dir = f"templates/{profile_folder}"
        spec_name = "login.spec.js"
        page_name = "LoginPage.js"
    else:
        template_dir = f"templates/features/{feature_folder}"
        spec_name = f"{feature_folder}.spec.js"
        page_name = f"{feature_folder.capitalize()}Page.js"

    pages_dir = "generated/pages"
    tests_dir = "generated/tests"

    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    copied = []

    if os.path.exists(f"{template_dir}/{page_name}"):
        shutil.copy(
            f"{template_dir}/{page_name}",
            f"{pages_dir}/{page_name}"
        )
        copied.append(f"{pages_dir}/{page_name}")

    if feature_type == "Login / Authentication":
        if os.path.exists(f"{template_dir}/InventoryPage.js"):
            shutil.copy(
                f"{template_dir}/InventoryPage.js",
                f"{pages_dir}/InventoryPage.js"
            )
            copied.append(f"{pages_dir}/InventoryPage.js")

    spec_src = f"{template_dir}/{spec_name}"
    if os.path.exists(spec_src):
        with open(spec_src, 'r') as f:
            spec_content = f.read()

        spec_content = re.sub(
            r"const APP_URL = .*?;",
            f"const APP_URL = '{actual_login_url.strip()}';",
            spec_content
        )

        with open(f"{tests_dir}/{spec_name}", 'w') as f:
            f.write(spec_content)

        copied.append(f"{tests_dir}/{spec_name}")

    if feature_type == "Login / Authentication":
        st.info(
            f"📁 Using profile: "
            f"**{get_profile_folder(app_profile, app_url)}**"
        )
    else:
        st.info(f"📁 Feature type: **{feature_type}**")

    return copied


def generate_config(
    run_chrome: bool,
    run_firefox: bool,
    run_safari: bool
) -> str:
    config_projects = []

    if run_chrome:
        config_projects.append("""
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    }""")
    if run_firefox:
        config_projects.append("""
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    }""")
    if run_safari:
        config_projects.append("""
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    }""")

    projects_str = ','.join(config_projects)

    return f"""const {{ defineConfig, devices }} = require('@playwright/test');

module.exports = defineConfig({{
  testDir: './tests',
  use: {{
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry',
  }},
  reporter: [
    ['html', {{ open: 'never' }}],
    ['list']
  ],
  projects: [{projects_str}
  ],
}});
"""


# ============================================================
# Generate Button
# ============================================================

if st.button("🚀 Generate Everything", type="primary"):

    if not feature:
        st.error("❌ Please enter a feature description")
    elif not app_url:
        st.error("❌ Please enter application URL")
    elif feature_type == "Login / Authentication" and \
         (not valid_username or not valid_password):
        st.error("❌ Please enter valid credentials")
    else:
        if login_path:
            actual_login_url = app_url.strip().rstrip('/') + login_path.strip()
        else:
            actual_login_url = app_url.strip()

        st.info(f"🔗 Login URL: {actual_login_url}")

        credentials = {
            "valid": {
                "username": valid_username,
                "password": valid_password,
                "description": "Valid credentials"
            },
            "invalid": {
                "username": invalid_username,
                "password": invalid_password,
                "description": "Invalid credentials"
            }
        }

        progress = st.progress(0)
        status = st.empty()

        status.text("📋 Generating test cases...")
        test_cases = generate_test_cases(feature, credentials)
        progress.progress(20)

        status.text("📊 Generating test data...")
        test_data = generate_test_data(
            feature, test_cases, credentials, feature_type
        )
        save_test_data(test_data)
        progress.progress(40)

        copied_files = []
        config_content = ""
        login_page_content = ""
        inventory_page_content = ""
        spec_content = ""

        if gen_playwright:
            status.text("🎭 Copying Playwright templates...")

            copied_files = copy_templates(
                actual_login_url,
                app_profile,
                app_url,
                feature_type
            )

            if os.path.exists("generated/pages/LoginPage.js"):
                with open("generated/pages/LoginPage.js") as f:
                    login_page_content = f.read()

            if os.path.exists("generated/pages/InventoryPage.js"):
                with open("generated/pages/InventoryPage.js") as f:
                    inventory_page_content = f.read()

            if os.path.exists("generated/tests/login.spec.js"):
                with open("generated/tests/login.spec.js") as f:
                    spec_content = f.read()

            config_content = generate_config(
                run_chrome, run_firefox, run_safari
            )

            with open('generated/playwright.config.js', 'w') as f:
                f.write(config_content)

            st.success(
                f"✅ {len(copied_files)} template files copied!"
            )

        progress.progress(60)

        # Compliance Traceability Matrix — build FIRST
        compliance_matrix = None
        if compliance_framework != "None":
            status.text("🏛️ Building compliance matrix...")
            from tools.compliance.traceability import (
                build_traceability_matrix,
                format_matrix_report
            )
            compliance_matrix = build_traceability_matrix(
                compliance_framework,
                test_data,
                feature
            )

        created_issues = []
        if gen_jira:
            status.text("🎫 Creating Jira tickets...")
            try:
                created_issues = log_test_cases_to_jira(
                    feature,
                    test_cases,
                    compliance_framework,
                    compliance_matrix
                )
            except Exception as e:
                st.warning(f"⚠️ Jira error: {str(e)}")
        progress.progress(80)

        if gen_report:
            status.text("📄 Generating report...")
            export_to_markdown(
                user_story=feature,
                test_cases=test_cases,
                playwright_tests=spec_content if gen_playwright else "",
                jira_tickets=created_issues
            )
        progress.progress(80)

        if gen_report:
            status.text("📄 Generating report...")
            export_to_markdown(
                user_story=feature,
                test_cases=test_cases,
                playwright_tests=spec_content if gen_playwright else "",
                jira_tickets=created_issues
            )

        # Compliance Traceability Matrix
        compliance_matrix = None
        if compliance_framework != "None":
            status.text("🏛️ Building compliance matrix...")
            from tools.compliance.traceability import (
                build_traceability_matrix,
                format_matrix_report
            )
            compliance_matrix = build_traceability_matrix(
                compliance_framework,
                test_data,
                feature
            )

        progress.progress(100)
        status.text("✅ Complete!")

        st.balloons()
        st.success("🎉 Everything generated successfully!")
        st.markdown("---")

        st.subheader("📊 Results")

        with st.expander("📋 View Test Cases", expanded=True):
            st.markdown(test_cases)

        if gen_playwright and copied_files:
            with st.expander("🎭 View Playwright Tests"):
                tab1, tab2, tab3 = st.tabs([
                    "spec.js",
                    "LoginPage.js",
                    "InventoryPage.js"
                ])
                with tab1:
                    st.code(spec_content, language="javascript")
                with tab2:
                    st.code(login_page_content, language="javascript")
                with tab3:
                    st.code(inventory_page_content, language="javascript")

            col6, col7, col8 = st.columns(3)
            with col6:
                st.download_button(
                    "⬇️ Download spec.js",
                    spec_content,
                    "login.spec.js",
                    "text/javascript"
                )
            with col7:
                st.download_button(
                    "⬇️ Download LoginPage.js",
                    login_page_content,
                    "LoginPage.js",
                    "text/javascript"
                )
            with col8:
                st.download_button(
                    "⬇️ Download InventoryPage.js",
                    inventory_page_content,
                    "InventoryPage.js",
                    "text/javascript"
                )

            if config_content:
                st.download_button(
                    "⬇️ Download playwright.config.js",
                    config_content,
                    "playwright.config.js",
                    "text/javascript"
                )

        if gen_jira and created_issues:
            st.subheader("🎫 Jira Tickets Created")
            for ticket in created_issues:
                st.success(f"✅ {ticket}")

        with st.expander("📊 View Test Data JSON"):
            st.json(test_data)

        if gen_report:
            report = f"""# QA Report
## Feature: {feature}
## App URL: {actual_login_url}

## Test Cases
{test_cases}

## Jira Tickets
{', '.join(created_issues) if created_issues else 'Not generated'}

---
Generated by TestGen AI
Built by Ahtsham Ijaz
github.com/Ahtsham-QA/qa-copilot-agent
"""
            st.download_button(
                "⬇️ Download Full Report",
                report,
                "qa_report.md",
                "text/markdown"
            )

        # Compliance Matrix Results
        if compliance_matrix:
            st.markdown("---")
            st.subheader("🏛️ Compliance Traceability Matrix")

            cov = compliance_matrix["coverage"]
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                st.metric("Framework", compliance_framework)
            with col_c2:
                st.metric(
                    "Controls Covered",
                    f"{cov['covered_controls']}/{cov['total_controls']}"
                )
            with col_c3:
                st.metric(
                    "Coverage",
                    f"{cov['coverage_percent']}%"
                )

            with st.expander(
                "📋 Test-to-Control Mappings",
                expanded=True
            ):
                for m in compliance_matrix["mappings"]:
                    if m["status"] == "Covered":
                        st.success(
                            f"✅ **{m['test']}**\n\n"
                            f"Control: `{m['control_id']}` — "
                            f"{m['control_title']}"
                        )
                    else:
                        st.info(
                            f"ℹ️ **{m['test']}**\n\n"
                            f"Informational — no compliance control mapped"
                        )

            if cov["uncovered"]:
                with st.expander(
                    "⚠️ Compliance Gaps — Auto-Generated Tests",
                    expanded=True
                ):
                    from tools.compliance.gap_filler import (
                        generate_gap_tests,
                        format_gap_tests_for_spec
                    )

                    gap_tests = generate_gap_tests(
                        compliance_matrix,
                        actual_login_url
                    )

                    for gap in gap_tests:
                        st.warning(
                            f"⚠️ **{gap['control_id']}** — "
                            f"{gap['control_title']}"
                        )
                        st.markdown(
                            f"**Required:** {gap['description']}"
                        )
                        st.code(
                            gap['playwright_test'],
                            language="javascript"
                        )
                        st.markdown("---")

                    if gap_tests:
                        gap_spec = format_gap_tests_for_spec(gap_tests)
                        st.download_button(
                            "⬇️ Download Gap Tests (Playwright)",
                            gap_spec,
                            f"compliance_gap_tests_{compliance_framework}.js",
                            "text/javascript"
                        )

            from tools.compliance.traceability import format_matrix_report
            matrix_report = format_matrix_report(compliance_matrix)
            st.download_button(
                "⬇️ Download Compliance Matrix (Audit Ready)",
                matrix_report,
                f"compliance_matrix_{compliance_framework}.txt",
                "text/plain"
            )


# ============================================================
# AI Failure Analyzer Section
# ============================================================
st.markdown("---")
st.subheader("🔍 AI Failure Analyzer")
st.markdown(
    "Run your generated tests and get AI-powered "
    "plain English analysis of any failures — "
    "with automatic Jira bug tickets created instantly."
)

col_fa1, col_fa2 = st.columns(2)
with col_fa1:
    analyze_url = st.text_input(
        "🌐 App URL (for bug tickets)",
        placeholder="https://your-app.com",
        key="analyze_url"
    )
with col_fa2:
    log_bugs_to_jira = st.checkbox(
        "🎫 Auto-create Jira Bug Tickets",
        value=True,
        key="log_bugs"
    )

if st.button(
    "🚀 Run Tests + Analyze Failures",
    type="primary",
    key="analyze_btn"
):
    if not analyze_url:
        st.error("❌ Please enter the app URL")
    else:
        from tools.failure_analyzer import (
            analyze_and_log_failures,
            format_report
        )

        with st.spinner(
            "🎭 Running tests and analyzing failures with AI..."
        ):
            analysis = analyze_and_log_failures(
                app_url=analyze_url,
                test_path="generated",
                log_to_jira=log_bugs_to_jira
            )
            report = format_report(analysis)

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("Total Tests", analysis.get("total", 0))
        with col_m2:
            st.metric("✅ Passed", analysis.get("passed", 0))
        with col_m3:
            st.metric("❌ Failed", analysis.get("failed", 0))

        if analysis.get("bug_tickets"):
            st.success(
                f"🐛 Auto-created {len(analysis['bug_tickets'])} "
                f"Jira bug tickets: "
                f"{', '.join(analysis['bug_tickets'])}"
            )

        if analysis.get("failures"):
            st.subheader("❌ AI Failure Analysis")
            for i, failure in enumerate(analysis["failures"], 1):
                with st.expander(
                    f"❌ Failure {i}: {failure['test']}",
                    expanded=True
                ):
                    st.markdown("**🤖 AI Analysis (Plain English):**")
                    st.info(failure["analysis"])
                    st.markdown("**Raw Error:**")
                    st.code(failure["error"])
                    if failure.get("screenshot") and \
                       os.path.exists(failure["screenshot"]):
                        st.image(
                            failure["screenshot"],
                            caption="📸 Failure Screenshot"
                        )
        else:
            st.success("✅ All tests passing — nothing to analyze!")

        st.download_button(
            "⬇️ Download Full Analysis Report",
            report,
            "failure_analysis_report.txt",
            "text/plain"
        )


# Footer
st.markdown("---")
col9, col10 = st.columns(2)
with col9:
    st.markdown(
        "🔗 [GitHub](https://github.com/Ahtsham-QA) | "
        "💼 [LinkedIn](https://linkedin.com/in/ahtshamijaz1984/)"
    )
with col10:
    st.markdown(
        "📧 Available for QA Consulting | "
        "🤖 TestGen AI — Powered by Claude"
    )
