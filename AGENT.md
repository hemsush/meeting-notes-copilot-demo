## Set Up
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
