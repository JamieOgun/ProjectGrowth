from fastapi.testclient import TestClient

from growth_op_agent.api import app as api_app
from growth_op_agent.api.helper import build_analytics_overview


def test_analytics_overview_endpoint_maps_supabase_rows(monkeypatch):
    monkeypatch.setattr(
        api_app,
        "select_daily_metrics",
        lambda days: [
            {
                "date": "2026-05-04",
                "total_posts": 1,
                "avg_likes": 4,
                "avg_retweets": 1,
                "avg_replies": 0,
                "avg_impressions": 50,
                "engagement_rate": 0.1,
                "top_posts": [
                    {
                        "id": "post-1",
                        "text": "A useful hook for operators",
                        "post_type": "post",
                        "published_at": "2026-05-04T09:00:00Z",
                        "likes": 4,
                        "retweets": 1,
                        "replies": 0,
                        "impressions": 50,
                    }
                ],
                "refreshed_at": "2026-05-06T12:00:00Z",
            }
        ],
    )
    monkeypatch.setattr(
        api_app,
        "select_audience_metrics",
        lambda days: [
            {"date": "2026-05-04", "followers": 100},
            {"date": "2026-05-05", "followers": 108},
        ],
    )
    monkeypatch.setattr(
        api_app,
        "select_latest_weekly_insights",
        lambda: {
            "strategic_takeaways": ["Specific hooks worked."],
            "suggested_content_adjustments": ["Use more concrete numbers."],
        },
    )

    response = TestClient(api_app.app).get("/api/analytics/overview?days=7")

    assert response.status_code == 200
    payload = response.json()
    assert payload["stat_cards"][0]["label"] == "impressions"
    assert payload["stat_cards"][0]["value"] == "50"
    assert payload["stat_cards"][1]["value"] == "108"
    assert payload["stat_cards"][1]["delta"] == "+8"
    assert payload["engagement_series"] == [10.0]
    assert payload["weekly_insight"]["summary"] == "Specific hooks worked."
    assert payload["weekly_insight"]["suggestions"] == ["Use more concrete numbers."]
    assert payload["posts"][0]["format"] == "post"
    assert payload["posts"][0]["eng"] == 5
    assert payload["posts"][0]["rate"] == 10.0


def test_analytics_overview_rejects_invalid_days():
    response = TestClient(api_app.app).get("/api/analytics/overview?days=0")

    assert response.status_code == 422


def test_build_analytics_overview_handles_empty_rows():
    overview = build_analytics_overview(7, [], [], None)

    assert overview.stat_cards[0].value == "0"
    assert overview.follower_series == []
    assert overview.engagement_series == []
    assert overview.weekly_insight is None
    assert overview.posts == []


def test_build_analytics_overview_formats_structured_insights():
    overview = build_analytics_overview(
        7,
        [],
        [],
        {
            "strategic_takeaways": [
                {"takeaway": "Personal posts work", "detail": "Replies increased."}
            ],
            "suggested_content_adjustments": [
                {
                    "adjustment": "Post more build notes",
                    "reasoning": "They map to the target audience.",
                }
            ],
        },
    )

    assert overview.weekly_insight is not None
    assert overview.weekly_insight.summary == "Personal posts work: Replies increased."
    assert overview.weekly_insight.suggestions == [
        "Post more build notes: They map to the target audience."
    ]
