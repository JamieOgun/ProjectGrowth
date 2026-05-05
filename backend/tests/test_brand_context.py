from growth_op_agent.brand import BrandContext


def test_brand_loads_voice_brief_and_format_templates(tmp_path):
    path = tmp_path / "brand.yaml"
    path.write_text(
        """
brand:
  name: "Jamie"
  handle: "@jamie"
audience: "founders"
voice_brief: |
  Write with practical conviction.
strategy_brief: |
  Build authority around practical AI products.
content_territories:
  - "AI products in production"
defaults:
  max_chars: 1000
formats:
  - name: "short_form"
    purpose: "Make one point."
    max_chars: 280
    template: |
      Observation:
      Takeaway:
"""
    )

    brand = BrandContext.from_yaml(path)

    assert brand.voice_brief.strip() == "Write with practical conviction."
    assert (
        brand.strategy_brief.strip() == "Build authority around practical AI products."
    )
    assert brand.content_territories == ["AI products in production"]
    assert brand.formats[0].name == "short_form"
    assert brand.formats[0].template.strip() == "Observation:\nTakeaway:"


def test_system_prompt_includes_format_library():
    brand = BrandContext(
        name="Jamie",
        handle="@jamie",
        voice_brief="Write with practical conviction.",
        strategy_brief="Build authority around practical AI products.",
        content_territories=["AI products in production"],
        target_audience="founders",
        post_max_chars=1000,
        formats=[
            {
                "name": "long_form",
                "purpose": "Explain a point of view.",
                "max_chars": 1000,
                "template": "Hook:\nArgument:\nTakeaway:",
            }
        ],
    )

    prompt = brand.to_system_prompt()

    assert "Brand voice:" in prompt
    assert "Stable content strategy:" in prompt
    assert "AI products in production" in prompt
    assert "Format library:" in prompt
    assert "long_form" in prompt
    assert "Hook:" in prompt
