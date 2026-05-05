import pytest

from growth_op_agent.intelligence.intelligence import _parse_ideas, _parse_json_object


def test_parse_json_object_strips_markdown_fence():
    raw = '```json\n{"takeaways": ["A"], "adjustments": ["B"]}\n```'

    parsed = _parse_json_object(raw)

    assert parsed == {"takeaways": ["A"], "adjustments": ["B"]}


def test_parse_json_object_reports_non_json_preview():
    with pytest.raises(ValueError, match="Claude returned non-JSON"):
        _parse_json_object("Here are the insights...")


def test_parse_ideas_reports_malformed_json_preview():
    with pytest.raises(ValueError, match="Claude returned malformed idea JSON"):
        _parse_ideas('[{"content": "unfinished')
