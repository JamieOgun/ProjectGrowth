from pathlib import Path

from click.testing import CliRunner

from growth_op_agent.content import IdeaRecord, IdeaStatus, IdeaStore
from growth_op_agent.intelligence.intelligence import PostIdea
from growth_op_agent.main import cli


def _idea() -> PostIdea:
    return PostIdea(
        content="one useful question beats ten dashboards",
        rationale="Operators respond to practical decision-making prompts.",
        format="short_form",
        estimated_engagement="medium",
    )


def test_import_posts_rejects_display_name_handle():
    result = CliRunner().invoke(cli, ["import-posts", "--handle", "Jamie Ogundiran"])

    assert result.exit_code != 0
    assert "Invalid X handle" in result.output
    assert "@your_username" in result.output


def test_ideas_list_shows_generated_records():
    runner = CliRunner()
    with runner.isolated_filesystem():
        IdeaStore(Path("data/ideas/2026-05-05.json")).save(
            [IdeaRecord(id="idea-1", idea=_idea())]
        )

        result = runner.invoke(cli, ["ideas", "list", "--date", "2026-05-05"])

    assert result.exit_code == 0
    assert "idea-1" in result.output
    assert "generated" in result.output
    assert "short_form" in result.output


def test_ideas_reject_updates_record_status():
    runner = CliRunner()
    with runner.isolated_filesystem():
        path = Path("data/ideas/2026-05-05.json")
        IdeaStore(path).save([IdeaRecord(id="idea-1", idea=_idea())])

        result = runner.invoke(
            cli, ["ideas", "reject", "idea-1", "--date", "2026-05-05"]
        )
        records = IdeaStore(path).load()

    assert result.exit_code == 0
    assert "Rejected idea idea-1" in result.output
    assert records[0].status == IdeaStatus.REJECTED


def test_ideas_reject_reports_unknown_id():
    runner = CliRunner()
    with runner.isolated_filesystem():
        IdeaStore(Path("data/ideas/2026-05-05.json")).save(
            [IdeaRecord(id="idea-1", idea=_idea())]
        )

        result = runner.invoke(
            cli, ["ideas", "reject", "missing", "--date", "2026-05-05"]
        )

    assert result.exit_code != 0
    assert "was not found" in result.output


def test_ideas_list_rejects_invalid_date():
    result = CliRunner().invoke(cli, ["ideas", "list", "--date", "05-05-2026"])

    assert result.exit_code != 0
    assert "YYYY-MM-DD" in result.output
