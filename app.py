import streamlit as st
import os
import json
import shutil
from dotenv import load_dotenv
from tools.test_generator import generate_test_cases
from tools.playwright_gen import generate_playwright_tests
from tools.jira_tool import log_test_cases_to_jira
from tools.data_generator import (
    generate_test_data,
    save_test_data
)
from tools.markdown_export import export_to_markdown

load_dotenv()

# Page config
st.set_page_config(
    page_title="TestGen AI",
    page_icon="🤖",
    layout="wide"
)

# Header
st.title("🤖 TestGen AI")
st.subheader("AI-Powered Universal Test Suite Generator")
st.markdown(
    "Built by **Ahtsham Ijaz** | "
    "Senior QA Lead & AI Consultant"
)
st.markdown("---")

# Input Section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 App Configuration")
    app_url = st.text_input(
        "🌐 Application URL",
        placeholder="https://your-app.com"
    )
    feature = st.text_area(
        "📝 Feature Description",
        placeholder="user can login with valid credentials",
        height=120
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

st.markdown("---")

# Browser Options
st.subheader("🌐 Browser Options")
col_b1, col_b2, col_b3 = st.columns(3)

with col_b1:
    run_chrome = st.checkbox("Chrome", value=True)
with col_b2:
    run_firefox = st.checkbox("Firefox", value=False)
with col_b3:
    run_safari = st.checkbox("Safari", value=False)

# Generate Options
st.subheader("⚙️ Options")
col3, col4, col5 = st.columns(3)

with col3:
    gen_playwright = st.checkbox(
        "🎭 Playwright Tests",
        value=True
    )
with col4:
    gen_jira = st.checkbox(
        "🎫 Jira Tickets",
        value=True
    )
with col5:
    gen_report = st.checkbox(
        "📄 Markdown Report",
        value=True
    )

st.markdown("---")

# Helper functions
def copy_templates(actual_login_url: str) -> list:
    """
    Copies template files to generated folder.
    Updates APP_URL in spec.js.
    Returns list of copied files.
    """
    template_dir = "templates"
    pages_dir = "generated/pages"
    tests_dir = "generated/tests"

    os.makedirs(pages_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    copied = []

    # Copy LoginPage.js
    if os.path.exists(f"{template_dir}/LoginPage.js"):
        shutil.copy(
            f"{template_dir}/LoginPage.js",
            f"{pages_dir}/LoginPage.js"
        )
        copied.append(f"{pages_dir}/LoginPage.js")

    # Copy InventoryPage.js
    if os.path.exists(f"{template_dir}/InventoryPage.js"):
        shutil.copy(
            f"{template_dir}/InventoryPage.js",
            f"{pages_dir}/InventoryPage.js"
        )
        copied.append(f"{pages_dir}/InventoryPage.js")

    # Copy spec.js and update APP_URL
    if os.path.exists(f"{template_dir}/login.spec.js"):
        with open(f"{template_dir}/login.spec.js", 'r') as f:
            spec_content = f.read()

        # Replace APP_URL with actual URL
        spec_content = spec_content.replace(
            "process.env.APP_URL || 'https://www.saucedemo.com'",
            f"'{actual_login_url}'"
        )

        with open(f"{tests_dir}/login.spec.js", 'w') as f:
            f.write(spec_content)

        copied.append(f"{tests_dir}/login.spec.js")

    return copied


def generate_config(
    run_chrome: bool,
    run_firefox: bool,
    run_safari: bool
) -> str:
    """Generates playwright.config.js"""
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


# Generate Button
if st.button("🚀 Generate Everything", type="primary"):

    # Validation
    if not feature:
        st.error("❌ Please enter a feature description")
    elif not app_url:
        st.error("❌ Please enter application URL")
    elif not valid_username or not valid_password:
        st.error("❌ Please enter valid credentials")
    else:
        # Build actual login URL
        if login_path:
            actual_login_url = app_url.rstrip('/') + login_path
        else:
            actual_login_url = app_url

        st.info(f"🔗 Login URL: {actual_login_url}")

        # Build credentials
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

        # Progress bar
        progress = st.progress(0)
        status = st.empty()

        # STEP 1 — Test Cases
        status.text("📋 Generating test cases...")
        test_cases = generate_test_cases(
            feature,
            credentials  # ← pass credentials
        )

        # STEP 2 — Test Data
        status.text("📊 Generating test data...")
        test_data = generate_test_data(
            feature,
            test_cases,
            credentials
        )
        save_test_data(test_data)
        progress.progress(40)

        # STEP 3 — Playwright Tests from Templates
        copied_files = []
        config_content = ""

        if gen_playwright:
            status.text("🎭 Copying Playwright templates...")

            # Copy templates with correct URL
            copied_files = copy_templates(actual_login_url)

            # Read template content for display
            login_page_content = ""
            inventory_page_content = ""
            spec_content = ""

            if os.path.exists("generated/pages/LoginPage.js"):
                with open("generated/pages/LoginPage.js") as f:
                    login_page_content = f.read()

            if os.path.exists("generated/pages/InventoryPage.js"):
                with open("generated/pages/InventoryPage.js") as f:
                    inventory_page_content = f.read()

            if os.path.exists("generated/tests/login.spec.js"):
                with open("generated/tests/login.spec.js") as f:
                    spec_content = f.read()

            # Generate config
            config_content = generate_config(
                run_chrome,
                run_firefox,
                run_safari
            )

            # Save config
            with open('generated/playwright.config.js', 'w') as f:
                f.write(config_content)

            st.success(
                f"✅ {len(copied_files)} template files copied!"
            )

        progress.progress(60)

        # STEP 4 — Jira Tickets
        created_issues = []
        if gen_jira:
            status.text("🎫 Creating Jira tickets...")
            try:
                created_issues = log_test_cases_to_jira(
                    feature,
                    test_cases
                )
            except Exception as e:
                st.warning(f"⚠️ Jira error: {str(e)}")
        progress.progress(80)

        # STEP 5 — Report
        if gen_report:
            status.text("📄 Generating report...")
            export_to_markdown(
                user_story=feature,
                test_cases=test_cases,
                playwright_tests=spec_content if gen_playwright else "",
                jira_tickets=created_issues
            )
        progress.progress(100)
        status.text("✅ Complete!")

        st.balloons()
        st.success("🎉 Everything generated successfully!")
        st.markdown("---")

        # Results Section
        st.subheader("📊 Results")

        # Test Cases
        with st.expander("📋 View Test Cases", expanded=True):
            st.markdown(test_cases)

        # Playwright Tests
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

            # Download buttons
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

            # Download config
            if config_content:
                st.download_button(
                    "⬇️ Download playwright.config.js",
                    config_content,
                    "playwright.config.js",
                    "text/javascript"
                )

        # Jira Results
        if gen_jira and created_issues:
            st.subheader("🎫 Jira Tickets Created")
            for ticket in created_issues:
                st.success(f"✅ {ticket}")

        # Test Data
        with st.expander("📊 View Test Data JSON"):
            st.json(test_data)

        # Full Report Download
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