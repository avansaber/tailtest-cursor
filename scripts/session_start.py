#!/usr/bin/env python3
"""tailtest sessionStart hook -- project orientation and context injection.

Fires when a new Cursor composer session begins.
- Scans project manifests to detect runners and test locations
- Creates/refreshes .cursor/hooks/state/tailtest.json
- Emits runner summary via additional_context (JSON output)
- Runs ramp-up scan on first session

Target: < 2 seconds.
"""

from __future__ import annotations

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "lib"))

from context import build_startup_context
from ramp_up import _write_orphaned_report, is_first_session, ramp_up_scan
from runners import create_session, read_depth, scan_runners


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

    _write_orphaned_report(project_root)

    runners = scan_runners(project_root)
    depth = read_depth(project_root)
    first_session = is_first_session(project_root)

    session = {}
    try:
        session = create_session(project_root, runners, depth)
    except OSError:
        pass

    ramp_up_count = 0
    if first_session and session:
        try:
            ramp_up_scan(project_root, runners, session)
            ramp_up_count = len(session.get("pending_files", []))
        except Exception:
            pass

    context = build_startup_context(
        project_root, runners, depth,
        ramp_up_count=ramp_up_count,
    )

    if context:
        print(json.dumps({"additional_context": context}))


if __name__ == "__main__":
    main()
