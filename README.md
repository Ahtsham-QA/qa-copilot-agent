# 🤖 QA Copilot Agent

An AI-powered universal QA automation agent that generates professional 
Playwright test cases, POM structure, test data, and Jira tickets 
automatically from one line of description.

Built by [Ahtsham Ijaz](https://github.com/Ahtsham-QA) — QA Automation Lead & AI QA Consultant.

---

## ✨ Key Features

- 🌐 **Universal** — Works on ANY web application
- 🔐 **Dynamic Credentials** — Enter your own app credentials at runtime
- 🎭 **POM Structure** — Generates Page Object Model automatically
- 📊 **Data Driven** — Separate JSON test data file
- 🎫 **Jira Integration** — Auto creates tickets with ADF format
- 📄 **Documentation** — Generates markdown report automatically
- 🤖 **AI Powered** — Claude Sonnet API for intelligent generation

---

## What It Does

1. Takes a feature description as input
2. Asks for app URL and test credentials
3. Uses Claude AI to generate structured test cases
4. Generates Page Object Model Playwright tests
5. Creates separate JSON test data file
6. Automatically creates Jira tickets for each test case
7. Exports full markdown documentation report

---

## 🚀 What Gets Generated

From one line input:
`python3 agent.py "user can login"`

Agent automatically creates:

| Output | Description |
|--------|-------------|
| Test Cases | Positive, negative, edge cases |
| pages/LoginPage.js | POM class with generic selectors |
| pages/InventoryPage.js | POM class for post-login page |
| tests/login.spec.js | Data driven Playwright spec |
| test-data/test_data.json | Separate JSON test data |
| Jira Tickets | One ticket per test case |
| qa_report.md | Full documentation report |

---

## 📊 Time Savings

| Task | Manual Time | With Agent |
|------|-------------|------------|
| Write test cases | 2-3 hours | 30 seconds |
| Write Playwright tests | 2-3 hours | 30 seconds |
| Create Jira tickets | 45 mins | 30 seconds |
| Write documentation | 45 mins | 30 seconds |
| **Total** | **6-7 hours** | **~2 minutes** |

---

## Tech Stack

| Layer | Tool |
|-------|------|
| AI Model | Anthropic Claude Sonnet API |
| Test Framework | Playwright (JavaScript) |
| Project Management | Jira Cloud REST API |
| Language | Python 3.9+ |
| Test Data | JSON data driven approach |
| Architecture | Page Object Model (POM) |

---

## Project Structure

qa-copilot-agent/
├── agent.py                    # Main entry point
├── tools/
│   ├── test_generator.py       # Claude AI test case generator
│   ├── playwright_gen.py       # POM Playwright code generator
│   ├── data_generator.py       # JSON test data generator
│   ├── jira_tool.py            # Jira REST API integration
│   └── markdown_export.py      # Documentation generator
├── generated/                  # Auto-generated output
│   ├── pages/                  # POM page classes
│   ├── tests/                  # Playwright spec files
│   └── test-data/              # JSON test data files
├── .env                        # API keys (never committed)
├── .env.example                # Safe template for others
├── .gitignore
└── README.md

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/Ahtsham-QA/qa-copilot-agent.git
cd qa-copilot-agent
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Then open `.env` and fill in your actual API keys.

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Get from console.anthropic.com |
| `JIRA_BASE_URL` | Your Jira domain e.g. https://yourname.atlassian.net |
| `JIRA_EMAIL` | Email you use to log into Jira |
| `JIRA_API_TOKEN` | Get from id.atlassian.com/manage-profile/security |
| `JIRA_PROJECT_KEY` | Your Jira project key e.g. SCRUM |

---

## Usage

### Interactive mode
```bash
python3 agent.py
```

### Inline mode
```bash
python3 agent.py "user can login with valid credentials"
```

### Agent will ask for:

🌐 App URL: https://your-app.com
✅ Valid username: your_username
✅ Valid password: your_password
❌ Invalid username: wrong_user
❌ Invalid password: wrong_pass
🔒 Locked username: locked_user

---

## 🌐 Universal App Support

Agent works on ANY web application:

**SauceDemo (username based):**
```bash
python3 agent.py "user can login"
# URL: https://www.saucedemo.com
# Username: standard_user
# Password: secret_sauce
```

**Automation Exercise (email based):**
```bash
python3 agent.py "user can login"
# URL: https://automationexercise.com
# Username: your@email.com
# Password: yourpassword
```

Same agent. Different apps. Everything generated automatically.

---

## Skills Demonstrated

- AI agent architecture and prompt engineering
- Anthropic Claude API integration
- Universal Page Object Model generation
- Data driven testing with JSON
- Jira REST API with ADF (Atlassian Document Format)
- Python project structure and modular design
- Real-world QA automation thinking
- CI-ready modular code structure

---

## ⚠️ Proprietary Software

This software is proprietary and confidential.
Viewing is permitted but copying, modifying,
or distributing requires written permission.

For licensing inquiries contact:
[LinkedIn](https://linkedin.com/in/ahtshamijaz1984/)

---

## 👤 Author

**Ahtsham Ijaz** — QA Automation Lead & AI QA Consultant

- 8 years QA experience | 5 years lead roles
- Specializing in AI-assisted test automation
- Available for QA consulting projects

🔗 [LinkedIn](https://linkedin.com/in/ahtshamijaz1984/)
🐙 [GitHub](https://github.com/Ahtsham-QA)
📧 Open to consulting inquiries