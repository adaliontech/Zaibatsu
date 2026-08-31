#!/usr/bin/env python3
"""Plan deterministic validation for one bound improvement candidate."""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from factory_composer import canonical_json_bytes, load_json_file, sha256_json
from factory_improvement_candidate import (
    TARGET_ARTIFACT_TYPES,
    verify_factory_improvement_candidate_for_inputs,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_IMPROVEMENT_VALIDATION_PLAN_SPEC_PATH = (
    ROOT / "examples" / "economic-factory.improvement-validation-plan-spec.json"
)
EXAMPLE_IMPROVEMENT_VALIDATION_PLAN_PATH = (
    ROOT / "examples" / "economic-factory.improvement-validation-plan.json"
)

IMPROVEMENT_VALIDATION_PLAN_SPEC_SCHEMA_VERSION = (
    "zaibatsu.factory-improvement-validation-plan-spec.v1"
)
IMPROVEMENT_VALIDATION_PLAN_SCHEMA_VERSION = (
    "zaibatsu.factory-improvement-validation-plan.v1"
)
IMPROVEMENT_VALIDATION_PLAN_SPEC_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.16.0/schemas/factory-improvement-validation-plan-spec.schema.json"
)
IMPROVEMENT_VALIDATION_PLAN_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.16.0/schemas/factory-improvement-validation-plan.schema.json"
)

MAX_IMPROVEMENT_VALIDATION_PLAN_SPEC_BYTES = 1024 * 1024
MAX_IMPROVEMENT_VALIDATION_PLAN_BYTES = 2 * 1024 * 1024
ID_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"

SPEC_FIELDS = {
    "contract_schema",
    "schema_version",
    "plan",
    "execution_policy",
    "validation_requirements",
    "planning_boundary",
}
PLAN_SPEC_FIELDS = {"id", "summary", "candidate_id", "target", "steps"}
TARGET_FIELDS = {"kind", "id", "operation"}
STEP_FIELDS = {
    "position",
    "id",
    "kind",
    "scope",
    "requires_steps",
    "required_evidence",
}
EVIDENCE_REQUIREMENT_FIELDS = {"id", "artifact_type"}

EXPECTED_STEPS: tuple[dict[str, Any], ...] = (
    {
        "position": 0,
        "id": "content-safety-preflight",
        "kind": "content_safety_scan",
        "scope": "candidate_artifact",
        "requires_steps": [],
        "required_evidence": [
            {
                "id": "content-safety-receipt",
                "artifact_type": "deterministic_scan_receipt",
            }
        ],
    },
    {
        "position": 1,
        "id": "secret-absence-preflight",
        "kind": "secret_scan",
        "scope": "candidate_artifact",
        "requires_steps": ["content-safety-preflight"],
        "required_evidence": [
            {
                "id": "secret-absence-receipt",
                "artifact_type": "deterministic_scan_receipt",
            }
        ],
    },
    {
        "position": 2,
        "id": "contract-schema-validation",
        "kind": "schema_validation",
        "scope": "candidate_artifact",
        "requires_steps": [
            "content-safety-preflight",
            "secret-absence-preflight",
        ],
        "required_evidence": [
            {
                "id": "contract-schema-validation-receipt",
                "artifact_type": "deterministic_validation_receipt",
            }
        ],
    },
    {
        "position": 3,
        "id": "deterministic-behavior-validation",
        "kind": "deterministic_test",
        "scope": "candidate_implementation",
        "requires_steps": ["contract-schema-validation"],
        "required_evidence": [
            {
                "id": "candidate-implementation-artifact",
                "artifact_type": "content_addressed_implementation",
            },
            {
                "id": "deterministic-behavior-receipt",
                "artifact_type": "deterministic_validation_receipt",
            },
        ],
    },
    {
        "position": 4,
        "id": "reporting-factory-regression",
        "kind": "regression_test",
        "scope": "reporting_factory",
        "requires_steps": ["deterministic-behavior-validation"],
        "required_evidence": [
            {
                "id": "reporting-factory-regression-fixture",
                "artifact_type": "content_addressed_test_fixture",
            },
            {
                "id": "reporting-factory-regression-receipt",
                "artifact_type": "deterministic_validation_receipt",
            },
        ],
    },
    {
        "position": 5,
        "id": "independent-regression",
        "kind": "regression_test",
        "scope": "independent_fixture",
        "requires_steps": ["deterministic-behavior-validation"],
        "required_evidence": [
            {
                "id": "independent-regression-fixture",
                "artifact_type": "content_addressed_test_fixture",
            },
            {
                "id": "independent-regression-receipt",
                "artifact_type": "deterministic_validation_receipt",
            },
        ],
    },
    {
        "position": 6,
        "id": "rollback-validation",
        "kind": "rollback_test",
        "scope": "candidate_implementation",
        "requires_steps": [
            "reporting-factory-regression",
            "independent-regression",
        ],
        "required_evidence": [
            {
                "id": "rollback-plan",
                "artifact_type": "content_addressed_rollback_plan",
            },
            {
                "id": "rollback-validation-receipt",
                "artifact_type": "deterministic_validation_receipt",
            },
        ],
    },
    {
        "position": 7,
        "id": "cross-factory-privilege-review",
        "kind": "privilege_review",
        "scope": "closed_portfolio",
        "requires_steps": [
            "reporting-factory-regression",
            "independent-regression",
        ],
        "required_evidence": [
            {
                "id": "cross-factory-privilege-review-receipt",
                "artifact_type": "deterministic_policy_receipt",
            }
        ],
    },
)

EXPECTED_EXECUTION_POLICY = {
    "planning_only": True,
    "isolated_workspace_required": True,
    "network_access_allowed": False,
    "production_credentials_allowed": False,
    "production_state_access_allowed": False,
    "model_output_accepted_as_verification": False,
    "content_addressed_evidence_required": True,
    "explicit_authorization_required_before_execution": True,
    "overwrite_existing_artifacts": False,
}

EXPECTED_VALIDATION_REQUIREMENTS = {
    "candidate_chain_reverification_required": True,
    "candidate_identity_alignment_required": True,
    "candidate_target_alignment_required": True,
    "candidate_behavior_checks_bound": True,
    "content_safety_preflight_required": True,
    "secret_absence_preflight_required": True,
    "contract_schema_validation_required": True,
    "candidate_implementation_required": True,
    "deterministic_behavior_validation_required": True,
    "reporting_factory_regression_required": True,
    "independent_regression_required": True,
    "rollback_validation_required": True,
    "cross_factory_privilege_review_required": True,
}

EXPECTED_SPEC_BOUNDARY = {
    "candidate_artifact_untrusted": True,
    "planning_contract_only": True,
    "contains_executable_commands": False,
    "candidate_implementation_present": False,
    "validation_plan_created": False,
    "validation_execution_authorized": False,
    "validation_executed": False,
    "reporting_factory_validation_passed": False,
    "independent_regression_validation_passed": False,
    "rollback_plan_verified": False,
    "cross_factory_privilege_review_passed": False,
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
    "validation_steps",
    "missing_evidence",
    "planning_checks",
    "summary",
    "planning_boundary",
    "factory_improvement_validation_plan_sha256",
}
RECORD_OBJECT_FIELDS = {"source", "candidate", "summary", "planning_boundary"}
CHECK_IDS = (
    "candidate_chain_reverified",
    "candidate_identity_aligned",
    "validation_profile_preserved",
    "missing_evidence_enumerated",
    "non_executing_plan",
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


def _validate_target(target: Any) -> list[str]:
    if not isinstance(target, dict) or set(target) != TARGET_FIELDS:
        return ["improvement validation-plan target must contain exactly kind, id, operation"]
    if target.get("kind") not in TARGET_ARTIFACT_TYPES:
        return ["improvement validation-plan target kind is unsupported"]
    if not _valid_id(target.get("id")):
        return ["improvement validation-plan target id must be lowercase kebab-case"]
    if target.get("operation") not in {"add", "modify", "replace"}:
        return ["improvement validation-plan target operation is unsupported"]
    return []


def load_factory_improvement_validation_plan_spec(
    path: Path = EXAMPLE_IMPROVEMENT_VALIDATION_PLAN_SPEC_PATH,
) -> Any:
    return load_json_file(path)


def load_factory_improvement_validation_plan(
    path: Path = EXAMPLE_IMPROVEMENT_VALIDATION_PLAN_PATH,
) -> Any:
    return load_json_file(path)


def validate_factory_improvement_validation_plan_spec(
    specification: Any,
) -> list[str]:
    """Validate a fixed, non-executable validation-planning contract."""
    errors: list[str] = []
    if not isinstance(specification, dict):
        return [
            "factory improvement validation-plan specification root must be an object"
        ]
    if set(specification) != SPEC_FIELDS:
        errors.append(
            "factory improvement validation-plan specification must contain "
            "exactly the versioned fields"
        )
    if (
        specification.get("contract_schema")
        != IMPROVEMENT_VALIDATION_PLAN_SPEC_SCHEMA_REFERENCE
    ):
        errors.append(
            "factory improvement validation-plan specification must reference its immutable schema"
        )
    if (
        specification.get("schema_version")
        != IMPROVEMENT_VALIDATION_PLAN_SPEC_SCHEMA_VERSION
    ):
        errors.append(
            "factory improvement validation-plan specification schema_version is invalid"
        )
    plan = specification.get("plan")
    if not isinstance(plan, dict) or set(plan) != PLAN_SPEC_FIELDS:
        errors.append(
            "factory improvement validation-plan specification plan fields are invalid"
        )
    else:
        if not _valid_id(plan.get("id")):
            errors.append("factory improvement validation-plan id must be lowercase kebab-case")
        if not _valid_text(plan.get("summary"), 512):
            errors.append("factory improvement validation-plan summary is invalid")
        if not _valid_id(plan.get("candidate_id")):
            errors.append("factory improvement validation-plan candidate_id is invalid")
        errors.extend(_validate_target(plan.get("target")))
        if not _canonical_equal(plan.get("steps"), EXPECTED_STEPS):
            errors.append(
                "factory improvement validation-plan must preserve the canonical validation stages"
            )
    if not _canonical_equal(
        specification.get("execution_policy"), EXPECTED_EXECUTION_POLICY
    ):
        errors.append(
            "factory improvement validation-plan execution policy must remain "
            "isolated and non-executing"
        )
    if not _canonical_equal(
        specification.get("validation_requirements"),
        EXPECTED_VALIDATION_REQUIREMENTS,
    ):
        errors.append(
            "factory improvement validation-plan must preserve every validation requirement"
        )
    if not _canonical_equal(
        specification.get("planning_boundary"), EXPECTED_SPEC_BOUNDARY
    ):
        errors.append(
            "factory improvement validation-plan specification boundary must remain "
            "non-authorizing"
        )
    try:
        canonical_size = len(canonical_json_bytes(specification))
    except (RecursionError, TypeError, ValueError):
        errors.append(
            "factory improvement validation-plan specification must be canonical JSON data"
        )
    else:
        if not 0 < canonical_size <= MAX_IMPROVEMENT_VALIDATION_PLAN_SPEC_BYTES:
            errors.append(
                "factory improvement validation-plan specification size is outside "
                "the accepted boundary"
            )
    return errors


def _precheck_factory_improvement_validation_plan(record: Any) -> list[str]:
    if not isinstance(record, dict):
        return ["factory improvement validation-plan root must be an object"]
    if set(record) != RECORD_FIELDS:
        return ["factory improvement validation-plan must contain exactly the versioned fields"]
    if record.get("contract_schema") != IMPROVEMENT_VALIDATION_PLAN_SCHEMA_REFERENCE:
        return ["factory improvement validation-plan must reference its immutable schema"]
    if record.get("schema_version") != IMPROVEMENT_VALIDATION_PLAN_SCHEMA_VERSION:
        return ["factory improvement validation-plan schema_version is invalid"]
    if any(not isinstance(record.get(field), dict) for field in RECORD_OBJECT_FIELDS):
        return ["factory improvement validation-plan sections must be objects"]
    if any(
        not isinstance(record.get(field), list)
        for field in ("validation_steps", "missing_evidence", "planning_checks")
    ):
        return ["factory improvement validation-plan ordered sections must be lists"]
    try:
        canonical_size = len(canonical_json_bytes(record))
    except (RecursionError, TypeError, ValueError):
        return ["factory improvement validation-plan must be canonical JSON data"]
    if not 0 < canonical_size <= MAX_IMPROVEMENT_VALIDATION_PLAN_BYTES:
        return ["factory improvement validation-plan size is outside the accepted boundary"]
    recorded_digest = record.get("factory_improvement_validation_plan_sha256")
    if (
        not isinstance(recorded_digest, str)
        or len(recorded_digest) != 64
        or any(character not in "0123456789abcdef" for character in recorded_digest)
    ):
        return ["factory improvement validation-plan digest must be lowercase SHA-256"]
    without_digest = dict(record)
    without_digest.pop("factory_improvement_validation_plan_sha256")
    if sha256_json(without_digest) != recorded_digest:
        return ["factory improvement validation-plan digest does not match its content"]
    return []


def _planning_boundary() -> dict[str, Any]:
    return {
        "candidate_chain_reverified": True,
        "validation_plan_specification_validated": True,
        "candidate_identity_aligned": True,
        "candidate_target_aligned": True,
        "candidate_artifact_bound": True,
        "candidate_behavior_checks_bound": True,
        "validation_steps_canonically_ordered": True,
        "required_evidence_enumerated": True,
        "validation_plan_created": True,
        "candidate_implementation_bound": False,
        "content_safety_scanned": False,
        "secret_absence_proved": False,
        "artifact_semantic_truth_verified": False,
        "validation_execution_authorized": False,
        "validation_executed": False,
        "reporting_factory_validation_passed": False,
        "independent_regression_validation_passed": False,
        "rollback_plan_verified": False,
        "cross_factory_privilege_review_passed": False,
        "owner_policy_approval_obtained": False,
        "changes_shared_policy": False,
        "shared_promotion_eligible": False,
        "promotion_authorized": False,
        "rollout_authorized": False,
        "activation_authorized": False,
        "execution_authorized": False,
        "cross_factory_effects_authorized": False,
    }


def build_factory_improvement_validation_plan(
    specification: dict[str, Any],
    candidate: dict[str, Any],
    candidate_specification: dict[str, Any],
) -> dict[str, Any]:
    """Bind a deterministic, non-executing validation plan to one candidate."""
    plan = specification["plan"]
    bound_candidate = candidate["candidate"]
    if plan["candidate_id"] != bound_candidate["id"]:
        raise ValueError("validation-plan candidate id does not match bound candidate")
    if not _canonical_equal(plan["target"], bound_candidate["target"]):
        raise ValueError("validation-plan target does not match bound candidate")
    artifact = candidate_specification["candidate"]["artifact"]
    behavior_check_ids = [check["id"] for check in artifact["behavior"]["checks"]]
    validation_steps = [
        {
            **deepcopy(step),
            "candidate_behavior_check_ids": (
                deepcopy(behavior_check_ids)
                if step["id"] == "deterministic-behavior-validation"
                else []
            ),
            "status": "not_run",
            "grants_authority": False,
        }
        for step in plan["steps"]
    ]
    missing_evidence: list[dict[str, Any]] = []
    for step in plan["steps"]:
        for requirement in step["required_evidence"]:
            missing_evidence.append(
                {
                    "position": len(missing_evidence),
                    "id": requirement["id"],
                    "stage_id": step["id"],
                    "artifact_type": requirement["artifact_type"],
                    "status": "missing",
                }
            )
    record_without_digest: dict[str, Any] = {
        "contract_schema": IMPROVEMENT_VALIDATION_PLAN_SCHEMA_REFERENCE,
        "schema_version": IMPROVEMENT_VALIDATION_PLAN_SCHEMA_VERSION,
        "source": {
            "validation_plan_specification_sha256": sha256_json(specification),
            "factory_improvement_candidate_sha256": candidate[
                "factory_improvement_candidate_sha256"
            ],
            "candidate_specification_sha256": candidate["source"][
                "candidate_specification_sha256"
            ],
            "candidate_artifact_sha256": candidate["source"][
                "candidate_artifact_sha256"
            ],
            "factory_improvement_classification_sha256": candidate["source"][
                "factory_improvement_classification_sha256"
            ],
            "factory_improvement_proposal_sha256": candidate["source"][
                "factory_improvement_proposal_sha256"
            ],
            "factory_improvement_observation_sha256": candidate["source"][
                "factory_improvement_observation_sha256"
            ],
            "factory_evidence_return_sha256": candidate["source"][
                "factory_evidence_return_sha256"
            ],
            "reporting_factory": candidate["source"]["reporting_factory"],
            "control_factory": candidate["source"]["control_factory"],
        },
        "candidate": {
            "id": bound_candidate["id"],
            "target": deepcopy(bound_candidate["target"]),
            "artifact_id": bound_candidate["artifact_id"],
            "artifact_type": bound_candidate["artifact_type"],
            "artifact_sha256": bound_candidate["artifact_sha256"],
            "artifact_canonical_bytes": bound_candidate[
                "artifact_canonical_bytes"
            ],
            "behavior_check_ids": deepcopy(behavior_check_ids),
        },
        "validation_steps": validation_steps,
        "missing_evidence": missing_evidence,
        "planning_checks": [
            {
                "position": 0,
                "id": CHECK_IDS[0],
                "status": "passed",
                "reason": "candidate_and_complete_evidence_chain_reverified",
            },
            {
                "position": 1,
                "id": CHECK_IDS[1],
                "status": "passed",
                "reason": "plan_candidate_id_and_target_match_bound_candidate",
            },
            {
                "position": 2,
                "id": CHECK_IDS[2],
                "status": "passed",
                "reason": "canonical_validation_stages_and_policy_preserved",
            },
            {
                "position": 3,
                "id": CHECK_IDS[3],
                "status": "passed",
                "reason": "all_required_validation_evidence_recorded_missing",
            },
            {
                "position": 4,
                "id": CHECK_IDS[4],
                "status": "passed",
                "reason": "plan_contains_no_commands_and_grants_no_authority",
            },
        ],
        "summary": {
            "validation_step_count": len(validation_steps),
            "required_evidence_count": len(missing_evidence),
            "missing_evidence_count": len(missing_evidence),
            "executed_steps": 0,
            "passed_steps": 0,
            "failed_steps": 0,
            "candidate_implementation_bound": False,
            "ready_for_validation_execution": False,
            "validation_execution_authorized": False,
        },
        "planning_boundary": _planning_boundary(),
    }
    record = dict(record_without_digest)
    record["factory_improvement_validation_plan_sha256"] = sha256_json(
        record_without_digest
    )
    return record


def factory_improvement_validation_plan_for_inputs(
    specification: Any,
    candidate: Any,
    candidate_specification: Any,
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
    specification_errors = validate_factory_improvement_validation_plan_spec(
        specification
    )
    if specification_errors:
        return specification_errors, None
    candidate_errors = verify_factory_improvement_candidate_for_inputs(
        candidate,
        candidate_specification,
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
    if candidate_errors:
        return [
            f"improvement validation-plan candidate: {error}"
            for error in candidate_errors
        ], None
    assert isinstance(specification, dict)
    assert isinstance(candidate, dict)
    assert isinstance(candidate_specification, dict)
    try:
        record = build_factory_improvement_validation_plan(
            specification,
            candidate,
            candidate_specification,
        )
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot build factory improvement validation-plan: {exc}"], None
    return [], record


def verify_factory_improvement_validation_plan_for_inputs(
    record: Any,
    specification: Any,
    candidate: Any,
    candidate_specification: Any,
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
    precheck_errors = _precheck_factory_improvement_validation_plan(record)
    if precheck_errors:
        return precheck_errors
    errors, expected = factory_improvement_validation_plan_for_inputs(
        specification,
        candidate,
        candidate_specification,
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
            "factory improvement validation-plan must exactly match its "
            "specification, bound candidate, and complete verified evidence chain"
        ]
    return []
