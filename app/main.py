from fastapi import FastAPI

from app.models import SummarizeRequest, SummarizeResponse
from app.service import summarize_notes

app = FastAPI(title="Meeting Notes Summarizer Demo", version="1.0.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest) -> SummarizeResponse:
    return summarize_notes(request)
