# tailtest off

Pause tailtest so it stops generating tests until resumed.

## Trigger phrases

- `/tailtest off`
- `tailtest off`
- `pause tailtest`
- `disable tailtest`
- `stop tailtest`

## Behavior

1. Read `.cursor/hooks/state/tailtest.json`
2. Set `paused: true` and write it back
3. Respond: "tailtest paused. Type /tailtest on to resume."
