# Changelog

All notable changes to tailtest-cursor will be documented in this file.

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
