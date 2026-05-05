"""Persistence models for generated ideas and their review state."""

import json
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from uuid import uuid4

from pydantic import BaseModel, Field

from growth_op_agent.intelligence.intelligence import PostIdea


class IdeaStatus(str, Enum):
    GENERATED = "generated"
    REJECTED = "rejected"


ALLOWED_TRANSITIONS = {
    IdeaStatus.GENERATED: {IdeaStatus.REJECTED},
    IdeaStatus.REJECTED: set(),
}


class IdeaRecord(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    idea: PostIdea
    status: IdeaStatus = IdeaStatus.GENERATED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def transition(
        self,
        status: IdeaStatus,
        *,
        now: datetime | None = None,
    ) -> "IdeaRecord":
        if status == self.status:
            return self.model_copy()
        if status not in ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(
                f"Cannot move idea from {self.status.value} to {status.value}."
            )

        return self.model_copy(
            update={
                "status": status,
                "updated_at": now or datetime.now(timezone.utc),
            }
        )


class IdeaStore:
    def __init__(self, path: Path) -> None:
        self._path = path

    def replace_generated(self, ideas: list[PostIdea]) -> list[IdeaRecord]:
        records = [IdeaRecord(idea=idea) for idea in ideas]
        self.save(records)
        return records

    def load(self) -> list[IdeaRecord]:
        if not self._path.exists():
            return []
        payload = json.loads(self._path.read_text())
        return [_record_from_payload(item) for item in payload]

    def save(self, records: list[IdeaRecord]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = [record.model_dump(mode="json") for record in records]
        self._path.write_text(json.dumps(payload, indent=2))


def _record_from_payload(item: dict) -> IdeaRecord:
    if "idea" in item:
        return IdeaRecord.model_validate(item)
    return IdeaRecord(idea=PostIdea.model_validate(item))
