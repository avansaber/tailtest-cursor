# tailtest-cursor -- AI software testing for Cursor IDE

[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-181_passing-emerald)](https://github.com/avansaber/tailtest-cursor)
[![Version](https://img.shields.io/badge/version-1.6.0-blue)](https://github.com/avansaber/tailtest-cursor/releases/latest)
[![Platform](https://img.shields.io/badge/platform-macOS_%7C_Linux-lightgrey)](https://tailtest.com/platform/agent-edits/)

**tailtest-cursor** is the open-source AI software testing layer for [Cursor IDE](https://cursor.com). It hooks into Cursor's `afterFileEdit` event: every time Cursor's AI agent edits a file, tailtest queues the file, generates production-shaped scenarios via the R1-R15 rule layer, runs them with your project's existing test runner, and surfaces failures back to Cursor. Hook-based. Deterministic. No prompting required.

Open source (MIT), no telemetry, no SaaS account. Same R1-R15 rule layer + adversarial mode (R15) as the Claude Code, Codex CLI, and Cline variants -- 1,234 plugin tests total across the four hosts.

**[Read more on tailtest.com](https://www.tailtest.com/) · [Platform overview](https://www.tailtest.com/platform/) · [Agent-edit testing deep dive](https://www.tailtest.com/platform/agent-edits/) · [Cursor docs](https://www.tailtest.com/docs/cursor/)**

---

## Install

**From the Cursor Marketplace (recommended):**

Search for **Tailtest** in the Cursor plugin marketplace and click Install. Restart Cursor.

**Manual:**

```bash
git clone https://github.com/avansaber/tailtest-cursor \
  ~/.cursor/plugins/local/tailtest-cursor
```

Restart Cursor after cloning.

---

## How it works

1. `afterFileEdit` hook fires as the agent writes files, recording each path
2. `stop` hook fires at turn end and sends `tailtest: run tests for: ...`
3. Cursor re-enters the agent -- scenarios are generated, tests are written, run, and reported

Pass = silent. Fail = one line surfaced before the agent moves on.

---

## Quick config

Create `.tailtest/config.json` in your project root:

```json
{ "depth": "standard" }
```

Options: `simple` (2-3 scenarios), `standard` (5-8, default), `thorough` (10-15).

See [tailtest.com/docs/config](https://tailtest.com/docs/config) for all options.

---

## Other tailtest variants

Same R1-R15 rule layer, same adversarial test mode, different host integration. **This repo is the Cursor variant.**

- **[tailtest](https://github.com/avansaber/tailtest)** -- Claude Code plugin (hook-driven)
- **[tailtest-cursor](https://github.com/avansaber/tailtest-cursor)** -- Cursor plugin (hook-driven; this repo)
- **[tailtest-codex](https://github.com/avansaber/tailtest-codex)** -- Codex CLI plugin (hook-driven)
- **[tailtest-cline](https://github.com/avansaber/tailtest-cline)** -- Cline plugin (MCP-driven; reaches 8+ editors via Cline's host coverage)

See [tailtest.com/demo/cursor](https://tailtest.com/demo/cursor) for a live walkthrough of this variant, [tailtest.com/comparison](https://tailtest.com/comparison) for a feature matrix across all four, or [tailtest.com](https://tailtest.com) for the project home.

---

## License

MIT
