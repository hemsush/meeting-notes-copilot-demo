from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class SummarizeRequest(BaseModel):
    ticket_id: str = Field(
        ...,
        min_length=1,
        description="JIRA or tracking ticket ID",
        examples=["PROJ-123"],
    )
    notes: str = Field(
        ...,
        min_length=1,
        description="Raw meeting notes to be summarized",
        examples=[
            "Alice will deploy the service by Friday. Bob needs to update the docs. "
            "Risk: dependency on external API not yet confirmed."
        ],
    )

    @field_validator("ticket_id", "notes")
    @classmethod
    def strip_and_validate(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must not be empty or whitespace")
        return cleaned

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ticket_id": "PROJ-123",
                    "notes": (
                        "Alice will deploy the service by Friday. "
                        "Bob needs to update the docs. "
                        "Risk: dependency on external API not yet confirmed."
                    ),
                }
            ]
        }
    }


class ActionItem(BaseModel):
    task: str = Field(..., description="Description of the action item")
    owner: Optional[str] = Field(None, description="Person or team responsible for the task")
    due_date: Optional[str] = Field(None, description="Due date or deadline for the task")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "task": "Alice will deploy the service by Friday",
                    "owner": "Alice",
                    "due_date": "by Friday",
                }
            ]
        }
    }


class SummarizeResponse(BaseModel):
    ticket_id: str = Field(..., description="The ticket ID from the request")
    summary: str = Field(..., description="High-level summary of the meeting notes")
    action_items: List[ActionItem] = Field(
        ..., description="List of action items extracted from the notes"
    )
    risks: List[str] = Field(
        ..., description="List of risks or blockers identified in the notes"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ticket_id": "PROJ-123",
                    "summary": (
                        "The meeting reviewed progress and identified follow-up work, "
                        "ownership, and operational risks."
                    ),
                    "action_items": [
                        {
                            "task": "Alice will deploy the service by Friday",
                            "owner": "Alice",
                            "due_date": "by Friday",
                        }
                    ],
                    "risks": ["dependency on external API not yet confirmed"],
                }
            ]
        }
    }
