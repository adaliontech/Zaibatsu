#!/usr/bin/env python3
"""Bind one exact, non-executable improvement candidate to its evidence chain."""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from factory_composer import canonical_json_bytes, load_json_file, sha256_json
from factory_improvement_classification import (
    verify_factory_improvement_classification_for_inputs,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_IMPROVEMENT_CANDIDATE_SPEC_PATH = (
    ROOT / "examples" / "economic-factory.improvement-candidate-spec.json"
)
EXAMPLE_IMPROVEMENT_CANDIDATE_PATH = (
    ROOT / "examples" / "economic-factory.improvement-candidate.json"
)

IMPROVEMENT_CANDIDATE_SPEC_SCHEMA_VERSION = (
    "zaibatsu.factory-improvement-candidate-spec.v1"
)
IMPROVEMENT_CANDIDATE_SCHEMA_VERSION = (
    "zaibatsu.factory-improvement-candidate.v1"
)
IMPROVEMENT_CANDIDATE_SPEC_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.15.0/schemas/factory-improvement-candidate-spec.schema.json"
)
IMPROVEMENT_CANDIDATE_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.15.0/schemas/factory-improvement-candidate.schema.json"
)

MAX_IMPROVEMENT_CANDIDATE_SPEC_BYTES = 1024 * 1024
MAX_IMPROVEMENT_CANDIDATE_BYTES = 2 * 1024 * 1024
MAX_CANDIDATE_ARTIFACT_BYTES = 512 * 1024
ID_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"

TARGET_ARTIFACT_TYPES = {
    "shared_module": "shared_module_contract",
    "factory_template": "factory_template_contract",
    "deterministic_gate": "deterministic_gate_contract",
}

SPEC_FIELDS = {
    "contract_schema",
    "schema_version",
    "candidate",
    "binding_requirements",
    "candidate_boundary",
}
CANDIDATE_SPEC_FIELDS = {"id", "summary", "artifact"}
ARTIFACT_FIELDS = {
    "artifact_id",
    "artifact_type",
    "target",
    "interface",
    "behavior",
    "authority_boundary",
}
TARGET_FIELDS = {"kind", "id", "operation"}
INTERFACE_FIELDS = {"input_contract", "output_contract", "deterministic"}
BEHAVIOR_FIELDS = {"summary", "checks", "failure_mode"}
BEHAVIOR_CHECK_FIELDS = {"position", "id", "description"}

EXPECTED_BINDING_REQUIREMENTS = {
    "classification_reverification_required": True,
    "target_alignment_required": True,
    "canonical_artifact_required": True,
    "content_safety_required_before_validation_execution": True,
    "semantic_validation_required_before_promotion": True,
    "reporting_factory_regression_required": True,
    "independent_regression_required": True,
    "rollback_required": True,
    "owner_policy_approval_required": True,
    "cross_factory_privilege_review_required": True,
}
EXPECTED_ARTIFACT_AUTHORITY_BOUNDARY = {
    "contract_only": True,
    "contains_executable_implementation": False,
    "reads_secrets": False,
    "invokes_models": False,
    "mutates_state": False,
    "executes_operations": False,
    "grants_authority": False,
}
EXPECTED_CANDIDATE_BOUNDARY = {
    "candidate_artifact_untrusted": True,
    "contains_candidate_contract": True,
    "content_safety_scanned": False,
    "secret_absence_proved": False,
    "artifact_semantic_truth_verified": False,
    "candidate_implementation_present": False,
    "validation_plan_created": False,
    "validation_execution_authorized": False,
    "reporting_factory_validation_passed": False,
    "independent_regression_validation_passed": False,
    "rollback_plan_verified": False,
    "owner_policy_approval_obtained": False,
    "shared_promotion_eligible": False,
    "promotion_authorized": False,
    "rollout_authorized": False,
    "activation_authorized": False,
    "execution_authorized": False,
    "cross_factory_effects_authorized": False,
}

RECORD_FIELDS = {
    "contract_schema",
    "schema_version",
    "source",
    "candidate",
    "binding_checks",
    "binding_boundary",
    "factory_improvement_candidate_sha256",
}
RECORD_OBJECT_FIELDS = {"source", "candidate", "binding_boundary"}
CHECK_IDS = (
    "classification_eligible",
    "target_aligned",
    "artifact_structurally_valid",
    "review_requirements_preserved",
    "non_authorizing_candidate",
)


def _canonical_equal(left: Any, right: Any) -> bool:
    try:
        return canonical_json_bytes(left) == canonical_json_bytes(right)
    except (RecursionError, TypeError, ValueError):
        return False


def _valid_id(value: Any) -> bool:
    return (
        isinstance(value, str)
        and 0 < len(value) <= 64
        and re.fullmatch(ID_PATTERN, value) is not None
    )


def _valid_text(value: Any, maximum: int) -> bool:
    return isinstance(value, str) and value == value.strip() and 0 < len(value) <= maximum


def _valid_id_list(value: Any, *, maximum: int = 32) -> bool:
    return (
        isinstance(value, list)
        and 0 < len(value) <= maximum
        and all(_valid_id(item) for item in value)
        and len(set(value)) == len(value)
    )


def load_factory_improvement_candidate_spec(
    path: Path = EXAMPLE_IMPROVEMENT_CANDIDATE_SPEC_PATH,
) -> Any:
    return load_json_file(path)


def load_factory_improvement_candidate(
    path: Path = EXAMPLE_IMPROVEMENT_CANDIDATE_PATH,
) -> Any:
    return load_json_file(path)


def _validate_target(target: Any) -> list[str]:
    if not isinstance(target, dict) or set(target) != TARGET_FIELDS:
        return ["improvement candidate target must contain exactly kind, id, operation"]
    if target.get("kind") not in TARGET_ARTIFACT_TYPES:
        return ["improvement candidate target kind is unsupported"]
    if not _valid_id(target.get("id")):
        return ["improvement candidate target id must be lowercase kebab-case"]
    if target.get("operation") not in {"add", "modify", "replace"}:
        return ["improvement candidate target operation is unsupported"]
    return []


def _validate_candidate_artifact(artifact: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(artifact, dict) or set(artifact) != ARTIFACT_FIELDS:
        return ["improvement candidate artifact must contain exactly the typed fields"]
    if not _valid_id(artifact.get("artifact_id")):
        errors.append("improvement candidate artifact_id must be lowercase kebab-case")
    target = artifact.get("target")
    errors.extend(_validate_target(target))
    if isinstance(target, dict):
        target_kind = target.get("kind")
        expected_type = (
            TARGET_ARTIFACT_TYPES.get(target_kind)
            if isinstance(target_kind, str)
            else None
        )
        if artifact.get("artifact_type") != expected_type:
            errors.append("improvement candidate artifact type must match its target kind")
    interface = artifact.get("interface")
    if not isinstance(interface, dict) or set(interface) != INTERFACE_FIELDS:
        errors.append("improvement candidate interface must contain exactly the typed fields")
    else:
        if not _valid_id_list(interface.get("input_contract")):
            errors.append("improvement candidate input contract must be a unique ID list")
        if not _valid_id_list(interface.get("output_contract")):
            errors.append("improvement candidate output contract must be a unique ID list")
        if interface.get("deterministic") is not True:
            errors.append("improvement candidate interface must remain deterministic")
    behavior = artifact.get("behavior")
    if not isinstance(behavior, dict) or set(behavior) != BEHAVIOR_FIELDS:
        errors.append("improvement candidate behavior must contain exactly the typed fields")
    else:
        if not _valid_text(behavior.get("summary"), 512):
            errors.append("improvement candidate behavior summary is invalid")
        checks = behavior.get("checks")
        if not isinstance(checks, list) or not 0 < len(checks) <= 32:
            errors.append("improvement candidate behavior checks must be a bounded list")
        else:
            check_ids: list[str] = []
            for position, check in enumerate(checks):
                if not isinstance(check, dict) or set(check) != BEHAVIOR_CHECK_FIELDS:
                    errors.append("improvement candidate behavior check has invalid fields")
                    continue
                if check.get("position") != position:
                    errors.append("improvement candidate behavior checks must be canonically ordered")
                if not _valid_id(check.get("id")):
                    errors.append("improvement candidate behavior check id is invalid")
                else:
                    check_ids.append(check["id"])
                if not _valid_text(check.get("description"), 512):
                    errors.append("improvement candidate behavior check description is invalid")
            if len(check_ids) != len(set(check_ids)):
                errors.append("improvement candidate behavior check ids must be unique")
        if behavior.get("failure_mode") != "deny":
            errors.append("improvement candidate behavior must fail closed")
    if not _canonical_equal(
        artifact.get("authority_boundary"),
        EXPECTED_ARTIFACT_AUTHORITY_BOUNDARY,
    ):
        errors.append("improvement candidate artifact boundary must remain contract-only and non-authorizing")
    try:
        artifact_size = len(canonical_json_bytes(artifact))
    except (RecursionError, TypeError, ValueError):
        errors.append("improvement candidate artifact must be canonical JSON data")
    else:
        if not 0 < artifact_size <= MAX_CANDIDATE_ARTIFACT_BYTES:
            errors.append("improvement candidate artifact size is outside the accepted boundary")
    return errors


def validate_factory_improvement_candidate_spec(specification: Any) -> list[str]:
    """Validate exact candidate contract bytes without trusting their semantics."""
    errors: list[str] = []
    if not isinstance(specification, dict):
        return ["factory improvement-candidate specification root must be an object"]
    if set(specification) != SPEC_FIELDS:
        errors.append("factory improvement-candidate specification must contain exactly the versioned fields")
    if specification.get("contract_schema") != IMPROVEMENT_CANDIDATE_SPEC_SCHEMA_REFERENCE:
        errors.append("factory improvement-candidate specification must reference its immutable schema")
    if specification.get("schema_version") != IMPROVEMENT_CANDIDATE_SPEC_SCHEMA_VERSION:
        errors.append("factory improvement-candidate specification schema_version is invalid")
    candidate = specification.get("candidate")
    if not isinstance(candidate, dict) or set(candidate) != CANDIDATE_SPEC_FIELDS:
        errors.append("factory improvement-candidate specification candidate fields are invalid")
    else:
        if not _valid_id(candidate.get("id")):
            errors.append("factory improvement-candidate id must be lowercase kebab-case")
        if not _valid_text(candidate.get("summary"), 512):
            errors.append("factory improvement-candidate summary is invalid")
        artifact = candidate.get("artifact")
        errors.extend(_validate_candidate_artifact(artifact))
    if not _canonical_equal(
        specification.get("binding_requirements"),
        EXPECTED_BINDING_REQUIREMENTS,
    ):
        errors.append("factory improvement-candidate must preserve every later review requirement")
    if not _canonical_equal(
        specification.get("candidate_boundary"),
        EXPECTED_CANDIDATE_BOUNDARY,
    ):
        errors.append("factory improvement-candidate boundary must remain untrusted and non-authorizing")
    try:
        canonical_size = len(canonical_json_bytes(specification))
    except (RecursionError, TypeError, ValueError):
        errors.append("factory improvement-candidate specification must be canonical JSON data")
    else:
        if not 0 < canonical_size <= MAX_IMPROVEMENT_CANDIDATE_SPEC_BYTES:
            errors.append("factory improvement-candidate specification size is outside the accepted boundary")
    return errors


def _precheck_factory_improvement_candidate(record: Any) -> list[str]:
    if not isinstance(record, dict):
        return ["factory improvement-candidate root must be an object"]
    if set(record) != RECORD_FIELDS:
        return ["factory improvement-candidate must contain exactly the versioned fields"]
    if record.get("contract_schema") != IMPROVEMENT_CANDIDATE_SCHEMA_REFERENCE:
        return ["factory improvement-candidate must reference its immutable schema"]
    if record.get("schema_version") != IMPROVEMENT_CANDIDATE_SCHEMA_VERSION:
        return ["factory improvement-candidate schema_version is invalid"]
    if any(not isinstance(record.get(field), dict) for field in RECORD_OBJECT_FIELDS):
        return ["factory improvement-candidate sections must be objects"]
    if not isinstance(record.get("binding_checks"), list):
        return ["factory improvement-candidate binding_checks must be a list"]
    try:
        canonical_size = len(canonical_json_bytes(record))
    except (RecursionError, TypeError, ValueError):
        return ["factory improvement-candidate must be canonical JSON data"]
    if not 0 < canonical_size <= MAX_IMPROVEMENT_CANDIDATE_BYTES:
        return ["factory improvement-candidate size is outside the accepted boundary"]
    recorded_digest = record.get("factory_improvement_candidate_sha256")
    if (
        not isinstance(recorded_digest, str)
        or len(recorded_digest) != 64
        or any(character not in "0123456789abcdef" for character in recorded_digest)
    ):
        return ["factory improvement-candidate digest must be lowercase SHA-256"]
    without_digest = dict(record)
    without_digest.pop("factory_improvement_candidate_sha256")
    if sha256_json(without_digest) != recorded_digest:
        return ["factory improvement-candidate digest does not match its content"]
    return []


def _binding_boundary() -> dict[str, Any]:
    return {
        "classification_chain_reverified": True,
        "candidate_specification_validated": True,
        "candidate_artifact_structurally_validated": True,
        "candidate_target_aligned": True,
        "candidate_artifact_canonical_json_bound": True,
        "candidate_artifact_bound": True,
        "content_safety_scanned": False,
        "secret_absence_proved": False,
        "artifact_semantic_truth_verified": False,
        "candidate_implementation_present": False,
        "validation_plan_created": False,
        "validation_execution_authorized": False,
        "reporting_factory_validation_passed": False,
        "independent_regression_validation_passed": False,
        "rollback_plan_verified": False,
        "owner_policy_approval_obtained": False,
        "changes_shared_policy": False,
        "shared_promotion_eligible": False,
        "promotion_authorized": False,
        "rollout_authorized": False,
        "activation_authorized": False,
        "execution_authorized": False,
        "cross_factory_effects_authorized": False,
    }


def build_factory_improvement_candidate(
    specification: dict[str, Any],
    classification: dict[str, Any],
) -> dict[str, Any]:
    """Bind one exact candidate contract to one eligible classification."""
    classified = classification["classification"]
    if classified["eligible_for_validation_planning"] is not True:
        raise ValueError("improvement classification is not eligible for candidate binding")
    artifact = specification["candidate"]["artifact"]
    if not _canonical_equal(artifact["target"], classified["target"]):
        raise ValueError("candidate artifact target does not match classification target")
    artifact_sha256 = sha256_json(artifact)
    artifact_size = len(canonical_json_bytes(artifact))
    record_without_digest: dict[str, Any] = {
        "contract_schema": IMPROVEMENT_CANDIDATE_SCHEMA_REFERENCE,
        "schema_version": IMPROVEMENT_CANDIDATE_SCHEMA_VERSION,
        "source": {
            "candidate_specification_sha256": sha256_json(specification),
            "candidate_artifact_sha256": artifact_sha256,
            "factory_improvement_classification_sha256": classification[
                "factory_improvement_classification_sha256"
            ],
            "factory_improvement_proposal_sha256": classification["source"][
                "factory_improvement_proposal_sha256"
            ],
            "factory_improvement_observation_sha256": classification["source"][
                "factory_improvement_observation_sha256"
            ],
            "factory_evidence_return_sha256": classification["source"][
                "factory_evidence_return_sha256"
            ],
            "reporting_factory": classification["source"]["reporting_factory"],
            "control_factory": classification["source"]["control_factory"],
        },
        "candidate": {
            "id": specification["candidate"]["id"],
            "target": deepcopy(artifact["target"]),
            "artifact_id": artifact["artifact_id"],
            "artifact_type": artifact["artifact_type"],
            "artifact_sha256": artifact_sha256,
            "artifact_canonical_bytes": artifact_size,
        },
        "binding_checks": [
            {
                "position": 0,
                "id": CHECK_IDS[0],
                "status": "passed",
                "reason": "classification_is_eligible_for_validation_planning",
            },
            {
                "position": 1,
                "id": CHECK_IDS[1],
                "status": "passed",
                "reason": "candidate_target_matches_classification_target",
            },
            {
                "position": 2,
                "id": CHECK_IDS[2],
                "status": "passed",
                "reason": "candidate_contract_structure_is_valid",
            },
            {
                "position": 3,
                "id": CHECK_IDS[3],
                "status": "passed",
                "reason": "all_later_review_requirements_preserved",
            },
            {
                "position": 4,
                "id": CHECK_IDS[4],
                "status": "passed",
                "reason": "candidate_contract_grants_no_authority",
            },
        ],
        "binding_boundary": _binding_boundary(),
    }
    record = dict(record_without_digest)
    record["factory_improvement_candidate_sha256"] = sha256_json(record_without_digest)
    return record


def factory_improvement_candidate_for_inputs(
    specification: Any,
    classification: Any,
    classification_policy: Any,
    proposal: Any,
    proposal_specification: Any,
    observation: Any,
    observation_specification: Any,
    evidence_return: Any,
    plan: Any,
    portfolio: Any,
    bundle_values: Any,
    source_factory_id: Any,
    runtime_evidence_pack: Any,
    qualification_plan: Any,
    qualification_policy: Any,
) -> tuple[list[str], dict[str, Any] | None]:
    specification_errors = validate_factory_improvement_candidate_spec(specification)
    if specification_errors:
        return specification_errors, None
    classification_errors = verify_factory_improvement_classification_for_inputs(
        classification,
        classification_policy,
        proposal,
        proposal_specification,
        observation,
        observation_specification,
        evidence_return,
        plan,
        portfolio,
        bundle_values,
        source_factory_id,
        runtime_evidence_pack,
        qualification_plan,
        qualification_policy,
    )
    if classification_errors:
        return [
            f"improvement candidate classification: {error}"
            for error in classification_errors
        ], None
    assert isinstance(specification, dict)
    assert isinstance(classification, dict)
    try:
        record = build_factory_improvement_candidate(specification, classification)
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot build factory improvement-candidate: {exc}"], None
    return [], record


def verify_factory_improvement_candidate_for_inputs(
    record: Any,
    specification: Any,
    classification: Any,
    classification_policy: Any,
    proposal: Any,
    proposal_specification: Any,
    observation: Any,
    observation_specification: Any,
    evidence_return: Any,
    plan: Any,
    portfolio: Any,
    bundle_values: Any,
    source_factory_id: Any,
    runtime_evidence_pack: Any,
    qualification_plan: Any,
    qualification_policy: Any,
) -> list[str]:
    precheck_errors = _precheck_factory_improvement_candidate(record)
    if precheck_errors:
        return precheck_errors
    errors, expected = factory_improvement_candidate_for_inputs(
        specification,
        classification,
        classification_policy,
        proposal,
        proposal_specification,
        observation,
        observation_specification,
        evidence_return,
        plan,
        portfolio,
        bundle_values,
        source_factory_id,
        runtime_evidence_pack,
        qualification_plan,
        qualification_policy,
    )
    if errors or expected is None:
        return errors
    if not _canonical_equal(record, expected):
        return [
            "factory improvement-candidate must exactly match its specification, "
            "eligible classification, and complete verified evidence chain"
        ]
    return []
