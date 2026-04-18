from fastapi import FastAPI

from app.models import SummarizeRequest, SummarizeResponse
from app.service import summarize_notes

_DESCRIPTION = """
## Meeting Notes Summarizer API

Automatically extract **summaries**, **action items**, and **risks** from raw meeting notes.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Liveness check |
| POST | `/summarize` | Summarize meeting notes |

### Usage

1. Supply a tracking ticket ID and the raw text of your meeting notes.
2. The API returns a structured summary with action items (owner, due date) and identified risks.
"""

_TAGS_METADATA = [
    {
        "name": "health",
        "description": "Service liveness and readiness checks.",
    },
    {
        "name": "summarize",
        "description": "Extract summaries, action items, and risks from meeting notes.",
    },
]

app = FastAPI(
    title="Meeting Notes Summarizer",
    version="1.0.0",
    description=_DESCRIPTION,
    openapi_tags=_TAGS_METADATA,
    contact={
        "name": "Meeting Notes Copilot Demo",
        "url": "https://github.com/hemsush/meeting-notes-copilot-demo",
    },
    license_info={
        "name": "MIT",
    },
)


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    response_description="Service status",
    responses={200: {"content": {"application/json": {"example": {"status": "ok"}}}}},
)
def health() -> dict[str, str]:
    """Return a simple liveness status for the service."""
    return {"status": "ok"}


@app.post(
    "/summarize",
    tags=["summarize"],
    summary="Summarize meeting notes",
    response_model=SummarizeResponse,
    response_description="Structured meeting summary with action items and risks",
    responses={
        200: {
            "description": "Successfully summarized meeting notes",
            "model": SummarizeResponse,
        },
        422: {
            "description": "Validation error — e.g. empty ticket_id or notes",
        },
    },
)
def summarize(request: SummarizeRequest) -> SummarizeResponse:
    """
    Summarize raw meeting notes for a given ticket.

    - **ticket_id**: JIRA or tracking ticket ID (e.g. `PROJ-123`)
    - **notes**: Free-form meeting notes text

    Returns a `SummarizeResponse` containing:
    - A high-level **summary** of the meeting
    - Extracted **action items** with optional owner and due date
    - Identified **risks** or blockers
    """
    return summarize_notes(request)
