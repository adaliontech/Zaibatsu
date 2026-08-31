#!/usr/bin/env python3
"""Bind one typed improvement proposal to one verified factory evidence return."""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from factory_composer import canonical_json_bytes, load_json_file, sha256_json
from factory_evidence_return import verify_factory_evidence_return_for_inputs


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_IMPROVEMENT_PROPOSAL_SPEC_PATH = (
    ROOT / "examples" / "economic-factory.improvement-proposal-spec.json"
)
EXAMPLE_IMPROVEMENT_PROPOSAL_PATH = (
    ROOT / "examples" / "economic-factory.improvement-proposal.json"
)

IMPROVEMENT_PROPOSAL_SPEC_SCHEMA_VERSION = (
    "zaibatsu.factory-improvement-proposal-spec.v1"
)
IMPROVEMENT_PROPOSAL_SCHEMA_VERSION = (
    "zaibatsu.factory-improvement-proposal.v1"
)
IMPROVEMENT_PROPOSAL_SPEC_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.13.0/schemas/factory-improvement-proposal-spec.schema.json"
)
IMPROVEMENT_PROPOSAL_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.13.0/schemas/factory-improvement-proposal.schema.json"
)

MAX_IMPROVEMENT_PROPOSAL_SPEC_BYTES = 128 * 1024
MAX_IMPROVEMENT_PROPOSAL_BYTES = 2 * 1024 * 1024
MAX_TEXT_LENGTH = 512
ID_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
TARGET_KINDS = {"shared_module", "factory_template", "deterministic_gate"}
TARGET_OPERATIONS = {"add", "modify", "replace"}

SPEC_FIELDS = {
    "contract_schema",
    "schema_version",
    "proposal",
    "target",
    "validation_requirements",
    "proposal_boundary",
}
SPEC_OBJECT_FIELDS = {
    "proposal",
    "target",
    "validation_requirements",
    "proposal_boundary",
}
PROPOSAL_FIELDS = {"id", "summary", "expected_outcome"}
TARGET_FIELDS = {"kind", "id", "operation"}

EXPECTED_VALIDATION_REQUIREMENTS = {
    "content_safety_scan_required": True,
    "candidate_classification_required": True,
    "reporting_factory_validation_required": True,
    "independent_regression_validation_required": True,
    "owner_policy_promotion_required": True,
    "rollback_plan_required": True,
    "cross_factory_privilege_review_required": True,
}
EXPECTED_PROPOSAL_BOUNDARY = {
    "proposal_only": True,
    "content_trusted": False,
    "proposer_authenticated": False,
    "grants_authority": False,
    "can_self_promote": False,
    "execution_authorized": False,
}

RECORD_FIELDS = {
    "contract_schema",
    "schema_version",
    "portfolio",
    "route",
    "source",
    "proposal",
    "review_boundary",
    "factory_improvement_proposal_sha256",
}
RECORD_OBJECT_FIELDS = {
    "portfolio",
    "route",
    "source",
    "proposal",
    "review_boundary",
}

REVIEW_BOUNDARY = {
    "evidence_return_reverified": True,
    "evidence_return_bound": True,
    "proposal_structure_validated": True,
    "proposal_canonical_json_bound": True,
    "proposal_recorded": True,
    "transport_observed": False,
    "proposal_content_safety_scanned": False,
    "secret_absence_proved": False,
    "proposer_authenticated": False,
    "source_artifact_semantic_truth_verified": False,
    "observation_normalized": False,
    "improvement_candidate_classified": False,
    "proposal_merit_verified": False,
    "reporting_factory_validation_passed": False,
    "independent_regression_validation_passed": False,
    "rollback_plan_verified": False,
    "changes_shared_policy": False,
    "shared_promotion_eligible": False,
    "owner_policy_approval_obtained": False,
    "promotion_authorized": False,
    "rollout_authorized": False,
    "activation_authorized": False,
    "execution_authorized": False,
    "cross_factory_effects_authorized": False,
}


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


def _valid_text(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and len(value) <= MAX_TEXT_LENGTH
    )


def load_factory_improvement_proposal_spec(
    path: Path = EXAMPLE_IMPROVEMENT_PROPOSAL_SPEC_PATH,
) -> Any:
    return load_json_file(path)


def load_factory_improvement_proposal(
    path: Path = EXAMPLE_IMPROVEMENT_PROPOSAL_PATH,
) -> Any:
    return load_json_file(path)


def validate_factory_improvement_proposal_spec(specification: Any) -> list[str]:
    """Validate an untrusted, non-authorizing proposal specification."""
    errors: list[str] = []
    if not isinstance(specification, dict):
        return ["factory improvement-proposal specification root must be an object"]
    if set(specification) != SPEC_FIELDS:
        errors.append(
            "factory improvement-proposal specification must contain exactly "
            "the versioned fields"
        )
    if (
        specification.get("contract_schema")
        != IMPROVEMENT_PROPOSAL_SPEC_SCHEMA_REFERENCE
    ):
        errors.append(
            "factory improvement-proposal specification must reference its "
            "immutable schema"
        )
    if (
        specification.get("schema_version")
        != IMPROVEMENT_PROPOSAL_SPEC_SCHEMA_VERSION
    ):
        errors.append(
            "factory improvement-proposal specification schema_version must equal "
            f"{IMPROVEMENT_PROPOSAL_SPEC_SCHEMA_VERSION}"
        )
    if any(
        not isinstance(specification.get(field), dict)
        for field in SPEC_OBJECT_FIELDS
    ):
        errors.append(
            "factory improvement-proposal specification sections must be objects"
        )
        return errors
    try:
        canonical_size = len(canonical_json_bytes(specification))
    except (RecursionError, TypeError, ValueError):
        return errors + [
            "factory improvement-proposal specification must be canonical JSON data"
        ]
    if not 0 < canonical_size <= MAX_IMPROVEMENT_PROPOSAL_SPEC_BYTES:
        errors.append(
            "factory improvement-proposal specification size is outside the "
            "accepted boundary"
        )

    proposal = specification["proposal"]
    if set(proposal) != PROPOSAL_FIELDS:
        errors.append(
            "factory improvement-proposal metadata contains missing or unexpected fields"
        )
    if not _valid_id(proposal.get("id")):
        errors.append(
            "factory improvement-proposal id must be a lowercase kebab-case identifier"
        )
    for field in ("summary", "expected_outcome"):
        if not _valid_text(proposal.get(field)):
            errors.append(
                f"factory improvement-proposal {field} must be non-empty and bounded"
            )

    target = specification["target"]
    if set(target) != TARGET_FIELDS:
        errors.append(
            "factory improvement-proposal target contains missing or unexpected fields"
        )
    target_kind = target.get("kind")
    if not isinstance(target_kind, str) or target_kind not in TARGET_KINDS:
        errors.append("factory improvement-proposal target kind is not supported")
    if not _valid_id(target.get("id")):
        errors.append(
            "factory improvement-proposal target id must be a lowercase kebab-case "
            "identifier"
        )
    target_operation = target.get("operation")
    if (
        not isinstance(target_operation, str)
        or target_operation not in TARGET_OPERATIONS
    ):
        errors.append("factory improvement-proposal target operation is not supported")

    if not _canonical_equal(
        specification["validation_requirements"],
        EXPECTED_VALIDATION_REQUIREMENTS,
    ):
        errors.append(
            "factory improvement-proposal validation requirements must preserve "
            "every review gate"
        )
    if not _canonical_equal(
        specification["proposal_boundary"],
        EXPECTED_PROPOSAL_BOUNDARY,
    ):
        errors.append(
            "factory improvement-proposal boundary must remain non-authorizing"
        )
    return errors


def _precheck_factory_improvement_proposal(record: Any) -> list[str]:
    """Reject structurally impossible or self-inconsistent records cheaply."""
    if not isinstance(record, dict):
        return ["factory improvement-proposal record root must be an object"]
    if set(record) != RECORD_FIELDS:
        return [
            "factory improvement-proposal record must contain exactly the "
            "versioned fields"
        ]
    if record.get("contract_schema") != IMPROVEMENT_PROPOSAL_SCHEMA_REFERENCE:
        return [
            "factory improvement-proposal record must reference its immutable schema"
        ]
    if record.get("schema_version") != IMPROVEMENT_PROPOSAL_SCHEMA_VERSION:
        return [
            "factory improvement-proposal record schema_version must equal "
            f"{IMPROVEMENT_PROPOSAL_SCHEMA_VERSION}"
        ]
    if any(
        not isinstance(record.get(field), dict)
        for field in RECORD_OBJECT_FIELDS
    ):
        return ["factory improvement-proposal record sections must be objects"]
    try:
        canonical_size = len(canonical_json_bytes(record))
    except (RecursionError, TypeError, ValueError):
        return ["factory improvement-proposal record must be canonical JSON data"]
    if not 0 < canonical_size <= MAX_IMPROVEMENT_PROPOSAL_BYTES:
        return [
            "factory improvement-proposal record size is outside the accepted boundary"
        ]
    recorded_digest = record.get("factory_improvement_proposal_sha256")
    if (
        not isinstance(recorded_digest, str)
        or len(recorded_digest) != 64
        or any(character not in "0123456789abcdef" for character in recorded_digest)
    ):
        return ["factory improvement-proposal record digest must be lowercase SHA-256"]
    without_digest = dict(record)
    without_digest.pop("factory_improvement_proposal_sha256")
    if sha256_json(without_digest) != recorded_digest:
        return [
            "factory improvement-proposal record digest does not match its content"
        ]
    return []


def build_factory_improvement_proposal(
    specification: dict[str, Any],
    evidence_return: dict[str, Any],
) -> dict[str, Any]:
    """Build one content-addressed proposal without interpreting or approving it."""
    record_without_digest: dict[str, Any] = {
        "contract_schema": IMPROVEMENT_PROPOSAL_SCHEMA_REFERENCE,
        "schema_version": IMPROVEMENT_PROPOSAL_SCHEMA_VERSION,
        "portfolio": {
            "id": evidence_return["portfolio"]["id"],
            "factory_portfolio_plan_sha256": evidence_return["portfolio"][
                "factory_portfolio_plan_sha256"
            ],
            "control_factory": evidence_return["route"]["to_factory"],
        },
        "route": deepcopy(evidence_return["route"]),
        "source": {
            "factory_evidence_return_sha256": evidence_return[
                "factory_evidence_return_sha256"
            ],
            "runtime_evidence_pack_sha256": evidence_return["evidence"][
                "runtime_evidence_pack_sha256"
            ],
            "reporting_factory": evidence_return["factory"]["id"],
        },
        "proposal": {
            "specification_sha256": sha256_json(specification),
            "id": specification["proposal"]["id"],
            "summary": specification["proposal"]["summary"],
            "expected_outcome": specification["proposal"]["expected_outcome"],
            "target": deepcopy(specification["target"]),
            "validation_requirements": deepcopy(
                specification["validation_requirements"]
            ),
            "proposal_boundary": deepcopy(specification["proposal_boundary"]),
        },
        "review_boundary": deepcopy(REVIEW_BOUNDARY),
    }
    record = dict(record_without_digest)
    record["factory_improvement_proposal_sha256"] = sha256_json(
        record_without_digest
    )
    return record


def factory_improvement_proposal_for_inputs(
    specification: Any,
    evidence_return: Any,
    plan: Any,
    portfolio: Any,
    bundle_values: Any,
    source_factory_id: Any,
    runtime_evidence_pack: Any,
    qualification_plan: Any,
    qualification_policy: Any,
) -> tuple[list[str], dict[str, Any] | None]:
    specification_errors = validate_factory_improvement_proposal_spec(specification)
    if specification_errors:
        return specification_errors, None
    evidence_errors = verify_factory_evidence_return_for_inputs(
        evidence_return,
        plan,
        portfolio,
        bundle_values,
        source_factory_id,
        runtime_evidence_pack,
        qualification_plan,
        qualification_policy,
    )
    if evidence_errors:
        return [
            f"improvement-proposal evidence return: {error}"
            for error in evidence_errors
        ], None
    assert isinstance(specification, dict)
    assert isinstance(evidence_return, dict)
    try:
        record = build_factory_improvement_proposal(specification, evidence_return)
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot build factory improvement-proposal record: {exc}"], None
    return [], record


def verify_factory_improvement_proposal_for_inputs(
    record: Any,
    specification: Any,
    evidence_return: Any,
    plan: Any,
    portfolio: Any,
    bundle_values: Any,
    source_factory_id: Any,
    runtime_evidence_pack: Any,
    qualification_plan: Any,
    qualification_policy: Any,
) -> list[str]:
    precheck_errors = _precheck_factory_improvement_proposal(record)
    if precheck_errors:
        return precheck_errors
    errors, expected = factory_improvement_proposal_for_inputs(
        specification,
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
            "factory improvement-proposal record must exactly match its proposal "
            "specification and verified evidence return"
        ]
    return []
