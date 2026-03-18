# AGET Security Specification

**Version**: 1.0.1
**Status**: Active
**Category**: Technical (Security)
**Format Version**: 1.2
**Created**: 2026-01-04
**Updated**: 2026-01-04
**Author**: aget-framework
**Location**: `aget/specs/AGET_SECURITY_SPEC.md`
**Change Origin**: PROJECT_PLAN_v3.2.0 Gate 2.6
**Related Specs**: AGET_LICENSE_SPEC, AGET_TEMPLATE_SPEC

---

## Abstract

This specification defines security requirements for the AGET framework, including content security, secrets management, pre-publication review, and public/private boundary management.

## Motivation

Security challenges observed in practice:

1. **Private content leakage**: Risk of publishing sensitive information (L430)
2. **Secrets in configs**: API keys or credentials in committed files
3. **No pre-publication review**: Content published without sanitization
4. **Audit gap**: No tracking of what was published when

L430 (Content Security for Public Repos) revealed these gaps.

## Scope

**Applies to**: All AGET repositories, especially public aget-framework repos.

**Defines**:
- Content security requirements
- Secrets management
- Pre-publication review process
- Public/private boundary

**Does not cover**:
- License compliance (see AGET_LICENSE_SPEC)
- Authentication/authorization (out of scope for config framework)

---

## Requirements

### CAP-SEC-001: Content Security (L430)

**SHALL** requirements for content security:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-SEC-001-01 | Public repos SHALL NOT contain PII | Privacy |
| CAP-SEC-001-02 | Public repos SHALL NOT contain secrets | Security |
| CAP-SEC-001-03 | Public repos SHALL NOT contain internal paths | Exposure |
| CAP-SEC-001-04 | L-docs for public repos SHALL be sanitized | Privacy |

**Content Categories:**

| Category | Public OK | Examples |
|----------|-----------|----------|
| Framework patterns | ✅ | Specs, templates, validators |
| Session learnings (sanitized) | ✅ | L-docs without PII |
| Internal agent names | ❌ | private-*-AGET |
| File paths with usernames | ❌ | /Users/username/ |
| API keys, tokens | ❌ | Any credential |
| Client names, projects | ❌ | Work-related content |

### CAP-SEC-002: Secrets Management

**SHALL** requirements for secrets:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-SEC-002-01 | .gitignore SHALL exclude credential files | Prevention |
| CAP-SEC-002-02 | .env files SHALL NOT be committed | Standard practice |
| CAP-SEC-002-03 | GitHub secrets SHALL be used for CI | Security |
| CAP-SEC-002-04 | Credential patterns SHALL be documented | Awareness |

**Credential File Patterns (for .gitignore):**

```gitignore
# Credentials and secrets
.env
.env.*
*.pem
*.key
credentials.json
secrets.yaml
*_SECRET*
*_TOKEN*
```

### CAP-SEC-003: Pre-Publication Review

**SHALL** requirements for publication review:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-SEC-003-01 | Content SHALL be reviewed before public push | Prevention |
| CAP-SEC-003-02 | Review SHALL check for PII | Privacy |
| CAP-SEC-003-03 | Review SHALL check for internal references | Exposure |
| CAP-SEC-003-04 | Large commits SHALL have explicit sign-off | Accountability |

**Pre-Publication Checklist:**

```markdown
## Pre-Publication Review

- [ ] No PII (names, emails, usernames)
- [ ] No secrets (API keys, tokens, passwords)
- [ ] No internal paths (/Users/*, /home/*)
- [ ] No internal agent names (private-*-AGET)
- [ ] No client/project references
- [ ] L-docs sanitized (abstract learnings only)
```

### CAP-SEC-004: Public/Private Boundary

**SHALL** requirements for boundary management:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-SEC-004-01 | Private repos SHALL be clearly marked | Awareness |
| CAP-SEC-004-02 | Public repos SHALL NOT reference private repos | Exposure |
| CAP-SEC-004-03 | Migration from private to public SHALL require review | Safety |

**Boundary Pattern:**

```
private-*-AGET (private)
    │
    ↓ sanitize + review
    │
aget-framework/* (public)
```

**Private Indicators:**

```yaml
# In private repos
private: true
visibility: internal

# In manifest.yaml
repo_visibility: private
```

### CAP-SEC-005: Audit Logging

**SHOULD** requirements for audit:

| ID | Requirement | Rationale |
|----|-------------|-----------|
| CAP-SEC-005-01 | Releases SHOULD record what was published | Accountability |
| CAP-SEC-005-02 | Publication dates SHOULD be tracked | Audit trail |
| CAP-SEC-005-03 | Reviewers SHOULD be recorded | Accountability |

---

## Sanitization Patterns

### L-doc Sanitization

**Before (private):**

```markdown
# L430: Content Security for Public Repos

During work with ClientX on the widget feature, we discovered
that /Users/johndoe/projects/clientx-api/... contained exposed
credentials in config.json.
```

**After (public):**

```markdown
# L430: Content Security for Public Repos

During framework development, we discovered that configuration
files may inadvertently contain credentials that should not be
committed to version control.
```

### Path Sanitization

```python
# Replace user-specific paths
path = path.replace("/Users/username/", "/path/to/")
path = path.replace("/home/username/", "/path/to/")

# Replace internal references
text = text.replace("private-supervisor-AGET", "supervisor-agent")
```

### CAP-SEC-006: EARS System-Level Requirements

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-SEC-006-01 | ubiquitous | The SYSTEM shall scan all public-facing content for private agent names and internal paths before publication. |
| CAP-SEC-006-02 | event-driven | WHEN a file is staged for commit to a public repository, THEN the SYSTEM shall validate it against CAP-SEC-001 content security rules. |
| CAP-SEC-006-03 | prohibited | The SYSTEM shall NOT include files matching `.env`, `credentials.*`, or `*_SECRET*` patterns in public commits. |

---

## Enforcement

| Requirement | Validator | Status |
|-------------|-----------|--------|
| CAP-SEC-001-* | validate_public_content.py | Planned |
| CAP-SEC-002-* | .gitignore review | Manual |
| CAP-SEC-003-* | PR review checklist | Manual |
| CAP-SEC-004-* | Manual review | Manual |

---

## Anti-Patterns

### Anti-Pattern 1: Unsanitized L-doc

```markdown
❌ ANTI-PATTERN: Personal info in public L-doc

During my (John Doe, john@company.com) work on ClientX...
```

### Anti-Pattern 2: Internal Paths

```markdown
❌ ANTI-PATTERN: User paths in examples

```bash
cd /Users/gabormelli/github/aget-framework/aget
```
```

```markdown
✅ CORRECT: Generic paths

```bash
cd /path/to/aget-framework/aget
```
```

---

## Verification Tests

| V-test ID | Requirement | Method | Description |
|-----------|-------------|--------|-------------|
| V-SEC-001 | CAP-SEC-001 | automated | Verify public repos do not contain PII, secrets, or internal paths by scanning for known private patterns |
| V-SEC-002 | CAP-SEC-002 | automated | Verify .gitignore excludes credential file patterns (.env, *.pem, *.key, credentials.json, secrets.yaml) |
| V-SEC-003 | CAP-SEC-003 | manual | Verify pre-publication review checklist is completed before public pushes (PII, secrets, internal paths, agent names) |
| V-SEC-004 | CAP-SEC-004 | automated | Verify public repos do not reference private repos (private-*-AGET, gmelli/*) |
| V-SEC-005 | CAP-SEC-005 | inspection | Verify releases record what was published with publication dates and reviewer |
| V-SEC-006 | CAP-SEC-006 | automated | Verify system scans public-facing content for private agent names and internal paths before publication |
| V-SEC-007 | CAP-SEC-002 | automated | Verify .env files are not committed to any repository |
| V-SEC-008 | CAP-SEC-001 | automated | Verify L-docs in public repos are sanitized (no PII, no user-specific paths) |

### Validation Commands

```bash
# Scan for private patterns in public repo (V-SEC-001, V-SEC-004)
grep -rE "private-\w+-[aA][gG][eE][tT]|gmelli/|/Users/\w+/" aget/ --include="*.md" && echo "FAIL: private content found" || echo "PASS: no private content"

# Verify .gitignore excludes credential patterns (V-SEC-002)
for pattern in ".env" "*.pem" "*.key" "credentials.json"; do
  grep -q "$pattern" .gitignore && echo "PASS: $pattern excluded" || echo "FAIL: $pattern not excluded"
done

# Verify no .env files committed (V-SEC-007)
git ls-files | grep -E "\.env$|\.env\." && echo "FAIL: .env files committed" || echo "PASS: no .env files"
```

---

## References

- L430: Content Security for Public Repos
- AGET_LICENSE_SPEC.md
- GitHub Security Best Practices

---

## Changelog

### v1.0.1 (2026-03-17)

- Added CAP-SEC-006: EARS System-Level Requirements (L682 L0→L1 uplift)
- 3 requirements with SYSTEM subject, ubiquitous/event-driven/prohibited patterns

### v1.0.0 (2026-01-04)

- Initial specification
- Content security requirements (L430)
- Secrets management
- Pre-publication review process
- Public/private boundary

---

*AGET_SECURITY_SPEC.md — Security standards for AGET framework*
