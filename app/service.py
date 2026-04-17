from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.models import ActionItem, SummarizeRequest, SummarizeResponse, WikiEntry, WikiPublishRequest

_OWNER_PATTERN = re.compile(r"\b([A-Z][a-zA-Z]+|DevOps|QA|Team)\b")
_DUE_PATTERN = re.compile(
    r"\b(by\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|tomorrow|next\s+week))\b",
    re.IGNORECASE,
)
_RISK_PATTERN = re.compile(r"\b(?:Risk|Blocker|Issue)\s*:\s*([^\.\n]+)", re.IGNORECASE)


def _split_sentences(notes: str) -> List[str]:
    return [s.strip() for s in re.split(r"[\.\n]+", notes) if s.strip()]


def _extract_action_items(sentences: List[str]) -> List[ActionItem]:
    items: List[ActionItem] = []
    for sentence in sentences:
        lowered = sentence.lower()
        if any(keyword in lowered for keyword in [" will ", " needs to ", " need to ", " should "]):
            owner_match = _OWNER_PATTERN.search(sentence)
            due_match = _DUE_PATTERN.search(sentence)
            owner = owner_match.group(1) if owner_match else None
            due_date = due_match.group(1) if due_match else None
            task = sentence
            items.append(ActionItem(task=task, owner=owner, due_date=due_date))
    return items


def _extract_risks(notes: str) -> List[str]:
    return [match.strip() for match in _RISK_PATTERN.findall(notes)]


def summarize_notes(request: SummarizeRequest) -> SummarizeResponse:
    notes = request.notes.strip()
    sentences = _split_sentences(notes)

    summary_sentence = (
        "The meeting reviewed progress and identified follow-up work, ownership, and operational risks."
        if sentences
        else "No meaningful meeting content was provided."
    )

    action_items = _extract_action_items(sentences)
    risks = _extract_risks(notes)

    if not action_items:
        action_items = [
            ActionItem(
                task="Review meeting notes and identify explicit follow-up actions",
                owner="Team Lead",
                due_date=None,
            )
        ]

    return SummarizeResponse(
        ticket_id=request.ticket_id,
        summary=summary_sentence,
        action_items=action_items,
        risks=risks,
    )


# In-memory wiki store: ticket_id -> WikiEntry
_wiki_store: Dict[str, WikiEntry] = {}


def publish_to_wiki(request: WikiPublishRequest) -> WikiEntry:
    summarize_req = SummarizeRequest(ticket_id=request.ticket_id, notes=request.notes)
    result = summarize_notes(summarize_req)

    title = request.title.strip() if request.title and request.title.strip() else f"Meeting Notes – {request.ticket_id}"
    now = datetime.now(timezone.utc).isoformat()

    existing = _wiki_store.get(request.ticket_id)
    created_at = existing.created_at if existing else now
    updated_at = now if existing else None

    entry = WikiEntry(
        ticket_id=request.ticket_id,
        title=title,
        summary=result.summary,
        action_items=result.action_items,
        risks=result.risks,
        created_at=created_at,
        updated_at=updated_at,
    )
    _wiki_store[request.ticket_id] = entry
    return entry


def get_wiki_entries() -> List[WikiEntry]:
    return list(_wiki_store.values())


def get_wiki_entry(ticket_id: str) -> Optional[WikiEntry]:
    return _wiki_store.get(ticket_id)
