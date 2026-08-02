# Claude Code hook-controls POC

This sanitized, isolated fixture makes the H-29-012 Claude Code acceptance leg reproducible from the
public release candidate. It does not install or register a project hook. The fixture names the
`PreToolUse` route and default permission boundary; the pure guard proves sensitive denial, ordinary-use
pass-through, individual affirmation, and denial without side effects.

Run both supported-client legs with:

```sh
python3 scripts/check_cross_client_hook_controls.py --json
```
