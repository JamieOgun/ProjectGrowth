"""Tracks weekly audience counts."""
import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field

from growth_op_agent.analytics.performance import WeekOf


FOLLOW_SNAPSHOTS_PATH = Path("data/performance/follow_snapshots.json")


class FollowSnapshot(BaseModel):
    week_of: WeekOf
    captured_at: datetime
    followers: int = Field(ge=0)
    unfollowers: int | None = Field(default=None, ge=0)
    following: int | None = Field(default=None, ge=0)


class FollowSummary(BaseModel):
    current: FollowSnapshot
    previous: FollowSnapshot | None = None
    follower_change: int | None = None
    following_change: int | None = None


class FollowTracker:
    def __init__(self, snapshots_path: Path | None = None) -> None:
        self._snapshots_path = snapshots_path or FOLLOW_SNAPSHOTS_PATH
        self._snapshots_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._snapshots_path.exists():
            self._snapshots_path.write_text("[]")

    def record_weekly_snapshot(
        self,
        followers: int,
        unfollowers: int | None = None,
        following: int | None = None,
        captured_at: datetime | None = None,
    ) -> FollowSnapshot:
        """Record or replace this week's follower and unfollower counts."""
        captured_at = captured_at or datetime.now(timezone.utc)
        iso = captured_at.isocalendar()
        snapshot = FollowSnapshot(
            week_of=WeekOf(year=iso.year, week=iso.week),
            captured_at=captured_at,
            followers=followers,
            unfollowers=unfollowers,
            following=following,
        )

        snapshots = [
            item for item in self._load_snapshots()
            if item.week_of.year != snapshot.week_of.year or item.week_of.week != snapshot.week_of.week
        ]
        snapshots.append(snapshot)
        snapshots.sort(key=lambda item: (item.week_of.year, item.week_of.week))
        self._save_snapshots(snapshots)
        return snapshot

    def latest_summary(self) -> FollowSummary | None:
        snapshots = self._load_snapshots()
        if not snapshots:
            return None

        current = snapshots[-1]
        previous = snapshots[-2] if len(snapshots) > 1 else None
        return FollowSummary(
            current=current,
            previous=previous,
            follower_change=(
                current.followers - previous.followers
                if previous is not None else None
            ),
            following_change=(
                current.following - previous.following
                if previous is not None
                and current.following is not None
                and previous.following is not None
                else None
            ),
        )

    def _load_snapshots(self) -> list[FollowSnapshot]:
        return [
            FollowSnapshot.model_validate(item)
            for item in json.loads(self._snapshots_path.read_text())
        ]

    def _save_snapshots(self, snapshots: list[FollowSnapshot]) -> None:
        payload = [item.model_dump(mode="json") for item in snapshots]
        self._snapshots_path.write_text(json.dumps(payload, indent=2))
