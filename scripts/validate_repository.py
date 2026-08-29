#!/usr/bin/env python3
"""Validate the public Zaibatsu architecture and documentation contract."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_PATH = ROOT / "architecture" / "system.json"
READINESS_PATH = ROOT / "architecture" / "submission-readiness.json"

REQUIRED_FILES = (
    "README.md",
    "AGENTS.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CHANGELOG.md",
    ".github/workflows/validate.yml",
    ".factory/prompts/review.md",
    ".factory/settings.local.example.json",
    "architecture/system.json",
    "architecture/submission-readiness.json",
    "docs/architecture.md",
    "docs/case-study.md",
    "docs/demo-script.md",
    "docs/droid-session.md",
    "docs/evidence.md",
    "docs/guild-application.md",
    "docs/guild-requirements.md",
    "docs/implementation-status.md",
    "docs/reproducibility.md",
    "docs/roadmap.md",
    "docs/security-and-threat-model.md",
    "scripts/droid_preflight.py",
    "scripts/validate_repository.py",
    "tests/test_droid_preflight.py",
    "tests/test_validate_repository.py",
)

ALLOWED_MATURITIES = {
    "operational",
    "validated_preproduction",
    "designed",
    "planned",
    "pending_evidence",
}

ALLOWED_GATE_STATUSES = {"complete", "pending_external", "blocked_by_dependency"}

PROJECT_NAME = "Zaibatsu"
ARCHITECTURE_SCHEMA_VERSION = "zaibatsu.architecture.v1"
READINESS_SCHEMA_VERSION = "zaibatsu.submission-readiness.v1"

REQUIRED_COMPONENT_IDS = {
    "current-systemd-executor",
    "tailscale-management-network",
    "ansible-configuration",
    "opentofu-resource-lifecycle",
    "dispatcher-api-and-policy",
    "postgresql-job-state",
    "project-sandboxes",
    "probabilistic-workers",
    "artifact-verification",
    "knowledge-memory",
    "nix-project-environments",
    "factory-droid-contribution",
}

REQUIRED_COMPONENT_MATURITIES = {
    "current-systemd-executor": "operational",
    "tailscale-management-network": "operational",
    "ansible-configuration": "validated_preproduction",
    "opentofu-resource-lifecycle": "validated_preproduction",
    "dispatcher-api-and-policy": "designed",
    "postgresql-job-state": "designed",
    "project-sandboxes": "planned",
    "probabilistic-workers": "designed",
    "artifact-verification": "validated_preproduction",
    "knowledge-memory": "operational",
    "nix-project-environments": "planned",
    "factory-droid-contribution": "validated_preproduction",
}

REQUIRED_SUBMISSION_GATES = {
    "public_package",
    "droid_cli_install",
    "local_qwen_endpoint",
    "local_model_credential",
    "factory_cli_authentication",
    "bounded_droid_contribution",
    "public_repository",
    "fresh_clone_reproduction",
    "public_demo",
    "applicant_materials",
}

SUBMISSION_DEPENDENCIES = {
    "bounded_droid_contribution": {
        "local_qwen_endpoint",
        "local_model_credential",
        "factory_cli_authentication",
    },
    "fresh_clone_reproduction": {"public_repository"},
    "public_demo": {"bounded_droid_contribution", "public_repository"},
}

REQUIRED_PROJECTS = ["orchestrator", "simbapool", "ffn"]

REQUIRED_TRUE_INVARIANTS = {
    "unknown_projects_fail_closed",
    "probabilistic_output_is_not_verification",
    "direct_agent_to_production_denied",
    "dispatcher_not_required_for_dispatcher_recovery",
    "jobs_outlive_workers",
    "operational_state_separate_from_knowledge",
    "failed_work_remains_inspectable",
    "every_terminal_state_retains_evidence",
}

PUBLIC_TEXT_SUFFIXES = {
    ".cfg",
    ".conf",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
PUBLIC_TEXT_FILENAMES = {".env", ".gitignore", "LICENSE", "Makefile"}
PUBLIC_SAFETY_PATTERNS = {
    "legacy pre-release brand": re.compile(
        "factory" + r"(?:²|\^2|[-_ ]squared)", re.IGNORECASE
    ),
    "absolute home path": re.compile(r"/home/[A-Za-z0-9._-]+/"),
    "Tailscale carrier-grade NAT address": re.compile(
        r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"
    ),
    "private RFC1918 address": re.compile(
        r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b"
    ),
    "secret assignment": re.compile(
        r"(?im)^\s*(?:[A-Za-z0-9]+[_-])*(?:api[_-]?key|token|password|"
        r"private[_-]?key)\s*[:=]\s*\S+"
    ),
    "literal JSON API key": re.compile(
        r'(?im)^\s*"(?:[A-Za-z0-9]+[_-])*(?:api[_-]?key|token|password|'
        r'private[_-]?key)"\s*:\s*"(?!\$\{|<)[^"]+"\s*,?\s*$'
    ),
    "private key material": re.compile(
        r"(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----$"
    ),
    "literal bearer credential": re.compile(
        r"(?im)^\s*(?:authorization\s*:\s*)?bearer\s+(?!<|\$\{)\S+"
    ),
}

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def load_architecture(path: Path = ARCHITECTURE_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_architecture(data: Any) -> list[str]:
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["architecture root must be an object"]

    if data.get("schema_version") != ARCHITECTURE_SCHEMA_VERSION:
        errors.append(f"schema_version must equal {ARCHITECTURE_SCHEMA_VERSION}")

    project = data.get("project")
    if not isinstance(project, dict):
        errors.append("project must be an object")
    elif (
        project.get("name") != PROJECT_NAME
        or project.get("spoken_name") != PROJECT_NAME
    ):
        errors.append(f"project name and spoken_name must equal {PROJECT_NAME}")

    if data.get("project_allowlist") != REQUIRED_PROJECTS:
        errors.append(
            "project_allowlist must exactly equal " + ", ".join(REQUIRED_PROJECTS)
        )

    definitions = data.get("maturity_definitions")
    if not isinstance(definitions, dict) or set(definitions) != ALLOWED_MATURITIES:
        errors.append("maturity_definitions must exactly match the allowed statuses")
    elif not all(isinstance(value, str) and value.strip() for value in definitions.values()):
        errors.append("every maturity definition must be a non-empty string")

    components = data.get("components")
    if not isinstance(components, list) or not components:
        errors.append("components must be a non-empty list")
        return errors

    seen_ids: set[str] = set()
    for index, component in enumerate(components):
        if not isinstance(component, dict):
            errors.append(f"component at index {index} must be an object")
            continue

        component_id = component.get("id")
        if not isinstance(component_id, str) or not component_id.strip():
            errors.append(f"component at index {index} must have a non-empty string id")
            continue
        if component_id in seen_ids:
            errors.append(f"duplicate component id: {component_id}")
        seen_ids.add(component_id)

        for field in ("plane", "responsibility"):
            if not isinstance(component.get(field), str) or not component[field].strip():
                errors.append(f"{component_id}: {field} must be a non-empty string")

        maturity = component.get("maturity")
        if not isinstance(maturity, str) or maturity not in ALLOWED_MATURITIES:
            errors.append(f"{component_id}: invalid maturity {maturity!r}")
        elif maturity != REQUIRED_COMPONENT_MATURITIES.get(component_id):
            expected_maturity = REQUIRED_COMPONENT_MATURITIES.get(component_id)
            errors.append(
                f"{component_id}: maturity must remain "
                f"{expected_maturity!r} until evidence policy changes"
            )

        kind = component.get("kind")
        if not isinstance(kind, str) or kind not in {"deterministic", "probabilistic"}:
            errors.append(f"{component_id}: invalid kind {kind!r}")

        side_effects = component.get("can_trigger_external_side_effects")
        if not isinstance(side_effects, bool):
            errors.append(
                f"{component_id}: can_trigger_external_side_effects must be boolean"
            )

        if kind == "probabilistic":
            if not isinstance(component.get("deterministic_precondition"), str) or not component[
                "deterministic_precondition"
            ].strip():
                errors.append(
                    f"{component_id}: probabilistic component lacks deterministic_precondition"
                )
            if not isinstance(component.get("deterministic_postcondition"), str) or not component[
                "deterministic_postcondition"
            ].strip():
                errors.append(
                    f"{component_id}: probabilistic component lacks deterministic_postcondition"
                )
            if side_effects is True:
                errors.append(
                    f"{component_id}: probabilistic component cannot directly "
                    "trigger external side effects"
                )

        if side_effects is True:
            policy_gate = component.get("policy_gate")
            if not isinstance(policy_gate, str) or not policy_gate.strip():
                errors.append(f"{component_id}: side-effecting component lacks policy_gate")

    if seen_ids != REQUIRED_COMPONENT_IDS:
        missing = sorted(REQUIRED_COMPONENT_IDS - seen_ids)
        unexpected = sorted(seen_ids - REQUIRED_COMPONENT_IDS)
        if missing:
            errors.append("components missing required ids: " + ", ".join(missing))
        if unexpected:
            errors.append("components contain unexpected ids: " + ", ".join(unexpected))

    invariants = data.get("invariants")
    if not isinstance(invariants, dict):
        errors.append("invariants must be an object")
    else:
        for invariant in sorted(REQUIRED_TRUE_INVARIANTS):
            if invariants.get(invariant) is not True:
                errors.append(f"invariant must be true: {invariant}")

    flow = data.get("task_flow")
    if not isinstance(flow, list) or not all(isinstance(stage, str) for stage in flow):
        errors.append("task_flow must be a list of strings")
        return errors
    if len(flow) != len(set(flow)):
        errors.append("task_flow stages must be unique")
    ordered_stages = (
        "persist",
        "execute_in_sandbox",
        "verify",
        "policy_decision",
        "controlled_side_effect",
    )
    for required_stage in ordered_stages:
        if required_stage not in flow:
            errors.append(f"task_flow missing required stage: {required_stage}")

    if all(stage in flow for stage in ordered_stages):
        positions = [flow.index(stage) for stage in ordered_stages]
        for index in range(len(ordered_stages) - 1):
            if positions[index] >= positions[index + 1]:
                errors.append(
                    f"task_flow must order {ordered_stages[index]} before "
                    f"{ordered_stages[index + 1]}"
                )

    return errors


def validate_submission_readiness(data: Any) -> list[str]:
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["submission readiness root must be an object"]

    if data.get("schema_version") != READINESS_SCHEMA_VERSION:
        errors.append(f"schema_version must equal {READINESS_SCHEMA_VERSION}")
    if not isinstance(data.get("submission_ready"), bool):
        errors.append("submission_ready must be boolean")
    if not isinstance(data.get("submitted"), bool):
        errors.append("submitted must be boolean")

    gates = data.get("gates")
    if not isinstance(gates, list):
        errors.append("submission readiness gates must be a list")
        return errors

    gate_by_id: dict[str, dict[str, Any]] = {}
    for index, gate in enumerate(gates):
        if not isinstance(gate, dict):
            errors.append(f"submission gate at index {index} must be an object")
            continue
        gate_id = gate.get("id")
        if not isinstance(gate_id, str) or not gate_id.strip():
            errors.append(f"submission gate at index {index} must have a string id")
            continue
        if gate_id in gate_by_id:
            errors.append(f"duplicate submission gate id: {gate_id}")
            continue
        gate_by_id[gate_id] = gate

    if set(gate_by_id) != REQUIRED_SUBMISSION_GATES or len(gates) != len(gate_by_id):
        errors.append("submission readiness must contain each required gate exactly once")
        return errors

    for gate_id, gate in gate_by_id.items():
        status = gate.get("status")
        if not isinstance(status, str) or status not in ALLOWED_GATE_STATUSES:
            errors.append(f"{gate_id}: invalid gate status {status!r}")
            continue
        if gate.get("required_for_submission") is not True:
            errors.append(f"{gate_id}: required_for_submission must be true")
        if not isinstance(gate.get("evidence"), str) or not gate["evidence"].strip():
            errors.append(f"{gate_id}: evidence or pending rationale is required")

        blockers = gate.get("blocked_by", [])
        if not isinstance(blockers, list) or not all(
            isinstance(blocker, str) for blocker in blockers
        ):
            errors.append(f"{gate_id}: blocked_by must be a list of gate ids")
            blockers = []
        if len(blockers) != len(set(blockers)):
            errors.append(f"{gate_id}: blocked_by entries must be unique")

        dependencies = SUBMISSION_DEPENDENCIES.get(gate_id, set())
        unresolved = {
            dependency
            for dependency in dependencies
            if gate_by_id[dependency].get("status") != "complete"
        }
        if unresolved:
            if status != "blocked_by_dependency":
                errors.append(
                    f"{gate_id}: must remain blocked until dependencies complete"
                )
            if set(blockers) != unresolved:
                errors.append(
                    f"{gate_id}: blocked_by must exactly match unresolved dependencies"
                )
        else:
            if status == "blocked_by_dependency":
                errors.append(f"{gate_id}: has no unresolved dependency")
            if blockers:
                errors.append(f"{gate_id}: resolved gate must not declare blocked_by")

    computed_ready = all(
        gate["status"] == "complete" for gate in gate_by_id.values()
    )
    if (
        isinstance(data.get("submission_ready"), bool)
        and data["submission_ready"] is not computed_ready
    ):
        errors.append("submission_ready must equal the state of all required gates")
    if data.get("submitted") is True and not computed_ready:
        errors.append("submitted cannot be true before every required gate is complete")

    return errors


def validate_contract_consistency(architecture: Any, readiness: Any) -> list[str]:
    """Prevent the Factory evidence gate and architecture maturity from drifting."""
    if not isinstance(architecture, dict) or not isinstance(readiness, dict):
        return []

    components = architecture.get("components")
    gates = readiness.get("gates")
    if not isinstance(components, list) or not isinstance(gates, list):
        return []

    droid_component = next(
        (
            component
            for component in components
            if isinstance(component, dict)
            and component.get("id") == "factory-droid-contribution"
        ),
        None,
    )
    droid_gate = next(
        (
            gate
            for gate in gates
            if isinstance(gate, dict)
            and gate.get("id") == "bounded_droid_contribution"
        ),
        None,
    )
    if droid_component is None or droid_gate is None:
        return []

    maturity = droid_component.get("maturity")
    evidence_complete = droid_gate.get("status") == "complete"
    if evidence_complete and maturity == "pending_evidence":
        return ["Factory Droid maturity must be promoted after its evidence gate completes"]
    if not evidence_complete and maturity != "pending_evidence":
        return ["Factory Droid maturity must remain pending until its evidence gate completes"]
    return []


def public_files(root: Path = ROOT) -> list[Path]:
    paths: list[Path] = []
    excluded_directories = {".git", "__pycache__", "runtime"}
    ignored_local_settings = root / ".factory" / "settings.local.json"
    for path in root.rglob("*"):
        if any(part in excluded_directories for part in path.relative_to(root).parts):
            continue
        if path == ignored_local_settings or not path.is_file():
            continue
        if path.suffix in PUBLIC_TEXT_SUFFIXES or path.name in PUBLIC_TEXT_FILENAMES:
            paths.append(path)
    return sorted(paths)


def validate_public_safety(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in public_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{path.relative_to(root)}: cannot scan public text: {exc}")
            continue
        for label, pattern in PUBLIC_SAFETY_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{path.relative_to(root)}: contains {label}")
    return errors


def validate_required_files(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.is_file():
            errors.append(f"missing required file: {relative}")
        elif path.is_symlink():
            errors.append(f"required file must not be a symlink: {relative}")
    return errors


def validate_local_links(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in public_files(root):
        if path.suffix != ".md":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{path.relative_to(root)}: cannot check links: {exc}")
            continue
        for target in MARKDOWN_LINK_RE.findall(text):
            target = target.strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "#", "<")):
                continue
            clean_target = target.split("#", 1)[0]
            if not clean_target:
                continue
            resolved = (path.parent / clean_target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(root)}: link escapes repository: {target}")
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(root)}: broken local link: {target}")
    return errors


def main() -> int:
    errors: list[str] = []
    data: Any = None
    readiness: Any = None
    errors.extend(validate_required_files())
    try:
        data = load_architecture()
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load architecture: {exc}")
    else:
        errors.extend(validate_architecture(data))
    try:
        readiness = json.loads(READINESS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load submission readiness: {exc}")
    else:
        errors.extend(validate_submission_readiness(readiness))
    errors.extend(validate_contract_consistency(data, readiness))
    errors.extend(validate_public_safety())
    errors.extend(validate_local_links())

    if errors:
        print("Zaibatsu validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Zaibatsu validation passed")
    print(f"- {len(REQUIRED_FILES)} required files present")
    print(f"- {len(data['components'])} architecture components checked")
    print(f"- {len(REQUIRED_TRUE_INVARIANTS)} fail-closed invariants checked")
    print(f"- {len(readiness['gates'])} submission gates checked")
    print("- public-safety and local-link checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
