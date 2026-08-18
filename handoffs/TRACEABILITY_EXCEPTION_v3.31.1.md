# Test Traceability Exception — AGET v3.31.1

**Decision**: Principal-authorized, bounded one-release exception
**Scope**: v3.31.1 manager-suite requirement-reference percentage only
**Expires**: before the next public AGET release

## Why publication proceeds

The public v3.31.0 package does not contain the complete close-gate correction. Waiting leaves every
supervisor whose migration depends on closing its prior work without a supported immutable repair. The
v3.31.1 receiver oracle and public continuous-integration checks pass, while the unmet assurance is a
test-to-requirement documentation ratio rather than a known behavioral failure.

The principal determined that this bounded migration delay is the greater harm. This decision does not waive receiver verification. It also does not waive any receiver test, package-integrity check, public automation check, or downstream verification.

## Measurement

The producing framework-manager test corpus was measured at commit `da9e1c3c` using this predicate:

- include every Python function whose name begins with `test_` in `tests/test_*.py`;
- exclude the traceability meta-test plus four named pre-pattern legacy files;
- count a method as linked only when its function docstring contains a recognized requirement,
  verification, or capability identifier;
- compute `100 × linked methods ÷ included methods`.

| Population | Linked methods | Included methods | Result |
|---|---:|---:|---:|
| Complete manager test corpus | 747 | 1,739 | **42.956%** |
| Release-critical filename subset | 189 | 311 | **60.772%** |
| Remaining corpus | 558 | 1,428 | **39.076%** |

The release-critical subset is selected by the disclosed filename expression
`close_gate|close_project|release|migration|v331|tag_|deploy`. Its result is above the 54% release
floor, so the missing links are not concentrated in the close-gate, migration, tagging, deployment, or
release-test files selected by that predicate.

Reproduce the arithmetic from the published counts:

```sh
python3 -c 'a,t,ca,ct=747,1739,189,311; print(round(100*a/t,3), round(100*ca/ct,3), round(100*(a-ca)/(t-ct),3))'
```

Expected output: `42.956 60.772 39.076`.

The source corpus is manager-owned and is not part of the public release. The predicate, source commit,
population counts, partition rule, arithmetic, result, and this limitation are public so a receiver can
audit what was waived without treating producer evidence as independent behavioral acceptance.

## Remediation contract

- **Owner**: the AGET framework manager.
- **Deadline**: before any public AGET release after v3.31.1.
- **Completion evidence**: a public artifact carrying the same predicate and a reproducible result of at
  least 54%, linked from that release's pre-publication evidence.
- **Missed-deadline consequence**: the next release is blocked; this exception cannot be renewed or used
  as precedent.

## Explicit non-precedent

This exception applies only to the 54% manager-suite traceability threshold for v3.31.1. It does not
change the threshold, redefine traceability, establish adoption, authorize a supervisor migration, or
permit another release to proceed below the requirement.
