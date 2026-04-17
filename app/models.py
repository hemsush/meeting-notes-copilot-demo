from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class SummarizeRequest(BaseModel):
    ticket_id: str = Field(..., min_length=1, description="JIRA or tracking ticket ID")
    notes: str = Field(..., min_length=1, description="Raw meeting notes")

    @field_validator("ticket_id", "notes")
    @classmethod
    def strip_and_validate(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be empty or whitespace")
        return cleaned


class ActionItem(BaseModel):
    task: str
    owner: Optional[str] = None
    due_date: Optional[str] = None


class SummarizeResponse(BaseModel):
    ticket_id: str
    summary: str
    decisions: List[str]
    action_items: List[ActionItem]
    risks: List[str]
    participants: List[str]
