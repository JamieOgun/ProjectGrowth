from pathlib import Path
import yaml
from pydantic import BaseModel


class ContentFormat(BaseModel):
    name: str
    purpose: str
    max_chars: int | None = None
    template: str
    example: str | None = None


class BrandContext(BaseModel):
    name: str
    handle: str
    voice_brief: str
    strategy_brief: str
    content_territories: list[str]
    target_audience: str
    post_max_chars: int
    formats: list[ContentFormat]

    @classmethod
    def from_yaml(cls, path: Path) -> "BrandContext":
        data = yaml.safe_load(path.read_text())
        return cls(
            name=data["brand"]["name"],
            handle=data["brand"]["handle"],
            voice_brief=data["voice_brief"],
            strategy_brief=data["strategy_brief"],
            content_territories=data.get("content_territories", []),
            target_audience=data.get("audience", ""),
            post_max_chars=data.get("defaults", {}).get("max_chars", 280),
            formats=[
                ContentFormat.model_validate(item) for item in data.get("formats", [])
            ],
        )

    def update_strategy_brief(self, new_brief: str, yaml_path: Path) -> None:
        data = yaml.safe_load(yaml_path.read_text())
        data["strategy_brief"] = new_brief
        yaml_path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False))

    def update_voice_brief(self, new_brief: str, yaml_path: Path) -> None:
        data = yaml.safe_load(yaml_path.read_text())
        data["voice_brief"] = new_brief
        yaml_path.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False))

    def to_system_prompt(self) -> str:
        territories_str = "\n".join(f"- {item}" for item in self.content_territories)
        formats_str = "\n\n".join(_format_to_prompt(item) for item in self.formats)
        return f"""You are a social media strategist for {self.name} ({self.handle}).

Brand voice:
{self.voice_brief.strip()}

Stable content strategy:
{self.strategy_brief.strip()}

Content territories:
{territories_str}

Target audience: {self.target_audience}.
Default post character limit: {self.post_max_chars}.

Format library:
{formats_str}"""


def _format_to_prompt(content_format: ContentFormat) -> str:
    max_chars = (
        f"\nMax chars: {content_format.max_chars}"
        if content_format.max_chars is not None
        else ""
    )
    example_section = (
        f"\nExample:\n{content_format.example.strip()}"
        if content_format.example
        else ""
    )
    return f"""- {content_format.name}
Purpose: {content_format.purpose}{max_chars}
Template:
{content_format.template.strip()}{example_section}"""
