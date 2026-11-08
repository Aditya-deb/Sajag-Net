from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_runs_without_errors(monkeypatch):
    monkeypatch.chdir(ROOT)
    at = AppTest.from_file(str(ROOT / "app" / "dashboard.py"), default_timeout=180)
    at.run()
    assert not at.exception, [str(e.value) for e in at.exception]
    assert len(at.button) > 0, "no button found on the dashboard"
    at.button[0].click().run()
    assert not at.exception, [str(e.value) for e in at.exception]
