#!/usr/bin/env python3
"""Validate the public Zaibatsu architecture and documentation contract."""

from __future__ import annotations

import ipaddress
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from factory_bundle import (
    BUNDLE_MANIFEST_SCHEMA_REFERENCE,
    build_factory_bundle,
    build_bundle_payloads,
    validate_bundle_manifest,
    verify_factory_bundle,
)
from factory_composer import (
    FACTORY_PLAN_SCHEMA_REFERENCE,
    MODULE_ARTIFACT_SCHEMA_REFERENCE,
    MODULE_CATALOG_SCHEMA_REFERENCE,
    load_json_file,
    load_factory_plan,
    load_module_catalog,
    load_module_artifacts,
    validate_factory_bindings,
    validate_factory_plan,
    validate_module_catalog,
)
from factory_qualification import (
    EXAMPLE_QUALIFICATION_ASSESSMENT_PATH,
    EXAMPLE_QUALIFICATION_EVIDENCE_PATH,
    EXAMPLE_QUALIFICATION_PLAN_PATH,
    QUALIFICATION_ASSESSMENT_SCHEMA_REFERENCE,
    QUALIFICATION_EVIDENCE_SCHEMA_REFERENCE,
    QUALIFICATION_PLAN_SCHEMA_REFERENCE,
    QUALIFICATION_POLICY_PATH,
    QUALIFICATION_POLICY_SCHEMA_REFERENCE,
    load_qualification_assessment,
    load_qualification_evidence,
    load_qualification_plan,
    load_qualification_policy,
    validate_qualification_assessment,
    validate_qualification_evidence,
    validate_qualification_plan,
    validate_qualification_policy,
)
from factory_rebuild import (
    EXAMPLE_REBUILD_PLAN_PATH,
    REBUILD_PLAN_SCHEMA_REFERENCE,
    load_rebuild_plan,
    verify_factory_rebuild_plan_for_bundle,
)
from factory_source_lock import (
    EXAMPLE_SOURCE_LOCK_PATH,
    SOURCE_LOCK_SCHEMA_REFERENCE,
    load_source_lock,
    validate_source_lock,
)


ROOT = Path(__file__).resolve().parents[1]
ARCHITECTURE_PATH = ROOT / "architecture" / "system.json"
FACTORY_MODEL_PATH = ROOT / "architecture" / "factory-model.json"
READINESS_PATH = ROOT / "architecture" / "submission-readiness.json"
EXAMPLE_FACTORY_PATH = ROOT / "examples" / "economic-factory.json"
EXAMPLE_BUNDLE_MANIFEST_PATH = (
    ROOT / "examples" / "economic-factory.bundle-manifest.json"
)

MODULE_ARTIFACT_RELATIVES = (
    "catalog/modules/ansible-host-reproduction/module.json",
    "catalog/modules/bounded-runtime-secrets/module.json",
    "catalog/modules/cron-scheduler/module.json",
    "catalog/modules/deterministic-verification/module.json",
    "catalog/modules/git-source/module.json",
    "catalog/modules/nix-worker-environment/module.json",
    "catalog/modules/owner-gated-feedback/module.json",
    "catalog/modules/sops-age-static-secrets/module.json",
    "catalog/modules/systemd-scheduler/module.json",
    "catalog/modules/typed-agent-execution/module.json",
)

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
    "architecture/factory-model.json",
    "architecture/system.json",
    "architecture/submission-readiness.json",
    "catalog/modules.json",
    *MODULE_ARTIFACT_RELATIVES,
    "examples/economic-factory.json",
    "examples/economic-factory-cron.json",
    "examples/economic-factory.bundle-manifest.json",
    "examples/economic-factory.plan.json",
    "examples/economic-factory.rebuild-plan.json",
    "examples/economic-factory.source-lock.json",
    "examples/economic-factory.qualification-assessment.json",
    "examples/economic-factory.qualification-evidence.json",
    "examples/economic-factory.qualification-plan.json",
    "evidence/dispatcher-validation-v1.json",
    "evidence/droid-contribution-v1.json",
    "evidence/meta-factory-foundations-v1.json",
    "evidence/qwen-model-observation-v1.json",
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
    "schemas/dispatcher-validation-receipt.schema.json",
    "schemas/droid-contribution-receipt.schema.json",
    "schemas/factory-definition.schema.json",
    "schemas/factory-bundle-comparison.schema.json",
    "schemas/factory-bundle-inspection.schema.json",
    "schemas/factory-bundle-manifest.schema.json",
    "schemas/factory-plan.schema.json",
    "schemas/factory-rebuild-plan.schema.json",
    "schemas/factory-source-lock.schema.json",
    "schemas/factory-qualification-assessment.schema.json",
    "schemas/factory-qualification-evidence.schema.json",
    "schemas/factory-qualification-plan.schema.json",
    "schemas/factory-model.schema.json",
    "schemas/meta-factory-foundations-receipt.schema.json",
    "schemas/module-catalog.schema.json",
    "schemas/module-artifact.schema.json",
    "schemas/module-qualification-policy.schema.json",
    "schemas/qwen-model-observation-receipt.schema.json",
    "schemas/submission-readiness.schema.json",
    "schemas/system.schema.json",
    "scripts/droid_preflight.py",
    "scripts/factory_bundle.py",
    "scripts/factory_composer.py",
    "scripts/factory_qualification.py",
    "scripts/factory_rebuild.py",
    "scripts/factory_source_lock.py",
    "scripts/zaibatsu.py",
    "scripts/validate_repository.py",
    "tests/test_droid_preflight.py",
    "tests/test_validate_repository.py",
    "policies/runtime-qualification-v1.json",
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
FACTORY_MODEL_SCHEMA_VERSION = "zaibatsu.factory-model.v1"
READINESS_SCHEMA_VERSION = "zaibatsu.submission-readiness.v1"
FACTORY_DEFINITION_SCHEMA_VERSION = "zaibatsu.factory-definition.v2"
INTEGRATED_TEST_COUNT = 183
DROID_FACTORY_CLI_VERSION = "0.206.0"
DROID_SESSION_REFERENCE = "46f941a9-82f8-4df3-a45c-b8158996360b"
PUBLIC_REPOSITORY_URL = "https://github.com/adaliontech/Zaibatsu"
PORTABLE_FACTORY_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.2.0/schemas/factory-definition.schema.json"
)

DISPATCHER_MIGRATIONS = {
    "0001_dispatcher_state.sql",
    "0002_job_leases_and_audit.sql",
    "0003_runtime_grants.sql",
    "0004_admin_projection.sql",
    "0005_api_idempotency.sql",
    "0006_coordinator_operations.sql",
}

DISPATCHER_RESTORE_TABLES = {
    "active_leases",
    "approval_decisions",
    "approval_requests",
    "artifacts",
    "audit_events",
    "job_attempts",
    "job_dependencies",
    "jobs",
    "policy_decisions",
    "projects",
    "request_ledger",
    "workers",
}

CONTRACT_SCHEMA_REFERENCES = {
    "architecture/factory-model.json": "../schemas/factory-model.schema.json",
    "architecture/system.json": "../schemas/system.schema.json",
    "architecture/submission-readiness.json": "../schemas/submission-readiness.schema.json",
    "catalog/modules.json": MODULE_CATALOG_SCHEMA_REFERENCE,
    **{
        relative: MODULE_ARTIFACT_SCHEMA_REFERENCE
        for relative in MODULE_ARTIFACT_RELATIVES
    },
    "examples/economic-factory.json": PORTABLE_FACTORY_SCHEMA_REFERENCE,
    "examples/economic-factory-cron.json": PORTABLE_FACTORY_SCHEMA_REFERENCE,
    "examples/economic-factory.bundle-manifest.json": BUNDLE_MANIFEST_SCHEMA_REFERENCE,
    "examples/economic-factory.plan.json": FACTORY_PLAN_SCHEMA_REFERENCE,
    "examples/economic-factory.rebuild-plan.json": REBUILD_PLAN_SCHEMA_REFERENCE,
    "examples/economic-factory.source-lock.json": SOURCE_LOCK_SCHEMA_REFERENCE,
    "examples/economic-factory.qualification-assessment.json": (
        QUALIFICATION_ASSESSMENT_SCHEMA_REFERENCE
    ),
    "examples/economic-factory.qualification-evidence.json": (
        QUALIFICATION_EVIDENCE_SCHEMA_REFERENCE
    ),
    "examples/economic-factory.qualification-plan.json": (
        QUALIFICATION_PLAN_SCHEMA_REFERENCE
    ),
    "policies/runtime-qualification-v1.json": QUALIFICATION_POLICY_SCHEMA_REFERENCE,
    "evidence/dispatcher-validation-v1.json": "../schemas/dispatcher-validation-receipt.schema.json",
    "evidence/droid-contribution-v1.json": "../schemas/droid-contribution-receipt.schema.json",
    "evidence/meta-factory-foundations-v1.json": "../schemas/meta-factory-foundations-receipt.schema.json",
    "evidence/qwen-model-observation-v1.json": "../schemas/qwen-model-observation-receipt.schema.json",
}

REMOTE_SCHEMA_LOCAL_PATHS = {
    "catalog/modules.json": "schemas/module-catalog.schema.json",
    **{
        relative: "schemas/module-artifact.schema.json"
        for relative in MODULE_ARTIFACT_RELATIVES
    },
    "examples/economic-factory.json": "schemas/factory-definition.schema.json",
    "examples/economic-factory-cron.json": "schemas/factory-definition.schema.json",
    "examples/economic-factory.bundle-manifest.json": (
        "schemas/factory-bundle-manifest.schema.json"
    ),
    "examples/economic-factory.plan.json": "schemas/factory-plan.schema.json",
    "examples/economic-factory.rebuild-plan.json": (
        "schemas/factory-rebuild-plan.schema.json"
    ),
    "examples/economic-factory.source-lock.json": (
        "schemas/factory-source-lock.schema.json"
    ),
    "examples/economic-factory.qualification-assessment.json": (
        "schemas/factory-qualification-assessment.schema.json"
    ),
    "examples/economic-factory.qualification-evidence.json": (
        "schemas/factory-qualification-evidence.schema.json"
    ),
    "examples/economic-factory.qualification-plan.json": (
        "schemas/factory-qualification-plan.schema.json"
    ),
    "policies/runtime-qualification-v1.json": (
        "schemas/module-qualification-policy.schema.json"
    ),
}

EVIDENCE_CONTRACTS = {
    "evidence/dispatcher-validation-v1.json": (
        "zaibatsu.dispatcher-validation-receipt.v1",
        "passed",
    ),
    "evidence/droid-contribution-v1.json": (
        "zaibatsu.droid-contribution-receipt.v1",
        "passed_and_reviewed",
    ),
    "evidence/meta-factory-foundations-v1.json": (
        "zaibatsu.meta-factory-foundations.v1",
        "passed_with_maturity_boundaries",
    ),
    "evidence/qwen-model-observation-v1.json": (
        "zaibatsu.qwen-model-observation.v1",
        "passed",
    ),
}

GATE_PROOF_FIELDS = {
    "public_package": {"contracts", "validator"},
    "droid_cli_install": {"receipt", "factory_cli_version"},
    "local_qwen_endpoint": {"receipt", "transport_tested"},
    "local_model_credential": {"receipt", "credential_value_recorded"},
    "factory_cli_authentication": {"receipt", "authenticated_session_recorded"},
    "bounded_droid_contribution": {"receipt", "session_reference"},
    "public_repository": {"url", "anonymous_access_verified"},
    "fresh_clone_reproduction": {
        "candidate_commit",
        "tests_passed",
        "gitleaks_version",
        "github_actions_run",
    },
    "public_demo": {"url", "release_tag"},
    "applicant_materials": {"submitted_by_applicant", "resume_provided_privately"},
}

REQUIRED_FACTORY_INSTANCES = {
    "orchestrator": ("control_factory", "operational"),
    "simbapool": ("economic_factory", "operational"),
    "ffn": ("economic_factory", "operational"),
}

REQUIRED_FACTORY_LIFECYCLE = (
    "define_factory",
    "version_factory",
    "reproduce_factory",
    "schedule_work",
    "execute_bounded_work",
    "verify_artifacts",
    "authorize_effect",
    "operate_factory",
    "observe_outcomes",
    "return_evidence",
    "improve_shared_patterns",
    "promote_reviewed_change",
)

REQUIRED_FACTORY_CAPABILITY_MATURITIES = {
    "factory-registry": "operational",
    "git-version-control": "operational",
    "sops-age-secret-versioning": "validated_preproduction",
    "ansible-reproduction": "validated_preproduction",
    "nix-environment-reproduction": "planned",
    "systemd-scheduling": "operational",
    "cron-scheduling": "operational",
    "modular-agent-skeletons": "validated_preproduction",
    "llm-harness-adapters": "validated_preproduction",
    "deterministic-output-gates": "validated_preproduction",
    "recursive-factory-improvement": "designed",
}

REQUIRED_FACTORY_INVARIANTS = {
    "zaibatsu_is_meta_factory",
    "factory_instances_are_project_scoped",
    "unknown_factories_fail_closed",
    "one_scheduler_of_record_per_workload",
    "plaintext_secrets_never_enter_git",
    "model_output_is_never_verification",
    "feedback_cannot_self_promote",
    "factory_changes_require_deterministic_evidence",
    "owner_controls_irreversible_effects",
}

REQUIRED_DETERMINISTIC_GATES = (
    "schemas",
    "linters",
    "tests",
    "hashes",
    "policy",
    "receipts",
    "owner_approval",
)

REQUIRED_COMPONENT_IDS = {
    "current-systemd-executor",
    "tailscale-management-network",
    "ansible-configuration",
    "opentofu-resource-lifecycle",
    "dispatcher-api-and-policy",
    "postgresql-job-state",
    "bounded-readonly-coordinator",
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
    "dispatcher-api-and-policy": "validated_preproduction",
    "postgresql-job-state": "validated_preproduction",
    "bounded-readonly-coordinator": "operational",
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
    "public_demo": {
        "bounded_droid_contribution",
        "public_repository",
        "fresh_clone_reproduction",
    },
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

PUBLIC_SAFETY_PATTERNS = {
    "legacy pre-release brand": re.compile(
        "factory" + r"(?:²|\^2|[-_ ]squared)", re.IGNORECASE
    ),
    "absolute home path": re.compile(
        r"(?:(?<![A-Za-z0-9._-])/(?:home|Users)/[A-Za-z0-9._-]+(?:/|\b)|"
        r"(?i:\b[A-Z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+(?:[\\/]|\b)))"
    ),
    "Tailscale DNS name": re.compile(
        r"(?i)\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+ts\.net\b"
    ),
    "Tailscale carrier-grade NAT address": re.compile(
        r"\b100\.(?:6[4-9]|[7-9]\d|1[01]\d|12[0-7])(?:\.\d{1,3}){2}\b"
    ),
    "private RFC1918 address": re.compile(
        r"\b(?:10(?:\.\d{1,3}){3}|192\.168(?:\.\d{1,3}){2}|"
        r"172\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2})\b"
    ),
    "secret assignment": re.compile(
        r"(?im)^\s*(?:[A-Za-z0-9]+[_-])*(?:api[_-]?key|token|password|"
        r"private[_-]?key|client[_-]?secret|secret[_-]?access[_-]?key|"
        r"access[_-]?token)\s*[:=]\s*\S+"
    ),
    "literal JSON API key": re.compile(
        r'(?im)^\s*"(?:[A-Za-z0-9]+[_-])*(?:api[_-]?key|token|password|'
        r'private[_-]?key|client[_-]?secret|secret[_-]?access[_-]?key|'
        r'access[_-]?token)"\s*:\s*"(?!\$\{|<)[^"]+"\s*,?\s*$'
    ),
    "private key material": re.compile(
        r"(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----$"
    ),
    "literal bearer credential": re.compile(
        r"(?i)\bbearer\s+(?!<|\$\{|\[?redacted\]?\b|token\b|credential\b|"
        r"authentication\b|header\b|forms?\b|scheme\b|syntax\b|value\b)\S+"
    ),
}
PUBLIC_SAFETY_ALLOWED_LITERALS = {
    "Tailscale DNS name": ("gateway.example.ts.net",),
}
IPV4_CANDIDATE_RE = re.compile(
    r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])"
)
IPV6_CANDIDATE_RE = re.compile(
    r"(?<![0-9A-Fa-f:.])\[?(?:[0-9A-Fa-f]{0,4}:){2,7}"
    r"[0-9A-Fa-f]{0,4}\]?(?![0-9A-Fa-f:.])"
)

MARKDOWN_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
HEX_40_RE = re.compile(r"^[0-9a-f]{40}$")
HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_architecture(path: Path = ARCHITECTURE_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_factory_model(path: Path = FACTORY_MODEL_PATH) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_factory_definition(path: Path = EXAMPLE_FACTORY_PATH) -> dict[str, Any]:
    return load_json_file(path)


def validate_factory_definition(data: Any) -> list[str]:
    """Validate one portable software-factory definition."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["factory definition root must be an object"]
    if set(data) != {
        "contract_schema",
        "schema_version",
        "factory",
        "versioning_policy",
        "reproducibility_policy",
        "scheduling_policy",
        "agent_policy",
        "feedback_policy",
        "module_bindings",
        "evidence_bindings",
    }:
        errors.append("factory definition contains missing or unexpected root fields")

    if data.get("contract_schema") != PORTABLE_FACTORY_SCHEMA_REFERENCE:
        errors.append("factory definition must reference its project-owned schema")
    if data.get("schema_version") != FACTORY_DEFINITION_SCHEMA_VERSION:
        errors.append(
            f"factory definition schema_version must equal {FACTORY_DEFINITION_SCHEMA_VERSION}"
        )

    factory = data.get("factory")
    factory_maturity: Any = None
    if not isinstance(factory, dict):
        errors.append("factory definition factory must be an object")
    else:
        if set(factory) != {"id", "class", "maturity", "purpose"}:
            errors.append("factory identity contains missing or unexpected fields")
        factory_id = factory.get("id")
        if not isinstance(factory_id, str) or not SLUG_RE.fullmatch(factory_id):
            errors.append("factory id must be a lowercase hyphenated slug")
        factory_class = factory.get("class")
        if not isinstance(factory_class, str) or factory_class not in {
            "control_factory",
            "economic_factory",
        }:
            errors.append("factory class must be control_factory or economic_factory")
        factory_maturity = factory.get("maturity")
        if not isinstance(factory_maturity, str) or factory_maturity not in ALLOWED_MATURITIES:
            errors.append("factory maturity must use a Zaibatsu maturity value")
        if not isinstance(factory.get("purpose"), str) or not factory["purpose"].strip():
            errors.append("factory purpose must be a non-empty string")

    versioning = data.get("versioning_policy")
    if not isinstance(versioning, dict) or versioning != {
        "source_and_intended_state": "git",
        "encrypted_static_secrets": "sops_age",
        "runtime_secrets": "bounded_secret_manager",
        "plaintext_secrets_in_git": False,
    }:
        errors.append("factory versioning must preserve Git, SOPS/age, and no plaintext")

    reproduction = data.get("reproducibility_policy")
    if not isinstance(reproduction, dict):
        errors.append("factory reproducibility_policy must be an object")
    else:
        if set(reproduction) != {
            "host_configuration",
            "worker_environments",
            "nix_maturity",
            "nix_cross_node_proof",
        }:
            errors.append("factory reproducibility policy has ambiguous fields")
        if reproduction.get("host_configuration") != "ansible":
            errors.append("factory host reproduction must use Ansible")
        if reproduction.get("worker_environments") != "nix":
            errors.append("factory worker-environment boundary must use Nix")
        nix_maturity = reproduction.get("nix_maturity")
        if not isinstance(nix_maturity, str) or nix_maturity not in ALLOWED_MATURITIES:
            errors.append("factory nix_maturity must use a Zaibatsu maturity value")
        if (
            reproduction.get("nix_cross_node_proof") is not True
            and isinstance(nix_maturity, str)
            and nix_maturity in {"operational", "validated_preproduction"}
        ):
            errors.append("factory Nix maturity requires cross-node reproduction proof")

    scheduling = data.get("scheduling_policy")
    if not isinstance(scheduling, dict):
        errors.append("factory scheduling_policy must be an object")
    else:
        if set(scheduling) != {
            "scheduler_of_record",
            "one_scheduler_of_record_per_workload",
        }:
            errors.append("factory scheduling policy has ambiguous fields")
        scheduler = scheduling.get("scheduler_of_record")
        if not isinstance(scheduler, str) or scheduler not in {"systemd", "cron"}:
            errors.append("factory scheduler_of_record must be systemd or cron")
        if scheduling.get("one_scheduler_of_record_per_workload") is not True:
            errors.append("factory workloads must have exactly one scheduler of record")

    agent = data.get("agent_policy")
    if not isinstance(agent, dict):
        errors.append("factory agent_policy must be an object")
    else:
        if set(agent) != {
            "skeleton_status",
            "harness_binding",
            "deterministic_gates",
            "model_may_authorize_external_effect",
        }:
            errors.append("factory agent policy has ambiguous fields")
        skeleton_status = agent.get("skeleton_status")
        if not isinstance(skeleton_status, str) or skeleton_status not in {
            "planned",
            "source_only",
            "validated_preproduction",
            "operational",
        }:
            errors.append("factory skeleton_status must declare an allowed boundary")
        if agent.get("harness_binding") != "model_independent_typed_ports":
            errors.append("factory harnesses must use model-independent typed ports")
        if agent.get("deterministic_gates") != list(REQUIRED_DETERMINISTIC_GATES):
            errors.append("factory deterministic gates must remain complete and ordered")
        if agent.get("model_may_authorize_external_effect") is not False:
            errors.append("a model may not authorize a factory external effect")

    feedback = data.get("feedback_policy")
    if not isinstance(feedback, dict) or feedback != {
        "return_evidence": True,
        "promotion_authority": "reviewed_deterministic_policy_and_owner_gate",
        "factory_may_self_promote": False,
    }:
        errors.append("factory feedback must return evidence without self-promotion")

    bindings = data.get("evidence_bindings")
    validated_bindings: list[dict[str, Any]] = []
    if not isinstance(bindings, list):
        errors.append("factory evidence_bindings must be a list")
    else:
        seen_capabilities: set[str] = set()
        for index, binding in enumerate(bindings):
            if not isinstance(binding, dict):
                errors.append(f"factory evidence binding at index {index} must be an object")
                continue
            if set(binding) != {
                "capability",
                "maturity",
                "receipt",
                "sha256",
                "independently_verified",
                "scope",
            }:
                errors.append(f"factory evidence binding at index {index} has ambiguous fields")
            capability = binding.get("capability")
            if not isinstance(capability, str) or not SLUG_RE.fullmatch(capability):
                errors.append(f"factory evidence binding at index {index} needs a capability slug")
                continue
            if capability in seen_capabilities:
                errors.append(f"duplicate factory evidence capability: {capability}")
            seen_capabilities.add(capability)
            binding_maturity = binding.get("maturity")
            if not isinstance(binding_maturity, str) or binding_maturity not in {
                "operational",
                "validated_preproduction",
            }:
                errors.append(f"{capability}: evidence binding needs a strong maturity")
            if not isinstance(binding.get("receipt"), str) or not binding["receipt"].strip():
                errors.append(f"{capability}: evidence binding receipt is required")
            digest = binding.get("sha256")
            if not isinstance(digest, str) or not HEX_64_RE.fullmatch(digest):
                errors.append(f"{capability}: evidence binding needs a SHA-256 digest")
            if binding.get("independently_verified") is not True:
                errors.append(f"{capability}: evidence binding needs independent verification")
            if not isinstance(binding.get("scope"), str) or not binding["scope"].strip():
                errors.append(f"{capability}: evidence binding scope is required")
            validated_bindings.append(binding)

    if (
        isinstance(factory_maturity, str)
        and factory_maturity in {"operational", "validated_preproduction"}
        and not any(
        binding.get("capability") == "factory-definition"
        and binding.get("maturity") == factory_maturity
        and binding.get("independently_verified") is True
        for binding in validated_bindings
        )
    ):
        errors.append("strong factory maturity requires a matching factory-definition receipt")

    if (
        isinstance(reproduction, dict)
        and isinstance(reproduction.get("nix_maturity"), str)
        and reproduction.get("nix_maturity")
        in {"operational", "validated_preproduction"}
        and not any(
            binding.get("capability") == "nix-environment-reproduction"
            and binding.get("maturity") == reproduction.get("nix_maturity")
            and binding.get("independently_verified") is True
            for binding in validated_bindings
        )
    ):
        errors.append("strong Nix maturity requires a content-addressed cross-node receipt")

    return errors


def _is_positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _validate_hash_map(value: Any, label: str) -> list[str]:
    if not isinstance(value, dict) or not value:
        return [f"{label} must be a non-empty object"]
    errors: list[str] = []
    for name, digest in value.items():
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{label} keys must be non-empty strings")
        if not isinstance(digest, str) or not HEX_64_RE.fullmatch(digest):
            errors.append(f"{label}.{name} must be a lowercase SHA-256 digest")
    return errors


def validate_evidence_receipt(relative: str, data: Any) -> list[str]:
    """Validate the semantic minimum for each sanitized evidence class."""
    errors: list[str] = []
    expected = EVIDENCE_CONTRACTS.get(relative)
    if expected is None:
        return [f"unknown evidence contract: {relative}"]
    if not isinstance(data, dict):
        return [f"{relative}: receipt root must be an object"]

    expected_schema, expected_status = expected
    if data.get("contract_schema") != CONTRACT_SCHEMA_REFERENCES[relative]:
        errors.append(f"{relative}: must reference its project-owned schema")
    if data.get("schema_version") != expected_schema:
        errors.append(f"{relative}: schema_version must equal {expected_schema}")
    if data.get("status") != expected_status:
        errors.append(f"{relative}: status must equal {expected_status}")
    observed_at = data.get("observed_at")
    if not isinstance(observed_at, str) or not re.fullmatch(
        r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z)?", observed_at
    ):
        errors.append(f"{relative}: observed_at must be an ISO date or UTC timestamp")

    if relative.endswith("dispatcher-validation-v1.json"):
        source = data.get("source")
        focused = data.get("focused_suite")
        postgres = data.get("postgresql_acceptance")
        if data.get("visibility") != "sanitized_from_private_source":
            errors.append(f"{relative}: visibility must preserve the private-source limitation")
        if not isinstance(source, dict):
            errors.append(f"{relative}: source must be an object")
        else:
            if not isinstance(source.get("base_revision"), str) or not HEX_40_RE.fullmatch(source["base_revision"]):
                errors.append(f"{relative}: source.base_revision must be a full Git commit")
            if source.get("scope") != "dispatcher" or source.get("state") != "reviewed_working_tree":
                errors.append(f"{relative}: source scope and reviewed state must remain explicit")
            if not _is_positive_int(source.get("source_file_count")):
                errors.append(f"{relative}: source.source_file_count must be positive")
            if not isinstance(source.get("source_tree_sha256"), str) or not HEX_64_RE.fullmatch(source["source_tree_sha256"]):
                errors.append(f"{relative}: source.source_tree_sha256 must be a SHA-256 digest")
            if not isinstance(source.get("limitation"), str) or not source["limitation"].strip():
                errors.append(f"{relative}: source.limitation must be recorded")
        if not isinstance(focused, dict) or focused.get("status") != "passed":
            errors.append(f"{relative}: focused suite must be a passed result")
        elif focused.get("tests_passed") != 158 or focused.get("tests_failed") != 0:
            errors.append(f"{relative}: focused suite counts must prove a zero-failure run")
        if not isinstance(postgres, dict) or postgres.get("status") != "passed":
            errors.append(f"{relative}: PostgreSQL acceptance must be a passed result")
        else:
            if postgres.get("network") != "unix-socket-only" or postgres.get("production_data") is not False:
                errors.append(f"{relative}: PostgreSQL acceptance must remain isolated from production")
            if postgres.get("postgresql_version") != "16.15":
                errors.append(f"{relative}: PostgreSQL version must remain bound to the observed run")
            if postgres.get("assertions_passed") != 104 or postgres.get("assertions_failed") != 0:
                errors.append(f"{relative}: PostgreSQL assertion counts must prove a zero-failure run")
            migrations = postgres.get("migration_sha256")
            if not isinstance(migrations, dict) or set(migrations) != DISPATCHER_MIGRATIONS:
                errors.append(f"{relative}: migration digest set must match the accepted run")
            errors.extend(
                f"{relative}: {error}"
                for error in _validate_hash_map(migrations, "migration_sha256")
            )
            restore = postgres.get("restore")
            if not isinstance(restore, dict):
                errors.append(f"{relative}: restore evidence must be an object")
            else:
                for field in ("dump_sha256", "fingerprint_sha256"):
                    value = restore.get(field)
                    if not isinstance(value, str) or not HEX_64_RE.fullmatch(value):
                        errors.append(f"{relative}: restore.{field} must be a SHA-256 digest")
                rows = restore.get("row_counts")
                if not isinstance(rows, dict) or set(rows) != DISPATCHER_RESTORE_TABLES or not all(
                    isinstance(name, str) and _is_nonnegative_int(count)
                    for name, count in rows.items()
                ):
                    errors.append(f"{relative}: restore.row_counts must be nonnegative integers")

    elif relative.endswith("droid-contribution-v1.json"):
        scope = data.get("scope")
        contribution = data.get("contribution")
        acceptance = data.get("acceptance")
        if data.get("factory_cli_version") != DROID_FACTORY_CLI_VERSION:
            errors.append(f"{relative}: factory_cli_version must match the accepted run")
        if data.get("session_reference") != DROID_SESSION_REFERENCE:
            errors.append(f"{relative}: session_reference must match the accepted run")
        if not isinstance(scope, dict) or scope.get("production_authority") is not False:
            errors.append(f"{relative}: contribution scope must deny production authority")
        elif (
            scope.get("files_changed")
            != ["scripts/validate_repository.py", "tests/test_validate_repository.py"]
            or scope.get("model_turns") != 15
            or scope.get("factory_credits") != 0
        ):
            errors.append(f"{relative}: contribution scope must match the accepted bounded run")
        if not isinstance(contribution, dict):
            errors.append(f"{relative}: contribution must be an object")
        elif (
            contribution.get("contribution_tests_passed") != 36
            or contribution.get("current_integrated_tests_passed")
            != INTEGRATED_TEST_COUNT
            or contribution.get("pre_change_result") != "mutation accepted"
            or contribution.get("post_change_result") != "mutation rejected"
        ):
            errors.append(f"{relative}: contribution result must match the accepted bounded run")
        if not isinstance(acceptance, dict) or acceptance != {
            "model_self_report_is_verification": False,
            "diff_reviewed": True,
            "independent_validation_passed": True,
            "credential_values_recorded": False,
        }:
            errors.append(f"{relative}: acceptance must preserve independent review and secret denial")

    elif relative.endswith("meta-factory-foundations-v1.json"):
        instances = data.get("factory_instances")
        operations = data.get("operations_foundation")
        scaffold = data.get("modular_agent_scaffold")
        harness = data.get("harness_and_verification")
        scheduling = data.get("scheduling")
        recursive = data.get("recursive_improvement")
        if data.get("visibility") != "sanitized_from_private_source":
            errors.append(f"{relative}: visibility must preserve the private-source limitation")
        if not isinstance(instances, dict) or instances.get("closed_registry") != REQUIRED_PROJECTS:
            errors.append(f"{relative}: factory registry must match current public authority")
        elif instances.get("control_factory_count") != 1 or instances.get("economic_factory_count") != 2:
            errors.append(f"{relative}: factory class counts must match the registry")
        if not isinstance(operations, dict) or (
            operations.get("policy_check") != "passed"
            or operations.get("ansible_maturity") != "validated_preproduction"
            or operations.get("sops_age_maturity") != "validated_preproduction"
            or operations.get("nix_maturity") != "planned"
            or not isinstance(operations.get("base_revision"), str)
            or not HEX_40_RE.fullmatch(operations["base_revision"])
            or not isinstance(operations.get("limitation"), str)
            or not operations["limitation"].strip()
        ):
            errors.append(f"{relative}: operations foundation must preserve evidence and maturity")
        if not isinstance(scaffold, dict):
            errors.append(f"{relative}: modular_agent_scaffold must be an object")
        else:
            if not isinstance(scaffold.get("source_tree_sha256"), str) or not HEX_64_RE.fullmatch(scaffold["source_tree_sha256"]):
                errors.append(f"{relative}: scaffold source digest must be a SHA-256 digest")
            if (
                scaffold.get("source_file_count") != 203
                or scaffold.get("tests_passed") != 309
                or scaffold.get("tests_failed") != 0
                or scaffold.get("logical_modules") != 21
                or scaffold.get("composed_flows") != 6
                or scaffold.get("deployment_profiles") != 12
            ):
                errors.append(f"{relative}: scaffold test counts must prove a zero-failure run")
            if scaffold.get("activation") != "none" or scaffold.get("production_authority") is not False:
                errors.append(f"{relative}: source-only scaffold may not claim activation or authority")
            if not isinstance(scaffold.get("limitation"), str) or not scaffold["limitation"].strip():
                errors.append(f"{relative}: source-only scaffold limitation must be recorded")
        if not isinstance(harness, dict) or harness.get("deterministic_gate_classes") != list(REQUIRED_DETERMINISTIC_GATES):
            errors.append(f"{relative}: deterministic gate classes must remain complete")
        elif (
            harness.get("model_independent_ports") != "source_present"
            or harness.get("general_unattended_multi_harness_routing") != "not_active"
        ):
            errors.append(f"{relative}: harness maturity boundary must remain explicit")
        if not isinstance(scheduling, dict) or scheduling != {
            "systemd": "operational_primary_durable_scheduler",
            "cron": "operational_selected_downstream_scheduler",
            "invariant": "one scheduler of record per workload",
        }:
            errors.append(f"{relative}: scheduler evidence must preserve single ownership")
        if not isinstance(recursive, dict) or recursive.get("autonomous_self_promotion") is not False:
            errors.append(f"{relative}: recursive improvement may not self-promote")
        elif recursive.get("shared_template_promotion") != "designed_owner_gated":
            errors.append(f"{relative}: shared promotion must remain designed and owner-gated")
        if data.get("external_changes_performed") is not False or data.get("credential_values_recorded") is not False:
            errors.append(f"{relative}: receipt must deny external changes and credential capture")

    elif relative.endswith("qwen-model-observation-v1.json"):
        observation = data.get("reported_observation")
        limitations = data.get("limitations")
        if data.get("transport") != "authenticated_private_openai_compatible_gateway":
            errors.append(f"{relative}: transport boundary must remain explicit")
        if not isinstance(observation, dict) or not all(
            isinstance(observation.get(field), str) and observation[field].strip()
            for field in ("loaded_filename_label", "artifact_filename_format", "server_reported_quantization")
        ):
            errors.append(f"{relative}: reported model observations must be non-empty strings")
        elif observation != {
            "loaded_filename_label": "Qwen 3.8 27B",
            "artifact_filename_format": "GGUF",
            "server_reported_quantization": "Q4_K - Small",
        }:
            errors.append(f"{relative}: model observation must match the bounded receipt")
        redactions = data.get("redactions")
        if (
            not isinstance(redactions, list)
            or not all(isinstance(item, str) for item in redactions)
            or set(redactions)
            != {"endpoint", "credential", "model_path", "model_alias"}
        ):
            errors.append(f"{relative}: endpoint, credential, model path, and alias must stay redacted")
        if not isinstance(limitations, list) or len(limitations) < 3 or not all(
            isinstance(item, str) and item.strip() for item in limitations
        ):
            errors.append(f"{relative}: model identity limitations must remain explicit")
        elif not any("does not independently verify" in item for item in limitations) or not any(
            "does not map a weight-file hash" in item for item in limitations
        ):
            errors.append(f"{relative}: model identity and provenance limitations are required")

    return errors


def validate_evidence_receipts(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for relative in EVIDENCE_CONTRACTS:
        path = root / relative
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: cannot load evidence receipt: {exc}")
            continue
        errors.extend(validate_evidence_receipt(relative, data))
    return errors


def validate_factory_model(data: Any) -> list[str]:
    """Validate Zaibatsu's factory-of-software-factories contract."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["factory model root must be an object"]

    if data.get("contract_schema") != CONTRACT_SCHEMA_REFERENCES[
        "architecture/factory-model.json"
    ]:
        errors.append("factory model must reference its project-owned schema")
    if data.get("schema_version") != FACTORY_MODEL_SCHEMA_VERSION:
        errors.append(
            f"factory schema_version must equal {FACTORY_MODEL_SCHEMA_VERSION}"
        )

    project = data.get("project")
    if not isinstance(project, dict):
        errors.append("factory model project must be an object")
    elif (
        project.get("name") != PROJECT_NAME
        or project.get("role") != "meta_factory_control_layer"
        or project.get("definition") != "A factory of software factories"
    ):
        errors.append("Zaibatsu must remain the meta-factory control layer")

    classes = data.get("factory_classes")
    if not isinstance(classes, dict) or set(classes) != {
        "control_factory",
        "economic_factory",
    }:
        errors.append("factory_classes must define control_factory and economic_factory")
    elif not all(isinstance(value, str) and value.strip() for value in classes.values()):
        errors.append("factory class definitions must be non-empty strings")

    instances = data.get("factory_instances")
    instance_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(instances, list):
        errors.append("factory_instances must be a list")
    else:
        for index, instance in enumerate(instances):
            if not isinstance(instance, dict):
                errors.append(f"factory instance at index {index} must be an object")
                continue
            instance_id = instance.get("id")
            if not isinstance(instance_id, str) or not instance_id.strip():
                errors.append(f"factory instance at index {index} must have a string id")
                continue
            if instance_id in instance_by_id:
                errors.append(f"duplicate factory instance id: {instance_id}")
                continue
            instance_by_id[instance_id] = instance
            expected = REQUIRED_FACTORY_INSTANCES.get(instance_id)
            if expected is not None and (
                instance.get("class"), instance.get("maturity")
            ) != expected:
                errors.append(
                    f"{instance_id}: factory class and maturity must remain {expected!r}"
                )
            if not isinstance(instance.get("purpose"), str) or not instance[
                "purpose"
            ].strip():
                errors.append(f"{instance_id}: factory purpose must be a non-empty string")
        if set(instance_by_id) != set(REQUIRED_FACTORY_INSTANCES):
            errors.append("factory_instances must exactly match the closed project registry")

    lifecycle = data.get("factory_lifecycle")
    if lifecycle != list(REQUIRED_FACTORY_LIFECYCLE):
        errors.append("factory_lifecycle must preserve the complete meta-factory order")

    capabilities = data.get("capabilities")
    capability_by_id: dict[str, dict[str, Any]] = {}
    if not isinstance(capabilities, list):
        errors.append("factory capabilities must be a list")
    else:
        for index, capability in enumerate(capabilities):
            if not isinstance(capability, dict):
                errors.append(f"factory capability at index {index} must be an object")
                continue
            capability_id = capability.get("id")
            if not isinstance(capability_id, str) or not capability_id.strip():
                errors.append(f"factory capability at index {index} must have a string id")
                continue
            if capability_id in capability_by_id:
                errors.append(f"duplicate factory capability id: {capability_id}")
                continue
            capability_by_id[capability_id] = capability
            expected_maturity = REQUIRED_FACTORY_CAPABILITY_MATURITIES.get(
                capability_id
            )
            if capability.get("maturity") != expected_maturity:
                errors.append(
                    f"{capability_id}: factory capability maturity must remain "
                    f"{expected_maturity!r}"
                )
            for field in ("layer", "scope"):
                if not isinstance(capability.get(field), str) or not capability[
                    field
                ].strip():
                    errors.append(
                        f"{capability_id}: factory capability {field} must be non-empty"
                    )
        if set(capability_by_id) != set(REQUIRED_FACTORY_CAPABILITY_MATURITIES):
            errors.append("factory capabilities must exactly match the required meta-factory set")

    reproduction = data.get("reproducibility_policy")
    if not isinstance(reproduction, dict) or reproduction != {
        "host_configuration": "ansible",
        "worker_environments": "nix",
        "nix_currently_deployed": False,
    }:
        errors.append("reproducibility policy must preserve the Ansible/Nix boundary")

    versioning = data.get("versioning_policy")
    if not isinstance(versioning, dict) or versioning != {
        "source_and_intended_state": "git",
        "encrypted_static_secrets": "sops_age",
        "runtime_machine_secrets": "bounded_secret_manager",
        "plaintext_secrets_in_git": False,
    }:
        errors.append("versioning policy must preserve Git, SOPS/age, and no plaintext")

    scheduling = data.get("scheduling_policy")
    if not isinstance(scheduling, dict) or scheduling != {
        "supported_schedulers": ["systemd", "cron"],
        "durable_default": "systemd",
        "one_scheduler_of_record_per_workload": True,
    }:
        errors.append("scheduling policy must preserve systemd, cron, and single ownership")

    agent_policy = data.get("agent_policy")
    if not isinstance(agent_policy, dict):
        errors.append("agent_policy must be an object")
    else:
        if agent_policy.get("skeleton_status") != "source_only":
            errors.append("agent skeletons must remain source_only until deployment evidence")
        if agent_policy.get("factory_deployment_status") != "planned":
            errors.append("agent factory deployment must remain planned")
        if agent_policy.get("harness_binding") != "model_independent_typed_ports":
            errors.append("agent harnesses must bind through model-independent typed ports")
        if agent_policy.get("deterministic_gates") != list(
            REQUIRED_DETERMINISTIC_GATES
        ):
            errors.append("agent deterministic gates must remain complete and ordered")
        if agent_policy.get("planned_gate_extensions") != ["repository_hooks"]:
            errors.append("repository hooks must remain an explicit planned gate extension")
        if agent_policy.get("model_may_authorize_external_effect") is not False:
            errors.append("a model may not authorize an external effect")

    feedback = data.get("feedback_policy")
    if not isinstance(feedback, dict) or feedback != {
        "evidence_return_maturity": "operational",
        "shared_pattern_promotion_maturity": "designed",
        "promotion_authority": "reviewed_deterministic_policy_and_owner_gate",
        "factory_may_self_promote": False,
    }:
        errors.append("feedback policy must remain evidence-bound and owner-gated")

    invariants = data.get("invariants")
    if not isinstance(invariants, dict) or set(invariants) != REQUIRED_FACTORY_INVARIANTS:
        errors.append("factory invariants must exactly match the required meta-factory set")
    elif not all(value is True for value in invariants.values()):
        errors.append("every factory invariant must remain true")

    return errors


def validate_architecture(data: Any) -> list[str]:
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["architecture root must be an object"]

    if data.get("contract_schema") != CONTRACT_SCHEMA_REFERENCES[
        "architecture/system.json"
    ]:
        errors.append("architecture must reference its project-owned schema")
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

    if data.get("contract_schema") != CONTRACT_SCHEMA_REFERENCES[
        "architecture/submission-readiness.json"
    ]:
        errors.append("submission readiness must reference its project-owned schema")
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

        proof = gate.get("proof")
        if status == "complete":
            required_fields = GATE_PROOF_FIELDS[gate_id]
            if not isinstance(proof, dict):
                errors.append(f"{gate_id}: complete gate requires structured proof")
            else:
                missing_proof = required_fields - set(proof)
                if missing_proof:
                    errors.append(
                        f"{gate_id}: proof missing required fields: "
                        + ", ".join(sorted(missing_proof))
                    )
                if any(
                    value is None or value == "" or value == [] or value == {}
                    for value in proof.values()
                ):
                    errors.append(f"{gate_id}: proof values must be non-empty")
        elif proof is not None:
            errors.append(f"{gate_id}: incomplete gate must not carry completion proof")

        if isinstance(proof, dict):
            receipt = proof.get("receipt")
            if receipt is not None and (
                not isinstance(receipt, str) or receipt not in EVIDENCE_CONTRACTS
            ):
                errors.append(f"{gate_id}: proof receipt must reference a validated receipt")
            if gate_id == "public_package":
                contracts = proof.get("contracts")
                required_contracts = {
                    "architecture/factory-model.json",
                    "architecture/system.json",
                    "architecture/submission-readiness.json",
                    "catalog/modules.json",
                    "examples/economic-factory.json",
                    "examples/economic-factory-cron.json",
                    "examples/economic-factory.bundle-manifest.json",
                    "examples/economic-factory.plan.json",
                    "examples/economic-factory.rebuild-plan.json",
                    "examples/economic-factory.source-lock.json",
                    "examples/economic-factory.qualification-assessment.json",
                    "examples/economic-factory.qualification-evidence.json",
                    "examples/economic-factory.qualification-plan.json",
                    "policies/runtime-qualification-v1.json",
                }
                if (
                    not isinstance(contracts, list)
                    or not all(isinstance(path, str) for path in contracts)
                    or set(contracts) != required_contracts
                    or len(contracts) != len(required_contracts)
                ):
                    errors.append(f"{gate_id}: proof contracts must reference public contracts")
                if proof.get("validator") != "scripts/validate_repository.py":
                    errors.append(f"{gate_id}: proof validator must name the enforced validator")
            elif gate_id == "droid_cli_install":
                if proof.get("receipt") != "evidence/droid-contribution-v1.json":
                    errors.append(f"{gate_id}: proof must use the Droid receipt")
                if proof.get("factory_cli_version") != DROID_FACTORY_CLI_VERSION:
                    errors.append(f"{gate_id}: proof must match the accepted Factory CLI version")
            elif gate_id == "local_qwen_endpoint":
                if proof.get("receipt") != "evidence/qwen-model-observation-v1.json":
                    errors.append(f"{gate_id}: proof must use the Qwen observation receipt")
                if proof.get("transport_tested") is not True:
                    errors.append(f"{gate_id}: proof must record a tested transport")
            elif gate_id == "local_model_credential":
                if proof.get("receipt") != "evidence/droid-contribution-v1.json":
                    errors.append(f"{gate_id}: proof must use the credential-safe Droid receipt")
                if proof.get("credential_value_recorded") is not False:
                    errors.append(f"{gate_id}: proof must deny credential-value recording")
            elif gate_id == "factory_cli_authentication":
                if proof.get("receipt") != "evidence/droid-contribution-v1.json":
                    errors.append(f"{gate_id}: proof must use the authenticated Droid receipt")
                if proof.get("authenticated_session_recorded") is not True:
                    errors.append(f"{gate_id}: proof must record an authenticated session")
            elif gate_id == "bounded_droid_contribution":
                if proof.get("receipt") != "evidence/droid-contribution-v1.json":
                    errors.append(f"{gate_id}: proof must use the Droid receipt")
                if proof.get("session_reference") != DROID_SESSION_REFERENCE:
                    errors.append(f"{gate_id}: proof must match the accepted session")
            elif gate_id == "public_repository":
                if proof.get("url") != PUBLIC_REPOSITORY_URL:
                    errors.append(f"{gate_id}: proof must use the canonical public repository")
                if proof.get("anonymous_access_verified") is not True:
                    errors.append(f"{gate_id}: proof must record anonymous access")
            elif gate_id == "fresh_clone_reproduction":
                commit = proof.get("candidate_commit")
                if not isinstance(commit, str) or not HEX_40_RE.fullmatch(commit):
                    errors.append(f"{gate_id}: proof must pin a full candidate commit")
                if proof.get("tests_passed") != INTEGRATED_TEST_COUNT:
                    errors.append(f"{gate_id}: proof must match the integrated test count")
                if not isinstance(proof.get("gitleaks_version"), str) or not proof["gitleaks_version"].strip():
                    errors.append(f"{gate_id}: proof must record the Gitleaks version")
                if not isinstance(proof.get("github_actions_run"), str) or not proof["github_actions_run"].startswith("https://github.com/"):
                    errors.append(f"{gate_id}: proof must link the GitHub Actions run")
            elif gate_id == "public_demo":
                if not isinstance(proof.get("url"), str) or not proof["url"].startswith("https://"):
                    errors.append(f"{gate_id}: proof must link the public demo")
                if not isinstance(proof.get("release_tag"), str) or not re.fullmatch(r"v\d+\.\d+\.\d+", proof["release_tag"]):
                    errors.append(f"{gate_id}: proof must name a semantic release tag")
            elif gate_id == "applicant_materials":
                if proof.get("submitted_by_applicant") is not True or proof.get("resume_provided_privately") is not True:
                    errors.append(f"{gate_id}: proof must preserve applicant-owned submission")

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
        gate.get("status") == "complete" for gate in gate_by_id.values()
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


def validate_factory_consistency(architecture: Any, factory_model: Any) -> list[str]:
    """Keep the component architecture and meta-factory model aligned."""
    if not isinstance(architecture, dict) or not isinstance(factory_model, dict):
        return []

    errors: list[str] = []
    instances = factory_model.get("factory_instances")
    if isinstance(instances, list) and all(
        isinstance(instance, dict) and isinstance(instance.get("id"), str)
        for instance in instances
    ):
        instance_ids = [instance["id"] for instance in instances]
        if architecture.get("project_allowlist") != instance_ids:
            errors.append(
                "architecture project_allowlist must match factory instance order"
            )

    components = architecture.get("components")
    capabilities = factory_model.get("capabilities")
    if not isinstance(components, list) or not isinstance(capabilities, list):
        return errors
    component_maturities = {
        component.get("id"): component.get("maturity")
        for component in components
        if isinstance(component, dict) and isinstance(component.get("id"), str)
    }
    capability_maturities = {
        capability.get("id"): capability.get("maturity")
        for capability in capabilities
        if isinstance(capability, dict) and isinstance(capability.get("id"), str)
    }
    required_matches = {
        "ansible-configuration": "ansible-reproduction",
        "nix-project-environments": "nix-environment-reproduction",
        "current-systemd-executor": "systemd-scheduling",
        "factory-droid-contribution": "llm-harness-adapters",
    }
    for component_id, capability_id in required_matches.items():
        if component_maturities.get(component_id) != capability_maturities.get(
            capability_id
        ):
            errors.append(
                f"{component_id} maturity must match meta-factory capability "
                f"{capability_id}"
            )
    return errors


def repository_candidate_paths(root: Path = ROOT) -> list[Path]:
    """Return tracked and non-ignored untracked paths, including force-added files."""
    if (root / ".git").exists():
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(root),
                    "ls-files",
                    "--cached",
                    "--others",
                    "--exclude-standard",
                    "-z",
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (OSError, subprocess.CalledProcessError):
            pass
        else:
            paths = [
                root / item.decode("utf-8", errors="surrogateescape")
                for item in result.stdout.split(b"\0")
                if item
            ]
            return sorted(paths, key=lambda path: str(path.relative_to(root)))

    return sorted(
        (
            path
            for path in root.rglob("*")
            if ".git" not in path.relative_to(root).parts
            and (path.is_file() or path.is_symlink())
        ),
        key=lambda path: str(path.relative_to(root)),
    )


def git_index_entries(root: Path = ROOT) -> list[tuple[str, str, str, Path]]:
    """Return mode, object id, stage, and path for every Git index entry."""
    if not (root / ".git").exists():
        return []
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--stage", "-z"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    entries: list[tuple[str, str, str, Path]] = []
    for raw_entry in result.stdout.split(b"\0"):
        if not raw_entry:
            continue
        metadata, separator, raw_path = raw_entry.partition(b"\t")
        parts = metadata.decode("ascii", errors="strict").split()
        if not separator or len(parts) != 3:
            raise ValueError("malformed Git index entry")
        mode, object_id, stage = parts
        path = root / raw_path.decode("utf-8", errors="surrogateescape")
        entries.append((mode, object_id, stage, path))
    return entries


def public_files(root: Path = ROOT) -> list[Path]:
    return [
        path
        for path in repository_candidate_paths(root)
        if not path.is_symlink() and path.is_file()
    ]


def validate_public_paths(root: Path = ROOT) -> list[str]:
    """Reject links that can hide or redirect public repository content."""
    errors: list[str] = []
    try:
        index_entries = git_index_entries(root)
    except (OSError, subprocess.CalledProcessError, UnicodeError, ValueError) as exc:
        errors.append(f"cannot inspect Git index paths: {exc}")
        index_entries = []
    special_index_paths: set[Path] = set()
    for mode, _object_id, stage, path in index_entries:
        relative = path.relative_to(root)
        if stage != "0":
            errors.append(f"{relative}: unresolved Git index stage must fail closed")
        if mode == "120000":
            errors.append(f"{relative}: public repository paths must not be symlinks")
            special_index_paths.add(path)
        elif mode == "160000":
            errors.append(f"{relative}: Git submodules are outside the public scan boundary")
            special_index_paths.add(path)
    for path in repository_candidate_paths(root):
        relative = path.relative_to(root)
        if path in special_index_paths:
            continue
        if path.is_symlink():
            errors.append(f"{relative}: public repository paths must not be symlinks")
        elif path.is_dir():
            errors.append(f"{relative}: Git submodules are outside the public scan boundary")
    return errors


def contains_disallowed_match(label: str, pattern: re.Pattern[str], text: str) -> bool:
    allowed = {
        literal.casefold()
        for literal in PUBLIC_SAFETY_ALLOWED_LITERALS.get(label, ())
    }
    return any(match.group(0).casefold() not in allowed for match in pattern.finditer(text))


def validate_public_content(relative: str, raw: bytes) -> list[str]:
    errors: list[str] = []
    if b"\x00" in raw:
        return [f"{relative}: opaque binary file cannot be safety-scanned"]
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [f"{relative}: cannot scan public text: {exc}"]
    for label, pattern in PUBLIC_SAFETY_PATTERNS.items():
        if contains_disallowed_match(label, pattern, text):
            errors.append(f"{relative}: contains {label}")
    for match in IPV4_CANDIDATE_RE.finditer(text):
        try:
            address = ipaddress.ip_address(match.group(0))
        except ValueError:
            continue
        if address.version == 4 and address.is_global:
            errors.append(f"{relative}: contains public IPv4 address")
            break
    for match in IPV6_CANDIDATE_RE.finditer(text):
        candidate = match.group(0).strip("[]")
        try:
            address = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        if address.version == 6 and not (
            address.is_loopback or address.is_unspecified
        ):
            errors.append(f"{relative}: contains IPv6 address")
            break
    return errors


def validate_public_safety(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in public_files(root):
        try:
            raw = path.read_bytes()
        except OSError as exc:
            errors.append(f"{path.relative_to(root)}: cannot scan public text: {exc}")
            continue
        errors.extend(validate_public_content(str(path.relative_to(root)), raw))

    try:
        index_entries = git_index_entries(root)
    except (OSError, subprocess.CalledProcessError, UnicodeError, ValueError) as exc:
        errors.append(f"cannot inspect Git index content: {exc}")
        return errors
    for mode, object_id, stage, path in index_entries:
        if stage != "0" or mode not in {"100644", "100755"}:
            continue
        try:
            result = subprocess.run(
                ["git", "-C", str(root), "cat-file", "blob", object_id],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (OSError, subprocess.CalledProcessError) as exc:
            errors.append(f"{path.relative_to(root)}: cannot scan Git index blob: {exc}")
            continue
        errors.extend(
            validate_public_content(
                f"{path.relative_to(root)} (Git index)", result.stdout
            )
        )
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


def validate_contract_schema_files(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    root_resolved = root.resolve()
    for relative, expected_reference in CONTRACT_SCHEMA_REFERENCES.items():
        instance_path = root / relative
        try:
            instance = json.loads(instance_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: cannot load schema-bound contract: {exc}")
            continue
        if not isinstance(instance, dict) or instance.get("contract_schema") != expected_reference:
            errors.append(f"{relative}: contract_schema must equal {expected_reference}")
            continue
        if relative in REMOTE_SCHEMA_LOCAL_PATHS:
            schema_path = (root / REMOTE_SCHEMA_LOCAL_PATHS[relative]).resolve()
        else:
            schema_path = (instance_path.parent / expected_reference).resolve()
        try:
            schema_path.relative_to(root_resolved)
        except ValueError:
            errors.append(f"{relative}: contract schema escapes the repository")
            continue
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{relative}: cannot load project-owned schema: {exc}")
            continue
        if not isinstance(schema, dict):
            errors.append(f"{relative}: project-owned schema root must be an object")
            continue
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"{relative}: project-owned schema must declare JSON Schema 2020-12")
        schema_release = (
            "v1.8.0"
            if schema_path.name == "factory-rebuild-plan.schema.json"
            else "v1.7.0"
            if schema_path.name == "factory-source-lock.schema.json"
            else "v1.6.0"
            if schema_path.name
            in {
                "factory-qualification-assessment.schema.json",
                "factory-qualification-evidence.schema.json",
            }
            else "v1.5.0"
            if schema_path.name
            in {
                "factory-qualification-plan.schema.json",
                "module-qualification-policy.schema.json",
            }
            else "v1.3.0"
            if schema_path.name
            in {
                "factory-bundle-manifest.schema.json",
                "factory-plan.schema.json",
                "module-artifact.schema.json",
                "module-catalog.schema.json",
            }
            else "v1.2.0"
            if schema_path.name == "factory-definition.schema.json"
            else "v1.1.1"
        )
        expected_id = (
            "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
            f"{schema_release}/schemas/{schema_path.name}"
        )
        if schema.get("$id") != expected_id:
            errors.append(f"{relative}: project-owned schema must use its immutable release id")
        if schema.get("type") != "object" or not isinstance(schema.get("required"), list):
            errors.append(f"{relative}: project-owned schema must define an object contract")
        properties = schema.get("properties")
        if (
            not isinstance(properties, dict)
            or not isinstance(properties.get("contract_schema"), dict)
            or properties["contract_schema"].get("const") != expected_reference
        ):
            errors.append(f"{relative}: schema must bind the instance contract_schema")
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
    factory_model: Any = None
    factory_definition: Any = None
    module_catalog: Any = None
    module_artifacts: dict[str, dict[str, Any]] = {}
    factory_plan: Any = None
    bundle_manifest: Any = None
    qualification_policy: Any = None
    qualification_plan: Any = None
    qualification_evidence: Any = None
    qualification_assessment: Any = None
    rebuild_plan_document: Any = None
    source_lock_document: Any = None
    qualification_bundle: bytes | None = None
    verified_qualification_bundle: Any = None
    readiness: Any = None
    errors.extend(validate_public_paths())
    errors.extend(validate_required_files())
    errors.extend(validate_contract_schema_files())
    try:
        data = load_architecture()
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load architecture: {exc}")
    else:
        errors.extend(validate_architecture(data))
    try:
        factory_model = load_factory_model()
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load factory model: {exc}")
    else:
        errors.extend(validate_factory_model(factory_model))
    try:
        factory_definition = load_factory_definition()
    except (OSError, ValueError) as exc:
        errors.append(f"cannot load example factory definition: {exc}")
    else:
        errors.extend(validate_factory_definition(factory_definition))
    try:
        module_catalog = load_module_catalog()
    except (OSError, ValueError) as exc:
        errors.append(f"cannot load module catalog: {exc}")
    else:
        errors.extend(validate_module_catalog(module_catalog))
        module_artifacts, artifact_errors = load_module_artifacts(module_catalog)
        errors.extend(artifact_errors)
        if isinstance(factory_definition, dict):
            errors.extend(validate_factory_bindings(factory_definition, module_catalog))
    try:
        factory_plan = load_factory_plan()
    except (OSError, ValueError) as exc:
        errors.append(f"cannot load example factory plan: {exc}")
    else:
        if isinstance(factory_definition, dict) and isinstance(module_catalog, dict):
            errors.extend(
                validate_factory_plan(factory_plan, factory_definition, module_catalog)
            )
    try:
        bundle_manifest = load_json_file(EXAMPLE_BUNDLE_MANIFEST_PATH)
    except (OSError, ValueError) as exc:
        errors.append(f"cannot load example bundle manifest: {exc}")
    else:
        if all(
            isinstance(value, dict)
            for value in (factory_definition, module_catalog, factory_plan)
        ) and module_artifacts:
            try:
                payloads = build_bundle_payloads(
                    factory_definition,
                    module_catalog,
                    factory_plan,
                    module_artifacts,
                )
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"cannot rebuild example bundle payloads: {exc}")
            else:
                errors.extend(
                    validate_bundle_manifest(
                        bundle_manifest,
                        factory_definition,
                        module_catalog,
                        factory_plan,
                        payloads,
                    )
                )
    try:
        qualification_policy = load_qualification_policy(
            QUALIFICATION_POLICY_PATH
        )
    except (OSError, ValueError) as exc:
        errors.append(f"cannot load qualification policy: {exc}")
    else:
        errors.extend(validate_qualification_policy(qualification_policy))
    try:
        qualification_plan = load_qualification_plan(
            EXAMPLE_QUALIFICATION_PLAN_PATH
        )
    except (OSError, ValueError) as exc:
        errors.append(f"cannot load example qualification plan: {exc}")
    else:
        if all(
            isinstance(value, dict)
            for value in (
                factory_definition,
                module_catalog,
                qualification_policy,
            )
        ) and module_artifacts:
            try:
                qualification_bundle, _ = build_factory_bundle(
                    factory_definition,
                    module_catalog,
                    module_artifacts,
                )
                bundle_errors, verified_qualification_bundle = verify_factory_bundle(
                    qualification_bundle
                )
            except (KeyError, TypeError, ValueError) as exc:
                errors.append(f"cannot rebuild qualification input bundle: {exc}")
            else:
                errors.extend(
                    f"qualification input bundle: {error}"
                    for error in bundle_errors
                )
                if verified_qualification_bundle is not None:
                    errors.extend(
                        validate_qualification_plan(
                            qualification_plan,
                            verified_qualification_bundle,
                            qualification_policy,
                        )
                    )
    try:
        qualification_evidence = load_qualification_evidence(
            EXAMPLE_QUALIFICATION_EVIDENCE_PATH
        )
    except (OSError, ValueError) as exc:
        errors.append(f"cannot load example qualification evidence: {exc}")
    else:
        if verified_qualification_bundle is not None:
            errors.extend(
                validate_qualification_evidence(
                    qualification_evidence,
                    verified_qualification_bundle,
                    qualification_plan,
                    qualification_policy,
                )
            )
    try:
        source_lock_document = load_source_lock(EXAMPLE_SOURCE_LOCK_PATH)
    except (OSError, ValueError) as exc:
        errors.append(f"cannot load example factory source lock: {exc}")
    else:
        if qualification_bundle is not None:
            errors.extend(
                validate_source_lock(
                    source_lock_document,
                    ROOT,
                    qualification_bundle,
                )
            )
    try:
        qualification_assessment = load_qualification_assessment(
            EXAMPLE_QUALIFICATION_ASSESSMENT_PATH
        )
    except (OSError, ValueError) as exc:
        errors.append(f"cannot load example qualification assessment: {exc}")
    else:
        if verified_qualification_bundle is not None:
            errors.extend(
                validate_qualification_assessment(
                    qualification_assessment,
                    qualification_evidence,
                    verified_qualification_bundle,
                    qualification_plan,
                    qualification_policy,
                )
            )
    try:
        rebuild_plan_document = load_rebuild_plan(EXAMPLE_REBUILD_PLAN_PATH)
    except (OSError, RecursionError, ValueError) as exc:
        errors.append(f"cannot load example factory rebuild plan: {exc}")
    else:
        if (
            qualification_bundle is not None
            and all(
                isinstance(value, dict)
                for value in (
                    source_lock_document,
                    qualification_assessment,
                    qualification_evidence,
                    qualification_plan,
                    qualification_policy,
                )
            )
        ):
            errors.extend(
                verify_factory_rebuild_plan_for_bundle(
                    rebuild_plan_document,
                    source_lock_document,
                    qualification_assessment,
                    qualification_evidence,
                    qualification_plan,
                    qualification_bundle,
                    qualification_policy,
                    ROOT,
                )
            )
    try:
        readiness = json.loads(READINESS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"cannot load submission readiness: {exc}")
    else:
        errors.extend(validate_submission_readiness(readiness))
    errors.extend(validate_contract_consistency(data, readiness))
    errors.extend(validate_factory_consistency(data, factory_model))
    errors.extend(validate_evidence_receipts())
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
    print(
        f"- {len(factory_model['factory_instances'])} software factories and "
        f"{len(factory_model['capabilities'])} meta-factory capabilities checked"
    )
    print(
        "- 2 reusable factory definitions, content-addressed modules, control "
        "plan, bundle manifest, source lock, qualification evidence, and "
        "non-executing rebuild DAG checked"
    )
    print(f"- {len(EVIDENCE_CONTRACTS)} evidence receipts checked")
    print(f"- {len(REQUIRED_FACTORY_INVARIANTS)} meta-factory invariants checked")
    print(f"- {len(REQUIRED_TRUE_INVARIANTS)} fail-closed invariants checked")
    print(f"- {len(readiness['gates'])} submission gates checked")
    print("- public-safety and local-link checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
