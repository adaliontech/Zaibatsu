#!/usr/bin/env python3
"""Build and verify canonical packs of improvement-validation inputs."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from factory_bundle import (
    canonical_tar_bytes,
    read_bounded_archive_payloads,
    sha256_bytes,
    verify_factory_bundle,
)
from factory_composer import canonical_json_bytes, load_json_bytes, load_json_file, sha256_json
from factory_improvement_validation_plan import (
    verify_factory_improvement_validation_plan_for_inputs,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_VALIDATION_PACK_MANIFEST_PATH = (
    ROOT / "examples" / "economic-factory.improvement-validation-pack-manifest.json"
)
VALIDATION_PACK_SCHEMA_PATH = (
    ROOT / "schemas" / "factory-improvement-validation-pack-manifest.schema.json"
)

VALIDATION_PACK_MANIFEST_SCHEMA_VERSION = (
    "zaibatsu.factory-improvement-validation-pack-manifest.v1"
)
VALIDATION_PACK_MANIFEST_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.17.0/schemas/factory-improvement-validation-pack-manifest.schema.json"
)
VALIDATION_PACK_MANIFEST_SCHEMA_SHA256 = (
    "6558043125427d6ca6342f7d143bf0768e349738e73ad5287b6b4ad8cea54148"
)

MAX_VALIDATION_PACK_BYTES = 32 * 1024 * 1024
MAX_VALIDATION_PACK_MEMBER_BYTES = 16 * 1024 * 1024
MAX_VALIDATION_PACK_MEMBERS = 82
MIN_FACTORY_BUNDLES = 2
MAX_FACTORY_BUNDLES = 64

MANIFEST_PATH = "MANIFEST.json"
PACKED_SCHEMA_PATH = "schemas/factory-improvement-validation-pack-manifest.schema.json"
VALIDATION_PLAN_PATH = "improvement/validation-plan.json"
VALIDATION_PLAN_SPEC_PATH = "improvement/validation-plan-spec.json"
CANDIDATE_PATH = "improvement/candidate.json"
CANDIDATE_SPEC_PATH = "improvement/candidate-spec.json"
CLASSIFICATION_PATH = "improvement/classification.json"
CLASSIFICATION_POLICY_PATH = "policies/improvement-classification.json"
PROPOSAL_PATH = "improvement/proposal.json"
PROPOSAL_SPEC_PATH = "improvement/proposal-spec.json"
OBSERVATION_PATH = "improvement/observation.json"
OBSERVATION_SPEC_PATH = "improvement/observation-spec.json"
EVIDENCE_RETURN_PATH = "improvement/evidence-return.json"
PORTFOLIO_PLAN_PATH = "portfolio/plan.json"
PORTFOLIO_DEFINITION_PATH = "portfolio/definition.json"
QUALIFICATION_PLAN_PATH = "qualification/plan.json"
QUALIFICATION_POLICY_PATH = "policies/runtime-qualification.json"
RUNTIME_EVIDENCE_PACK_PATH = "runtime/evidence-pack.tar"

JSON_PATH_ROLES = {
    PACKED_SCHEMA_PATH: "manifest_schema",
    VALIDATION_PLAN_PATH: "validation_plan",
    VALIDATION_PLAN_SPEC_PATH: "validation_plan_specification",
    CANDIDATE_PATH: "improvement_candidate",
    CANDIDATE_SPEC_PATH: "candidate_specification",
    CLASSIFICATION_PATH: "improvement_classification",
    CLASSIFICATION_POLICY_PATH: "improvement_classification_policy",
    PROPOSAL_PATH: "improvement_proposal",
    PROPOSAL_SPEC_PATH: "improvement_proposal_specification",
    OBSERVATION_PATH: "improvement_observation",
    OBSERVATION_SPEC_PATH: "improvement_observation_specification",
    EVIDENCE_RETURN_PATH: "factory_evidence_return",
    PORTFOLIO_PLAN_PATH: "factory_portfolio_plan",
    PORTFOLIO_DEFINITION_PATH: "factory_portfolio_definition",
    QUALIFICATION_PLAN_PATH: "qualification_plan",
    QUALIFICATION_POLICY_PATH: "runtime_qualification_policy",
}

PACK_BOUNDARY = {
    "canonical_archive": True,
    "portable_validation_inputs": True,
    "all_input_digests_verified": True,
    "nested_archives_verified": True,
    "complete_candidate_chain_reverified": True,
    "validation_plan_reverified": True,
    "candidate_artifact_untrusted": True,
    "contains_executable_commands": False,
    "candidate_implementation_embedded": False,
    "validation_stage_evidence_embedded": False,
    "input_pack_verifier_implementation_embedded": False,
    "verifier_execution_environment_reproduced": False,
    "network_access_required": False,
    "live_production_credentials_required": False,
    "live_production_state_required": False,
    "content_safety_scanned": False,
    "secret_absence_proved": False,
    "artifact_semantic_truth_verified": False,
    "validation_executed": False,
    "ready_for_validation_execution": False,
    "validation_execution_authorized": False,
    "owner_policy_approval_obtained": False,
    "shared_promotion_eligible": False,
    "promotion_authorized": False,
    "rollout_authorized": False,
    "activation_authorized": False,
    "execution_authorized": False,
    "cross_factory_effects_authorized": False,
}


def _factory_path(factory_id: str) -> str:
    return f"factories/{factory_id}.factory.tar"


def _bundle_index(bundle_values: Any) -> tuple[list[str], dict[str, bytes]]:
    if not isinstance(bundle_values, (list, tuple)):
        return ["factory bundles must be an ordered collection"], {}
    if not MIN_FACTORY_BUNDLES <= len(bundle_values) <= MAX_FACTORY_BUNDLES:
        return ["factory bundle count is outside the accepted boundary"], {}
    errors: list[str] = []
    bundles: dict[str, bytes] = {}
    for position, bundle in enumerate(bundle_values):
        if not isinstance(bundle, bytes):
            errors.append(f"factory bundle {position} must be bytes")
            continue
        bundle_errors, verified = verify_factory_bundle(bundle)
        errors.extend(
            f"factory bundle {position}: {error}" for error in bundle_errors
        )
        if verified is None:
            continue
        factory_id = verified["factory_id"]
        if factory_id in bundles:
            errors.append(f"duplicate factory bundle id: {factory_id}")
            continue
        bundles[factory_id] = bundle
    return errors, bundles


def _load_checked_schema(schema: Any | None = None) -> dict[str, Any]:
    checked = schema if schema is not None else load_json_file(VALIDATION_PACK_SCHEMA_PATH)
    if (
        not isinstance(checked, dict)
        or checked.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or checked.get("$id") != VALIDATION_PACK_MANIFEST_SCHEMA_REFERENCE
        or sha256_json(checked) != VALIDATION_PACK_MANIFEST_SCHEMA_SHA256
    ):
        raise ValueError("improvement-validation input-pack manifest schema is invalid")
    return checked


def _pack_payloads(
    validation_plan: dict[str, Any],
    validation_plan_specification: dict[str, Any],
    candidate: dict[str, Any],
    candidate_specification: dict[str, Any],
    classification: dict[str, Any],
    classification_policy: dict[str, Any],
    proposal: dict[str, Any],
    proposal_specification: dict[str, Any],
    observation: dict[str, Any],
    observation_specification: dict[str, Any],
    evidence_return: dict[str, Any],
    portfolio_plan: dict[str, Any],
    portfolio_definition: dict[str, Any],
    bundle_index: dict[str, bytes],
    runtime_evidence_pack: bytes,
    qualification_plan: dict[str, Any],
    qualification_policy: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, bytes]:
    documents = {
        VALIDATION_PLAN_PATH: validation_plan,
        VALIDATION_PLAN_SPEC_PATH: validation_plan_specification,
        CANDIDATE_PATH: candidate,
        CANDIDATE_SPEC_PATH: candidate_specification,
        CLASSIFICATION_PATH: classification,
        CLASSIFICATION_POLICY_PATH: classification_policy,
        PROPOSAL_PATH: proposal,
        PROPOSAL_SPEC_PATH: proposal_specification,
        OBSERVATION_PATH: observation,
        OBSERVATION_SPEC_PATH: observation_specification,
        EVIDENCE_RETURN_PATH: evidence_return,
        PORTFOLIO_PLAN_PATH: portfolio_plan,
        PORTFOLIO_DEFINITION_PATH: portfolio_definition,
        QUALIFICATION_PLAN_PATH: qualification_plan,
        QUALIFICATION_POLICY_PATH: qualification_policy,
        PACKED_SCHEMA_PATH: schema,
    }
    payloads = {
        path: canonical_json_bytes(document) for path, document in documents.items()
    }
    payloads[RUNTIME_EVIDENCE_PACK_PATH] = runtime_evidence_pack
    for factory in portfolio_plan["factories"]:
        factory_id = factory["id"]
        if factory_id not in bundle_index:
            raise ValueError(f"missing factory bundle for portfolio member: {factory_id}")
        payloads[_factory_path(factory_id)] = bundle_index[factory_id]
    if set(bundle_index) != {factory["id"] for factory in portfolio_plan["factories"]}:
        raise ValueError("factory bundles must exactly match the portfolio plan")
    return payloads


def _file_role(path: str) -> str:
    if path in JSON_PATH_ROLES:
        return JSON_PATH_ROLES[path]
    if path == RUNTIME_EVIDENCE_PACK_PATH:
        return "runtime_evidence_pack"
    if path.startswith("factories/") and path.endswith(".factory.tar"):
        return "factory_bundle"
    raise ValueError(f"unknown improvement-validation input-pack member: {path}")


def build_validation_pack_manifest(
    validation_plan: dict[str, Any],
    validation_plan_specification: dict[str, Any],
    candidate: dict[str, Any],
    candidate_specification: dict[str, Any],
    classification: dict[str, Any],
    classification_policy: dict[str, Any],
    proposal: dict[str, Any],
    proposal_specification: dict[str, Any],
    observation: dict[str, Any],
    observation_specification: dict[str, Any],
    evidence_return: dict[str, Any],
    portfolio_plan: dict[str, Any],
    portfolio_definition: dict[str, Any],
    runtime_evidence_pack: bytes,
    qualification_plan: dict[str, Any],
    qualification_policy: dict[str, Any],
    payloads: dict[str, bytes],
) -> dict[str, Any]:
    source = validation_plan["source"]
    return {
        "contract_schema": VALIDATION_PACK_MANIFEST_SCHEMA_REFERENCE,
        "schema_version": VALIDATION_PACK_MANIFEST_SCHEMA_VERSION,
        "source": {
            "factory_improvement_validation_plan_sha256": validation_plan[
                "factory_improvement_validation_plan_sha256"
            ],
            "validation_plan_specification_sha256": sha256_json(
                validation_plan_specification
            ),
            "factory_improvement_candidate_sha256": candidate[
                "factory_improvement_candidate_sha256"
            ],
            "candidate_specification_sha256": sha256_json(candidate_specification),
            "candidate_artifact_sha256": source["candidate_artifact_sha256"],
            "factory_improvement_classification_sha256": classification[
                "factory_improvement_classification_sha256"
            ],
            "improvement_classification_policy_sha256": sha256_json(
                classification_policy
            ),
            "factory_improvement_proposal_sha256": proposal[
                "factory_improvement_proposal_sha256"
            ],
            "improvement_proposal_specification_sha256": sha256_json(
                proposal_specification
            ),
            "factory_improvement_observation_sha256": observation[
                "factory_improvement_observation_sha256"
            ],
            "improvement_observation_specification_sha256": sha256_json(
                observation_specification
            ),
            "factory_evidence_return_sha256": evidence_return[
                "factory_evidence_return_sha256"
            ],
            "factory_portfolio_plan_sha256": portfolio_plan[
                "factory_portfolio_plan_sha256"
            ],
            "portfolio_definition_sha256": sha256_json(portfolio_definition),
            "factory_bundle_set_sha256": portfolio_plan["source"][
                "factory_bundle_set_sha256"
            ],
            "runtime_evidence_pack_sha256": sha256_bytes(runtime_evidence_pack),
            "qualification_plan_sha256": qualification_plan[
                "qualification_plan_sha256"
            ],
            "qualification_policy_id": qualification_policy["policy_id"],
            "qualification_policy_sha256": sha256_json(qualification_policy),
            "reporting_factory": source["reporting_factory"],
            "control_factory": source["control_factory"],
        },
        "files": [
            {
                "path": path,
                "role": _file_role(path),
                "media_type": (
                    "application/json"
                    if path in JSON_PATH_ROLES
                    else "application/x-ustar"
                ),
                "sha256": sha256_bytes(payloads[path]),
                "size": len(payloads[path]),
            }
            for path in sorted(payloads)
        ],
        "factories": [
            {
                "position": factory["position"],
                "id": factory["id"],
                "class": factory["class"],
                "path": _factory_path(factory["id"]),
                "bundle_sha256": factory["bundle_sha256"],
            }
            for factory in portfolio_plan["factories"]
        ],
        "validation_summary": deepcopy(validation_plan["summary"]),
        "pack_boundary": deepcopy(PACK_BOUNDARY),
    }


def _verify_complete_chain(
    validation_plan: Any,
    validation_plan_specification: Any,
    candidate: Any,
    candidate_specification: Any,
    classification: Any,
    classification_policy: Any,
    proposal: Any,
    proposal_specification: Any,
    observation: Any,
    observation_specification: Any,
    evidence_return: Any,
    portfolio_plan: Any,
    portfolio_definition: Any,
    bundle_values: Any,
    runtime_evidence_pack: Any,
    qualification_plan: Any,
    qualification_policy: Any,
) -> list[str]:
    if not isinstance(validation_plan, dict):
        return ["improvement validation plan must be an object"]
    source = validation_plan.get("source")
    source_factory_id = source.get("reporting_factory") if isinstance(source, dict) else None
    return verify_factory_improvement_validation_plan_for_inputs(
        validation_plan,
        validation_plan_specification,
        candidate,
        candidate_specification,
        classification,
        classification_policy,
        proposal,
        proposal_specification,
        observation,
        observation_specification,
        evidence_return,
        portfolio_plan,
        portfolio_definition,
        bundle_values,
        source_factory_id,
        runtime_evidence_pack,
        qualification_plan,
        qualification_policy,
    )


def factory_improvement_validation_pack_for_inputs(
    validation_plan: Any,
    validation_plan_specification: Any,
    candidate: Any,
    candidate_specification: Any,
    classification: Any,
    classification_policy: Any,
    proposal: Any,
    proposal_specification: Any,
    observation: Any,
    observation_specification: Any,
    evidence_return: Any,
    portfolio_plan: Any,
    portfolio_definition: Any,
    bundle_values: Any,
    runtime_evidence_pack: Any,
    qualification_plan: Any,
    qualification_policy: Any,
    schema: Any | None = None,
) -> tuple[list[str], bytes | None, dict[str, Any] | None]:
    errors = _verify_complete_chain(
        validation_plan,
        validation_plan_specification,
        candidate,
        candidate_specification,
        classification,
        classification_policy,
        proposal,
        proposal_specification,
        observation,
        observation_specification,
        evidence_return,
        portfolio_plan,
        portfolio_definition,
        bundle_values,
        runtime_evidence_pack,
        qualification_plan,
        qualification_policy,
    )
    bundle_errors, bundles = _bundle_index(bundle_values)
    errors.extend(bundle_errors)
    if errors:
        return errors, None, None
    try:
        checked_schema = _load_checked_schema(schema)
        document_values = (
            validation_plan,
            validation_plan_specification,
            candidate,
            candidate_specification,
            classification,
            classification_policy,
            proposal,
            proposal_specification,
            observation,
            observation_specification,
            evidence_return,
            portfolio_plan,
            portfolio_definition,
            qualification_plan,
            qualification_policy,
        )
        if not all(isinstance(value, dict) for value in document_values):
            raise ValueError("every improvement-validation pack document must be an object")
        if not isinstance(runtime_evidence_pack, bytes):
            raise ValueError("runtime-evidence pack must be bytes")
        payloads = _pack_payloads(
            validation_plan,
            validation_plan_specification,
            candidate,
            candidate_specification,
            classification,
            classification_policy,
            proposal,
            proposal_specification,
            observation,
            observation_specification,
            evidence_return,
            portfolio_plan,
            portfolio_definition,
            bundles,
            runtime_evidence_pack,
            qualification_plan,
            qualification_policy,
            checked_schema,
        )
        manifest = build_validation_pack_manifest(
            validation_plan,
            validation_plan_specification,
            candidate,
            candidate_specification,
            classification,
            classification_policy,
            proposal,
            proposal_specification,
            observation,
            observation_specification,
            evidence_return,
            portfolio_plan,
            portfolio_definition,
            runtime_evidence_pack,
            qualification_plan,
            qualification_policy,
            payloads,
        )
        archive_payloads = dict(payloads)
        archive_payloads[MANIFEST_PATH] = canonical_json_bytes(manifest)
        if len(archive_payloads) > MAX_VALIDATION_PACK_MEMBERS:
            raise ValueError("improvement-validation input-pack member count exceeds boundary")
        if any(
            not value or len(value) > MAX_VALIDATION_PACK_MEMBER_BYTES
            for value in archive_payloads.values()
        ):
            raise ValueError("improvement-validation input-pack member size exceeds boundary")
        pack = canonical_tar_bytes(archive_payloads)
        if len(pack) > MAX_VALIDATION_PACK_BYTES:
            raise ValueError("improvement-validation input-pack exceeds size boundary")
    except (KeyError, OSError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot build improvement-validation input pack: {exc}"], None, None
    return [], pack, manifest


def _parse_json_payloads(
    payloads: dict[str, bytes], paths: set[str]
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    parsed: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for path in paths:
        value = payloads.get(path)
        if value is None:
            continue
        try:
            document = load_json_bytes(value)
            if not isinstance(document, dict):
                raise ValueError("root must be an object")
            if canonical_json_bytes(document) != value:
                raise ValueError("member is not canonical JSON")
        except (RecursionError, TypeError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"cannot parse improvement-validation input-pack member {path}: {exc}")
            continue
        parsed[path] = document
    return parsed, errors


def verify_factory_improvement_validation_pack(
    pack: bytes,
) -> tuple[list[str], dict[str, Any] | None]:
    payloads, errors = read_bounded_archive_payloads(
        pack,
        label="improvement-validation input pack",
        max_archive_bytes=MAX_VALIDATION_PACK_BYTES,
        max_member_bytes=MAX_VALIDATION_PACK_MEMBER_BYTES,
        max_members=MAX_VALIDATION_PACK_MEMBERS,
    )
    fixed_paths = {MANIFEST_PATH, *JSON_PATH_ROLES, RUNTIME_EVIDENCE_PACK_PATH}
    missing = fixed_paths - set(payloads)
    if missing:
        errors.append(
            "improvement-validation input pack missing required members: "
            + ", ".join(sorted(missing))
        )
    json_paths = {MANIFEST_PATH, *JSON_PATH_ROLES}
    parsed, parse_errors = _parse_json_payloads(payloads, json_paths)
    errors.extend(parse_errors)
    if errors or not json_paths <= set(parsed):
        return errors, None

    manifest = parsed[MANIFEST_PATH]
    schema = parsed[PACKED_SCHEMA_PATH]
    try:
        _load_checked_schema(schema)
    except (OSError, RecursionError, TypeError, ValueError) as exc:
        errors.append(str(exc))

    bundle_paths = {
        path
        for path in payloads
        if path.startswith("factories/") and path.endswith(".factory.tar")
    }
    other_extra = set(payloads) - fixed_paths - bundle_paths
    if other_extra:
        errors.append(
            "improvement-validation input pack contains unexpected members: "
            + ", ".join(sorted(other_extra))
        )
    bundle_values = [payloads[path] for path in sorted(bundle_paths)]
    bundle_errors, bundles = _bundle_index(bundle_values)
    errors.extend(bundle_errors)
    if errors:
        return errors, None

    validation_plan = parsed[VALIDATION_PLAN_PATH]
    validation_plan_specification = parsed[VALIDATION_PLAN_SPEC_PATH]
    candidate = parsed[CANDIDATE_PATH]
    candidate_specification = parsed[CANDIDATE_SPEC_PATH]
    classification = parsed[CLASSIFICATION_PATH]
    classification_policy = parsed[CLASSIFICATION_POLICY_PATH]
    proposal = parsed[PROPOSAL_PATH]
    proposal_specification = parsed[PROPOSAL_SPEC_PATH]
    observation = parsed[OBSERVATION_PATH]
    observation_specification = parsed[OBSERVATION_SPEC_PATH]
    evidence_return = parsed[EVIDENCE_RETURN_PATH]
    portfolio_plan = parsed[PORTFOLIO_PLAN_PATH]
    portfolio_definition = parsed[PORTFOLIO_DEFINITION_PATH]
    qualification_plan = parsed[QUALIFICATION_PLAN_PATH]
    qualification_policy = parsed[QUALIFICATION_POLICY_PATH]
    runtime_evidence_pack = payloads[RUNTIME_EVIDENCE_PACK_PATH]

    chain_errors = _verify_complete_chain(
        validation_plan,
        validation_plan_specification,
        candidate,
        candidate_specification,
        classification,
        classification_policy,
        proposal,
        proposal_specification,
        observation,
        observation_specification,
        evidence_return,
        portfolio_plan,
        portfolio_definition,
        bundle_values,
        runtime_evidence_pack,
        qualification_plan,
        qualification_policy,
    )
    errors.extend(f"embedded validation chain: {error}" for error in chain_errors)
    if errors:
        return errors, None
    try:
        expected_payloads = _pack_payloads(
            validation_plan,
            validation_plan_specification,
            candidate,
            candidate_specification,
            classification,
            classification_policy,
            proposal,
            proposal_specification,
            observation,
            observation_specification,
            evidence_return,
            portfolio_plan,
            portfolio_definition,
            bundles,
            runtime_evidence_pack,
            qualification_plan,
            qualification_policy,
            schema,
        )
        expected_members = {MANIFEST_PATH, *expected_payloads}
        missing = expected_members - set(payloads)
        extra = set(payloads) - expected_members
        if missing:
            errors.append(
                "improvement-validation input pack missing exact members: "
                + ", ".join(sorted(missing))
            )
        if extra:
            errors.append(
                "improvement-validation input pack contains unexpected members: "
                + ", ".join(sorted(extra))
            )
        expected_manifest = build_validation_pack_manifest(
            validation_plan,
            validation_plan_specification,
            candidate,
            candidate_specification,
            classification,
            classification_policy,
            proposal,
            proposal_specification,
            observation,
            observation_specification,
            evidence_return,
            portfolio_plan,
            portfolio_definition,
            runtime_evidence_pack,
            qualification_plan,
            qualification_policy,
            expected_payloads,
        )
        if canonical_json_bytes(manifest) != canonical_json_bytes(expected_manifest):
            errors.append(
                "improvement-validation input-pack manifest does not exactly match its verified inputs"
            )
        rebuilt_payloads = dict(expected_payloads)
        rebuilt_payloads[MANIFEST_PATH] = canonical_json_bytes(expected_manifest)
        if pack != canonical_tar_bytes(rebuilt_payloads):
            errors.append("improvement-validation input pack is not the canonical archive")
    except (KeyError, OSError, RecursionError, TypeError, ValueError) as exc:
        errors.append(f"cannot reconstruct improvement-validation input pack: {exc}")
    if errors:
        return errors, None
    return [], manifest
