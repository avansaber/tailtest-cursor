# Changelog

All notable changes to tailtest-cursor will be documented in this file.

## [1.2.0] - 2026-04-23

Spring Boot R2 baseline + Bun test, Deno test, pytest-asyncio detection. 146 tests.

**Spring Boot (R2 completion):** Spring Boot projects (Maven or Gradle with `spring-boot` referenced) now get auto-included baseline scenarios on top of the Java baseline: valid request returns 200, missing required field returns 400, unauthenticated request returns 401, controller slice test with `@WebMvcTest`, service dependency overridden via `@MockBean`. Detection and Scenario rules already shipped in v1.1.0; this completes the R2 framework template row.

**Bun test detection:** Projects with `bun test` in `package.json` `scripts.test` or with `bunfig.toml` present now get the `bun test` runner instead of falling back to `vitest`. Precedence is explicit: scripts > deps > `bunfig.toml` tiebreaker.

**Deno test detection:** New `detect_deno_runner` function picks up Deno projects via `deno.json` or `deno.jsonc`. Tests are colocated (`*_test.ts` style) with `deno test` as the runner. When both `package.json` and `deno.json` exist, Node wins.

**pytest-asyncio:** Detected via `pytest-asyncio` in pyproject deps. Adds an additive `async_framework` field on the python runner entry. No schema break.

**Mock the right library (S-rules update):** Expanded to cover Bun and Deno mocking syntax with warning against mixing runners.

## [1.1.0] - 2026-04-20

Quality layer and cross-session memory. 142 tests.

**Rule layer:** Fourteen rules now govern test generation -- requirement-first derivation, language-keyed baseline scenarios, flakiness ban list, AAA structure, one-behavior-per-test, plain-English names, no-internals rule, boundary-only mocking, framework templates (Django, FastAPI, Next.js), equivalence partitioning, pre-write API check, SCENARIO PLAN label, and failure classification (real bug / environment issue / test bug stated before asking to fix).

**Hook enrichment:** Per-file depth scoring (path signals: auth/billing +4, admin/delete +3; content signals: HTTP/DB +3 each; up to 15 scenarios for critical files). Cross-turn context: prior session failures injected at session start. Long test output compressed to function name, assertion, expected/received.

**Cross-session memory:** `.tailtest/history.json` tracks outcomes across sessions (1000-entry cap, gap/passed/fixed/regression classification). Recurring failures (3+ sessions) flagged at startup.

**Opt-in:** Impact tracing (Python AST, `impact_tracing: true`), API validation (`api_validation: true`).

## [1.0.0] - 2026-04-19

### Added

- `afterFileEdit` hook: per-edit accumulator fires on every agent file write
- `stop` hook: turn trigger emits `followup_message` listing files to test
- `sessionStart` hook: detects runners, emits context, runs ramp-up on first session
- `rules/tailtest.mdc`: always-on instructions (Steps 1-6, scenario rules, fix loop)
- Skills: `tailtest-on`, `tailtest-off`, `tailtest-summary`
- Support for Python, TypeScript, JavaScript, Go, Rust, Ruby, Java, PHP
- Ramp-up scan: first-session coverage bootstrap selects top-priority existing files
- Orphaned report recovery: writes report for sessions that ended without a summary
- Style context sampling: samples recent test files to match project conventions
- `.tailtest-ignore` support: gitignore-style exclusion patterns
- Depth configuration via `.tailtest/config.json`
- Session state at `.cursor/hooks/state/tailtest.json`
