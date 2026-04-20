"""Unit tests for scripts/after_file_edit.py -- the afterFileEdit accumulator hook.

Tests: file_path validation (missing/relative), accumulation into pending_files,
duplicate deduplication, intelligence filter enforcement, language detection,
.cursor/ path fragment skipped, RUNNER_REQUIRED_LANGUAGES silently accepted.
"""

import json
import os
import sys

import pytest

HOOK_PATH = os.path.join(os.path.dirname(__file__), "..", "scripts", "after_file_edit.py")


def _state_path(tmp_path) -> str:
    return str(tmp_path / ".cursor" / "hooks" / "state" / "tailtest.json")


def _write_session(tmp_path, session: dict) -> None:
    state = tmp_path / ".cursor" / "hooks" / "state"
    state.mkdir(parents=True, exist_ok=True)
    with open(state / "tailtest.json", "w") as fh:
        json.dump(session, fh)


def _read_session(tmp_path) -> dict:
    path = _state_path(tmp_path)
    with open(path) as fh:
        return json.load(fh)


def _run_hook(tmp_path, event: dict) -> tuple[int, str, str]:
    import subprocess
    result = subprocess.run(
        [sys.executable, HOOK_PATH],
        input=json.dumps(event),
        capture_output=True,
        text=True,
        cwd=str(tmp_path),
    )
    return result.returncode, result.stdout, result.stderr


def _base_session(**kwargs) -> dict:
    session = {
        "pending_files": [],
        "touched_files": [],
        "runners": {"python": {"command": "pytest", "test_location": "tests/"}},
        "fix_attempts": {},
        "deferred_failures": [],
        "generated_tests": {},
        "packages": {},
    }
    session.update(kwargs)
    return session


def _event(tmp_path, file_path: str | None = None, **kwargs) -> dict:
    ev: dict = {"workspace_roots": [str(tmp_path)]}
    if file_path is not None:
        ev["file_path"] = file_path
    ev.update(kwargs)
    return ev


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


class TestInputValidation:
    def test_missing_file_path_no_output_exit_0(self, tmp_path):
        rc, out, _ = _run_hook(tmp_path, _event(tmp_path))
        assert rc == 0
        assert out == ""

    def test_empty_file_path_no_output(self, tmp_path):
        rc, out, _ = _run_hook(tmp_path, _event(tmp_path, file_path=""))
        assert rc == 0
        assert out == ""

    def test_relative_file_path_no_output(self, tmp_path):
        rc, out, _ = _run_hook(tmp_path, _event(tmp_path, file_path="src/billing.py"))
        assert rc == 0
        assert out == ""

    def test_empty_stdin_no_crash(self, tmp_path):
        import subprocess
        result = subprocess.run(
            [sys.executable, HOOK_PATH],
            input="",
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert result.returncode == 0
        assert result.stdout == ""

    def test_invalid_json_no_crash(self, tmp_path):
        import subprocess
        result = subprocess.run(
            [sys.executable, HOOK_PATH],
            input="{not valid json",
            capture_output=True,
            text=True,
            cwd=str(tmp_path),
        )
        assert result.returncode == 0


# ---------------------------------------------------------------------------
# File accumulation
# ---------------------------------------------------------------------------


class TestFileAccumulation:
    def test_python_file_appended_to_pending(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        billing = src / "billing.py"
        billing.write_text("def billing(): pass\n")
        _write_session(tmp_path, _base_session())
        rc, out, _ = _run_hook(tmp_path, _event(tmp_path, file_path=str(billing)))
        assert rc == 0
        assert out == ""
        session = _read_session(tmp_path)
        paths = [p["path"] for p in session["pending_files"]]
        assert "src/billing.py" in paths

    def test_pending_entry_has_correct_language(self, tmp_path):
        billing = tmp_path / "billing.py"
        billing.write_text("def billing(): pass\n")
        _write_session(tmp_path, _base_session())
        _run_hook(tmp_path, _event(tmp_path, file_path=str(billing)))
        session = _read_session(tmp_path)
        entry = next(p for p in session["pending_files"] if "billing.py" in p["path"])
        assert entry["language"] == "python"

    def test_pending_entry_has_status(self, tmp_path):
        billing = tmp_path / "billing.py"
        billing.write_text("def billing(): pass\n")
        _write_session(tmp_path, _base_session())
        _run_hook(tmp_path, _event(tmp_path, file_path=str(billing)))
        session = _read_session(tmp_path)
        entry = next(p for p in session["pending_files"] if "billing.py" in p["path"])
        assert entry["status"] in ("new-file", "legacy-file")

    def test_typescript_file_appended(self, tmp_path):
        service = tmp_path / "service.ts"
        service.write_text("export const x = 1;\n")
        _write_session(tmp_path, _base_session())
        _run_hook(tmp_path, _event(tmp_path, file_path=str(service)))
        session = _read_session(tmp_path)
        paths = [p["path"] for p in session["pending_files"]]
        assert "service.ts" in paths

    def test_go_file_appended_without_runner(self, tmp_path):
        handler = tmp_path / "handler.go"
        handler.write_text("package main\nfunc main() {}\n")
        _write_session(tmp_path, _base_session(runners={}))
        _run_hook(tmp_path, _event(tmp_path, file_path=str(handler)))
        session = _read_session(tmp_path)
        paths = [p["path"] for p in session["pending_files"]]
        # afterFileEdit always accumulates -- stop.py applies RUNNER_REQUIRED filter
        assert "handler.go" in paths

    def test_file_added_to_touched_files(self, tmp_path):
        billing = tmp_path / "billing.py"
        billing.write_text("def billing(): pass\n")
        _write_session(tmp_path, _base_session())
        _run_hook(tmp_path, _event(tmp_path, file_path=str(billing)))
        session = _read_session(tmp_path)
        assert "billing.py" in session.get("touched_files", [])

    def test_no_session_creates_session_file(self, tmp_path):
        billing = tmp_path / "billing.py"
        billing.write_text("def billing(): pass\n")
        # No session file pre-written
        rc, out, _ = _run_hook(tmp_path, _event(tmp_path, file_path=str(billing)))
        assert rc == 0
        assert os.path.exists(_state_path(tmp_path))


# ---------------------------------------------------------------------------
# Deduplication
# ---------------------------------------------------------------------------


class TestDeduplication:
    def test_duplicate_file_not_added_again(self, tmp_path):
        billing = tmp_path / "billing.py"
        billing.write_text("def billing(): pass\n")
        session = _base_session(
            pending_files=[{"path": "billing.py", "language": "python", "status": "new-file"}]
        )
        _write_session(tmp_path, session)
        _run_hook(tmp_path, _event(tmp_path, file_path=str(billing)))
        saved = _read_session(tmp_path)
        paths = [p["path"] for p in saved["pending_files"]]
        assert paths.count("billing.py") == 1

    def test_second_call_adds_different_file(self, tmp_path):
        billing = tmp_path / "billing.py"
        billing.write_text("def billing(): pass\n")
        checkout = tmp_path / "checkout.py"
        checkout.write_text("def checkout(): pass\n")
        _write_session(tmp_path, _base_session())
        _run_hook(tmp_path, _event(tmp_path, file_path=str(billing)))
        _run_hook(tmp_path, _event(tmp_path, file_path=str(checkout)))
        saved = _read_session(tmp_path)
        paths = [p["path"] for p in saved["pending_files"]]
        assert "billing.py" in paths
        assert "checkout.py" in paths


# ---------------------------------------------------------------------------
# Intelligence filter -- files that should NOT be accumulated
# ---------------------------------------------------------------------------


class TestFilteredFilesNotAccumulated:
    def _assert_not_pending(self, tmp_path, file_path: str, content: str = "x"):
        f = tmp_path / file_path
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
        _write_session(tmp_path, _base_session())
        _run_hook(tmp_path, _event(tmp_path, file_path=str(f)))
        session = _read_session(tmp_path)
        assert session["pending_files"] == [], f"Expected {file_path} to be filtered"

    def test_yaml_not_accumulated(self, tmp_path):
        self._assert_not_pending(tmp_path, "config.yaml")

    def test_json_not_accumulated(self, tmp_path):
        self._assert_not_pending(tmp_path, "tsconfig.json")

    def test_markdown_not_accumulated(self, tmp_path):
        self._assert_not_pending(tmp_path, "README.md")

    def test_test_file_not_accumulated(self, tmp_path):
        self._assert_not_pending(tmp_path, "tests/test_billing.py", "def test_foo(): pass\n")

    def test_node_modules_not_accumulated(self, tmp_path):
        self._assert_not_pending(tmp_path, "node_modules/lodash/index.js")

    def test_cursor_state_not_accumulated(self, tmp_path):
        state_dir = tmp_path / ".cursor" / "hooks" / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        # The tailtest.json itself should never be queued
        f = state_dir / "other.py"
        f.write_text("# state file\n")
        _write_session(tmp_path, _base_session())
        _run_hook(tmp_path, _event(tmp_path, file_path=str(f)))
        session = _read_session(tmp_path)
        assert session["pending_files"] == []

    def test_unknown_extension_not_accumulated(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("a,b,c\n")
        _write_session(tmp_path, _base_session())
        _run_hook(tmp_path, _event(tmp_path, file_path=str(f)))
        session = _read_session(tmp_path)
        assert session["pending_files"] == []

    def test_vite_config_not_accumulated(self, tmp_path):
        self._assert_not_pending(tmp_path, "vite.config.ts")

    def test_dist_file_not_accumulated(self, tmp_path):
        self._assert_not_pending(tmp_path, "dist/bundle.js")

    def test_go_test_file_not_accumulated(self, tmp_path):
        self._assert_not_pending(tmp_path, "handler_test.go", "package main\n")
