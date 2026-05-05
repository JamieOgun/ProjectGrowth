from datetime import datetime, timezone

from growth_op_agent.analytics.follow_tracker import FollowTracker


def test_follow_tracker_records_weekly_snapshot_and_change(tmp_path):
    tracker = FollowTracker(snapshots_path=tmp_path / "follow_snapshots.json")
    tracker.record_weekly_snapshot(
        followers=100,
        unfollowers=2,
        captured_at=datetime(2026, 4, 27, 9, tzinfo=timezone.utc),
    )
    tracker.record_weekly_snapshot(
        followers=108,
        unfollowers=1,
        captured_at=datetime(2026, 5, 4, 9, tzinfo=timezone.utc),
    )

    summary = tracker.latest_summary()

    assert summary is not None
    assert summary.current.followers == 108
    assert summary.current.unfollowers == 1
    assert summary.follower_change == 8


def test_follow_tracker_summarizes_following_change(tmp_path):
    tracker = FollowTracker(snapshots_path=tmp_path / "follow_snapshots.json")
    tracker.record_weekly_snapshot(
        followers=100,
        following=40,
        captured_at=datetime(2026, 4, 27, 9, tzinfo=timezone.utc),
    )
    tracker.record_weekly_snapshot(
        followers=108,
        following=45,
        captured_at=datetime(2026, 5, 4, 9, tzinfo=timezone.utc),
    )

    summary = tracker.latest_summary()

    assert summary is not None
    assert summary.follower_change == 8
    assert summary.following_change == 5


def test_follow_tracker_replaces_snapshot_for_same_week(tmp_path):
    tracker = FollowTracker(snapshots_path=tmp_path / "follow_snapshots.json")
    tracker.record_weekly_snapshot(
        followers=100,
        captured_at=datetime(2026, 5, 4, 9, tzinfo=timezone.utc),
    )
    tracker.record_weekly_snapshot(
        followers=105,
        captured_at=datetime(2026, 5, 5, 9, tzinfo=timezone.utc),
    )

    summary = tracker.latest_summary()

    assert summary is not None
    assert summary.current.followers == 105
    assert summary.previous is None
