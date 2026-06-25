# 🤖 QA Copilot Agent

An AI-powered QA automation agent that generates professional Playwright 
test cases from user stories and automatically logs them as Jira tickets.

Built by [Ahtsham Ijaz](https://github.com/Ahtsham-QA) — QA Automation Lead & Consultant.

---

## What It Does

1. Takes a user story as input
2. Uses Claude AI to generate structured Playwright test cases
3. Automatically creates Jira tickets for each test case
4. Each ticket includes user story, test steps, and Playwright code

---

## Tech Stack

| Layer | Tool |
|---|---|
| AI Model | Anthropic Claude API |
| Test Framework | Playwright (JavaScript) |
| Project Management | Jira Cloud REST API |
| Language | Python 3.9+ |

---

## Project Structure

    qa-copilot-agent/
    ├── agent.py                  # Main entry point
    ├── tools/
    │   ├── test_generator.py     # Claude AI test case generator
    │   └── jira_tool.py          # Jira REST API integration
    ├── .env                      # API keys (never committed)
    ├── .env.example              # Safe template for others
    ├── .gitignore
    └── README.md
---

## Setup

### 1. Clone the repo
    git clone https://github.com/Ahtsham-QA/qa-copilot-agent.git
    cd qa-copilot-agent

### 2. Create virtual environment
    python3 -m venv venv
    source venv/bin/activate

### 3. Install dependencies
    pip install anthropic python-dotenv requests

### 4. Configure environment variables
    cp .env.example .env

Then open `.env` and fill in your actual API keys.

---

## Environment Variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Get from console.anthropic.com |
| `JIRA_BASE_URL` | Your Jira domain e.g. https://yourname.atlassian.net |
| `JIRA_EMAIL` | Email you use to log into Jira |
| `JIRA_API_TOKEN` | Get from id.atlassian.com/manage-profile/security |
| `JIRA_PROJECT_KEY` | Your Jira project key e.g. SCRUM |

---

## Usage

### Interactive mode
    python3 agent.py

Paste your user story when prompted, then press Enter twice.

### Inline mode
    python3 agent.py "As a user I want to reset my password so I can regain access"

---

## Skills Demonstrated

- AI agent architecture and prompt engineering
- Anthropic Claude API integration
- Jira REST API with ADF (Atlassian Document Format)
- Python project structure and virtual environments
- Real-world QA automation thinking
- CI-ready modular code structure

---

## Author

**Ahtsham Ijaz** — QA Automation Lead & Consultant
GitHub: https://github.com/Ahtsham-QA
LinkedIn: https://www.linkedin.com/in/ahtshamijaz1984/