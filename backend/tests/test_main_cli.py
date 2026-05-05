from click.testing import CliRunner

from growth_op_agent.main import cli


def test_import_posts_rejects_display_name_handle():
    result = CliRunner().invoke(cli, ["import-posts", "--handle", "Jamie Ogundiran"])

    assert result.exit_code != 0
    assert "Invalid X handle" in result.output
    assert "@your_username" in result.output
