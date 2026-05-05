from datetime import datetime, timezone

import pytest

from growth_op_agent.content.idea_store import IdeaRecord, IdeaStatus, IdeaStore
from growth_op_agent.intelligence.intelligence import PostIdea


def _idea() -> PostIdea:
    return PostIdea(
        content="one useful question beats ten dashboards",
        rationale="Operators respond to practical decision-making prompts.",
        format="short_form",
        estimated_engagement="medium",
    )


def test_idea_store_persists_generated_records(tmp_path):
    path = tmp_path / "ideas.json"
    store = IdeaStore(path)

    records = store.replace_generated([_idea()])
    loaded = store.load()

    assert len(records) == 1
    assert loaded[0].id == records[0].id
    assert loaded[0].status == IdeaStatus.GENERATED
    assert loaded[0].idea.content == "one useful question beats ten dashboards"


def test_idea_store_loads_legacy_post_idea_payload(tmp_path):
    path = tmp_path / "ideas.json"
    path.write_text(
        """
[
  {
    "content": "legacy idea",
    "rationale": "legacy rationale",
    "format": "short_form",
    "estimated_engagement": "low"
  }
]
"""
    )

    loaded = IdeaStore(path).load()

    assert loaded[0].status == IdeaStatus.GENERATED
    assert loaded[0].idea.content == "legacy idea"


def test_idea_record_allows_rejecting_generated_idea():
    record = IdeaRecord(idea=_idea())
    now = datetime(2026, 5, 5, 12, tzinfo=timezone.utc)

    updated = record.transition(IdeaStatus.REJECTED, now=now)

    assert updated.status == IdeaStatus.REJECTED
    assert updated.updated_at == now
    assert record.status == IdeaStatus.GENERATED


def test_idea_record_rejects_transition_from_rejected():
    record = IdeaRecord(idea=_idea()).transition(IdeaStatus.REJECTED)

    with pytest.raises(ValueError, match="Cannot move idea"):
        record.transition(IdeaStatus.GENERATED)
