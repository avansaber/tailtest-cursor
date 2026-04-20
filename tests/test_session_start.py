"""Unit tests for scripts/session_start.py -- the sessionStart hook.

Tests: JSON output with additional_context, runner detection from manifests,
empty-project graceful handling, session file created at correct path.
"""

import json
import os
import sys

import pytest

HOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "session_start.py")


def _run_hook(tmp_path, workspace_roots: list[str] | None = None) -> dict:
    import subprocess
    event = {
        "hook_event_name": "sessionStart",
        "workspace_roots": workspace_roots or [str(tmp_path)],
    }
    result = subprocess.run(
        [sys.executable, HOOK_PATH],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    assert result.returncode == 0, f"Hook exited non-zero: {result.stderr}"
    return json.loads(result.stdout) if result.stdout.strip() else {}


def _state_path(tmp_path) -> str:
    return str(tmp_path / ".cursor" / "hooks" / "state" / "tailtest.json")


# ---------------------------------------------------------------------------
# Output format
# ---------------------------------------------------------------------------


class TestOutputFormat:
    def test_returns_json_with_additional_context(self, tmp_path):
        out = _run_hook(tmp_path)
        assert "additional_context" in out

    def test_additional_context_is_string(self, tmp_path):
        out = _run_hook(tmp_path)
        assert isinstance(out["additional_context"], str)

    def test_additional_context_mentions_tailtest(self, tmp_path):
        out = _run_hook(tmp_path)
        assert "tailtest" in out["additional_context"].lower()

    def test_additional_context_mentions_project_root(self, tmp_path):
        out = _run_hook(tmp_path)
        assert str(tmp_path) in out["additional_context"]

    def test_exits_zero(self, tmp_path):
        import subprocess
        event = {"hook_event_name": "sessionStart", "workspace_roots": [str(tmp_path)]}
        result = subprocess.run(
            [sys.executable, HOOK_PATH],
            input=json.dumps(event),
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# Runner detection
# ---------------------------------------------------------------------------


class TestRunnerDetection:
    def test_pyproject_toml_detects_python_runner(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text(
            '[tool.pytest.ini_options]\ntestpaths = ["tests"]\n'
        )
        out = _run_hook(tmp_path)
        assert "pytest" in out["additional_context"]

    def test_package_json_vitest_detects_ts_runner(self, tmp_path):
        pkg = {
            "name": "myapp",
            "scripts": {"test": "vitest run"},
            "devDependencies": {"vitest": "^1.0.0"},
        }
        (tmp_path / "package.json").write_text(json.dumps(pkg))
        out = _run_hook(tmp_path)
        assert "vitest" in out["additional_context"]

    def test_go_mod_detects_go_runner(self, tmp_path):
        (tmp_path / "go.mod").write_text("module example.com/myapp\n\ngo 1.21\n")
        out = _run_hook(tmp_path)
        assert "go test" in out["additional_context"]

    def test_no_manifest_still_returns_additional_context(self, tmp_path):
        # Empty project -- graceful, context still returned
        out = _run_hook(tmp_path)
        assert "additional_context" in out


# ---------------------------------------------------------------------------
# Session state file created
# ---------------------------------------------------------------------------


class TestSessionFileCreated:
    def test_session_file_created_at_cursor_state_path(self, tmp_path):
        _run_hook(tmp_path)
        assert os.path.exists(_state_path(tmp_path))

    def test_session_file_has_pending_files_key(self, tmp_path):
        _run_hook(tmp_path)
        with open(_state_path(tmp_path)) as fh:
            session = json.load(fh)
        assert "pending_files" in session

    def test_session_file_has_runners_key(self, tmp_path):
        _run_hook(tmp_path)
        with open(_state_path(tmp_path)) as fh:
            session = json.load(fh)
        assert "runners" in session

    def test_session_depth_default_standard(self, tmp_path):
        _run_hook(tmp_path)
        with open(_state_path(tmp_path)) as fh:
            session = json.load(fh)
        assert session.get("depth") == "standard"

    def test_session_depth_respects_config(self, tmp_path):
        tailtest = tmp_path / ".tailtest"
        tailtest.mkdir()
        (tailtest / "config.json").write_text('{"depth": "thorough"}\n')
        _run_hook(tmp_path)
        with open(_state_path(tmp_path)) as fh:
            session = json.load(fh)
        assert session.get("depth") == "thorough"
