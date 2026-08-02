# Codex hook-controls POC

This is an isolated outcome-level POC for Codex CLI 0.144.5+. It does not install project hooks, alter
`.codex/config.toml`, or change `trust_level`. It proves the proposed PreToolUse decision contract before
adoption:

- trusted + sensitive governance target + no individual affirmation → block;
- trusted + ordinary target → allow;
- trusted + sensitive target + individual affirmation → allow;
- untrusted → hook unavailable, never reported as an enforcing PASS;
- the guard never executes the proposed operation, so a denial has no side effect.

Run the two-client acceptance matrix with:

```sh
python3 scripts/check_cross_client_hook_controls.py --json
```
