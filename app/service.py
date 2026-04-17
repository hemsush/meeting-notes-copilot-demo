from __future__ import annotations

import logging
import re
from typing import List, Set

from app.models import ActionItem, SummarizeRequest, SummarizeResponse

logger = logging.getLogger(__name__)

_OWNER_PATTERN = re.compile(r"\b([A-Z][a-zA-Z]+|DevOps|QA|Team)\b")
_DUE_PATTERN = re.compile(
    r"\b(by\s+(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|tomorrow|next\s+week))\b",
    re.IGNORECASE,
)
_RISK_PATTERN = re.compile(r"\b(?:Risk|Blocker|Issue)\s*:\s*([^\.\n]+)", re.IGNORECASE)
# Matches decision-signal phrases such as "decided to", "agreed to", "approved", etc.
# Bounded quantifier prevents ReDoS on long inputs lacking sentence delimiters.
_DECISION_PATTERN = re.compile(
    r"\b(?:decided|agreed|approved|confirmed|resolved|concluded)\b[^.\n]{0,500}",
    re.IGNORECASE,
)
# Matches lines that list attendees / participants explicitly.
# Use bounded quantifiers to avoid ReDoS on inputs with many spaces.
_PARTICIPANTS_HEADER = re.compile(
    r"^(?:participants?|attendees?|present|invited)[ \t]{0,20}[:\-]?[ \t]{0,20}([^\n\r]+)$",
    re.IGNORECASE,
)
# Capitalised first-name tokens that likely represent people (≥3 chars, not all-caps acronyms).
# Bounded space between tokens to avoid backtracking on many consecutive spaces.
_NAME_TOKEN = re.compile(r"\b([A-Z][a-z]{2,}(?:[ ]{1,3}[A-Z][a-z]{2,})?)\b")
# Words that look like names but are common English / technical terms we want to exclude.
_NON_NAME_WORDS = frozenset(
    {
        "The", "This", "That", "Team", "Risk", "Issue", "Blocker", "Meeting",
        "Sprint", "Friday", "Monday", "Tuesday", "Wednesday", "Thursday",
        "Saturday", "Sunday", "Action", "Follow", "Review", "Next", "Today",
        "Tomorrow", "API", "UI", "QA", "DevOps",
    }
)


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


def _extract_decisions(sentences: List[str]) -> List[str]:
    """Return sentences that contain decision-signal language."""
    decisions: List[str] = []
    for sentence in sentences:
        if _DECISION_PATTERN.search(sentence):
            decisions.append(sentence.strip())
    return decisions


def _extract_participants(notes: str) -> List[str]:
    """Extract participant names from the transcript.

    Two strategies are applied in order:
    1. Look for an explicit "Participants / Attendees" header line.
    2. Fall back to collecting capitalised name tokens from the full text.
    """
    participants: List[str] = []

    for line in notes.splitlines():
        header_match = _PARTICIPANTS_HEADER.match(line.strip())
        if header_match:
            # Names may be comma- or semicolon-separated on the header line.
            raw = header_match.group(1)
            participants = [p.strip() for p in re.split(r"[,;]+", raw) if p.strip()]
            logger.debug("Participants extracted from header: %s", participants)
            return participants

    # Fallback: harvest capitalised tokens that look like personal names.
    seen: Set[str] = set()
    for match in _NAME_TOKEN.finditer(notes):
        name = match.group(1)
        if name not in _NON_NAME_WORDS and name not in seen:
            seen.add(name)
            participants.append(name)

    logger.debug("Participants extracted via name-token fallback: %s", participants)
    return participants


def summarize_notes(request: SummarizeRequest) -> SummarizeResponse:
    notes = request.notes.strip()
    sentences = _split_sentences(notes)

    logger.info("Processing notes for ticket %s (%d sentences)", request.ticket_id, len(sentences))

    summary_sentence = (
        "The meeting reviewed progress and identified follow-up work, ownership, and operational risks."
        if sentences
        else "No meaningful meeting content was provided."
    )

    action_items = _extract_action_items(sentences)
    risks = _extract_risks(notes)
    decisions = _extract_decisions(sentences)
    participants = _extract_participants(notes)

    if not action_items:
        action_items = [
            ActionItem(
                task="Review meeting notes and identify explicit follow-up actions",
                owner="Team Lead",
                due_date=None,
            )
        ]

    logger.debug(
        "Extraction complete — decisions: %d, action_items: %d, risks: %d, participants: %d",
        len(decisions),
        len(action_items),
        len(risks),
        len(participants),
    )

    return SummarizeResponse(
        ticket_id=request.ticket_id,
        summary=summary_sentence,
        decisions=decisions,
        action_items=action_items,
        risks=risks,
        participants=participants,
    )
