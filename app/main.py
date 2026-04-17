from fastapi import FastAPI, HTTPException

from app.models import SummarizeRequest, SummarizeResponse, WikiEntry, WikiPublishRequest
from app.service import get_wiki_entries, get_wiki_entry, publish_to_wiki, summarize_notes

app = FastAPI(title="Meeting Notes Summarizer Demo", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest) -> SummarizeResponse:
    return summarize_notes(request)


@app.post("/wiki", response_model=WikiEntry, status_code=201)
def create_wiki_entry(request: WikiPublishRequest) -> WikiEntry:
    return publish_to_wiki(request)


@app.get("/wiki", response_model=list[WikiEntry])
def list_wiki_entries() -> list[WikiEntry]:
    return get_wiki_entries()


@app.get("/wiki/{ticket_id}", response_model=WikiEntry)
def read_wiki_entry(ticket_id: str) -> WikiEntry:
    entry = get_wiki_entry(ticket_id)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Wiki entry for ticket '{ticket_id}' not found")
    return entry
