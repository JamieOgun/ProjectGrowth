import urllib.error

from growth_op_agent import supabase


def test_upsert_rows_uses_write_key(monkeypatch):
    captured = {}

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

    def capture(req, timeout):
        captured["authorization"] = req.headers["Authorization"]
        captured["apikey"] = req.headers["Apikey"]
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(supabase, "SUPABASE_WRITE_KEY", "service-role-key")
    monkeypatch.setattr(supabase.urllib.request, "urlopen", capture)

    supabase.upsert_rows("daily_metrics", [{"date": "2026-05-04"}], "date")

    assert captured == {
        "authorization": "Bearer service-role-key",
        "apikey": "service-role-key",
        "timeout": 10,
    }


def test_upsert_rows_logs_network_errors_without_raising(monkeypatch, capsys):
    def fail(_req, timeout):
        raise urllib.error.URLError("offline")

    monkeypatch.setattr(supabase.urllib.request, "urlopen", fail)

    supabase.upsert_rows("daily_metrics", [{"date": "2026-05-04"}], "date")

    assert "daily_metrics upsert failed: offline" in capsys.readouterr().out
