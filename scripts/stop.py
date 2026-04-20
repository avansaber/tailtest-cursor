#!/usr/bin/env python3
"""tailtest stop hook -- turn trigger.

Fires at the end of every agent turn.
Reads pending_files from session state, clears the list, and returns
followup_message to trigger test generation in the next turn.

If no files pending: returns empty JSON (continue).
If files pending: returns followup_message and clears the list immediately
to prevent re-triggering on the following stop.

Target: < 200ms.
"""

from __future__ import annotations

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "lib"))

from complexity_scorer import complexity_context_note, score_file
from filter import RUNNER_REQUIRED_LANGUAGES
from last_failures_formatter import compute_last_failures
from scenario_log import append_to_log, build_scenario_entries
from session import load_session, save_session


def main() -> None:
    try:
        raw = sys.stdin.read()
        event: dict = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        event = {}

    workspace_roots = event.get("workspace_roots", [])
    project_root: str = (
        workspace_roots[0] if workspace_roots
        else os.environ.get("CURSOR_PROJECT_DIR", os.getcwd())
    )

    session = load_session(project_root)
    pending_files: list[dict] = session.get("pending_files", [])

    if not pending_files:
        print(json.dumps({}))
        return

    if session.get("paused", False):
        print(json.dumps({}))
        return

    runners: dict = session.get("runners", {})

    # Filter out languages that need an explicit runner but none is configured
    qualified: list[dict] = [
        f for f in pending_files
        if not (f.get("language") in RUNNER_REQUIRED_LANGUAGES
                and f.get("language") not in runners)
    ]

    if not qualified:
        print(json.dumps({}))
        return

    # Clear BEFORE returning -- prevents re-trigger on next stop
    session["pending_files"] = []
    session["last_failures"] = compute_last_failures(session)

    # H3: append scenario log entries
    new_entries = build_scenario_entries(session)
    if new_entries:
        session["scenario_log"] = append_to_log(session.get("scenario_log", []), new_entries)

    # H1: store complexity scores for pending files
    scores = session.get("complexity_scores", {})
    configured_depth = session.get("depth", "standard")
    for entry in qualified:
        p = entry.get("path", "")
        if p:
            try:
                sc, _ = score_file(os.path.join(project_root, p))
                scores[p] = sc
            except Exception:
                pass
    session["complexity_scores"] = scores

    try:
        save_session(project_root, session)
    except OSError:
        pass

    parts = []
    for entry in qualified:
        path = entry.get("path", "")
        lang = entry.get("language", "unknown")
        runner_info = runners.get(lang) or (next(iter(runners.values())) if runners else None)
        runner_cmd = runner_info.get("command", "?") if runner_info else "?"
        hint = complexity_context_note(os.path.join(project_root, path), configured_depth)
        hint_str = f", {hint}" if hint else ""
        parts.append(f"{path} ({lang}, {runner_cmd}{hint_str})")

    n = len(qualified)
    listed = parts[:5]
    suffix = f" (+{n - 5} more)" if n > 5 else ""
    files_str = ", ".join(listed) + suffix

    msg = (
        f"tailtest: run tests for: {files_str}. "
        f"Read .cursor/hooks/state/tailtest.json for session state."
    )
    print(json.dumps({"followup_message": msg}))


if __name__ == "__main__":
    main()
