#!/usr/bin/env python3
"""Build deterministic, non-executing factory rebuild plans."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from factory_bundle import verify_factory_bundle
from factory_composer import canonical_json_bytes, load_json_file, sha256_json
from factory_qualification import validate_qualification_assessment
from factory_source_lock import validate_source_lock


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_REBUILD_PLAN_PATH = ROOT / "examples" / "economic-factory.rebuild-plan.json"
REBUILD_PLAN_SCHEMA_VERSION = "zaibatsu.factory-rebuild-plan.v1"
REBUILD_PLAN_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.8.0/schemas/factory-rebuild-plan.schema.json"
)

ACTION_INTENTS = {
    "source_versioning": "bind_versioned_runtime_source",
    "static_secrets": "recover_encrypted_static_secrets",
    "runtime_secrets": "materialize_bounded_runtime_secrets",
    "host_reproduction": "apply_host_configuration",
    "worker_environment": "realize_worker_environment",
    "scheduling": "install_scheduler_disabled",
    "execution": "run_isolated_worker_acceptance",
    "verification": "verify_candidate_artifacts",
    "feedback": "configure_evidence_return",
}

REBUILD_PLAN_FIELDS = {
    "contract_schema",
    "schema_version",
    "factory",
    "source",
    "actions",
    "gates",
    "summary",
    "rebuild_boundary",
    "factory_rebuild_plan_sha256",
}

REBUILD_BOUNDARY = {
    "plan_only": True,
    "control_inputs_reverified": True,
    "remote_repository_contacted": False,
    "contains_runtime_implementations": False,
    "executes_rebuild_actions": False,
    "reads_or_materializes_secrets": False,
    "runs_ansible": False,
    "realizes_nix": False,
    "installs_or_enables_scheduler": False,
    "invokes_model": False,
    "grants_qualification_evidence": False,
    "grants_owner_approval": False,
    "activation_authorized": False,
    "deploys_infrastructure": False,
    "proves_runtime_recovery": False,
}


def load_rebuild_plan(
    path: Path = EXAMPLE_REBUILD_PLAN_PATH,
) -> dict[str, Any]:
    return load_json_file(path)


def _action_id(slot: str) -> str:
    return "realize-" + slot.replace("_", "-")


def _json_exactly_equal(left: Any, right: Any) -> bool:
    try:
        return canonical_json_bytes(left) == canonical_json_bytes(right)
    except (RecursionError, TypeError, ValueError):
        return False


def build_factory_rebuild_plan(
    verified_bundle: dict[str, Any],
    source_lock: dict[str, Any],
    qualification_assessment: dict[str, Any],
) -> dict[str, Any]:
    """Compile verified control and qualification state into an inert DAG."""
    control_plan = verified_bundle["plan"]
    assessed_by_position = {
        module["position"]: module
        for module in qualification_assessment["modules"]
    }
    eligible_by_slot = {
        module["slot"]: module["runtime_eligible"]
        for module in qualification_assessment["modules"]
    }
    action_ids = {
        module["slot"]: _action_id(module["slot"])
        for module in control_plan["modules"]
    }

    actions: list[dict[str, Any]] = []
    qualification_ready_actions = 0
    for resolved in control_plan["modules"]:
        assessed = assessed_by_position[resolved["position"]]
        requires_actions = [
            action_ids[slot] for slot in resolved["requires_slots"]
        ]
        dependency_blockers = [
            action_ids[slot]
            for slot in resolved["requires_slots"]
            if not eligible_by_slot[slot]
        ]
        missing_evidence = list(assessed["missing_evidence"])
        qualification_ready = (
            assessed["runtime_eligible"]
            and not missing_evidence
            and not dependency_blockers
        )
        if missing_evidence:
            status = "blocked_missing_evidence"
        elif dependency_blockers:
            status = "blocked_dependency"
        elif not assessed["runtime_eligible"]:
            status = "blocked_qualification"
        else:
            status = "qualified_not_authorized"
        qualification_ready_actions += int(qualification_ready)
        actions.append(
            {
                "position": resolved["position"],
                "action_id": action_ids[resolved["slot"]],
                "intent": ACTION_INTENTS[resolved["slot"]],
                "slot": resolved["slot"],
                "module": resolved["module"],
                "artifact_sha256": resolved["artifact"]["sha256"],
                "requires_actions": requires_actions,
                "verified_evidence": list(assessed["verified_evidence"]),
                "missing_evidence": missing_evidence,
                "dependency_blockers": dependency_blockers,
                "status": status,
                "qualification_ready": qualification_ready,
                "execution_authorized": False,
                "side_effect_authority": False,
            }
        )

    blocked_actions = [
        action["action_id"]
        for action in actions
        if not action["qualification_ready"]
    ]
    qualification_complete = not blocked_actions
    gates = [
        {
            "position": 0,
            "gate_id": "control-artifacts-reverified",
            "requires_gates": [],
            "status": "passed",
            "blockers": [],
            "grants_authority": False,
        },
        {
            "position": 1,
            "gate_id": "all-modules-runtime-qualified",
            "requires_gates": ["control-artifacts-reverified"],
            "status": "passed" if qualification_complete else "blocked",
            "blockers": blocked_actions,
            "grants_authority": False,
        },
        {
            "position": 2,
            "gate_id": "owner-activation-approval",
            "requires_gates": ["all-modules-runtime-qualified"],
            "status": "not_requested",
            "blockers": (
                [] if qualification_complete else ["runtime-qualification-incomplete"]
            ),
            "grants_authority": False,
        },
        {
            "position": 3,
            "gate_id": "factory-activation",
            "requires_gates": ["owner-activation-approval"],
            "status": "not_authorized",
            "blockers": [
                *(
                    []
                    if qualification_complete
                    else ["runtime-qualification-incomplete"]
                ),
                "owner-approval-not-granted",
            ],
            "grants_authority": False,
        },
    ]

    assessment_source = qualification_assessment["source"]
    plan_without_digest: dict[str, Any] = {
        "contract_schema": REBUILD_PLAN_SCHEMA_REFERENCE,
        "schema_version": REBUILD_PLAN_SCHEMA_VERSION,
        "factory": deepcopy(qualification_assessment["factory"]),
        "source": {
            "bundle_sha256": verified_bundle["bundle_sha256"],
            "factory_plan_sha256": verified_bundle["plan_sha256"],
            "module_catalog_sha256": verified_bundle["manifest"]["source"][
                "module_catalog_sha256"
            ],
            "factory_source_lock_sha256": source_lock[
                "factory_source_lock_sha256"
            ],
            "control_source_release_tag": source_lock["repository"][
                "release_tag"
            ],
            "control_source_commit_oid": source_lock["repository"]["commit_oid"],
            "qualification_policy_id": assessment_source[
                "qualification_policy_id"
            ],
            "qualification_policy_sha256": assessment_source[
                "qualification_policy_sha256"
            ],
            "qualification_plan_sha256": assessment_source[
                "qualification_plan_sha256"
            ],
            "qualification_evidence_sha256": assessment_source[
                "qualification_evidence_sha256"
            ],
            "qualification_assessment_sha256": qualification_assessment[
                "qualification_assessment_sha256"
            ],
            "module_api_version": assessment_source["module_api_version"],
        },
        "actions": actions,
        "gates": gates,
        "summary": {
            "action_count": len(actions),
            "qualification_ready_actions": qualification_ready_actions,
            "blocked_actions": len(actions) - qualification_ready_actions,
            "verified_evidence_bindings": qualification_assessment["summary"][
                "verified_evidence_bindings"
            ],
            "missing_evidence_bindings": qualification_assessment["summary"][
                "missing_evidence_bindings"
            ],
            "all_rebuild_actions_qualified": qualification_complete,
            "rebuild_executed": False,
            "factory_rebuilt": False,
            "activation_authorized": False,
        },
        "rebuild_boundary": deepcopy(REBUILD_BOUNDARY),
    }
    rebuild_plan = dict(plan_without_digest)
    rebuild_plan["factory_rebuild_plan_sha256"] = sha256_json(
        plan_without_digest
    )
    return rebuild_plan


def validate_factory_rebuild_plan(
    rebuild_plan: Any,
    expected: Any,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(rebuild_plan, dict):
        return ["factory rebuild plan root must be an object"]
    if set(rebuild_plan) != REBUILD_PLAN_FIELDS:
        errors.append("factory rebuild plan contains missing or unexpected fields")
    if rebuild_plan.get("contract_schema") != REBUILD_PLAN_SCHEMA_REFERENCE:
        errors.append("factory rebuild plan must reference its immutable schema")
    if rebuild_plan.get("schema_version") != REBUILD_PLAN_SCHEMA_VERSION:
        errors.append("factory rebuild plan schema_version is invalid")
    if not _json_exactly_equal(
        rebuild_plan.get("rebuild_boundary"),
        REBUILD_BOUNDARY,
    ):
        errors.append("factory rebuild plan must preserve the non-executing boundary")
    if not _json_exactly_equal(rebuild_plan, expected):
        errors.append(
            "factory rebuild plan does not exactly match its verified inputs"
        )
    return errors


def _verify_rebuild_inputs(
    source_lock: Any,
    qualification_assessment: Any,
    qualification_evidence: Any,
    qualification_plan: Any,
    bundle: bytes,
    qualification_policy: Any,
    repository: Path,
) -> tuple[list[str], dict[str, Any] | None]:
    bundle_errors, verified_bundle = verify_factory_bundle(bundle)
    errors = [f"factory bundle: {error}" for error in bundle_errors]
    if verified_bundle is None:
        return errors, None

    source_errors = validate_source_lock(source_lock, repository, bundle)
    errors.extend(f"factory source lock: {error}" for error in source_errors)
    assessment_errors = validate_qualification_assessment(
        qualification_assessment,
        qualification_evidence,
        verified_bundle,
        qualification_plan,
        qualification_policy,
    )
    errors.extend(
        f"qualification assessment: {error}" for error in assessment_errors
    )
    if errors:
        return errors, None
    return [], verified_bundle


def factory_rebuild_plan_for_bundle(
    source_lock: Any,
    qualification_assessment: Any,
    qualification_evidence: Any,
    qualification_plan: Any,
    bundle: bytes,
    qualification_policy: Any,
    repository: Path,
) -> tuple[list[str], dict[str, Any] | None]:
    errors, verified_bundle = _verify_rebuild_inputs(
        source_lock,
        qualification_assessment,
        qualification_evidence,
        qualification_plan,
        bundle,
        qualification_policy,
        repository,
    )
    if errors or verified_bundle is None:
        return errors, None
    try:
        rebuild_plan = build_factory_rebuild_plan(
            verified_bundle,
            source_lock,
            qualification_assessment,
        )
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot build factory rebuild plan: {exc}"], None
    return [], rebuild_plan


def verify_factory_rebuild_plan_for_bundle(
    rebuild_plan: Any,
    source_lock: Any,
    qualification_assessment: Any,
    qualification_evidence: Any,
    qualification_plan: Any,
    bundle: bytes,
    qualification_policy: Any,
    repository: Path,
) -> list[str]:
    errors, verified_bundle = _verify_rebuild_inputs(
        source_lock,
        qualification_assessment,
        qualification_evidence,
        qualification_plan,
        bundle,
        qualification_policy,
        repository,
    )
    if errors or verified_bundle is None:
        return errors
    try:
        expected = build_factory_rebuild_plan(
            verified_bundle,
            source_lock,
            qualification_assessment,
        )
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot rebuild expected factory rebuild plan: {exc}"]
    return validate_factory_rebuild_plan(rebuild_plan, expected)
