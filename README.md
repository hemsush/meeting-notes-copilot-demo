# From Ticket to Tested API with GitHub Copilot

A demo-ready Python project for showing how GitHub Copilot can help move from a simple JIRA-style ticket to:

1. requirement understanding
2. architecture design in Mermaid
3. Python API generation
4. unit test generation

## Demo storyline

Start with a single ticket file. Use Copilot to understand the requirement, produce a Mermaid architecture diagram, scaffold a FastAPI API, and then generate tests.

## Repo structure

```text
meeting-notes-copilot-demo/
├── ticket.txt
├── design.md
├── architecture.mmd
├── prompts/
│   ├── 01_requirements_prompt.md
│   ├── 02_architecture_prompt.md
│   ├── 03_api_prompt.md
│   ├── 04_tests_prompt.md
│   └── 05_refinement_prompt.md
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models.py
│   └── service.py
├── tests/
│   └── test_main.py
├── sample_data/
│   └── meeting_notes.txt
├── requirements.txt
└── .gitignore
```

## Quick start

```bash
python -m venv .venv
```

### Windows

```bash
.venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run the API

```bash
uvicorn app.main:app --reload
```

### Run tests

```bash
pytest -q
```

## API

### Health

`GET /health`

### Summarize meeting notes

`POST /summarize`

Request body:

```json
{
  "ticket_id": "JIRA-241",
  "notes": "Ravi completed login API. Priya will finish dashboard UI by Friday. DevOps needs to confirm deployment access. Risk: staging environment instability."
}
```

Example response:

```json
{
  "ticket_id": "JIRA-241",
  "summary": "The meeting reviewed current progress and identified follow-up work for UI completion and deployment readiness.",
  "action_items": [
    {
      "task": "Finish dashboard UI",
      "owner": "Priya",
      "due_date": "Friday"
    },
    {
      "task": "Confirm deployment access",
      "owner": "DevOps",
      "due_date": null
    }
  ],
  "risks": [
    "staging environment instability"
  ]
}
```

## How to demo this in VS Code

### Step 1: Start from the ticket
Open `ticket.txt` and ask Copilot to extract:
- functional requirements
- non-functional requirements
- ambiguities
- proposed API capabilities

Use `prompts/01_requirements_prompt.md`.

### Step 2: Generate architecture in Mermaid
Open `design.md` and ask Copilot to produce:
- a concise architecture explanation
- a Mermaid flowchart
- design assumptions

Use `prompts/02_architecture_prompt.md`.

### Step 3: Generate Python API
Ask Copilot to scaffold or refine the FastAPI app using the ticket and design.

Use `prompts/03_api_prompt.md`.

### Step 4: Generate tests
Open `tests/test_main.py` and ask Copilot to add or improve test coverage.

Use `prompts/04_tests_prompt.md`.

### Step 5: Discuss refinement
Use `prompts/05_refinement_prompt.md` to show how Copilot can improve the project with production thinking.

## Suggested talk line

> We are not starting from code. We are starting from intent, converting that intent into design, and using AI to accelerate the journey to an executable, testable API.
