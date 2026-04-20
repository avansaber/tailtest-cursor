#!/usr/bin/env python3
"""tailtest afterFileEdit hook -- per-edit accumulator.

Fires after every agent file write (NOT Tab autocomplete writes).
Reads file_path from stdin, applies intelligence filter, and appends
eligible files to pending_files in .cursor/hooks/state/tailtest.json.

No output. Fire-and-forget.

Target: < 100ms.
"""

from __future__ import annotations

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "lib"))

from filter import detect_language, is_filtered, load_ignore_patterns
from session import determine_status, load_session, save_session


def main() -> None:
    try:
        raw = sys.stdin.read()
        event: dict = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        event = {}

    file_path: str = event.get("file_path", "")
    if not file_path or not os.path.isabs(file_path):
        return

    workspace_roots = event.get("workspace_roots", [])
    project_root: str = (
        workspace_roots[0] if workspace_roots
        else os.environ.get("CURSOR_PROJECT_DIR", os.path.dirname(os.path.abspath(file_path)))
    )

    ignore_patterns = load_ignore_patterns(project_root)
    if is_filtered(file_path, project_root, ignore_patterns):
        return

    language = detect_language(file_path)
    if not language:
        return

    session = load_session(project_root)

    # Skip if no session runners yet (session_start hasn't fired or was skipped)
    # Still accumulate -- session_start will backfill runner info on next turn.

    rel_path = os.path.relpath(os.path.abspath(file_path), project_root).replace("\\", "/")

    pending_files: list[dict] = session.get("pending_files", [])
    existing_paths = {p["path"] for p in pending_files}

    if rel_path not in existing_paths:
        touched_files: list[str] = session.get("touched_files", [])
        status = determine_status(file_path, project_root, touched_files)
        pending_files.append({
            "path": rel_path,
            "language": language,
            "status": status,
        })
        session["pending_files"] = pending_files
        if rel_path not in touched_files:
            session.setdefault("touched_files", []).append(rel_path)
        try:
            save_session(project_root, session)
        except OSError:
            pass


if __name__ == "__main__":
    main()
