#!/usr/bin/env python3
"""Bind a verified runtime-evidence pack to one non-authorizing portfolio route."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from factory_composer import canonical_json_bytes, load_json_file, sha256_json
from factory_evidence_pack import (
    MAX_PACK_BYTES,
    verify_runtime_evidence_pack_for_bundle,
)
from factory_portfolio import (
    build_factory_portfolio_plan,
    verified_factory_portfolio_inputs,
)


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_EVIDENCE_RETURN_PATH = (
    ROOT / "examples" / "economic-factory.evidence-return.json"
)

EVIDENCE_RETURN_SCHEMA_VERSION = "zaibatsu.factory-evidence-return.v1"
EVIDENCE_RETURN_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.12.0/schemas/factory-evidence-return.schema.json"
)
MAX_EVIDENCE_RETURN_JSON_BYTES = 2 * 1024 * 1024

EVIDENCE_RETURN_FIELDS = {
    "contract_schema",
    "schema_version",
    "portfolio",
    "route",
    "factory",
    "evidence",
    "review_boundary",
    "factory_evidence_return_sha256",
}
EVIDENCE_RETURN_OBJECT_FIELDS = {
    "portfolio",
    "route",
    "factory",
    "evidence",
    "review_boundary",
}

REVIEW_BOUNDARY = {
    "portfolio_plan_verified": True,
    "route_binding_verified": True,
    "source_bundle_verified": True,
    "runtime_evidence_pack_verified": True,
    "evidence_only_route_declared": True,
    "signatures_and_bindings_reverified": True,
    "artifact_digests_verified": True,
    "transport_observed": False,
    "content_safety_scanned": False,
    "secret_absence_proved": False,
    "verifier_assertions_reexecuted": False,
    "artifact_semantic_truth_verified": False,
    "contains_improvement_candidate": False,
    "classification_performed": False,
    "changes_shared_policy": False,
    "shared_promotion_eligible": False,
    "promotion_authorized": False,
    "activation_authorized": False,
    "execution_authorized": False,
    "cross_factory_effects_authorized": False,
}


def _canonical_equal(left: Any, right: Any) -> bool:
    try:
        return canonical_json_bytes(left) == canonical_json_bytes(right)
    except (RecursionError, TypeError, ValueError):
        return False


def load_factory_evidence_return(
    path: Path = EXAMPLE_EVIDENCE_RETURN_PATH,
) -> Any:
    return load_json_file(path)


def _precheck_factory_evidence_return(record: Any) -> list[str]:
    """Reject structurally impossible or self-inconsistent records cheaply."""
    if not isinstance(record, dict):
        return ["factory evidence-return record root must be an object"]
    if set(record) != EVIDENCE_RETURN_FIELDS:
        return [
            "factory evidence-return record must contain exactly the "
            "versioned fields"
        ]
    if record.get("contract_schema") != EVIDENCE_RETURN_SCHEMA_REFERENCE:
        return ["factory evidence-return record must reference its immutable schema"]
    if record.get("schema_version") != EVIDENCE_RETURN_SCHEMA_VERSION:
        return [
            "factory evidence-return record schema_version must equal "
            f"{EVIDENCE_RETURN_SCHEMA_VERSION}"
        ]
    if any(
        not isinstance(record.get(field), dict)
        for field in EVIDENCE_RETURN_OBJECT_FIELDS
    ):
        return ["factory evidence-return record sections must be objects"]
    try:
        canonical_size = len(canonical_json_bytes(record))
    except (RecursionError, TypeError, ValueError):
        return ["factory evidence-return record must be canonical JSON data"]
    if not 0 < canonical_size <= MAX_EVIDENCE_RETURN_JSON_BYTES:
        return ["factory evidence-return record size is outside the accepted boundary"]
    recorded_digest = record.get("factory_evidence_return_sha256")
    if (
        not isinstance(recorded_digest, str)
        or len(recorded_digest) != 64
        or any(character not in "0123456789abcdef" for character in recorded_digest)
    ):
        return ["factory evidence-return record digest must be lowercase SHA-256"]
    without_digest = dict(record)
    without_digest.pop("factory_evidence_return_sha256")
    if sha256_json(without_digest) != recorded_digest:
        return ["factory evidence-return record digest does not match its content"]
    return []


def _economic_factory_and_route(
    portfolio: dict[str, Any],
    plan: dict[str, Any],
    source_factory_id: Any,
) -> tuple[list[str], dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(source_factory_id, str):
        return ["evidence-return source factory id must be a string"], None, None
    factory = next(
        (
            item
            for item in portfolio["factories"]
            if item["id"] == source_factory_id
        ),
        None,
    )
    if factory is None:
        return ["evidence-return source factory is not in the closed registry"], None, None
    if factory["class"] != "economic_factory":
        return ["evidence-return source must be an economic factory"], None, None
    routes = [
        route
        for route in plan["evidence_routes"]
        if route["from_factory"] == source_factory_id
    ]
    if len(routes) != 1:
        return ["evidence-return source must have exactly one verified route"], None, None
    return [], factory, routes[0]


def build_factory_evidence_return(
    portfolio: dict[str, Any],
    plan: dict[str, Any],
    factory: dict[str, Any],
    route: dict[str, Any],
    verified_pack: dict[str, Any],
) -> dict[str, Any]:
    """Build the exact route-bound record from fully verified inputs."""
    manifest = verified_pack["manifest"]
    source = manifest["source"]
    record_without_digest: dict[str, Any] = {
        "contract_schema": EVIDENCE_RETURN_SCHEMA_REFERENCE,
        "schema_version": EVIDENCE_RETURN_SCHEMA_VERSION,
        "portfolio": {
            "id": portfolio["portfolio"]["id"],
            "factory_portfolio_plan_sha256": plan[
                "factory_portfolio_plan_sha256"
            ],
            "portfolio_definition_sha256": plan["source"][
                "portfolio_definition_sha256"
            ],
            "factory_bundle_set_sha256": plan["source"][
                "factory_bundle_set_sha256"
            ],
        },
        "route": deepcopy(route),
        "factory": {
            "id": factory["id"],
            "class": factory["class"],
            "bundle_sha256": route["from_bundle_sha256"],
        },
        "evidence": {
            "kind": "runtime_evidence_pack",
            "runtime_evidence_pack_sha256": verified_pack[
                "runtime_evidence_pack_sha256"
            ],
            "runtime_evidence_pack_manifest_sha256": sha256_json(manifest),
            "runtime_evidence_set_sha256": source[
                "runtime_evidence_set_sha256"
            ],
            "verifier_registry_sha256": source["verifier_registry_sha256"],
            "qualification_plan_sha256": source["qualification_plan_sha256"],
            "qualification_policy_sha256": source[
                "qualification_policy_sha256"
            ],
            "qualification_scope": source["qualification_scope"],
            "signed_receipt_count": len(manifest["receipts"]),
        },
        "review_boundary": deepcopy(REVIEW_BOUNDARY),
    }
    record = dict(record_without_digest)
    record["factory_evidence_return_sha256"] = sha256_json(record_without_digest)
    return record


def factory_evidence_return_for_inputs(
    plan: Any,
    portfolio: Any,
    bundle_values: Any,
    source_factory_id: Any,
    runtime_evidence_pack: Any,
    qualification_plan: Any,
    qualification_policy: Any,
) -> tuple[list[str], dict[str, Any] | None]:
    errors, verified_bundles, bundle_bytes = verified_factory_portfolio_inputs(
        portfolio,
        bundle_values,
    )
    if errors or not isinstance(portfolio, dict):
        return errors, None
    try:
        expected_plan = build_factory_portfolio_plan(portfolio, verified_bundles)
    except (KeyError, StopIteration, TypeError, ValueError) as exc:
        return [f"cannot derive expected factory portfolio plan: {exc}"], None
    if not _canonical_equal(plan, expected_plan):
        return ["evidence return requires the exact verified portfolio plan"], None
    route_errors, factory, route = _economic_factory_and_route(
        portfolio,
        expected_plan,
        source_factory_id,
    )
    if route_errors or factory is None or route is None:
        return route_errors, None
    if not isinstance(runtime_evidence_pack, bytes):
        return ["runtime-evidence pack must be bytes"], None
    if not 0 < len(runtime_evidence_pack) <= MAX_PACK_BYTES:
        return ["runtime-evidence pack size is outside the accepted boundary"], None
    try:
        pack_errors, verified_pack = verify_runtime_evidence_pack_for_bundle(
            runtime_evidence_pack,
            qualification_plan,
            bundle_bytes[source_factory_id],
            qualification_policy,
        )
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot verify runtime-evidence pack for return: {exc}"], None
    if pack_errors or verified_pack is None:
        return [
            f"evidence-return runtime-evidence pack: {error}"
            for error in pack_errors
        ], None
    try:
        record = build_factory_evidence_return(
            portfolio,
            expected_plan,
            factory,
            route,
            verified_pack,
        )
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot build factory evidence-return record: {exc}"], None
    return [], record


def verify_factory_evidence_return_for_inputs(
    record: Any,
    plan: Any,
    portfolio: Any,
    bundle_values: Any,
    source_factory_id: Any,
    runtime_evidence_pack: Any,
    qualification_plan: Any,
    qualification_policy: Any,
) -> list[str]:
    precheck_errors = _precheck_factory_evidence_return(record)
    if precheck_errors:
        return precheck_errors
    errors, expected = factory_evidence_return_for_inputs(
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
            "factory evidence-return record must exactly match its verified "
            "route, bundle, and runtime-evidence pack"
        ]
    return []
