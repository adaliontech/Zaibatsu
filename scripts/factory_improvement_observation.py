#!/usr/bin/env python3
"""Structurally normalize one untrusted observation against returned evidence."""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from factory_composer import canonical_json_bytes, load_json_file, sha256_json
from factory_evidence_return import verify_factory_evidence_return_for_inputs


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_IMPROVEMENT_OBSERVATION_SPEC_PATH = (
    ROOT / "examples" / "economic-factory.improvement-observation-spec.json"
)
EXAMPLE_IMPROVEMENT_OBSERVATION_PATH = (
    ROOT / "examples" / "economic-factory.improvement-observation.json"
)

IMPROVEMENT_OBSERVATION_SPEC_SCHEMA_VERSION = (
    "zaibatsu.factory-improvement-observation-spec.v1"
)
IMPROVEMENT_OBSERVATION_SCHEMA_VERSION = (
    "zaibatsu.factory-improvement-observation.v1"
)
IMPROVEMENT_OBSERVATION_SPEC_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.14.0/schemas/factory-improvement-observation-spec.schema.json"
)
IMPROVEMENT_OBSERVATION_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.14.0/schemas/factory-improvement-observation.schema.json"
)

MAX_IMPROVEMENT_OBSERVATION_SPEC_BYTES = 128 * 1024
MAX_IMPROVEMENT_OBSERVATION_BYTES = 2 * 1024 * 1024
MAX_TEXT_LENGTH = 512
ID_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
OBSERVATION_KINDS = {
    "failure",
    "artifact_outcome",
    "correction",
    "observation",
}
SUBJECT_KINDS = {"shared_module", "factory_template", "deterministic_gate"}

SPEC_FIELDS = {
    "contract_schema",
    "schema_version",
    "observation",
    "subject",
    "normalization_requirements",
    "observation_boundary",
}
SPEC_OBJECT_FIELDS = {
    "observation",
    "subject",
    "normalization_requirements",
    "observation_boundary",
}
OBSERVATION_FIELDS = {
    "id",
    "kind",
    "summary",
    "observed_condition",
    "expected_condition",
}
SUBJECT_FIELDS = {"kind", "id"}

EXPECTED_NORMALIZATION_REQUIREMENTS = {
    "source_evidence_required": True,
    "canonical_category_required": True,
    "content_safety_scan_required": True,
    "semantic_review_required": True,
    "classification_required": True,
}
EXPECTED_OBSERVATION_BOUNDARY = {
    "untrusted_report": True,
    "content_safety_scanned": False,
    "secret_absence_proved": False,
    "reporter_authenticated": False,
    "semantic_truth_claimed": False,
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
    "observation",
    "normalization_boundary",
    "factory_improvement_observation_sha256",
}
RECORD_OBJECT_FIELDS = {
    "portfolio",
    "route",
    "source",
    "observation",
    "normalization_boundary",
}

NORMALIZATION_BOUNDARY = {
    "evidence_return_reverified": True,
    "evidence_return_bound": True,
    "observation_structure_validated": True,
    "observation_canonical_json_bound": True,
    "observation_structurally_normalized": True,
    "transport_observed": False,
    "content_safety_scanned": False,
    "secret_absence_proved": False,
    "reporter_authenticated": False,
    "source_artifact_semantic_truth_verified": False,
    "observation_semantic_truth_verified": False,
    "improvement_candidate_classified": False,
    "proposal_merit_verified": False,
    "changes_shared_policy": False,
    "shared_promotion_eligible": False,
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


def load_factory_improvement_observation_spec(
    path: Path = EXAMPLE_IMPROVEMENT_OBSERVATION_SPEC_PATH,
) -> Any:
    return load_json_file(path)


def load_factory_improvement_observation(
    path: Path = EXAMPLE_IMPROVEMENT_OBSERVATION_PATH,
) -> Any:
    return load_json_file(path)


def validate_factory_improvement_observation_spec(
    specification: Any,
) -> list[str]:
    """Validate a typed observation without trusting its content or reporter."""
    errors: list[str] = []
    if not isinstance(specification, dict):
        return ["factory improvement-observation specification root must be an object"]
    if set(specification) != SPEC_FIELDS:
        errors.append(
            "factory improvement-observation specification must contain exactly "
            "the versioned fields"
        )
    if (
        specification.get("contract_schema")
        != IMPROVEMENT_OBSERVATION_SPEC_SCHEMA_REFERENCE
    ):
        errors.append(
            "factory improvement-observation specification must reference its "
            "immutable schema"
        )
    if (
        specification.get("schema_version")
        != IMPROVEMENT_OBSERVATION_SPEC_SCHEMA_VERSION
    ):
        errors.append(
            "factory improvement-observation specification schema_version must "
            f"equal {IMPROVEMENT_OBSERVATION_SPEC_SCHEMA_VERSION}"
        )
    if any(
        not isinstance(specification.get(field), dict)
        for field in SPEC_OBJECT_FIELDS
    ):
        errors.append(
            "factory improvement-observation specification sections must be objects"
        )
        return errors
    try:
        canonical_size = len(canonical_json_bytes(specification))
    except (RecursionError, TypeError, ValueError):
        return errors + [
            "factory improvement-observation specification must be canonical JSON data"
        ]
    if not 0 < canonical_size <= MAX_IMPROVEMENT_OBSERVATION_SPEC_BYTES:
        errors.append(
            "factory improvement-observation specification size is outside the "
            "accepted boundary"
        )

    observation = specification["observation"]
    if set(observation) != OBSERVATION_FIELDS:
        errors.append(
            "factory improvement-observation metadata contains missing or "
            "unexpected fields"
        )
    if not _valid_id(observation.get("id")):
        errors.append(
            "factory improvement-observation id must be a lowercase kebab-case "
            "identifier"
        )
    observation_kind = observation.get("kind")
    if (
        not isinstance(observation_kind, str)
        or observation_kind not in OBSERVATION_KINDS
    ):
        errors.append("factory improvement-observation kind is not supported")
    for field in ("summary", "observed_condition", "expected_condition"):
        if not _valid_text(observation.get(field)):
            errors.append(
                f"factory improvement-observation {field} must be non-empty and "
                "bounded"
            )

    subject = specification["subject"]
    if set(subject) != SUBJECT_FIELDS:
        errors.append(
            "factory improvement-observation subject contains missing or "
            "unexpected fields"
        )
    subject_kind = subject.get("kind")
    if not isinstance(subject_kind, str) or subject_kind not in SUBJECT_KINDS:
        errors.append("factory improvement-observation subject kind is not supported")
    if not _valid_id(subject.get("id")):
        errors.append(
            "factory improvement-observation subject id must be a lowercase "
            "kebab-case identifier"
        )

    if not _canonical_equal(
        specification["normalization_requirements"],
        EXPECTED_NORMALIZATION_REQUIREMENTS,
    ):
        errors.append(
            "factory improvement-observation requirements must preserve every "
            "normalization and review gate"
        )
    if not _canonical_equal(
        specification["observation_boundary"],
        EXPECTED_OBSERVATION_BOUNDARY,
    ):
        errors.append(
            "factory improvement-observation boundary must remain untrusted and "
            "non-authorizing"
        )
    return errors


def _precheck_factory_improvement_observation(record: Any) -> list[str]:
    if not isinstance(record, dict):
        return ["factory improvement-observation record root must be an object"]
    if set(record) != RECORD_FIELDS:
        return [
            "factory improvement-observation record must contain exactly the "
            "versioned fields"
        ]
    if record.get("contract_schema") != IMPROVEMENT_OBSERVATION_SCHEMA_REFERENCE:
        return [
            "factory improvement-observation record must reference its immutable "
            "schema"
        ]
    if record.get("schema_version") != IMPROVEMENT_OBSERVATION_SCHEMA_VERSION:
        return [
            "factory improvement-observation record schema_version must equal "
            f"{IMPROVEMENT_OBSERVATION_SCHEMA_VERSION}"
        ]
    if any(
        not isinstance(record.get(field), dict)
        for field in RECORD_OBJECT_FIELDS
    ):
        return ["factory improvement-observation record sections must be objects"]
    try:
        canonical_size = len(canonical_json_bytes(record))
    except (RecursionError, TypeError, ValueError):
        return ["factory improvement-observation record must be canonical JSON data"]
    if not 0 < canonical_size <= MAX_IMPROVEMENT_OBSERVATION_BYTES:
        return [
            "factory improvement-observation record size is outside the accepted "
            "boundary"
        ]
    recorded_digest = record.get("factory_improvement_observation_sha256")
    if (
        not isinstance(recorded_digest, str)
        or len(recorded_digest) != 64
        or any(character not in "0123456789abcdef" for character in recorded_digest)
    ):
        return [
            "factory improvement-observation record digest must be lowercase SHA-256"
        ]
    without_digest = dict(record)
    without_digest.pop("factory_improvement_observation_sha256")
    if sha256_json(without_digest) != recorded_digest:
        return [
            "factory improvement-observation record digest does not match its content"
        ]
    return []


def build_factory_improvement_observation(
    specification: dict[str, Any],
    evidence_return: dict[str, Any],
) -> dict[str, Any]:
    """Build a structural normalization record without semantic interpretation."""
    record_without_digest: dict[str, Any] = {
        "contract_schema": IMPROVEMENT_OBSERVATION_SCHEMA_REFERENCE,
        "schema_version": IMPROVEMENT_OBSERVATION_SCHEMA_VERSION,
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
        "observation": {
            "specification_sha256": sha256_json(specification),
            **deepcopy(specification["observation"]),
            "subject": deepcopy(specification["subject"]),
            "normalization_requirements": deepcopy(
                specification["normalization_requirements"]
            ),
            "observation_boundary": deepcopy(
                specification["observation_boundary"]
            ),
        },
        "normalization_boundary": deepcopy(NORMALIZATION_BOUNDARY),
    }
    record = dict(record_without_digest)
    record["factory_improvement_observation_sha256"] = sha256_json(
        record_without_digest
    )
    return record


def factory_improvement_observation_for_inputs(
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
    specification_errors = validate_factory_improvement_observation_spec(
        specification
    )
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
            f"improvement-observation evidence return: {error}"
            for error in evidence_errors
        ], None
    assert isinstance(specification, dict)
    assert isinstance(evidence_return, dict)
    try:
        record = build_factory_improvement_observation(
            specification,
            evidence_return,
        )
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot build factory improvement-observation record: {exc}"], None
    return [], record


def verify_factory_improvement_observation_for_inputs(
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
    precheck_errors = _precheck_factory_improvement_observation(record)
    if precheck_errors:
        return precheck_errors
    errors, expected = factory_improvement_observation_for_inputs(
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
            "factory improvement-observation record must exactly match its "
            "specification and verified evidence return"
        ]
    return []
