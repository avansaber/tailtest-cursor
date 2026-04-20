# tailtest for Cursor

A Cursor plugin that automatically generates and runs tests every time the agent edits a file. Silent on pass, interrupts on failure.

## How it works

1. Every time the Cursor agent writes a file, the `afterFileEdit` hook accumulates the file path
2. When the agent turn ends, the `stop` hook sends a `tailtest: run tests for:` message listing the changed files
3. The agent generates scenarios, writes test code, executes it, and reports only failures

Pass = completely silent. Fail = interrupts with the exact failure before you move on.

## Installation

**From Cursor Marketplace:**
Search for "Tailtest" in the Cursor plugin marketplace and click Install.

**Manual install:**
```bash
git clone https://github.com/avansaber/tailtest-cursor ~/.cursor/plugins/local/tailtest-cursor
```
Then restart Cursor.

## Supported languages

Python, TypeScript, JavaScript, Go, Rust, Ruby, Java, PHP

## Configuration

Create `.tailtest/config.json` in your project root to configure depth:

```json
{
  "depth": "standard"
}
```

| Depth | Scenarios | Scope |
|---|---|---|
| `simple` | 2-3 | Happy path only |
| `standard` | 5-8 | Happy path + key edge cases |
| `thorough` | 10-15 | Happy path + edge cases + failure modes |

To ignore specific files, create `.tailtest-ignore` in your project root (same syntax as `.gitignore`).

## Commands

| Command | Effect |
|---|---|
| `/tailtest off` | Pause test generation |
| `/tailtest on` | Resume test generation |
| `/summary` | Show session summary |
| `/tailtest <file>` | Run tailtest on a specific file |

## Session state

Session state is stored at `.cursor/hooks/state/tailtest.json`. Session reports are written to `.tailtest/reports/`.

## Related

- [tailtest for Claude Code](https://github.com/avansaber/tailtest) -- the Claude Code version
- [tailtest for Codex CLI](https://github.com/avansaber/tailtest-codex) -- the Codex CLI version
- [tailtest.com](https://tailtest.com) -- documentation and case studies
