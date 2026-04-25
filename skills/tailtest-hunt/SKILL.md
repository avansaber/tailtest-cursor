# tailtest hunt

Run an adversarial pass on a specific file -- explicitly try to break the source code with R15 adversarial scenarios. Forces an adversarial-biased pass regardless of project depth setting.

## Trigger phrases

- `/tailtest hunt <file>`
- `tailtest hunt <file>`
- `hunt for bugs in <file>`
- `adversarial test <file>`

## Behavior

1. Read the source file at the named path
2. Generate 8-12 adversarial test scenarios from the R15 categories in `rules/tailtest.mdc`:
   - Boundary inputs (`MAX_INT`, `MIN_INT`, empty, single-element, unicode, null bytes, malformed UTF-8)
   - Format / injection (path traversal `..`, regex specials, shell metacharacters, SQL fragments)
   - Type confusion (wrong type passed)
   - Concurrent state (race conditions, shared mutable state)
   - Time / locale edges (DST, leap year, timezone)
   - Error handling under partial failures (network mid-call fail, disk full, EINTR)
   - Resource exhaustion (very large input, deeply nested input)
   - Off-by-one logic (boundary indices, fence-post errors)
3. Pick categories that genuinely apply; skip any that do not (state which were skipped and why)
4. Output a SCENARIO PLAN with each scenario labeled `[adversarial: <category>]`
5. Write to a SEPARATE hunt test file (NOT the regular test file)
6. Run the hunt test file
7. Apply R12 classification on any failures (real_bug / environment / test_bug)
8. Report failing scenarios with classification, e.g. `[adversarial: type-confusion] real_bug -- function returns None on int input where str expected.`
9. If all pass: `tailtest hunt: {N} adversarial scenarios on {file}, all passed.`

## Where to write the hunt test file

| Source file | Hunt test file |
|---|---|
| `services/billing.py` | `tests/test_billing_hunt.py` |
| `app/Http/Controllers/OrderController.php` | `tests/Feature/OrderControllerHuntTest.php` |
| `internal/handler.go` | `internal/handler_hunt_test.go` |
| `components/Button.tsx` | `__tests__/Button_hunt.test.tsx` |

The separate hunt file does not contaminate the main test suite. User decides whether to keep, merge into the main test file, or discard after review.

## Bypass behavior

This skill bypasses `depth` from `.tailtest/config.json`. Even at `depth: simple` (which normally generates 0 adversarial scenarios per R15), `/tailtest hunt` runs the full 8-12 adversarial pass on the named file.

## Constraints

- **Do not auto-fix.** Always ask before fixing any `real_bug` found by hunt.
- **No update-existing-tests behavior.** Hunt always writes to the separate hunt test file. If the hunt file already exists, replace its contents (the user is asking for a fresh hunt).
- Treat the named file as `new-file` regardless of git status.
- Update `.cursor/hooks/state/tailtest.json` `generated_tests` to record the hunt test file mapping (source -> hunt test file).
