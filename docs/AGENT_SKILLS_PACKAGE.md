# AGET Session Core — bounded Agent Skills package

v3.30 publishes a manifest and conformance check for three session skills already present in the v3.29
canonical tree. The new capability is the **bounded, digest-addressed package contract**; the three skill
instruction files themselves are not credited again.

## Included subset

| Skill | Purpose | Canonical package path |
|---|---|---|
| `aget-wake-up` | Start an AGET session and render its readiness summary | `.agents/skills/aget-wake-up/` |
| `aget-study-topic` | Review relevant knowledge before implementation | `.agents/skills/aget-study-topic/` |
| `aget-save-state` | Save resumable workflow state at a natural breakpoint | `.agents/skills/aget-save-state/` |

`AGENT_SKILLS_PACKAGE.json` binds each package path to its canonical source and SHA-256 digest.

## Verify before use

From the repository root:

```bash
python3 scripts/validate_agent_skill_package.py
```

Exit `0` means the manifest, paths, digests, and Agent Skills frontmatter pass the shipped checks. Any
missing file, path escape, digest drift, malformed required field, unsupported frontmatter field, or
package/disclosure mismatch exits non-zero.

## Manual use — no installer required

1. Clone or otherwise obtain the public `aget-framework/aget` repository at the desired tag.
2. Run the conformance command above and require exit `0`.
3. Point a compatible client's project-level skill discovery at `.agents/skills/`, or copy one resolved
   directory into that client's documented skill directory. For example:

   ```bash
   cp -RL .agents/skills/aget-wake-up /path/to/client/skills/
   ```

4. Ask the client to invoke `aget-wake-up`. Its documented output is a readiness summary containing the
   session identity, AGET version, purpose, managed repository, template count, git status, and `Ready.`

Client discovery and invocation syntax vary. The package deliberately does not claim a one-command
installer or marketplace registration; the manual path is the supported v3.30 receipt path.

## What does not travel

This package carries model-followed skill instructions. It does **not** carry AGET's structural hooks,
permission settings, public-push controls, D71 route enforcement, or the rest of the source agent's
governance environment. `allowed-tools`, where present, is experimental in the Agent Skills specification
and must not be read as portable enforcement.

The receiving seat remains responsible for its own authorization and safety controls. A successful
package-conformance check proves package integrity and format, not equivalent enforcement.
