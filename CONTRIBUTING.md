# Contributing to AGET

Thanks for your interest in AGET. This guide covers how to propose changes to the
framework core and to the agent templates.

## Where things live

| Repository | What it holds | Issues |
|---|---|---|
| [`aget-framework/aget`](https://github.com/aget-framework/aget) | Framework core: specs, SOPs, validators, docs | **Open here** |
| `aget-framework/template-*-aget` | Agent templates, one per archetype | Disabled — use `aget` |

Template repositories have issues disabled deliberately, so that discussion is not
fragmented across fourteen trackers. **File everything against `aget-framework/aget`.**

## Contribution types

| Type | Description | Typical effort |
|---|---|---|
| Bug fix | Fix an existing defect | Low |
| Documentation | Correct or extend docs and examples | Low |
| Enhancement | Improve an existing capability | Medium |
| New feature | Add a new capability | High |

## Before you start

1. **Search existing issues** on `aget-framework/aget` — including closed ones.
2. **Identify the target.** Each template is independent and versioned separately;
   a change to one template usually needs the same change in the others. Say in
   your issue which repositories you believe are affected.
3. **Read the relevant spec.** Framework behaviour is specified, not just
   implemented — see [`specs/`](https://github.com/aget-framework/aget/tree/main/specs).
   If the code and the spec disagree, that is itself a reportable defect, and the
   spec may be the thing that is wrong.

### Template structure

```
template-*/
├── .aget/
│   ├── version.json    ← version info
│   └── evolution/      ← learning documents
├── AGENTS.md           ← agent configuration
├── CHANGELOG.md        ← release history
└── ...
```

## Workflow

```bash
# 1. Fork via the GitHub UI, then clone your fork
git clone git@github.com:YOUR_USERNAME/aget.git
cd aget

# 2. Branch
git checkout -b fix/short-description     # or feature/short-description

# 3. Make your changes, then test
python -m pytest tests -q

# 4. Commit and push
git commit -m "fix: brief description"
git push origin fix/short-description

# 5. Open a PR against aget-framework/aget
```

CI runs tests on Python 3.10–3.14, a blocking lint set (`ruff --select E9,F63,F7,F82`),
and a check that no operator-identifying home paths appear in the repository.

## Pull request requirements

- [ ] Clear description of what changes and why
- [ ] Tests pass
- [ ] `CHANGELOG.md` updated under `## [Unreleased]`
- [ ] Documentation updated where behaviour changed
- [ ] No breaking changes, or a migration note is included

Changelog entries follow [Keep a Changelog](https://keepachangelog.com/):

```markdown
## [Unreleased]

### Added
- Your new capability (#PR)

### Fixed
- Defect description (#PR)
```

## Code standards

**`AGENTS.md` changes**
- Follow the existing section structure.
- Keep the file within **40,000 characters** (`CAP-TPL-008-01`, `specs/AGET_TEMPLATE_SPEC.md`).
- Verify the wake-up and wind-down protocols still run.

**`.aget/` changes**
- Update `version.json` when adding capabilities.
- Record significant patterns under `evolution/`.

**Pattern changes**
- Patterns expose an `apply_pattern()` function.
- Include a docstring with a usage example.
- Add a corresponding test.

**Specification changes**
- Requirements use [EARS](https://alistairmavin.com/ears/) patterns and carry a
  `CAP-{DOMAIN}-{NNN}` identifier.
- A requirement should name how it is verified. A requirement with no verification
  path is documentation, not a specification.

## Review process

1. PR submitted
2. Maintainer review
3. Feedback addressed
4. Approval and merge to `main`
5. Released on the next version cycle — see
   [`docs/RELEASES.md`](https://github.com/aget-framework/aget/blob/main/docs/RELEASES.md)
   and [`CHANGELOG.md`](https://github.com/aget-framework/aget/blob/main/CHANGELOG.md)

## Questions

Open an issue on [`aget-framework/aget`](https://github.com/aget-framework/aget/issues).

## License

By contributing, you agree that your contributions are licensed under the
[Apache License 2.0](https://github.com/aget-framework/aget/blob/main/LICENSE),
the same license that covers this project.
