# tailtest on

Resume tailtest after it has been paused.

## Trigger phrases

- `/tailtest on`
- `tailtest on`
- `resume tailtest`
- `enable tailtest`
- `unpause tailtest`

## Behavior

1. Read `.cursor/hooks/state/tailtest.json`
2. Set `paused: false` and write it back
3. Respond: "tailtest resumed."
