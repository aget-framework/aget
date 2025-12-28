# AGET License Specification

**Version**: 1.0.0
**Status**: Active
**Category**: Standards (Governance)
**Format Version**: 1.2
**Created**: 2025-12-27
**Author**: private-aget-framework-AGET
**Location**: `aget/specs/AGET_LICENSE_SPEC.md`

---

## Abstract

This specification defines the licensing model for the AGET framework. The model establishes a clear separation between framework licensing (Apache 2.0) and agent instance licensing (user's choice), enabling both open ecosystem development and proprietary agent creation.

## Motivation

Licensing clarity is essential for:
1. **Enterprise adoption**: Legal teams require clear licensing terms
2. **Contributor protection**: Patent grants protect all ecosystem participants
3. **User freedom**: Agents built with AGET remain user property
4. **Ecosystem health**: Open framework enables community innovation

## Scope

**Applies to**: All AGET framework components, templates, and agent instances.

**Defines**:
- Framework licensing requirements
- Agent instance licensing rights
- Contribution licensing
- License file requirements

---

## Vocabulary

```yaml
vocabulary:
  meta:
    domain: "licensing"
    version: "1.0.0"
    inherits: "aget_core"

  licensing:
    Framework_License:
      skos:definition: "License governing AGET framework code and templates"
      skos:notation: "Apache-2.0"
    Instance_License:
      skos:definition: "License chosen by user for their agent instance"
      skos:example: ["Apache-2.0", "MIT", "GPL-3.0", "Proprietary"]
    Patent_Grant:
      skos:definition: "License provision granting patent rights to users"
    Patent_Retaliation:
      skos:definition: "License provision terminating rights if user initiates patent litigation"
    Framework_Code:
      skos:definition: "Code provided by AGET framework including templates and patterns"
      skos:narrower: ["Template_Code", "Pattern_Code", "Validator_Code"]
    Instance_Code:
      skos:definition: "Code created by user within their agent instance"
    Contribution:
      skos:definition: "Code or documentation submitted to AGET framework"
```

---

## Requirements

### CAP-LIC-001: Framework License

The SYSTEM shall license all Framework_Code under Apache License 2.0.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-LIC-001-01 | ubiquitous | The SYSTEM shall include LICENSE file containing Apache-2.0 text |
| CAP-LIC-001-02 | ubiquitous | The SYSTEM shall include copyright notice in LICENSE file |
| CAP-LIC-001-03 | ubiquitous | The SYSTEM shall grant Patent_Grant to all users |
| CAP-LIC-001-04 | ubiquitous | The SYSTEM shall include Patent_Retaliation clause |

**Enforcement**: License file validation

#### Why Apache 2.0

| Benefit | Description |
|---------|-------------|
| Patent Grant | Contributors cannot patent contributions and sue adopters |
| Patent Retaliation | Litigation initiators lose license rights |
| Ecosystem Immunity | Framework remains free as it gains value |
| Enterprise Adoption | Legal teams approve Apache 2.0 readily |

**Precedent**: Kubernetes, Android, Swift, TensorFlow

### CAP-LIC-002: Instance License

The SYSTEM shall allow users to choose Instance_License for their agents.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-LIC-002-01 | ubiquitous | The SYSTEM shall NOT impose license requirements on Instance_Code |
| CAP-LIC-002-02 | ubiquitous | The SYSTEM shall allow proprietary Instance_License |
| CAP-LIC-002-03 | ubiquitous | The SYSTEM shall allow open-source Instance_License |
| CAP-LIC-002-04 | ubiquitous | The SYSTEM shall document license choice in agent README |

**Enforcement**: Documentation review

#### Instance License Options

| Option | Use Case | Recommended For |
|--------|----------|-----------------|
| Apache 2.0 | Patent protection, enterprise | Public/shared agents |
| MIT | Permissive, simple | Quick projects |
| GPL-3.0 | Copyleft, open | Community agents |
| Proprietary | All rights reserved | Private/commercial |

### CAP-LIC-003: License Separation

The SYSTEM shall maintain clear separation between Framework_Code and Instance_Code.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-LIC-003-01 | ubiquitous | The SYSTEM shall identify Framework_Code in .aget/ directory |
| CAP-LIC-003-02 | ubiquitous | The SYSTEM shall treat code outside .aget/ as Instance_Code |
| CAP-LIC-003-03 | conditional | IF user modifies Framework_Code THEN modifications remain Apache 2.0 |
| CAP-LIC-003-04 | ubiquitous | The SYSTEM shall NOT require Instance_Code license disclosure |

**Enforcement**: Directory structure validation

#### License Boundary

```
agent-instance/
├── .aget/                    # Framework_Code (Apache 2.0)
│   ├── version.json          # Apache 2.0
│   ├── identity.json         # Apache 2.0
│   ├── patterns/             # Apache 2.0
│   └── ...                   # Apache 2.0
│
├── governance/               # Instance_Code (User's choice)
├── planning/                 # Instance_Code (User's choice)
├── src/                      # Instance_Code (User's choice)
├── docs/                     # Instance_Code (User's choice)
└── LICENSE                   # Instance_License declaration
```

### CAP-LIC-004: Contribution License

The SYSTEM shall require Contribution licensing under Apache 2.0.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-LIC-004-01 | ubiquitous | The SYSTEM shall require Apache-2.0 for all Contributions |
| CAP-LIC-004-02 | ubiquitous | The SYSTEM shall include DCO (Developer Certificate of Origin) |
| CAP-LIC-004-03 | event-driven | WHEN Contribution submitted, the SYSTEM shall verify license compatibility |
| CAP-LIC-004-04 | ubiquitous | The SYSTEM shall NOT accept Contributions with incompatible licenses |

**Enforcement**: Contribution review process

### CAP-LIC-005: License Files

The SYSTEM shall maintain required license files.

| ID | Pattern | Statement |
|----|---------|-----------|
| CAP-LIC-005-01 | ubiquitous | The SYSTEM shall include LICENSE in template root |
| CAP-LIC-005-02 | ubiquitous | The SYSTEM shall include NOTICE file if third-party components exist |
| CAP-LIC-005-03 | conditional | IF agent instance is public THEN the SYSTEM should include LICENSE |
| CAP-LIC-005-04 | ubiquitous | The SYSTEM shall NOT commit LICENSE to .gitignore |

**Enforcement**: `validate_license_compliance.py`

---

## Authority Model

```yaml
authority:
  applies_to: "all_aget_components"

  governed_by:
    spec: "AGET_LICENSE_SPEC"
    owner: "private-aget-framework-AGET"

  framework_authority:
    license: "Apache-2.0"
    can_change: false
    rationale: "License stability is foundational to ecosystem trust"

  instance_authority:
    license: "user_choice"
    can_change: true
    rationale: "User ownership of their work"

  contribution_authority:
    license: "Apache-2.0"
    required: true
    rationale: "Contribution compatibility with framework"
```

---

## Inviolables

```yaml
inviolables:
  inherited:
    - id: "INV-LIC-001"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT change Framework_License from Apache-2.0"
      rationale: "License stability is foundational to ecosystem trust"

    - id: "INV-LIC-002"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT impose license requirements on Instance_Code"
      rationale: "User freedom is core principle"

    - id: "INV-LIC-003"
      source: "aget_framework"
      statement: "The SYSTEM shall NOT accept Contributions under incompatible licenses"
      rationale: "Ecosystem license coherence"
```

---

## Structural Requirements

```yaml
structure:
  required_files:
    - path: "LICENSE"
      purpose: "License declaration"
      content: "Apache License 2.0 full text"
      scope: "templates"

  optional_files:
    - path: "NOTICE"
      purpose: "Third-party attribution"
      condition: "IF third-party components exist"

    - path: "LICENSE"
      purpose: "Instance license declaration"
      scope: "agent_instances"
      content: "User's choice"
```

---

## License Text Reference

### Apache License 2.0 Header

```
Copyright [year] [owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```

---

## Migration

### Upgrading from MIT

Agents created from earlier MIT-licensed templates:
1. Remain valid under MIT (grandfathered)
2. Can optionally upgrade to Apache 2.0
3. Upgrade provides patent protection benefits

```bash
# To upgrade: Replace LICENSE file content
cp /path/to/apache-2.0-license.txt LICENSE
git add LICENSE
git commit -m "chore: Upgrade license to Apache 2.0 for patent protection"
```

---

## Theoretical Basis

```yaml
theoretical_basis:
  primary: "Open Source Definition"
  secondary:
    - "Patent Commons"
    - "Contributor License Agreement principles"
  rationale: >
    Apache 2.0 balances open ecosystem development with contributor
    and user protection. The dual-license model (framework vs instance)
    enables both community innovation and commercial adoption.
  reference: "https://opensource.org/licenses/Apache-2.0"
```

---

## Validation

```bash
# Validate license compliance
python3 validation/validate_license_compliance.py --dir /path/to/template

# Expected output:
# ✅ LICENSE file exists
# ✅ LICENSE contains Apache-2.0
# ✅ Copyright notice present
# ⚠️  NOTICE file missing (optional)
```

---

## References

- Apache License 2.0: https://www.apache.org/licenses/LICENSE-2.0
- Open Source Initiative: https://opensource.org/
- AGET Framework: https://github.com/aget-framework

---

## Graduation History

```yaml
graduation:
  source: "README.md licensing section"
  pattern_origin: "Framework licensing practice"
  rationale: "Formalize implicit licensing model into testable specification"
```

---

*AGET License Specification v1.0.0*
*Format: AGET_SPEC_FORMAT v1.2 (EARS + SKOS)*
*"The framework is open commons. What you build with it is yours."*
