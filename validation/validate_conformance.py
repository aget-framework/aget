#!/usr/bin/env python3
"""
AGET v3.x Conformance Assessment Validator.

Implements: L518 (Conformance Assessment Rubric Pattern)
Traces to: AGET_5D_ARCHITECTURE_SPEC.md, AGET_TEMPLATE_SPEC.md, AGET_INSTANCE_SPEC.md

Unified validator that assesses agent conformance against v3.x requirements,
producing a composite score across 5 dimensions with conformance level classification.

Usage:
    python3 validate_conformance.py <agent_path>
    python3 validate_conformance.py --dir /path/to/agent
    python3 validate_conformance.py --json
    python3 validate_conformance.py --verbose

Exit codes:
    0: L2 Compliant or higher (>=60%)
    1: L1 Baseline or L0 Non-Conformant (<60%)
    2: File/path errors
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Version
__version__ = "1.0.0"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class Check:
    """Individual conformance check result."""
    id: str
    name: str
    passed: bool
    score: float  # 0-5 scale
    max_score: float = 5.0
    message: str = ""
    critical: bool = False


@dataclass
class DimensionResult:
    """Result for a single dimension."""
    dimension: str
    weight: float
    checks: List[Check] = field(default_factory=list)

    @property
    def raw_score(self) -> float:
        """Average score across checks (0-5 scale)."""
        if not self.checks:
            return 0.0
        return sum(c.score for c in self.checks) / len(self.checks)

    @property
    def weighted_score(self) -> float:
        """Weighted contribution to composite."""
        return self.raw_score * self.weight

    @property
    def percentage(self) -> float:
        """Percentage score (0-100)."""
        return (self.raw_score / 5.0) * 100

    @property
    def passed(self) -> bool:
        """True if all critical checks passed."""
        return all(c.passed for c in self.checks if c.critical)


@dataclass
class ConformanceResult:
    """Overall conformance assessment result."""
    agent_path: str
    agent_name: str = ""
    agent_type: str = ""  # "instance" or "template"
    archetype: str = ""
    framework_version: str = ""
    assessed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    dimensions: Dict[str, DimensionResult] = field(default_factory=dict)
    critical_failures: List[str] = field(default_factory=list)

    @property
    def composite_score(self) -> float:
        """Weighted composite score (0-5 scale)."""
        if not self.dimensions:
            return 0.0
        return sum(d.weighted_score for d in self.dimensions.values())

    @property
    def percentage(self) -> float:
        """Percentage score (0-100)."""
        return (self.composite_score / 5.0) * 100

    @property
    def level(self) -> str:
        """Conformance level classification."""
        if self.critical_failures:
            return "L0_NON_CONFORMANT"
        pct = self.percentage
        if pct >= 85:
            return "L3_EXEMPLARY"
        elif pct >= 60:
            return "L2_COMPLIANT"
        elif pct >= 40:
            return "L1_BASELINE"
        else:
            return "L0_NON_CONFORMANT"

    @property
    def level_label(self) -> str:
        """Human-readable level label."""
        labels = {
            "L0_NON_CONFORMANT": "Non-Conformant",
            "L1_BASELINE": "Baseline",
            "L2_COMPLIANT": "Compliant",
            "L3_EXEMPLARY": "Exemplary"
        }
        return labels.get(self.level, "Unknown")

    @property
    def passed(self) -> bool:
        """True if L2 or higher."""
        return self.level in ("L2_COMPLIANT", "L3_EXEMPLARY")

    def gaps(self) -> List[Dict[str, str]]:
        """List of gaps requiring attention."""
        gaps = []
        for dim_name, dim in self.dimensions.items():
            for check in dim.checks:
                if check.score < 3.0:  # Below "Adequate"
                    gaps.append({
                        "dimension": dim_name,
                        "criterion": check.id,
                        "score": f"{check.score}/5.0",
                        "message": check.message
                    })
        return gaps


# =============================================================================
# Conformance Validator
# =============================================================================

class ConformanceValidator:
    """AGET v3.x Conformance Assessment Validator."""

    # Dimension weights (must sum to 1.0)
    DIMENSION_WEIGHTS = {
        "D1_PERSONA": 0.15,
        "D2_MEMORY": 0.25,
        "D3_REASONING": 0.25,
        "D4_SKILLS": 0.20,
        "D5_CONTEXT": 0.15,
    }

    def __init__(self, agent_path: str):
        """Initialize validator with agent path."""
        self.agent_path = Path(agent_path).resolve()
        self.result = ConformanceResult(agent_path=str(self.agent_path))

    def validate(self) -> ConformanceResult:
        """Run full conformance assessment."""
        # First, check critical requirements
        self._check_critical_requirements()

        # If critical failures, still assess dimensions for feedback
        # Load agent metadata
        self._load_agent_metadata()

        # Assess each dimension
        self.result.dimensions["D1_PERSONA"] = self._assess_d1_persona()
        self.result.dimensions["D2_MEMORY"] = self._assess_d2_memory()
        self.result.dimensions["D3_REASONING"] = self._assess_d3_reasoning()
        self.result.dimensions["D4_SKILLS"] = self._assess_d4_skills()
        self.result.dimensions["D5_CONTEXT"] = self._assess_d5_context()

        return self.result

    # -------------------------------------------------------------------------
    # Critical Requirements
    # -------------------------------------------------------------------------

    def _check_critical_requirements(self):
        """Check critical requirements that cause immediate L0."""
        critical_files = [
            (".aget/version.json", "version.json missing"),
            (".aget/identity.json", "identity.json missing"),
            ("AGENTS.md", "AGENTS.md missing"),
            ("governance", "governance/ directory missing"),
        ]

        for path, message in critical_files:
            full_path = self.agent_path / path
            if not full_path.exists():
                self.result.critical_failures.append(message)

        # Check AGENTS.md size limit
        agents_md = self.agent_path / "AGENTS.md"
        if agents_md.exists():
            size = agents_md.stat().st_size
            if size > 40000:
                self.result.critical_failures.append(
                    f"AGENTS.md exceeds 40KB limit ({size} bytes)"
                )

        # Check manifest.yaml for templates
        version_json = self.agent_path / ".aget/version.json"
        if version_json.exists():
            try:
                with open(version_json) as f:
                    data = json.load(f)
                if data.get("instance_type") == "template":
                    manifest = self.agent_path / "manifest.yaml"
                    if not manifest.exists():
                        self.result.critical_failures.append(
                            "manifest.yaml missing (required for templates)"
                        )
            except (json.JSONDecodeError, IOError):
                pass

    def _load_agent_metadata(self):
        """Load agent metadata from version.json."""
        version_json = self.agent_path / ".aget/version.json"
        if version_json.exists():
            try:
                with open(version_json) as f:
                    data = json.load(f)
                self.result.agent_name = data.get("agent_name", "")
                self.result.agent_type = data.get("instance_type", "unknown")
                self.result.archetype = data.get("archetype", data.get("template", ""))
                self.result.framework_version = data.get("aget_version", "")
            except (json.JSONDecodeError, IOError):
                pass

    # -------------------------------------------------------------------------
    # D1: PERSONA Assessment
    # -------------------------------------------------------------------------

    def _assess_d1_persona(self) -> DimensionResult:
        """Assess D1 PERSONA dimension."""
        result = DimensionResult(
            dimension="D1_PERSONA",
            weight=self.DIMENSION_WEIGHTS["D1_PERSONA"]
        )

        # P1: Archetype Declaration
        result.checks.append(self._check_p1_archetype())

        # P2: Governance Intensity
        result.checks.append(self._check_p2_governance())

        # P3: Identity Artifacts
        result.checks.append(self._check_p3_identity_artifacts())

        # P4: Goal Orientation (North Star)
        result.checks.append(self._check_p4_goal_orientation())

        # P5: Version Coherence (L444)
        result.checks.append(self._check_p5_version_coherence())

        return result

    def _check_p1_archetype(self) -> Check:
        """P1: Archetype Declaration."""
        version_json = self.agent_path / ".aget/version.json"
        agents_md = self.agent_path / "AGENTS.md"

        score = 0.0
        message = ""

        if version_json.exists():
            try:
                with open(version_json) as f:
                    data = json.load(f)
                archetype = data.get("archetype") or data.get("template")
                if archetype:
                    score = 3.0
                    message = f"Archetype: {archetype}"

                    # Check if also in AGENTS.md
                    if agents_md.exists():
                        with open(agents_md) as f:
                            content = f.read()
                        if archetype.lower() in content.lower():
                            score = 4.0
                            message += " (documented in AGENTS.md)"
                else:
                    score = 1.0
                    message = "No archetype declared"
            except (json.JSONDecodeError, IOError):
                score = 0.0
                message = "version.json unreadable"
        else:
            score = 0.0
            message = "version.json missing"

        return Check(
            id="P1",
            name="Archetype Declaration",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_p2_governance(self) -> Check:
        """P2: Governance Intensity."""
        manifest = self.agent_path / "manifest.yaml"
        agents_md = self.agent_path / "AGENTS.md"

        score = 1.0  # Default: no governance capability (defaults to balanced)
        message = "No explicit governance capability"

        governance_caps = []

        # Check manifest.yaml
        if manifest.exists():
            try:
                with open(manifest) as f:
                    content = f.read()
                for cap in ["capability-governance-rigorous",
                           "capability-governance-balanced",
                           "capability-governance-exploratory"]:
                    if cap in content:
                        governance_caps.append(cap)
            except IOError:
                pass

        # Check AGENTS.md
        if agents_md.exists():
            try:
                with open(agents_md) as f:
                    content = f.read()
                for cap in ["capability-governance-rigorous",
                           "capability-governance-balanced",
                           "capability-governance-exploratory"]:
                    if cap in content:
                        if cap not in governance_caps:
                            governance_caps.append(cap)
            except IOError:
                pass

        if len(governance_caps) == 1:
            score = 4.0
            message = f"Governance: {governance_caps[0]}"
        elif len(governance_caps) > 1:
            score = 2.0
            message = f"Multiple governance capabilities (conflict): {governance_caps}"

        return Check(
            id="P2",
            name="Governance Intensity",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_p3_identity_artifacts(self) -> Check:
        """P3: Identity Artifacts."""
        files = [
            ".aget/version.json",
            ".aget/identity.json",
            "governance/CHARTER.md",
            "governance/MISSION.md",
            "AGENTS.md"
        ]

        existing = sum(1 for f in files if (self.agent_path / f).exists())

        if existing == 5:
            score = 4.0
            message = f"All {existing} identity files present"
        elif existing >= 3:
            score = 3.0
            message = f"{existing}/5 identity files present"
        elif existing >= 2:
            score = 2.0
            message = f"{existing}/5 identity files present"
        elif existing >= 1:
            score = 1.0
            message = f"{existing}/5 identity files present"
        else:
            score = 0.0
            message = "No identity files"

        return Check(
            id="P3",
            name="Identity Artifacts",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=True
        )

    def _check_p4_goal_orientation(self) -> Check:
        """P4: Goal Orientation (North Star)."""
        identity_json = self.agent_path / ".aget/identity.json"

        score = 0.0
        message = "No goal orientation"

        if identity_json.exists():
            try:
                with open(identity_json) as f:
                    data = json.load(f)
                north_star = data.get("north_star")
                if north_star:
                    if isinstance(north_star, dict) and north_star.get("statement"):
                        score = 4.0
                        message = "North Star defined (object format)"
                    elif isinstance(north_star, str) and len(north_star) > 10:
                        score = 3.0
                        message = "North Star defined (string format)"
                    else:
                        score = 2.0
                        message = "North Star present but minimal"
                else:
                    score = 1.0
                    message = "identity.json exists but no north_star"
            except (json.JSONDecodeError, IOError):
                score = 0.0
                message = "identity.json unreadable"
        else:
            # Check AGENTS.md for purpose statement
            agents_md = self.agent_path / "AGENTS.md"
            if agents_md.exists():
                try:
                    with open(agents_md) as f:
                        content = f.read().lower()
                    if "purpose" in content or "north star" in content:
                        score = 2.0
                        message = "Purpose in AGENTS.md only"
                except IOError:
                    pass

        return Check(
            id="P4",
            name="Goal Orientation",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_p5_version_coherence(self) -> Check:
        """P5: Version Coherence (L444)."""
        version_json = self.agent_path / ".aget/version.json"
        agents_md = self.agent_path / "AGENTS.md"

        score = 0.0
        message = ""
        versions = {}

        # Get version from version.json
        if version_json.exists():
            try:
                with open(version_json) as f:
                    data = json.load(f)
                versions["version.json"] = data.get("aget_version", "")
            except (json.JSONDecodeError, IOError):
                pass

        # Get version from AGENTS.md
        if agents_md.exists():
            try:
                with open(agents_md) as f:
                    for line in f:
                        if "@aget-version:" in line.lower():
                            parts = line.split(":")
                            if len(parts) >= 2:
                                versions["AGENTS.md"] = parts[1].strip()
                            break
            except IOError:
                pass

        if len(versions) >= 2:
            if len(set(versions.values())) == 1:
                score = 5.0
                message = f"Version coherent: {list(versions.values())[0]}"
            else:
                score = 2.0
                message = f"Version mismatch: {versions}"
        elif len(versions) == 1:
            score = 3.0
            message = f"Single version source: {versions}"
        else:
            score = 0.0
            message = "No version information"

        return Check(
            id="P5",
            name="Version Coherence",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    # -------------------------------------------------------------------------
    # D2: MEMORY Assessment
    # -------------------------------------------------------------------------

    def _assess_d2_memory(self) -> DimensionResult:
        """Assess D2 MEMORY dimension."""
        result = DimensionResult(
            dimension="D2_MEMORY",
            weight=self.DIMENSION_WEIGHTS["D2_MEMORY"]
        )

        # M1: Memory Structure
        result.checks.append(self._check_m1_memory_structure())

        # M2: Learning Capture
        result.checks.append(self._check_m2_learning_capture())

        # M3: Session Protocols
        result.checks.append(self._check_m3_session_protocols())

        # M4: Memory Directories
        result.checks.append(self._check_m4_memory_directories())

        # M5: CLAUDE.md Symlink
        result.checks.append(self._check_m5_claude_symlink())

        return result

    def _check_m1_memory_structure(self) -> Check:
        """M1: Memory Structure (6-layer model)."""
        layers = {
            "evolution": self.agent_path / ".aget/evolution",
            "patterns": self.agent_path / ".aget/patterns",
            "governance": self.agent_path / "governance",
            "planning": self.agent_path / "planning",
            "sessions": self.agent_path / "sessions",
            "inherited": self.agent_path / "inherited",
        }

        existing = sum(1 for p in layers.values() if p.exists())

        if existing >= 5:
            score = 4.0
            message = f"{existing}/6 memory layers present"
        elif existing >= 4:
            score = 3.0
            message = f"{existing}/6 memory layers present"
        elif existing >= 2:
            score = 2.0
            message = f"{existing}/6 memory layers present"
        else:
            score = 1.0
            message = f"{existing}/6 memory layers present"

        return Check(
            id="M1",
            name="Memory Structure",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_m2_learning_capture(self) -> Check:
        """M2: Learning Capture (L-docs)."""
        evolution_dir = self.agent_path / ".aget/evolution"

        score = 0.0
        message = ""

        if evolution_dir.exists():
            ldocs = list(evolution_dir.glob("L*.md"))
            count = len(ldocs)

            if count >= 10:
                score = 5.0
                message = f"{count} L-docs (excellent)"
            elif count >= 5:
                score = 4.0
                message = f"{count} L-docs"
            elif count >= 1:
                score = 3.0
                message = f"{count} L-doc(s)"
            else:
                score = 2.0
                message = "evolution/ exists but no L-docs"
        else:
            score = 1.0
            message = "No evolution/ directory"

        return Check(
            id="M2",
            name="Learning Capture",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_m3_session_protocols(self) -> Check:
        """M3: Session Protocols (wake/wind scripts)."""
        patterns_dir = self.agent_path / ".aget/patterns"
        scripts_dir = self.agent_path / "scripts"

        wake_up = None
        wind_down = None

        # Check multiple locations
        for base in [patterns_dir / "session", scripts_dir, self.agent_path]:
            if (base / "wake_up.py").exists():
                wake_up = base / "wake_up.py"
            if (base / "wind_down.py").exists():
                wind_down = base / "wind_down.py"

        if wake_up and wind_down:
            score = 4.0
            message = "Wake/wind-down scripts present"
        elif wake_up or wind_down:
            score = 3.0
            message = "Partial session scripts"
        else:
            # Check if protocols documented in AGENTS.md
            agents_md = self.agent_path / "AGENTS.md"
            if agents_md.exists():
                try:
                    with open(agents_md) as f:
                        content = f.read().lower()
                    if "wake" in content and "wind" in content:
                        score = 2.0
                        message = "Session protocols documented (no scripts)"
                    else:
                        score = 1.0
                        message = "No session protocols"
                except IOError:
                    score = 1.0
                    message = "No session protocols"
            else:
                score = 1.0
                message = "No session protocols"

        return Check(
            id="M3",
            name="Session Protocols",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_m4_memory_directories(self) -> Check:
        """M4: Core Memory Directories."""
        dirs = [
            "governance",
            "planning",
            "sessions",
            "knowledge",
        ]

        existing = sum(1 for d in dirs if (self.agent_path / d).exists())

        if existing == 4:
            score = 4.0
            message = "All 4 core directories present"
        elif existing >= 3:
            score = 3.0
            message = f"{existing}/4 core directories"
        elif existing >= 2:
            score = 2.0
            message = f"{existing}/4 core directories"
        else:
            score = 1.0
            message = f"{existing}/4 core directories"

        return Check(
            id="M4",
            name="Memory Directories",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_m5_claude_symlink(self) -> Check:
        """M5: CLAUDE.md is symlink to AGENTS.md."""
        claude_md = self.agent_path / "CLAUDE.md"
        agents_md = self.agent_path / "AGENTS.md"

        score = 0.0
        message = ""

        if claude_md.exists():
            if claude_md.is_symlink():
                target = claude_md.resolve()
                if target == agents_md.resolve():
                    score = 5.0
                    message = "CLAUDE.md → AGENTS.md symlink correct"
                else:
                    score = 3.0
                    message = f"CLAUDE.md symlink to different target"
            else:
                score = 2.0
                message = "CLAUDE.md exists but not symlink"
        else:
            score = 0.0
            message = "CLAUDE.md missing"

        return Check(
            id="M5",
            name="CLAUDE.md Symlink",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=True
        )

    # -------------------------------------------------------------------------
    # D3: REASONING Assessment
    # -------------------------------------------------------------------------

    def _assess_d3_reasoning(self) -> DimensionResult:
        """Assess D3 REASONING dimension."""
        result = DimensionResult(
            dimension="D3_REASONING",
            weight=self.DIMENSION_WEIGHTS["D3_REASONING"]
        )

        # R1: Planning Patterns
        result.checks.append(self._check_r1_planning_patterns())

        # R2: Gate Discipline
        result.checks.append(self._check_r2_gate_discipline())

        # R3: Decision Framework
        result.checks.append(self._check_r3_decision_framework())

        # R4: V-Tests in Plans
        result.checks.append(self._check_r4_v_tests())

        # R5: 5D Directories
        result.checks.append(self._check_r5_5d_directories())

        return result

    def _check_r1_planning_patterns(self) -> Check:
        """R1: Planning Patterns (PROJECT_PLAN usage)."""
        planning_dir = self.agent_path / "planning"

        score = 0.0
        message = ""

        if planning_dir.exists():
            plans = list(planning_dir.glob("PROJECT_PLAN*.md"))
            count = len(plans)

            if count >= 5:
                score = 4.0
                message = f"{count} PROJECT_PLANs"
            elif count >= 2:
                score = 3.0
                message = f"{count} PROJECT_PLANs"
            elif count >= 1:
                score = 2.0
                message = f"{count} PROJECT_PLAN"
            else:
                score = 1.0
                message = "planning/ exists but no PROJECT_PLANs"
        else:
            score = 0.0
            message = "No planning/ directory"

        return Check(
            id="R1",
            name="Planning Patterns",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_r2_gate_discipline(self) -> Check:
        """R2: Gate Discipline (gates in plans)."""
        planning_dir = self.agent_path / "planning"

        score = 0.0
        message = ""

        if planning_dir.exists():
            plans = list(planning_dir.glob("PROJECT_PLAN*.md"))
            plans_with_gates = 0

            for plan in plans[:5]:  # Sample up to 5
                try:
                    with open(plan) as f:
                        content = f.read().lower()
                    if "gate" in content and ("go/nogo" in content or "decision point" in content):
                        plans_with_gates += 1
                except IOError:
                    pass

            if plans:
                ratio = plans_with_gates / min(len(plans), 5)
                if ratio >= 0.8:
                    score = 4.0
                    message = f"Gate discipline evident ({plans_with_gates} plans)"
                elif ratio >= 0.5:
                    score = 3.0
                    message = f"Partial gate discipline ({plans_with_gates} plans)"
                elif plans_with_gates > 0:
                    score = 2.0
                    message = f"Some gates ({plans_with_gates} plans)"
                else:
                    score = 1.0
                    message = "No gate structure in plans"
            else:
                score = 1.0
                message = "No plans to evaluate"
        else:
            score = 0.0
            message = "No planning/ directory"

        return Check(
            id="R2",
            name="Gate Discipline",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_r3_decision_framework(self) -> Check:
        """R3: Decision Framework (authority documented)."""
        charter = self.agent_path / "governance/CHARTER.md"
        agents_md = self.agent_path / "AGENTS.md"

        score = 0.0
        message = ""

        authority_found = False

        for path in [charter, agents_md]:
            if path.exists():
                try:
                    with open(path) as f:
                        content = f.read().lower()
                    if "authority" in content or "escalat" in content:
                        authority_found = True
                        break
                except IOError:
                    pass

        if authority_found:
            score = 3.0
            message = "Decision authority documented"

            # Check for authority matrix
            if charter.exists():
                try:
                    with open(charter) as f:
                        content = f.read().lower()
                    if "matrix" in content or "autonomous" in content:
                        score = 4.0
                        message = "Authority matrix present"
                except IOError:
                    pass
        else:
            score = 2.0
            message = "No explicit decision framework"

        return Check(
            id="R3",
            name="Decision Framework",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_r4_v_tests(self) -> Check:
        """R4: V-Tests in Plans."""
        planning_dir = self.agent_path / "planning"

        score = 0.0
        message = ""

        if planning_dir.exists():
            plans = list(planning_dir.glob("PROJECT_PLAN*.md"))
            plans_with_vtests = 0

            for plan in plans[:5]:
                try:
                    with open(plan) as f:
                        content = f.read()
                    if "V-G" in content or "V-Test" in content or "| V-" in content:
                        plans_with_vtests += 1
                except IOError:
                    pass

            if plans:
                ratio = plans_with_vtests / min(len(plans), 5)
                if ratio >= 0.8:
                    score = 4.0
                    message = f"V-tests in {plans_with_vtests} plans"
                elif ratio >= 0.5:
                    score = 3.0
                    message = f"V-tests in {plans_with_vtests} plans"
                elif plans_with_vtests > 0:
                    score = 2.0
                    message = f"V-tests in {plans_with_vtests} plan(s)"
                else:
                    score = 1.0
                    message = "No V-tests in plans"
            else:
                score = 1.0
                message = "No plans to evaluate"
        else:
            score = 0.0
            message = "No planning/ directory"

        return Check(
            id="R4",
            name="V-Tests in Plans",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_r5_5d_directories(self) -> Check:
        """R5: 5D Dimension Directories."""
        dirs = [
            ".aget/persona",
            ".aget/memory",
            ".aget/reasoning",
            ".aget/skills",
            ".aget/context",
        ]

        existing = sum(1 for d in dirs if (self.agent_path / d).exists())

        if existing == 5:
            score = 5.0
            message = "All 5D directories present"
        elif existing >= 4:
            score = 4.0
            message = f"{existing}/5 5D directories"
        elif existing >= 3:
            score = 3.0
            message = f"{existing}/5 5D directories"
        elif existing >= 1:
            score = 2.0
            message = f"{existing}/5 5D directories"
        else:
            score = 1.0
            message = "No 5D directories"

        return Check(
            id="R5",
            name="5D Directories",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    # -------------------------------------------------------------------------
    # D4: SKILLS Assessment
    # -------------------------------------------------------------------------

    def _assess_d4_skills(self) -> DimensionResult:
        """Assess D4 SKILLS dimension."""
        result = DimensionResult(
            dimension="D4_SKILLS",
            weight=self.DIMENSION_WEIGHTS["D4_SKILLS"]
        )

        # S1: Capability Declaration
        result.checks.append(self._check_s1_capabilities())

        # S2: Tool Availability
        result.checks.append(self._check_s2_tools())

        # S3: Contract Tests
        result.checks.append(self._check_s3_contract_tests())

        # S4: Shell Integration
        result.checks.append(self._check_s4_shell_integration())

        # S5: Documentation
        result.checks.append(self._check_s5_documentation())

        return result

    def _check_s1_capabilities(self) -> Check:
        """S1: Capability Declaration."""
        manifest = self.agent_path / "manifest.yaml"
        version_json = self.agent_path / ".aget/version.json"

        score = 0.0
        message = ""

        if manifest.exists():
            try:
                with open(manifest) as f:
                    content = f.read()
                if "capabilities:" in content:
                    score = 4.0
                    message = "Capabilities in manifest.yaml"
                else:
                    score = 3.0
                    message = "manifest.yaml exists (no capabilities section)"
            except IOError:
                score = 2.0
                message = "manifest.yaml unreadable"
        elif version_json.exists():
            try:
                with open(version_json) as f:
                    data = json.load(f)
                if data.get("capabilities"):
                    score = 3.0
                    message = "Capabilities in version.json"
                else:
                    score = 2.0
                    message = "version.json exists (no capabilities)"
            except (json.JSONDecodeError, IOError):
                score = 1.0
                message = "version.json unreadable"
        else:
            score = 0.0
            message = "No capability declaration"

        return Check(
            id="S1",
            name="Capability Declaration",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_s2_tools(self) -> Check:
        """S2: Tool Availability."""
        patterns_dir = self.agent_path / ".aget/patterns"
        scripts_dir = self.agent_path / "scripts"

        script_count = 0

        if patterns_dir.exists():
            script_count += len(list(patterns_dir.rglob("*.py")))

        if scripts_dir.exists():
            script_count += len(list(scripts_dir.glob("*.py")))

        if script_count >= 10:
            score = 5.0
            message = f"{script_count} scripts/tools"
        elif script_count >= 5:
            score = 4.0
            message = f"{script_count} scripts/tools"
        elif script_count >= 3:
            score = 3.0
            message = f"{script_count} scripts/tools"
        elif script_count >= 1:
            score = 2.0
            message = f"{script_count} script(s)"
        else:
            score = 1.0
            message = "No scripts/tools"

        return Check(
            id="S2",
            name="Tool Availability",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_s3_contract_tests(self) -> Check:
        """S3: Contract Tests."""
        tests_dir = self.agent_path / "tests"

        score = 0.0
        message = ""

        if tests_dir.exists():
            test_files = list(tests_dir.glob("test_*.py"))
            count = len(test_files)

            if count >= 3:
                score = 4.0
                message = f"{count} test files"
            elif count >= 1:
                score = 3.0
                message = f"{count} test file(s)"
            else:
                score = 2.0
                message = "tests/ exists but no test_*.py"
        else:
            score = 1.0
            message = "No tests/ directory"

        return Check(
            id="S3",
            name="Contract Tests",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_s4_shell_integration(self) -> Check:
        """S4: Shell Integration (v3.3 feature)."""
        shell_dir = self.agent_path / "shell"

        score = 0.0
        message = ""

        if shell_dir.exists():
            profile = list(shell_dir.glob("*_profile.zsh"))
            readme = shell_dir / "README.md"

            if profile and readme.exists():
                score = 4.0
                message = "Shell profile + README present"
            elif profile:
                score = 3.0
                message = "Shell profile present"
            else:
                score = 2.0
                message = "shell/ exists but no profile"
        else:
            score = 1.0
            message = "No shell/ directory (v3.3 feature)"

        return Check(
            id="S4",
            name="Shell Integration",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_s5_documentation(self) -> Check:
        """S5: Documentation."""
        readme = self.agent_path / "README.md"
        changelog = self.agent_path / "CHANGELOG.md"

        score = 0.0

        if readme.exists() and changelog.exists():
            score = 4.0
            message = "README.md + CHANGELOG.md present"
        elif readme.exists():
            score = 3.0
            message = "README.md present"
        elif changelog.exists():
            score = 2.0
            message = "CHANGELOG.md only"
        else:
            score = 1.0
            message = "No documentation"

        return Check(
            id="S5",
            name="Documentation",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    # -------------------------------------------------------------------------
    # D5: CONTEXT Assessment
    # -------------------------------------------------------------------------

    def _assess_d5_context(self) -> DimensionResult:
        """Assess D5 CONTEXT dimension."""
        result = DimensionResult(
            dimension="D5_CONTEXT",
            weight=self.DIMENSION_WEIGHTS["D5_CONTEXT"]
        )

        # C1: Relationship Structure
        result.checks.append(self._check_c1_relationships())

        # C2: Scope Boundaries
        result.checks.append(self._check_c2_scope_boundaries())

        # C3: Environmental Awareness
        result.checks.append(self._check_c3_environmental_awareness())

        # C4: Archetype Directories
        result.checks.append(self._check_c4_archetype_directories())

        return result

    def _check_c1_relationships(self) -> Check:
        """C1: Relationship Structure."""
        version_json = self.agent_path / ".aget/version.json"
        charter = self.agent_path / "governance/CHARTER.md"

        score = 0.0
        message = ""

        managed_by = None

        if version_json.exists():
            try:
                with open(version_json) as f:
                    data = json.load(f)
                managed_by = data.get("managed_by")
            except (json.JSONDecodeError, IOError):
                pass

        if managed_by:
            score = 3.0
            message = f"managed_by: {managed_by}"

            # Check if documented in CHARTER.md
            if charter.exists():
                try:
                    with open(charter) as f:
                        content = f.read().lower()
                    if "supervis" in content or "manag" in content:
                        score = 4.0
                        message += " (documented in CHARTER)"
                except IOError:
                    pass
        else:
            score = 2.0
            message = "No managed_by field"

        return Check(
            id="C1",
            name="Relationship Structure",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_c2_scope_boundaries(self) -> Check:
        """C2: Scope Boundaries."""
        charter = self.agent_path / "governance/CHARTER.md"
        scope_boundaries = self.agent_path / "governance/SCOPE_BOUNDARIES.md"

        score = 0.0
        message = ""

        if scope_boundaries.exists():
            score = 4.0
            message = "SCOPE_BOUNDARIES.md present"
        elif charter.exists():
            try:
                with open(charter) as f:
                    content = f.read().lower()
                if "scope" in content or "in scope" in content or "out of scope" in content:
                    score = 3.0
                    message = "Scope in CHARTER.md"
                else:
                    score = 2.0
                    message = "CHARTER.md exists (no explicit scope)"
            except IOError:
                score = 2.0
                message = "CHARTER.md unreadable"
        else:
            score = 1.0
            message = "No scope documentation"

        return Check(
            id="C2",
            name="Scope Boundaries",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_c3_environmental_awareness(self) -> Check:
        """C3: Environmental Awareness (L185)."""
        agents_md = self.agent_path / "AGENTS.md"

        score = 2.0  # Default: implicit
        message = "Environmental awareness implicit"

        if agents_md.exists():
            try:
                with open(agents_md) as f:
                    content = f.read().lower()
                if "environmental" in content or "grounding" in content or "verify" in content:
                    score = 3.0
                    message = "Environmental awareness documented"
                if "l185" in content:
                    score = 4.0
                    message = "L185 environmental grounding referenced"
            except IOError:
                pass

        return Check(
            id="C3",
            name="Environmental Awareness",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )

    def _check_c4_archetype_directories(self) -> Check:
        """C4: Archetype-Specific Directories."""
        archetype = self.result.archetype.lower() if self.result.archetype else ""

        archetype_dirs = {
            "supervisor": ["fleet", "sops"],
            "developer": ["products", "workspace", "src"],
            "advisor": ["clients", "engagements"],
            "consultant": ["clients", "engagements"],
            "analyst": ["reports"],
            "architect": ["decisions"],
            "researcher": ["research"],
            "operator": ["operations"],
            "spec-engineer": ["specs"],
        }

        required_dirs = archetype_dirs.get(archetype, [])

        if not required_dirs:
            score = 3.0  # No specific requirements
            message = f"No archetype-specific dirs for {archetype or 'unknown'}"
        else:
            existing = sum(1 for d in required_dirs if (self.agent_path / d).exists())
            ratio = existing / len(required_dirs)

            if ratio >= 1.0:
                score = 5.0
                message = f"All {existing} archetype dirs present"
            elif ratio >= 0.5:
                score = 3.0
                message = f"{existing}/{len(required_dirs)} archetype dirs"
            else:
                score = 2.0
                message = f"{existing}/{len(required_dirs)} archetype dirs (missing: {[d for d in required_dirs if not (self.agent_path / d).exists()]})"

        return Check(
            id="C4",
            name="Archetype Directories",
            passed=score >= 3.0,
            score=score,
            message=message,
            critical=False
        )


# =============================================================================
# Output Formatters
# =============================================================================

def format_json(result: ConformanceResult) -> str:
    """Format result as JSON."""
    output = {
        "meta": {
            "agent": result.agent_name or result.agent_path,
            "type": result.agent_type,
            "archetype": result.archetype,
            "framework_version": result.framework_version,
            "assessed": result.assessed_at,
            "validator_version": __version__
        },
        "dimensions": {},
        "composite": {
            "score": round(result.composite_score, 2),
            "percentage": round(result.percentage, 1),
            "level": result.level
        },
        "critical": {
            "passed": len(result.critical_failures) == 0,
            "failures": result.critical_failures
        },
        "gaps": result.gaps()
    }

    for dim_name, dim in result.dimensions.items():
        output["dimensions"][dim_name] = {
            "score": round(dim.raw_score, 2),
            "max": 5.0,
            "percentage": round(dim.percentage, 1),
            "weight": dim.weight,
            "checks": [
                {
                    "id": c.id,
                    "name": c.name,
                    "passed": c.passed,
                    "score": c.score,
                    "message": c.message
                }
                for c in dim.checks
            ]
        }

    return json.dumps(output, indent=2)


def format_verbose(result: ConformanceResult) -> str:
    """Format result for verbose human output."""
    lines = []

    # Header
    lines.append("=" * 60)
    lines.append("AGET v3.x Conformance Assessment")
    lines.append("=" * 60)
    lines.append("")

    # Agent info
    lines.append(f"Agent: {result.agent_name or result.agent_path}")
    lines.append(f"Type: {result.agent_type} (archetype: {result.archetype})")
    lines.append(f"Framework Version: {result.framework_version}")
    lines.append(f"Assessed: {result.assessed_at}")
    lines.append("")

    # Critical failures
    if result.critical_failures:
        lines.append("❌ CRITICAL FAILURES:")
        for failure in result.critical_failures:
            lines.append(f"   • {failure}")
        lines.append("")

    # Dimension scores
    lines.append("Dimension Scores:")
    lines.append("-" * 50)

    for dim_name, dim in result.dimensions.items():
        icon = "✅" if dim.percentage >= 60 else "⚠️" if dim.percentage >= 40 else "❌"
        band = "Exemplary" if dim.percentage >= 85 else "Strong" if dim.percentage >= 70 else "Adequate" if dim.percentage >= 50 else "Developing"
        lines.append(f"  {icon} {dim_name}: {dim.raw_score:.1f}/5.0 ({dim.percentage:.0f}%) - {band}")

        for check in dim.checks:
            check_icon = "✓" if check.passed else "✗"
            lines.append(f"      [{check_icon}] {check.id}: {check.name} ({check.score:.1f}/5)")
            if check.message:
                lines.append(f"          {check.message}")

    lines.append("-" * 50)
    lines.append("")

    # Composite score
    level_icon = "✅" if result.passed else "❌"
    lines.append(f"Composite Score: {result.composite_score:.2f}/5.0 ({result.percentage:.1f}%)")
    lines.append(f"{level_icon} Level: {result.level} ({result.level_label})")
    lines.append("")

    # Gaps
    gaps = result.gaps()
    if gaps:
        lines.append("Gaps Requiring Attention:")
        for gap in gaps[:5]:  # Top 5
            lines.append(f"  • {gap['dimension']}-{gap['criterion']}: {gap['message']} ({gap['score']})")
        if len(gaps) > 5:
            lines.append(f"  ... and {len(gaps) - 5} more")

    return "\n".join(lines)


def format_summary(result: ConformanceResult) -> str:
    """Format minimal summary output."""
    icon = "✅" if result.passed else "❌"
    return f"{icon} {result.agent_name or result.agent_path}: {result.percentage:.1f}% - {result.level_label}"


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='AGET v3.x Conformance Assessment Validator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Conformance Levels:
  L0 Non-Conformant  (<40%)  - Fails critical requirements
  L1 Baseline        (40-59%) - Meets structural minimums
  L2 Compliant       (60-84%) - Meets v3.x CAP requirements
  L3 Exemplary       (85-100%) - Reference implementation quality

Exit codes:
  0: L2 Compliant or higher (>=60%)
  1: L1 Baseline or L0 Non-Conformant (<60%)
  2: File/path errors

Examples:
  python3 validate_conformance.py /path/to/agent
  python3 validate_conformance.py --dir . --json
  python3 validate_conformance.py --verbose
        """
    )

    parser.add_argument('path', nargs='?', default='.', help='Path to agent (default: current directory)')
    parser.add_argument('--dir', help='Agent directory (alternative to positional)')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output with all checks')
    parser.add_argument('--quiet', '-q', action='store_true', help='Only show summary line')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()

    agent_path = args.dir if args.dir else args.path

    # Validate path exists
    if not os.path.exists(agent_path):
        print(f"Error: Path does not exist: {agent_path}", file=sys.stderr)
        return 2

    # Run validation
    validator = ConformanceValidator(agent_path)
    result = validator.validate()

    # Output results
    if args.json:
        print(format_json(result))
    elif args.quiet:
        print(format_summary(result))
    elif args.verbose:
        print(format_verbose(result))
    else:
        # Default: summary + key info
        print(format_summary(result))
        if result.critical_failures:
            print("\nCritical failures:")
            for f in result.critical_failures:
                print(f"  ❌ {f}")
        gaps = result.gaps()
        if gaps and not result.passed:
            print("\nTop gaps:")
            for gap in gaps[:3]:
                print(f"  • {gap['dimension']}-{gap['criterion']}: {gap['message']}")

    # Exit code based on conformance level
    return 0 if result.passed else 1


if __name__ == '__main__':
    sys.exit(main())
