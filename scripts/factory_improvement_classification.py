#!/usr/bin/env python3
"""Classify an observation/proposal pair for validation planning only."""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from factory_composer import canonical_json_bytes, load_json_file, sha256_json
from factory_improvement_observation import (
    EXPECTED_NORMALIZATION_REQUIREMENTS,
    EXPECTED_OBSERVATION_BOUNDARY,
    verify_factory_improvement_observation_for_inputs,
)
from factory_improvement_proposal import (
    EXPECTED_PROPOSAL_BOUNDARY,
    EXPECTED_VALIDATION_REQUIREMENTS,
    verify_factory_improvement_proposal_for_inputs,
)


ROOT = Path(__file__).resolve().parents[1]
IMPROVEMENT_CLASSIFICATION_POLICY_PATH = (
    ROOT / "policies" / "improvement-classification-v1.json"
)
EXAMPLE_IMPROVEMENT_CLASSIFICATION_PATH = (
    ROOT / "examples" / "economic-factory.improvement-classification.json"
)

IMPROVEMENT_CLASSIFICATION_POLICY_SCHEMA_VERSION = (
    "zaibatsu.improvement-classification-policy.v1"
)
IMPROVEMENT_CLASSIFICATION_SCHEMA_VERSION = (
    "zaibatsu.factory-improvement-classification.v1"
)
IMPROVEMENT_CLASSIFICATION_POLICY_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.14.0/schemas/improvement-classification-policy.schema.json"
)
IMPROVEMENT_CLASSIFICATION_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.14.0/schemas/factory-improvement-classification.schema.json"
)

MAX_IMPROVEMENT_CLASSIFICATION_POLICY_BYTES = 128 * 1024
MAX_IMPROVEMENT_CLASSIFICATION_BYTES = 2 * 1024 * 1024
ID_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
OBSERVATION_KIND_ORDER = (
    "failure",
    "artifact_outcome",
    "correction",
    "observation",
)
OPERATION_ORDER = ("add", "modify", "replace")
TARGET_CLASSIFICATIONS = (
    {
        "position": 0,
        "target_kind": "shared_module",
        "candidate_class": "shared_module_candidate",
    },
    {
        "position": 1,
        "target_kind": "factory_template",
        "candidate_class": "factory_template_candidate",
    },
    {
        "position": 2,
        "target_kind": "deterministic_gate",
        "candidate_class": "deterministic_gate_candidate",
    },
)

POLICY_FIELDS = {
    "contract_schema",
    "schema_version",
    "policy_id",
    "classification_rules",
    "decision_boundary",
}
RULE_FIELDS = {
    "accepted_observation_kinds",
    "accepted_operations",
    "target_classifications",
    "require_same_evidence_return",
    "require_subject_target_match",
    "require_complete_review_requirements",
    "require_non_authorizing_inputs",
}
EXPECTED_DECISION_BOUNDARY = {
    "classification_scope": "validation_planning_only",
    "content_safety_required_before_validation_execution": True,
    "semantic_evidence_required_before_promotion": True,
    "owner_approval_required_before_promotion": True,
    "rollback_required_before_rollout": True,
    "policy_grants_mutation_authority": False,
    "policy_grants_promotion_authority": False,
    "policy_grants_execution_authority": False,
    "policy_grants_cross_factory_authority": False,
}

CLASSIFICATION_FIELDS = {
    "contract_schema",
    "schema_version",
    "source",
    "classification",
    "classification_boundary",
    "factory_improvement_classification_sha256",
}
CLASSIFICATION_OBJECT_FIELDS = {
    "source",
    "classification",
    "classification_boundary",
}
CHECK_IDS = (
    "same_evidence_return",
    "subject_target_match",
    "observation_kind_allowed",
    "target_operation_allowed",
    "review_requirements_preserved",
    "non_authorizing_inputs",
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


def _valid_ordered_subset(value: Any, complete_order: tuple[str, ...]) -> bool:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) for item in value)
        or len(set(value)) != len(value)
    ):
        return False
    return value == [item for item in complete_order if item in value]


def load_improvement_classification_policy(
    path: Path = IMPROVEMENT_CLASSIFICATION_POLICY_PATH,
) -> Any:
    return load_json_file(path)


def load_factory_improvement_classification(
    path: Path = EXAMPLE_IMPROVEMENT_CLASSIFICATION_PATH,
) -> Any:
    return load_json_file(path)


def validate_improvement_classification_policy(policy: Any) -> list[str]:
    """Validate a policy that may classify only for validation planning."""
    errors: list[str] = []
    if not isinstance(policy, dict):
        return ["improvement classification policy root must be an object"]
    if set(policy) != POLICY_FIELDS:
        errors.append(
            "improvement classification policy must contain exactly the "
            "versioned fields"
        )
    if (
        policy.get("contract_schema")
        != IMPROVEMENT_CLASSIFICATION_POLICY_SCHEMA_REFERENCE
    ):
        errors.append(
            "improvement classification policy must reference its immutable schema"
        )
    if (
        policy.get("schema_version")
        != IMPROVEMENT_CLASSIFICATION_POLICY_SCHEMA_VERSION
    ):
        errors.append(
            "improvement classification policy schema_version must equal "
            f"{IMPROVEMENT_CLASSIFICATION_POLICY_SCHEMA_VERSION}"
        )
    if not _valid_id(policy.get("policy_id")):
        errors.append(
            "improvement classification policy_id must be a lowercase kebab-case "
            "identifier"
        )
    rules = policy.get("classification_rules")
    boundary = policy.get("decision_boundary")
    if not isinstance(rules, dict) or not isinstance(boundary, dict):
        errors.append(
            "improvement classification policy rules and boundary must be objects"
        )
        return errors
    try:
        canonical_size = len(canonical_json_bytes(policy))
    except (RecursionError, TypeError, ValueError):
        return errors + [
            "improvement classification policy must be canonical JSON data"
        ]
    if not 0 < canonical_size <= MAX_IMPROVEMENT_CLASSIFICATION_POLICY_BYTES:
        errors.append(
            "improvement classification policy size is outside the accepted boundary"
        )
    if set(rules) != RULE_FIELDS:
        errors.append(
            "improvement classification rules contain missing or unexpected fields"
        )
    if not _valid_ordered_subset(
        rules.get("accepted_observation_kinds"),
        OBSERVATION_KIND_ORDER,
    ):
        errors.append(
            "improvement classification observation kinds must be a non-empty "
            "canonical subset"
        )
    if not _valid_ordered_subset(
        rules.get("accepted_operations"),
        OPERATION_ORDER,
    ):
        errors.append(
            "improvement classification operations must be a non-empty canonical "
            "subset"
        )
    if not _canonical_equal(
        rules.get("target_classifications"),
        list(TARGET_CLASSIFICATIONS),
    ):
        errors.append(
            "improvement classification target mapping must remain complete and "
            "canonical"
        )
    for field in (
        "require_same_evidence_return",
        "require_subject_target_match",
        "require_complete_review_requirements",
        "require_non_authorizing_inputs",
    ):
        if rules.get(field) is not True:
            errors.append(f"improvement classification rule {field} must remain true")
    if not _canonical_equal(boundary, EXPECTED_DECISION_BOUNDARY):
        errors.append(
            "improvement classification decision boundary must remain planning-only "
            "and non-authorizing"
        )
    return errors


def _precheck_factory_improvement_classification(record: Any) -> list[str]:
    if not isinstance(record, dict):
        return ["factory improvement-classification root must be an object"]
    if set(record) != CLASSIFICATION_FIELDS:
        return [
            "factory improvement-classification must contain exactly the "
            "versioned fields"
        ]
    if record.get("contract_schema") != IMPROVEMENT_CLASSIFICATION_SCHEMA_REFERENCE:
        return [
            "factory improvement-classification must reference its immutable schema"
        ]
    if record.get("schema_version") != IMPROVEMENT_CLASSIFICATION_SCHEMA_VERSION:
        return [
            "factory improvement-classification schema_version must equal "
            f"{IMPROVEMENT_CLASSIFICATION_SCHEMA_VERSION}"
        ]
    if any(
        not isinstance(record.get(field), dict)
        for field in CLASSIFICATION_OBJECT_FIELDS
    ):
        return ["factory improvement-classification sections must be objects"]
    try:
        canonical_size = len(canonical_json_bytes(record))
    except (RecursionError, TypeError, ValueError):
        return ["factory improvement-classification must be canonical JSON data"]
    if not 0 < canonical_size <= MAX_IMPROVEMENT_CLASSIFICATION_BYTES:
        return [
            "factory improvement-classification size is outside the accepted boundary"
        ]
    recorded_digest = record.get("factory_improvement_classification_sha256")
    if (
        not isinstance(recorded_digest, str)
        or len(recorded_digest) != 64
        or any(character not in "0123456789abcdef" for character in recorded_digest)
    ):
        return [
            "factory improvement-classification digest must be lowercase SHA-256"
        ]
    without_digest = dict(record)
    without_digest.pop("factory_improvement_classification_sha256")
    if sha256_json(without_digest) != recorded_digest:
        return [
            "factory improvement-classification digest does not match its content"
        ]
    return []


def _check(
    position: int,
    check_id: str,
    passed: bool,
    passed_reason: str,
    failed_reason: str,
) -> dict[str, Any]:
    return {
        "position": position,
        "id": check_id,
        "status": "passed" if passed else "failed",
        "reason": passed_reason if passed else failed_reason,
    }


def _classification_boundary(classified: bool) -> dict[str, Any]:
    return {
        "proposal_reverified": True,
        "observation_reverified": True,
        "classification_policy_validated": True,
        "observation_structural_normalization_verified": True,
        "source_alignment_checked": True,
        "target_alignment_checked": True,
        "classification_performed": True,
        "improvement_candidate_classified": classified,
        "validation_planning_eligible": classified,
        "content_safety_scanned": False,
        "secret_absence_proved": False,
        "reporter_authenticated": False,
        "proposer_authenticated": False,
        "source_artifact_semantic_truth_verified": False,
        "observation_semantic_truth_verified": False,
        "proposal_merit_verified": False,
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


def build_factory_improvement_classification(
    policy: dict[str, Any],
    proposal: dict[str, Any],
    observation: dict[str, Any],
) -> dict[str, Any]:
    """Classify workflow type without judging truth, merit, or authority."""
    proposal_target = proposal["proposal"]["target"]
    observation_subject = observation["observation"]["subject"]
    same_source = (
        proposal["source"]["factory_evidence_return_sha256"]
        == observation["source"]["factory_evidence_return_sha256"]
        and _canonical_equal(proposal["portfolio"], observation["portfolio"])
        and _canonical_equal(proposal["route"], observation["route"])
        and proposal["source"]["reporting_factory"]
        == observation["source"]["reporting_factory"]
    )
    target_matches = _canonical_equal(
        {"kind": proposal_target["kind"], "id": proposal_target["id"]},
        observation_subject,
    )
    observation_allowed = (
        observation["observation"]["kind"]
        in policy["classification_rules"]["accepted_observation_kinds"]
    )
    operation_allowed = (
        proposal_target["operation"]
        in policy["classification_rules"]["accepted_operations"]
    )
    requirements_preserved = (
        _canonical_equal(
            proposal["proposal"]["validation_requirements"],
            EXPECTED_VALIDATION_REQUIREMENTS,
        )
        and _canonical_equal(
            observation["observation"]["normalization_requirements"],
            EXPECTED_NORMALIZATION_REQUIREMENTS,
        )
    )
    inputs_non_authorizing = (
        _canonical_equal(
            proposal["proposal"]["proposal_boundary"],
            EXPECTED_PROPOSAL_BOUNDARY,
        )
        and _canonical_equal(
            observation["observation"]["observation_boundary"],
            EXPECTED_OBSERVATION_BOUNDARY,
        )
    )
    checks = [
        _check(
            0,
            CHECK_IDS[0],
            same_source,
            "exact_evidence_return_and_route_match",
            "evidence_return_or_route_mismatch",
        ),
        _check(
            1,
            CHECK_IDS[1],
            target_matches,
            "observation_subject_matches_proposal_target",
            "observation_subject_does_not_match_proposal_target",
        ),
        _check(
            2,
            CHECK_IDS[2],
            observation_allowed,
            "observation_kind_allowed_by_policy",
            "observation_kind_denied_by_policy",
        ),
        _check(
            3,
            CHECK_IDS[3],
            operation_allowed,
            "target_operation_allowed_by_policy",
            "target_operation_denied_by_policy",
        ),
        _check(
            4,
            CHECK_IDS[4],
            requirements_preserved,
            "all_later_review_requirements_preserved",
            "later_review_requirements_incomplete",
        ),
        _check(
            5,
            CHECK_IDS[5],
            inputs_non_authorizing,
            "proposal_and_observation_are_non_authorizing",
            "input_authority_boundary_inflated",
        ),
    ]
    classified = all(check["status"] == "passed" for check in checks)
    class_by_target = {
        item["target_kind"]: item["candidate_class"]
        for item in TARGET_CLASSIFICATIONS
    }
    candidate_class = class_by_target[proposal_target["kind"]] if classified else None
    record_without_digest: dict[str, Any] = {
        "contract_schema": IMPROVEMENT_CLASSIFICATION_SCHEMA_REFERENCE,
        "schema_version": IMPROVEMENT_CLASSIFICATION_SCHEMA_VERSION,
        "source": {
            "classification_policy_id": policy["policy_id"],
            "classification_policy_sha256": sha256_json(policy),
            "factory_improvement_proposal_sha256": proposal[
                "factory_improvement_proposal_sha256"
            ],
            "factory_improvement_observation_sha256": observation[
                "factory_improvement_observation_sha256"
            ],
            "factory_evidence_return_sha256": proposal["source"][
                "factory_evidence_return_sha256"
            ],
            "reporting_factory": proposal["source"]["reporting_factory"],
            "control_factory": proposal["portfolio"]["control_factory"],
        },
        "classification": {
            "proposal_id": proposal["proposal"]["id"],
            "observation_id": observation["observation"]["id"],
            "observation_kind": observation["observation"]["kind"],
            "target": deepcopy(proposal_target),
            "checks": checks,
            "decision": (
                "classified_for_validation_planning"
                if classified
                else "not_classified"
            ),
            "candidate_class": candidate_class,
            "eligible_for_validation_planning": classified,
        },
        "classification_boundary": _classification_boundary(classified),
    }
    record = dict(record_without_digest)
    record["factory_improvement_classification_sha256"] = sha256_json(
        record_without_digest
    )
    return record


def factory_improvement_classification_for_inputs(
    policy: Any,
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
    policy_errors = validate_improvement_classification_policy(policy)
    if policy_errors:
        return policy_errors, None
    proposal_errors = verify_factory_improvement_proposal_for_inputs(
        proposal,
        proposal_specification,
        evidence_return,
        plan,
        portfolio,
        bundle_values,
        source_factory_id,
        runtime_evidence_pack,
        qualification_plan,
        qualification_policy,
    )
    if proposal_errors:
        return [
            f"improvement classification proposal: {error}"
            for error in proposal_errors
        ], None
    observation_errors = verify_factory_improvement_observation_for_inputs(
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
    if observation_errors:
        return [
            f"improvement classification observation: {error}"
            for error in observation_errors
        ], None
    assert isinstance(policy, dict)
    assert isinstance(proposal, dict)
    assert isinstance(observation, dict)
    try:
        record = build_factory_improvement_classification(
            policy,
            proposal,
            observation,
        )
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot build factory improvement-classification: {exc}"], None
    return [], record


def verify_factory_improvement_classification_for_inputs(
    record: Any,
    policy: Any,
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
    precheck_errors = _precheck_factory_improvement_classification(record)
    if precheck_errors:
        return precheck_errors
    errors, expected = factory_improvement_classification_for_inputs(
        policy,
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
            "factory improvement-classification must exactly match its policy, "
            "proposal, normalized observation, and verified evidence return"
        ]
    return []
