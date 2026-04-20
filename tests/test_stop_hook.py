"""Unit tests for scripts/stop.py -- the stop hook turn trigger.

Tests: empty pending returns {}, paused session returns {}, files pending returns
followup_message, RUNNER_REQUIRED_LANGUAGES enforcement, pending cleared after stop,
missing session returns {}, multiple files formatted correctly.
"""

import json
import os
import sys

import pytest

HOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "stop.py")


def _state_path(tmp_path) -> str:
    return str(tmp_path / ".cursor" / "hooks" / "state" / "tailtest.json")


def _write_session(tmp_path, session: dict) -> None:
    state = tmp_path / ".cursor" / "hooks" / "state"
    state.mkdir(parents=True, exist_ok=True)
    with open(state / "tailtest.json", "w") as fh:
        json.dump(session, fh)


def _read_session(tmp_path) -> dict:
    with open(_state_path(tmp_path)) as fh:
        return json.load(fh)


def _run_hook(tmp_path, event: dict | None = None) -> dict:
    import subprocess
    if event is None:
        event = {"workspace_roots": [str(tmp_path)], "status": "completed"}
    result = subprocess.run(
        [sys.executable, HOOK_PATH],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0, f"Hook exited non-zero: {result.stderr}"
    return json.loads(result.stdout)


def _event(tmp_path) -> dict:
    return {"workspace_roots": [str(tmp_path)], "status": "completed"}


def _base_session(**kwargs) -> dict:
    session = {
        "pending_files": [],
        "touched_files": [],
        "runners": {"python": {"command": "pytest", "test_location": "tests/"}},
        "paused": False,
        "fix_attempts": {},
        "deferred_failures": [],
        "generated_tests": {},
        "packages": {},
    }
    session.update(kwargs)
    return session


# ---------------------------------------------------------------------------
# Empty pending_files
# ---------------------------------------------------------------------------


class TestEmptyPendingFiles:
    def test_no_pending_returns_empty_dict(self, tmp_path):
        _write_session(tmp_path, _base_session())
        out = _run_hook(tmp_path, _event(tmp_path))
        assert out == {}

    def test_no_pending_no_followup_message(self, tmp_path):
        _write_session(tmp_path, _base_session())
        out = _run_hook(tmp_path, _event(tmp_path))
        assert "followup_message" not in out


# ---------------------------------------------------------------------------
# Paused session
# ---------------------------------------------------------------------------


class TestPausedSession:
    def test_paused_returns_empty_dict(self, tmp_path):
        session = _base_session(
            paused=True,
            pending_files=[{"path": "billing.py", "language": "python", "status": "new-file"}],
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert out == {}

    def test_paused_does_not_clear_pending(self, tmp_path):
        session = _base_session(
            paused=True,
            pending_files=[{"path": "billing.py", "language": "python", "status": "new-file"}],
        )
        _write_session(tmp_path, session)
        _run_hook(tmp_path, _event(tmp_path))
        saved = _read_session(tmp_path)
        assert len(saved["pending_files"]) == 1


# ---------------------------------------------------------------------------
# followup_message triggered
# ---------------------------------------------------------------------------


class TestFollowupMessageTriggered:
    def test_python_file_returns_followup_message(self, tmp_path):
        session = _base_session(
            pending_files=[{"path": "billing.py", "language": "python", "status": "new-file"}]
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert "followup_message" in out

    def test_followup_message_contains_filename(self, tmp_path):
        session = _base_session(
            pending_files=[{"path": "billing.py", "language": "python", "status": "new-file"}]
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert "billing.py" in out["followup_message"]

    def test_followup_message_contains_tailtest_prefix(self, tmp_path):
        session = _base_session(
            pending_files=[{"path": "billing.py", "language": "python", "status": "new-file"}]
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert out["followup_message"].startswith("tailtest: run tests for:")

    def test_followup_message_contains_runner(self, tmp_path):
        session = _base_session(
            pending_files=[{"path": "billing.py", "language": "python", "status": "new-file"}]
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert "pytest" in out["followup_message"]

    def test_followup_message_contains_state_path_hint(self, tmp_path):
        session = _base_session(
            pending_files=[{"path": "billing.py", "language": "python", "status": "new-file"}]
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert ".cursor/hooks/state/tailtest.json" in out["followup_message"]

    def test_pending_files_cleared_after_stop(self, tmp_path):
        session = _base_session(
            pending_files=[{"path": "billing.py", "language": "python", "status": "new-file"}]
        )
        _write_session(tmp_path, session)
        _run_hook(tmp_path, _event(tmp_path))
        saved = _read_session(tmp_path)
        assert saved["pending_files"] == []

    def test_multiple_files_all_listed(self, tmp_path):
        session = _base_session(
            pending_files=[
                {"path": "billing.py", "language": "python", "status": "new-file"},
                {"path": "checkout.py", "language": "python", "status": "new-file"},
            ]
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert "billing.py" in out["followup_message"]
        assert "checkout.py" in out["followup_message"]

    def test_typescript_file_returns_followup_message(self, tmp_path):
        session = _base_session(
            runners={"typescript": {"command": "vitest run", "test_location": "__tests__/"}},
            pending_files=[{"path": "src/service.ts", "language": "typescript", "status": "new-file"}],
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert "followup_message" in out
        assert "service.ts" in out["followup_message"]


# ---------------------------------------------------------------------------
# RUNNER_REQUIRED_LANGUAGES enforcement
# ---------------------------------------------------------------------------


class TestRunnerRequiredLanguagesEnforced:
    def test_go_without_runner_returns_empty(self, tmp_path):
        session = _base_session(
            runners={},
            pending_files=[{"path": "handler.go", "language": "go", "status": "new-file"}],
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert out == {}

    def test_rust_without_runner_returns_empty(self, tmp_path):
        session = _base_session(
            runners={},
            pending_files=[{"path": "src/lib.rs", "language": "rust", "status": "new-file"}],
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert out == {}

    def test_php_without_runner_returns_empty(self, tmp_path):
        session = _base_session(
            runners={},
            pending_files=[{"path": "Invoice.php", "language": "php", "status": "new-file"}],
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert out == {}

    def test_ruby_without_runner_returns_empty(self, tmp_path):
        session = _base_session(
            runners={},
            pending_files=[{"path": "user.rb", "language": "ruby", "status": "new-file"}],
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert out == {}

    def test_java_without_runner_returns_empty(self, tmp_path):
        session = _base_session(
            runners={},
            pending_files=[{"path": "Invoice.java", "language": "java", "status": "new-file"}],
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert out == {}

    def test_go_with_runner_returns_followup_message(self, tmp_path):
        session = _base_session(
            runners={"go": {"command": "go test", "test_location": "./..."}},
            pending_files=[{"path": "handler.go", "language": "go", "status": "new-file"}],
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert "followup_message" in out
        assert "handler.go" in out["followup_message"]

    def test_mixed_qualified_and_unqualified(self, tmp_path):
        session = _base_session(
            runners={"python": {"command": "pytest", "test_location": "tests/"}},
            pending_files=[
                {"path": "billing.py", "language": "python", "status": "new-file"},
                {"path": "handler.go", "language": "go", "status": "new-file"},
            ],
        )
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert "followup_message" in out
        assert "billing.py" in out["followup_message"]
        # go is filtered since no go runner
        assert "handler.go" not in out["followup_message"]


# ---------------------------------------------------------------------------
# Missing session file
# ---------------------------------------------------------------------------


class TestMissingSession:
    def test_no_session_returns_empty_dict(self, tmp_path):
        out = _run_hook(tmp_path, _event(tmp_path))
        assert out == {}

    def test_no_session_exits_cleanly(self, tmp_path):
        import subprocess
        result = subprocess.run(
            [sys.executable, HOOK_PATH],
            input=json.dumps({"workspace_roots": [str(tmp_path)]}),
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# More than 5 files -- truncation
# ---------------------------------------------------------------------------


class TestManyFilesFormatting:
    def test_six_files_shows_plus_more(self, tmp_path):
        pending = [
            {"path": f"file{i}.py", "language": "python", "status": "new-file"}
            for i in range(6)
        ]
        session = _base_session(pending_files=pending)
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert "+1 more" in out["followup_message"]

    def test_five_files_no_truncation(self, tmp_path):
        pending = [
            {"path": f"file{i}.py", "language": "python", "status": "new-file"}
            for i in range(5)
        ]
        session = _base_session(pending_files=pending)
        _write_session(tmp_path, session)
        out = _run_hook(tmp_path, _event(tmp_path))
        assert "more" not in out["followup_message"]
