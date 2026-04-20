# tailtest summary

Show a summary of all tests generated and their outcomes in the current session.

## Trigger phrases

- `/summary`
- `tailtest summary`
- `what did tailtest do`
- `what did you test`
- `show test summary`

## Behavior

1. Read `.cursor/hooks/state/tailtest.json`
2. If missing: "No tailtest session active in this directory."
3. If `generated_tests` is empty: "No tests were generated this session."
4. Otherwise output in the format below and write to `report_path`

## Output format

```
tailtest session summary
Runner: {language}/{command}  Depth: {depth}

{N} file(s) covered:
  {source_file}  →  {test_file}  {status}
  ...

{N} fixed, {N} deferred, {N} unresolved.
```
