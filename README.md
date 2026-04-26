# tailtest for Cursor

tailtest fires a test cycle at the end of every Cursor agent turn -- automatically, with no prompting.

**[Full documentation at tailtest.com/docs/cursor](https://tailtest.com/docs/cursor)**

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

See [tailtest.com/comparison](https://tailtest.com/comparison) for a feature matrix and [tailtest.com](https://tailtest.com) for the project home page.

---

## License

MIT
