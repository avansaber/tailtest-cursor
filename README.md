# tailtest for Cursor

A Cursor plugin that automatically generates and runs tests every time the agent edits a file. Silent on pass, interrupts on failure.

## How it works

1. Every time the Cursor agent writes a file, the `afterFileEdit` hook fires and records the path
2. When the agent turn ends, the `stop` hook sends a `tailtest: run tests for:` message
3. Cursor re-enters the agent with that message -- the agent generates scenarios, writes test code, executes it, and reports only failures

Pass = completely silent. Fail = the agent surfaces the failure before moving on.

## Prerequisites

- **Cursor** 0.40 or later (hooks support required)
- **Python 3.8+** in your `PATH` -- the hooks run Python scripts

Verify:
```sh
python3 --version   # must be 3.8 or later
cursor --version    # optional, confirms Cursor is installed
```

## Installation

### From Cursor Marketplace (recommended)

Search for **Tailtest** in the Cursor plugin marketplace and click Install. Restart Cursor.

### Manual (local install)

```sh
git clone https://github.com/avansaber/tailtest-cursor \
  ~/.cursor/plugins/local/tailtest-cursor
```

Restart Cursor after cloning.

### Verify the plugin is active

Open a Cursor composer session and type:

```
what plugins do you have active?
```

You should see tailtest mentioned. Alternatively, open any project, let the agent write a Python or TypeScript file, and watch for a `tailtest: run tests for:` message at the end of the turn.

## Supported languages

Python, TypeScript, JavaScript, Go, Rust, Ruby, Java, PHP

Runners are auto-detected from `pyproject.toml`, `package.json`, `go.mod`, `Gemfile`, `Cargo.toml`, `pom.xml`, `build.gradle`, and `composer.json`.

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

To exclude specific files from test generation, create `.tailtest-ignore` in your project root using `.gitignore` syntax:

```
# Skip generated files
src/generated/
migrations/
```

## Commands

Type these in any Cursor composer session:

| Command | Effect |
|---|---|
| `/tailtest off` | Pause test generation |
| `/tailtest on` | Resume test generation |
| `/summary` | Show session summary |
| `/tailtest <file>` | Force-run tests for a specific file |

## Session state

Session state is stored at `.cursor/hooks/state/tailtest.json`. Session reports are written to `.tailtest/reports/`.

Add `.cursor/hooks/state/` to `.gitignore` to keep session state out of version control:

```sh
echo '.cursor/hooks/state/' >> .gitignore
```

## Troubleshooting

**Hooks not firing:** Verify Cursor version supports hooks (0.40+). Check that Python 3 is available as `python3` in your PATH.

**`tailtest: run tests for:` message appears but no test is generated:** The agent may have filtered the file (config file, template, test file itself). This is expected -- see the filter rules in `rules/tailtest.mdc`.

**Wrong runner detected:** Create `.tailtest/config.json` and check `.cursor/hooks/state/tailtest.json` to see what runners were detected. If the runner is wrong, your manifest file (`pyproject.toml`, `package.json`) may be missing the test framework dependency.

**Performance:** The `afterFileEdit` hook runs in < 100ms. The `stop` hook runs in < 200ms. Neither makes network requests.

## Related

- [tailtest for Claude Code](https://github.com/avansaber/tailtest) -- the Claude Code version
- [tailtest for Codex CLI](https://github.com/avansaber/tailtest-codex) -- the Codex CLI version
- [tailtest.com](https://tailtest.com) -- documentation and case studies
