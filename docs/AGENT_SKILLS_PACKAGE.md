# AGET Session Core — bounded Agent Skills package for AGET repositories

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

Exit `0` means the manifest, paths, digests, Agent Skills frontmatter, and declared receiver-runtime
targets pass the shipped checks. Any missing file, path escape, digest drift, malformed required field,
unsupported frontmatter field, dangling invocation target, or package/disclosure mismatch exits non-zero.

## Runtime boundary

The package is **client-format portable, not substrate-free**. Its skill instructions expect an AGET
repository layout and use receiver-local files that are not carried or digest-bound by this package:

- `aget-wake-up` invokes receiver-local `scripts/wake_up.py`, with an AGET-file fallback;
- `aget-study-topic` invokes receiver-local `scripts/study_topic.py`;
- all three skills may read or write AGET paths such as `.aget/`, `AGENTS.md`, `planning/`, and `sessions/`.

Therefore a compatible Agent Skills client is necessary but not sufficient. Run these skills only in an
AGET repository that supplies the named runtime paths and its own authorization controls. The immutable
`v3.30.0` tag's `aget-study-topic` instruction used the retired name `scripts/study_up.py`; mutable `main`
contains the post-tag correction. Do not combine a manifest from one ref with skill files from another.

## Manual use — no installer required

1. Clone or otherwise obtain the public `aget-framework/aget` repository at the desired tag.
2. Run the conformance command above and require exit `0`.
3. Point a compatible client's project-level skill discovery at `.agents/skills/`, or copy one resolved
   directory into that client's documented skill directory. Use a new destination, bypass shell aliases,
   require copy success, and verify the destination digest. For example:

   ```bash
   client_skills_dir=/path/to/client/skills
   test ! -e "$client_skills_dir/aget-wake-up"
   command cp -RL .agents/skills/aget-wake-up "$client_skills_dir/"
   python3 -c 'import hashlib,json,pathlib,sys; m=json.load(open(sys.argv[1])); e=next(x for x in m["skills"] if x["name"]==sys.argv[3]); p=pathlib.Path(sys.argv[2])/"SKILL.md"; a=hashlib.sha256(p.read_bytes()).hexdigest(); assert a==e["sha256"], f"destination digest mismatch: {a} != {e['"'"'sha256'"'"']}"; print(a)' AGENT_SKILLS_PACKAGE.json "$client_skills_dir/aget-wake-up" aget-wake-up
   ```

4. From the receiving AGET repository, ask the client to invoke `aget-wake-up`. When receiver-local
   `scripts/wake_up.py` is present, record exit status and the repository-defined wake-up summary. The
   v3.30 canonical script reports session identity, AGET version, purpose, and git status and terminates
   with `Ready.`; it does not promise a managed-repository field or template count. If the skill takes its
   fallback path, record that fact and the fallback's concise agent/version, location, git, Skills, and
   Learnings briefing instead of claiming script-path equivalence.

Client discovery and invocation syntax vary. The package deliberately does not claim a one-command
installer or marketplace registration; the manual path is the supported v3.30 receipt path.

## What does not travel

This package carries model-followed skill instructions. It does **not** carry the receiver-local scripts
and AGET repository substrate named above, AGET's structural hooks, permission settings, public-push
controls, D71 route enforcement, or the rest of the source agent's governance environment.
`allowed-tools`, where present, is experimental in the Agent Skills specification and must not be read as
portable enforcement.

The receiving seat remains responsible for its own authorization and safety controls. A successful
package-conformance check proves package integrity and format, not equivalent enforcement.
