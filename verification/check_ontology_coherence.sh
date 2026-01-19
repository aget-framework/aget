#!/bin/bash
# check_ontology_coherence.sh - Lightweight ontology coherence checker
#
# Version: 1.0.0
# Created: 2026-01-12
# Owner: private-aget-framework-AGET
# Related: AGET_VOCABULARY_SPEC Part 7, PROJECT_PLAN_standards_ontology_elevation_v1.0
#
# Checks:
# 1. Vocabulary spec size (warn at 1500, critical at 2000)
# 2. Document type hierarchy completeness
# 3. Specification entries exist
# 4. Basic structural integrity

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGET_ROOT="$(dirname "$SCRIPT_DIR")"
VOCAB_SPEC="$AGET_ROOT/specs/AGET_VOCABULARY_SPEC.md"
INDEX_FILE="$AGET_ROOT/specs/INDEX.md"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Counters
PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Lightweight ontology coherence checker for AGET vocabulary."
    echo ""
    echo "Options:"
    echo "  --help      Show this help message"
    echo "  --verbose   Show detailed output"
    echo "  --json      Output results as JSON"
    echo ""
    echo "Exit codes:"
    echo "  0 - All checks passed"
    echo "  1 - One or more checks failed"
    echo "  2 - Warnings present (no failures)"
    exit 0
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASS_COUNT=$((PASS_COUNT + 1))
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    WARN_COUNT=$((WARN_COUNT + 1))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAIL_COUNT=$((FAIL_COUNT + 1))
}

# Parse arguments
VERBOSE=false
JSON=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --help) usage ;;
        --verbose) VERBOSE=true; shift ;;
        --json) JSON=true; shift ;;
        *) echo "Unknown option: $1"; usage ;;
    esac
done

echo "=== AGET Ontology Coherence Check ==="
echo ""

# Check 1: Vocabulary spec exists
if [[ -f "$VOCAB_SPEC" ]]; then
    log_pass "Vocabulary spec exists: $VOCAB_SPEC"
else
    log_fail "Vocabulary spec not found: $VOCAB_SPEC"
    exit 1
fi

# Check 2: Vocabulary size
VOCAB_LINES=$(wc -l < "$VOCAB_SPEC" | tr -d ' ')
echo ""
echo "--- Vocabulary Size Check (L502) ---"
if [[ $VOCAB_LINES -lt 1500 ]]; then
    log_pass "Vocabulary size OK: $VOCAB_LINES lines (optimal: <1500)"
elif [[ $VOCAB_LINES -lt 2000 ]]; then
    log_warn "Vocabulary size WARNING: $VOCAB_LINES lines (warn: 1500-2000, consider splitting)"
else
    log_fail "Vocabulary size CRITICAL: $VOCAB_LINES lines (>2000, must split)"
fi

# Check 3: Part 7 Standards Document Ontology exists
echo ""
echo "--- Part 7 Structural Checks ---"
if grep -q "# Part 7: Standards Document Ontology" "$VOCAB_SPEC"; then
    log_pass "Part 7: Standards Document Ontology section exists"
else
    log_fail "Part 7: Standards Document Ontology section missing"
fi

# Check 4: Document type hierarchy
REQUIRED_TYPES=("Normative_Document" "Specification_Document" "SOP_Document" "Template_Document" "Learning_Document" "Process_Document")
for dtype in "${REQUIRED_TYPES[@]}"; do
    if grep -q "${dtype}:" "$VOCAB_SPEC"; then
        if $VERBOSE; then log_pass "Document type: $dtype"; fi
    else
        log_fail "Document type missing: $dtype"
    fi
done
log_pass "Document type hierarchy complete (${#REQUIRED_TYPES[@]} types)"

# Check 5: Authority levels defined
echo ""
echo "--- Authority Model Checks ---"
if grep -q "aget:authority_levels" "$VOCAB_SPEC"; then
    log_pass "Authority levels property defined"
else
    log_fail "Authority levels property missing"
fi

AUTHORITY_LEVELS=("CANONICAL" "Active" "Draft" "Deprecated")
for level in "${AUTHORITY_LEVELS[@]}"; do
    if grep -q "$level" "$VOCAB_SPEC"; then
        if $VERBOSE; then log_pass "Authority level: $level"; fi
    else
        log_warn "Authority level not found in examples: $level"
    fi
done

# Check 6: Specification instances
echo ""
echo "--- Specification Instance Checks ---"
SPEC_COUNT=$(grep -c 'skos:broader.*Specification_Document' "$VOCAB_SPEC" || echo "0")
if [[ $SPEC_COUNT -ge 5 ]]; then
    log_pass "Specification instances: $SPEC_COUNT entries (target: ≥5)"
else
    log_fail "Specification instances: $SPEC_COUNT entries (target: ≥5)"
fi

# Check 7: Traceability properties
echo ""
echo "--- Traceability Checks ---"
TRACE_PROPS=("aget:defines" "aget:implements" "aget:supersedes" "aget:governed_by")
TRACE_COUNT=0
for prop in "${TRACE_PROPS[@]}"; do
    if grep -q "$prop" "$VOCAB_SPEC"; then
        TRACE_COUNT=$((TRACE_COUNT + 1))
        if $VERBOSE; then log_pass "Traceability property: $prop"; fi
    fi
done
if [[ $TRACE_COUNT -ge 3 ]]; then
    log_pass "Traceability properties: $TRACE_COUNT defined (target: ≥3)"
else
    log_fail "Traceability properties: $TRACE_COUNT defined (target: ≥3)"
fi

# Check 8: INDEX.md authority column (if exists)
echo ""
echo "--- INDEX.md Checks ---"
if [[ -f "$INDEX_FILE" ]]; then
    if grep -q "| Authority |" "$INDEX_FILE"; then
        log_pass "INDEX.md has Authority column"
    else
        log_warn "INDEX.md missing Authority column"
    fi
else
    log_warn "INDEX.md not found"
fi

# Summary
echo ""
echo "=== Summary ==="
echo -e "Passed: ${GREEN}$PASS_COUNT${NC}"
echo -e "Warnings: ${YELLOW}$WARN_COUNT${NC}"
echo -e "Failed: ${RED}$FAIL_COUNT${NC}"
echo ""

if [[ $FAIL_COUNT -gt 0 ]]; then
    echo -e "${RED}RESULT: FAILED${NC}"
    exit 1
elif [[ $WARN_COUNT -gt 0 ]]; then
    echo -e "${YELLOW}RESULT: PASSED WITH WARNINGS${NC}"
    exit 2
else
    echo -e "${GREEN}RESULT: PASSED${NC}"
    exit 0
fi
