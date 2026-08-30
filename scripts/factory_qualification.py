#!/usr/bin/env python3
"""Build deterministic, non-authorizing runtime-qualification plans."""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from factory_bundle import verify_factory_bundle
from factory_composer import (
    MODULE_API_VERSION,
    canonical_json_bytes,
    load_json_file,
    sha256_json,
)


ROOT = Path(__file__).resolve().parents[1]
QUALIFICATION_POLICY_PATH = ROOT / "policies" / "runtime-qualification-v1.json"
EXAMPLE_QUALIFICATION_PLAN_PATH = (
    ROOT / "examples" / "economic-factory.qualification-plan.json"
)
EXAMPLE_QUALIFICATION_EVIDENCE_PATH = (
    ROOT / "examples" / "economic-factory.qualification-evidence.json"
)
EXAMPLE_QUALIFICATION_ASSESSMENT_PATH = (
    ROOT / "examples" / "economic-factory.qualification-assessment.json"
)

QUALIFICATION_POLICY_SCHEMA_VERSION = "zaibatsu.module-qualification-policy.v1"
QUALIFICATION_PLAN_SCHEMA_VERSION = "zaibatsu.factory-qualification-plan.v1"
QUALIFICATION_EVIDENCE_SCHEMA_VERSION = (
    "zaibatsu.factory-qualification-evidence.v1"
)
QUALIFICATION_ASSESSMENT_SCHEMA_VERSION = (
    "zaibatsu.factory-qualification-assessment.v1"
)
QUALIFICATION_POLICY_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.5.0/schemas/module-qualification-policy.schema.json"
)
QUALIFICATION_PLAN_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.5.0/schemas/factory-qualification-plan.schema.json"
)
QUALIFICATION_EVIDENCE_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.6.0/schemas/factory-qualification-evidence.schema.json"
)
QUALIFICATION_ASSESSMENT_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.6.0/schemas/factory-qualification-assessment.schema.json"
)

REQUIRED_SLOTS = (
    "source_versioning",
    "static_secrets",
    "runtime_secrets",
    "host_reproduction",
    "worker_environment",
    "scheduling",
    "execution",
    "verification",
    "feedback",
)
MANDATORY_BASE_REQUIREMENTS = {
    "contract_conformance_receipt",
    "environment_lock_digest",
    "implementation_artifact_digest",
    "recovery_receipt",
    "source_revision",
}
MANDATORY_SLOT_REQUIREMENTS = {
    "source_versioning": {"repository_lineage_receipt"},
    "static_secrets": {
        "ciphertext_policy_receipt",
        "secret_recovery_receipt",
    },
    "runtime_secrets": {
        "secret_revocation_receipt",
        "secret_scope_receipt",
    },
    "host_reproduction": {
        "clean_host_recovery_receipt",
        "idempotence_receipt",
    },
    "worker_environment": {
        "cache_independence_receipt",
        "cross_node_reproduction_receipt",
    },
    "scheduling": {
        "duplicate_trigger_denial_receipt",
        "failure_route_receipt",
        "scheduler_authority_receipt",
    },
    "execution": {
        "budget_policy_receipt",
        "fixed_fixture_evaluation_receipt",
        "network_policy_receipt",
        "sandbox_isolation_receipt",
        "secret_policy_receipt",
        "typed_port_conformance_receipt",
    },
    "verification": {
        "adversarial_fixture_receipt",
        "deterministic_gate_receipt",
    },
    "feedback": {
        "promotion_authority_receipt",
        "rollback_receipt",
    },
}
POLICY_FIELDS = {
    "contract_schema",
    "schema_version",
    "policy_id",
    "module_api_version",
    "scope",
    "base_requirements",
    "slot_requirements",
    "decision_boundary",
}
SLOT_POLICY_FIELDS = {"slot", "requirements"}
DECISION_BOUNDARY = {
    "evidence_must_be_content_addressed": True,
    "missing_evidence_fails_closed": True,
    "owner_approval_required_for_activation": True,
    "qualification_grants_activation": False,
    "qualification_plan_is_evidence": False,
    "self_attestation_accepted": False,
}
PLAN_FIELDS = {
    "contract_schema",
    "schema_version",
    "factory",
    "source",
    "modules",
    "summary",
    "qualification_boundary",
    "qualification_plan_sha256",
}
EVIDENCE_FIELDS = {
    "contract_schema",
    "schema_version",
    "factory",
    "source",
    "receipts",
    "summary",
    "evidence_boundary",
    "qualification_evidence_sha256",
}
EVIDENCE_RECEIPT_FIELDS = {
    "position",
    "slot",
    "module",
    "artifact_sha256",
    "requirement",
    "verifier",
    "verification_method",
    "evidence_scope",
    "result",
    "receipt_sha256",
}
ASSESSMENT_FIELDS = {
    "contract_schema",
    "schema_version",
    "factory",
    "source",
    "modules",
    "summary",
    "assessment_boundary",
    "qualification_assessment_sha256",
}
CONTRACT_EVIDENCE_REQUIREMENT = "contract_conformance_receipt"
CONTRACT_EVIDENCE_VERIFIER = "zaibatsu.factory-bundle-verifier.v1"
CONTRACT_EVIDENCE_METHOD = "canonical_contract_catalog_and_digest"
CONTRACT_EVIDENCE_SCOPE = "module_contract_only"
EVIDENCE_BOUNDARY = {
    "source_is_verified_control_bundle": True,
    "contract_conformance_only": True,
    "external_independent_verification_included": False,
    "contains_runtime_implementation_evidence": False,
    "self_attestation_accepted": False,
    "runtime_eligibility_granted": False,
    "activation_authorized": False,
    "owner_approval_required_for_activation": True,
}
ASSESSMENT_BOUNDARY = {
    "assesses_bundle_contract_evidence_only": True,
    "external_independent_verification_included": False,
    "contains_runtime_implementation_evidence": False,
    "self_attestation_accepted": False,
    "runtime_eligibility_granted": False,
    "activation_authorized": False,
    "owner_approval_required_for_activation": True,
}
REQUIREMENT_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def load_qualification_policy(
    path: Path = QUALIFICATION_POLICY_PATH,
) -> dict[str, Any]:
    return load_json_file(path)


def load_qualification_plan(
    path: Path = EXAMPLE_QUALIFICATION_PLAN_PATH,
) -> dict[str, Any]:
    return load_json_file(path)


def load_qualification_evidence(
    path: Path = EXAMPLE_QUALIFICATION_EVIDENCE_PATH,
) -> dict[str, Any]:
    return load_json_file(path)


def load_qualification_assessment(
    path: Path = EXAMPLE_QUALIFICATION_ASSESSMENT_PATH,
) -> dict[str, Any]:
    return load_json_file(path)


def _validate_requirement_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        return [f"{label} must be a non-empty requirement list"]
    if not all(
        isinstance(requirement, str) and REQUIREMENT_RE.fullmatch(requirement)
        for requirement in value
    ):
        return [f"{label} contains an invalid requirement id"]
    errors: list[str] = []
    if len(value) != len(set(value)):
        errors.append(f"{label} requirements must be unique")
    if value != sorted(value):
        errors.append(f"{label} requirements must be sorted")
    return errors


def _json_exactly_equal(actual: Any, expected: Any) -> bool:
    """Compare JSON values without Python's bool/integer equivalence."""
    try:
        return canonical_json_bytes(actual) == canonical_json_bytes(expected)
    except (TypeError, ValueError):
        return False


def validate_qualification_policy(policy: Any) -> list[str]:
    """Reject qualification policies that weaken the public minimum."""
    errors: list[str] = []
    if not isinstance(policy, dict):
        return ["qualification policy root must be an object"]
    if set(policy) != POLICY_FIELDS:
        errors.append("qualification policy contains missing or unexpected fields")
    if policy.get("contract_schema") != QUALIFICATION_POLICY_SCHEMA_REFERENCE:
        errors.append("qualification policy must reference its immutable schema")
    if policy.get("schema_version") != QUALIFICATION_POLICY_SCHEMA_VERSION:
        errors.append("qualification policy schema_version is invalid")
    policy_id = policy.get("policy_id")
    if not isinstance(policy_id, str) or not SLUG_RE.fullmatch(policy_id):
        errors.append("qualification policy_id must be a lowercase slug")
    if policy.get("module_api_version") != MODULE_API_VERSION:
        errors.append("qualification policy module API is invalid")
    if policy.get("scope") != "runtime_eligibility_prerequisites":
        errors.append("qualification policy scope must remain runtime prerequisites")

    base = policy.get("base_requirements")
    errors.extend(_validate_requirement_list(base, "base qualification"))
    all_requirements: list[str] = []
    if isinstance(base, list) and all(isinstance(item, str) for item in base):
        all_requirements.extend(base)
        missing = MANDATORY_BASE_REQUIREMENTS - set(base)
        if missing:
            errors.append(
                "base qualification requirements are missing: "
                + ", ".join(sorted(missing))
            )

    entries = policy.get("slot_requirements")
    if not isinstance(entries, list):
        errors.append("qualification slot requirements must be a list")
    else:
        slots: list[Any] = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                errors.append(f"qualification slot entry {index} must be an object")
                continue
            if set(entry) != SLOT_POLICY_FIELDS:
                errors.append(
                    f"qualification slot entry {index} has ambiguous fields"
                )
            slot = entry.get("slot")
            slots.append(slot)
            if not isinstance(slot, str) or slot not in REQUIRED_SLOTS:
                errors.append(f"qualification slot entry {index} has an invalid slot")
                continue
            requirements = entry.get("requirements")
            errors.extend(
                _validate_requirement_list(
                    requirements,
                    f"{slot} qualification",
                )
            )
            if isinstance(requirements, list) and all(
                isinstance(item, str) for item in requirements
            ):
                all_requirements.extend(requirements)
                missing = MANDATORY_SLOT_REQUIREMENTS[slot] - set(requirements)
                if missing:
                    errors.append(
                        f"{slot} qualification requirements are missing: "
                        + ", ".join(sorted(missing))
                    )
        if slots != list(REQUIRED_SLOTS):
            errors.append(
                "qualification slot requirements must cover every slot in control order"
            )

    if len(all_requirements) != len(set(all_requirements)):
        errors.append("qualification requirement ids must be globally unique")
    if not _json_exactly_equal(
        policy.get("decision_boundary"),
        DECISION_BOUNDARY,
    ):
        errors.append("qualification policy must preserve the fail-closed boundary")
    return errors


def _requirements_by_slot(policy: dict[str, Any]) -> dict[str, list[str]]:
    return {
        entry["slot"]: entry["requirements"]
        for entry in policy["slot_requirements"]
    }


def build_qualification_plan(
    verified_bundle: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Build a missing-evidence plan from an already verified control bundle."""
    manifest = verified_bundle["manifest"]
    slot_requirements = _requirements_by_slot(policy)
    modules: list[dict[str, Any]] = []
    unique_requirements: set[str] = set()
    missing_bindings = 0
    for selected in manifest["selected_modules"]:
        requirements = sorted(
            set(policy["base_requirements"])
            | set(slot_requirements[selected["slot"]])
        )
        unique_requirements.update(requirements)
        missing_bindings += len(requirements)
        modules.append(
            {
                "position": selected["position"],
                "slot": selected["slot"],
                "module": selected["module"],
                "artifact_sha256": selected["artifact_sha256"],
                "required_evidence": requirements,
                "evidence_status": "not_provided",
                "runtime_eligible": False,
                "reason": "control_bundle_contains_no_runtime_implementation",
            }
        )

    source = manifest["source"]
    plan_without_digest: dict[str, Any] = {
        "contract_schema": QUALIFICATION_PLAN_SCHEMA_REFERENCE,
        "schema_version": QUALIFICATION_PLAN_SCHEMA_VERSION,
        "factory": deepcopy(manifest["factory"]),
        "source": {
            "bundle_sha256": verified_bundle["bundle_sha256"],
            "factory_plan_sha256": source["factory_plan_sha256"],
            "module_catalog_sha256": source["module_catalog_sha256"],
            "qualification_policy_id": policy["policy_id"],
            "qualification_policy_sha256": sha256_json(policy),
            "module_api_version": source["module_api_version"],
        },
        "modules": modules,
        "summary": {
            "module_count": len(modules),
            "runtime_eligible_modules": 0,
            "runtime_ineligible_modules": len(modules),
            "missing_evidence_bindings": missing_bindings,
            "unique_requirement_types": len(unique_requirements),
            "all_requirements_satisfied": False,
        },
        "qualification_boundary": {
            "contains_qualification_evidence": False,
            "self_attestation_accepted": False,
            "runtime_eligibility_granted": False,
            "activation_authorized": False,
            "owner_approval_required_for_activation": True,
        },
    }
    plan = dict(plan_without_digest)
    plan["qualification_plan_sha256"] = sha256_json(plan_without_digest)
    return plan


def validate_qualification_plan(
    plan: Any,
    verified_bundle: Any,
    policy: Any,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["qualification plan root must be an object"]
    if set(plan) != PLAN_FIELDS:
        errors.append("qualification plan contains missing or unexpected fields")
    if plan.get("contract_schema") != QUALIFICATION_PLAN_SCHEMA_REFERENCE:
        errors.append("qualification plan must reference its immutable schema")
    if plan.get("schema_version") != QUALIFICATION_PLAN_SCHEMA_VERSION:
        errors.append("qualification plan schema_version is invalid")
    boundary = plan.get("qualification_boundary")
    if not isinstance(boundary, dict) or not _json_exactly_equal(
        boundary,
        {
            "contains_qualification_evidence": False,
            "self_attestation_accepted": False,
            "runtime_eligibility_granted": False,
            "activation_authorized": False,
            "owner_approval_required_for_activation": True,
        },
    ):
        errors.append("qualification plan must preserve the non-authorizing boundary")

    policy_errors = validate_qualification_policy(policy)
    errors.extend(f"qualification policy: {error}" for error in policy_errors)
    if not isinstance(verified_bundle, dict) or not isinstance(
        verified_bundle.get("manifest"), dict
    ):
        return errors + ["qualification plan requires a verified bundle result"]
    if policy_errors:
        return errors
    try:
        expected = build_qualification_plan(verified_bundle, policy)
    except (KeyError, TypeError, ValueError) as exc:
        return errors + [f"cannot rebuild expected qualification plan: {exc}"]
    if not _json_exactly_equal(plan, expected):
        errors.append(
            "qualification plan does not exactly match its verified bundle and policy"
        )
    return errors


def qualification_plan_for_bundle(
    bundle: bytes,
    policy: Any,
) -> tuple[list[str], dict[str, Any] | None]:
    policy_errors = validate_qualification_policy(policy)
    bundle_errors, verified = verify_factory_bundle(bundle)
    errors = [f"qualification policy: {error}" for error in policy_errors]
    errors.extend(f"factory bundle: {error}" for error in bundle_errors)
    if errors or verified is None:
        return errors, None
    return [], build_qualification_plan(verified, policy)


def verify_qualification_plan_for_bundle(
    plan: Any,
    bundle: bytes,
    policy: Any,
) -> list[str]:
    bundle_errors, verified = verify_factory_bundle(bundle)
    if bundle_errors or verified is None:
        return [f"factory bundle: {error}" for error in bundle_errors]
    return validate_qualification_plan(plan, verified, policy)


def _qualification_source(
    verified_bundle: dict[str, Any],
    plan: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    return {
        "bundle_sha256": verified_bundle["bundle_sha256"],
        "qualification_plan_sha256": plan["qualification_plan_sha256"],
        "qualification_policy_id": policy["policy_id"],
        "qualification_policy_sha256": sha256_json(policy),
        "module_api_version": plan["source"]["module_api_version"],
    }


def build_qualification_evidence(
    verified_bundle: dict[str, Any],
    plan: dict[str, Any],
    policy: dict[str, Any],
) -> dict[str, Any]:
    """Derive reproducible contract-only evidence from a verified bundle."""
    receipts: list[dict[str, Any]] = []
    required_bindings = 0
    for module in plan["modules"]:
        required_bindings += len(module["required_evidence"])
        receipt_without_digest: dict[str, Any] = {
            "position": module["position"],
            "slot": module["slot"],
            "module": module["module"],
            "artifact_sha256": module["artifact_sha256"],
            "requirement": CONTRACT_EVIDENCE_REQUIREMENT,
            "verifier": CONTRACT_EVIDENCE_VERIFIER,
            "verification_method": CONTRACT_EVIDENCE_METHOD,
            "evidence_scope": CONTRACT_EVIDENCE_SCOPE,
            "result": "passed",
        }
        receipt = dict(receipt_without_digest)
        receipt["receipt_sha256"] = sha256_json(receipt_without_digest)
        receipts.append(receipt)

    evidence_without_digest: dict[str, Any] = {
        "contract_schema": QUALIFICATION_EVIDENCE_SCHEMA_REFERENCE,
        "schema_version": QUALIFICATION_EVIDENCE_SCHEMA_VERSION,
        "factory": deepcopy(plan["factory"]),
        "source": _qualification_source(verified_bundle, plan, policy),
        "receipts": receipts,
        "summary": {
            "receipt_count": len(receipts),
            "required_evidence_bindings": required_bindings,
            "verified_evidence_bindings": len(receipts),
            "remaining_evidence_bindings": required_bindings - len(receipts),
            "verified_requirement_types": 1,
            "full_qualification_evidence": False,
        },
        "evidence_boundary": deepcopy(EVIDENCE_BOUNDARY),
    }
    evidence = dict(evidence_without_digest)
    evidence["qualification_evidence_sha256"] = sha256_json(
        evidence_without_digest
    )
    return evidence


def validate_qualification_evidence(
    evidence: Any,
    verified_bundle: Any,
    plan: Any,
    policy: Any,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(evidence, dict):
        return ["qualification evidence root must be an object"]
    if set(evidence) != EVIDENCE_FIELDS:
        errors.append(
            "qualification evidence contains missing or unexpected fields"
        )
    if evidence.get("contract_schema") != QUALIFICATION_EVIDENCE_SCHEMA_REFERENCE:
        errors.append("qualification evidence must reference its immutable schema")
    if evidence.get("schema_version") != QUALIFICATION_EVIDENCE_SCHEMA_VERSION:
        errors.append("qualification evidence schema_version is invalid")
    if not _json_exactly_equal(
        evidence.get("evidence_boundary"),
        EVIDENCE_BOUNDARY,
    ):
        errors.append(
            "qualification evidence must preserve the contract-only boundary"
        )

    plan_errors = validate_qualification_plan(plan, verified_bundle, policy)
    errors.extend(f"qualification plan: {error}" for error in plan_errors)
    if plan_errors:
        return errors
    try:
        expected = build_qualification_evidence(
            verified_bundle,
            plan,
            policy,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return errors + [f"cannot rebuild expected qualification evidence: {exc}"]
    if not _json_exactly_equal(evidence, expected):
        errors.append(
            "qualification evidence does not exactly match its verified "
            "bundle, plan, and policy"
        )
    return errors


def qualification_evidence_for_bundle(
    plan: Any,
    bundle: bytes,
    policy: Any,
) -> tuple[list[str], dict[str, Any] | None]:
    bundle_errors, verified = verify_factory_bundle(bundle)
    if bundle_errors or verified is None:
        return [f"factory bundle: {error}" for error in bundle_errors], None
    plan_errors = validate_qualification_plan(plan, verified, policy)
    if plan_errors:
        return [f"qualification plan: {error}" for error in plan_errors], None
    return [], build_qualification_evidence(verified, plan, policy)


def verify_qualification_evidence_for_bundle(
    evidence: Any,
    plan: Any,
    bundle: bytes,
    policy: Any,
) -> list[str]:
    bundle_errors, verified = verify_factory_bundle(bundle)
    if bundle_errors or verified is None:
        return [f"factory bundle: {error}" for error in bundle_errors]
    return validate_qualification_evidence(evidence, verified, plan, policy)


def build_qualification_assessment(
    verified_bundle: dict[str, Any],
    plan: dict[str, Any],
    policy: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Assess bundle-derived contract evidence without granting eligibility."""
    verified_by_module = {
        (receipt["position"], receipt["module"]): receipt["requirement"]
        for receipt in evidence["receipts"]
    }
    modules: list[dict[str, Any]] = []
    missing_requirement_types: set[str] = set()
    required_bindings = 0
    verified_bindings = 0
    for module in plan["modules"]:
        required = list(module["required_evidence"])
        verified_requirement = verified_by_module[
            (module["position"], module["module"])
        ]
        verified = [verified_requirement]
        missing = [item for item in required if item != verified_requirement]
        required_bindings += len(required)
        verified_bindings += len(verified)
        missing_requirement_types.update(missing)
        modules.append(
            {
                "position": module["position"],
                "slot": module["slot"],
                "module": module["module"],
                "artifact_sha256": module["artifact_sha256"],
                "required_evidence": required,
                "verified_evidence": verified,
                "missing_evidence": missing,
                "evidence_status": "partial",
                "runtime_eligible": False,
                "reason": "runtime_evidence_incomplete",
            }
        )

    assessment_without_digest: dict[str, Any] = {
        "contract_schema": QUALIFICATION_ASSESSMENT_SCHEMA_REFERENCE,
        "schema_version": QUALIFICATION_ASSESSMENT_SCHEMA_VERSION,
        "factory": deepcopy(plan["factory"]),
        "source": {
            **_qualification_source(verified_bundle, plan, policy),
            "qualification_evidence_sha256": evidence[
                "qualification_evidence_sha256"
            ],
        },
        "modules": modules,
        "summary": {
            "module_count": len(modules),
            "runtime_eligible_modules": 0,
            "runtime_ineligible_modules": len(modules),
            "required_evidence_bindings": required_bindings,
            "verified_evidence_bindings": verified_bindings,
            "missing_evidence_bindings": required_bindings - verified_bindings,
            "verified_requirement_types": 1,
            "missing_requirement_types": len(missing_requirement_types),
            "all_requirements_satisfied": False,
        },
        "assessment_boundary": deepcopy(ASSESSMENT_BOUNDARY),
    }
    assessment = dict(assessment_without_digest)
    assessment["qualification_assessment_sha256"] = sha256_json(
        assessment_without_digest
    )
    return assessment


def validate_qualification_assessment(
    assessment: Any,
    evidence: Any,
    verified_bundle: Any,
    plan: Any,
    policy: Any,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(assessment, dict):
        return ["qualification assessment root must be an object"]
    if set(assessment) != ASSESSMENT_FIELDS:
        errors.append(
            "qualification assessment contains missing or unexpected fields"
        )
    if (
        assessment.get("contract_schema")
        != QUALIFICATION_ASSESSMENT_SCHEMA_REFERENCE
    ):
        errors.append("qualification assessment must reference its immutable schema")
    if (
        assessment.get("schema_version")
        != QUALIFICATION_ASSESSMENT_SCHEMA_VERSION
    ):
        errors.append("qualification assessment schema_version is invalid")
    if not _json_exactly_equal(
        assessment.get("assessment_boundary"),
        ASSESSMENT_BOUNDARY,
    ):
        errors.append(
            "qualification assessment must preserve the non-authorizing boundary"
        )

    evidence_errors = validate_qualification_evidence(
        evidence,
        verified_bundle,
        plan,
        policy,
    )
    errors.extend(
        f"qualification evidence: {error}" for error in evidence_errors
    )
    if evidence_errors:
        return errors
    try:
        expected = build_qualification_assessment(
            verified_bundle,
            plan,
            policy,
            evidence,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return errors + [f"cannot rebuild expected qualification assessment: {exc}"]
    if not _json_exactly_equal(assessment, expected):
        errors.append(
            "qualification assessment does not exactly match its verified "
            "evidence, bundle, plan, and policy"
        )
    return errors


def qualification_assessment_for_bundle(
    evidence: Any,
    plan: Any,
    bundle: bytes,
    policy: Any,
) -> tuple[list[str], dict[str, Any] | None]:
    bundle_errors, verified = verify_factory_bundle(bundle)
    if bundle_errors or verified is None:
        return [f"factory bundle: {error}" for error in bundle_errors], None
    evidence_errors = validate_qualification_evidence(
        evidence,
        verified,
        plan,
        policy,
    )
    if evidence_errors:
        return [
            f"qualification evidence: {error}" for error in evidence_errors
        ], None
    return [], build_qualification_assessment(
        verified,
        plan,
        policy,
        evidence,
    )


def verify_qualification_assessment_for_bundle(
    assessment: Any,
    evidence: Any,
    plan: Any,
    bundle: bytes,
    policy: Any,
) -> list[str]:
    bundle_errors, verified = verify_factory_bundle(bundle)
    if bundle_errors or verified is None:
        return [f"factory bundle: {error}" for error in bundle_errors]
    return validate_qualification_assessment(
        assessment,
        evidence,
        verified,
        plan,
        policy,
    )
