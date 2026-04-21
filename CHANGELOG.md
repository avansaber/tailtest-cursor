# Changelog

All notable changes to tailtest-cursor will be documented in this file.

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
