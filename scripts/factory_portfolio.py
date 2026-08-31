#!/usr/bin/env python3
"""Compose verified factory bundles into a closed, non-executing portfolio plan."""

from __future__ import annotations

import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from factory_bundle import verify_factory_bundle
from factory_composer import canonical_json_bytes, load_json_file, sha256_json


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PORTFOLIO_PATH = ROOT / "examples" / "factory-portfolio.json"
EXAMPLE_PORTFOLIO_PLAN_PATH = ROOT / "examples" / "factory-portfolio.plan.json"

PORTFOLIO_SCHEMA_VERSION = "zaibatsu.factory-portfolio.v1"
PORTFOLIO_PLAN_SCHEMA_VERSION = "zaibatsu.factory-portfolio-plan.v1"
PORTFOLIO_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.11.0/schemas/factory-portfolio.schema.json"
)
PORTFOLIO_PLAN_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.11.0/schemas/factory-portfolio-plan.schema.json"
)

MIN_FACTORIES = 2
MAX_FACTORIES = 64
MAX_PORTFOLIO_BYTES = 256 * 1024
MAX_PORTFOLIO_PLAN_BYTES = 1024 * 1024
MAX_ID_LENGTH = 64
MAX_PURPOSE_LENGTH = 512
FACTORY_ID_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"

PORTFOLIO_FIELDS = {
    "contract_schema",
    "schema_version",
    "portfolio",
    "factories",
    "evidence_routes",
    "policies",
}
PORTFOLIO_METADATA_FIELDS = {"id", "purpose", "control_factory"}
FACTORY_FIELDS = {"position", "id", "class"}
ROUTE_FIELDS = {
    "position",
    "from_factory",
    "to_factory",
    "kind",
    "payload_scope",
    "grants_authority",
    "can_self_promote",
}
EXPECTED_POLICIES = {
    "closed_registry": True,
    "unknown_factories_fail_closed": True,
    "one_control_factory": True,
    "factory_scoped_authority": True,
    "factory_scoped_secrets": True,
    "factory_scoped_workers": True,
    "factory_scoped_artifacts": True,
    "evidence_only_cross_factory_routes": True,
    "cross_factory_route_grants_authority": False,
    "factory_may_self_promote": False,
    "plan_executes_operations": False,
}
NAMESPACE_KINDS = (
    "authority",
    "repository",
    "static_secrets",
    "runtime_secrets",
    "worker_pool",
    "artifacts",
    "scheduler",
)


def _is_int(value: Any) -> bool:
    return type(value) is int


def _canonical_equal(left: Any, right: Any) -> bool:
    try:
        return canonical_json_bytes(left) == canonical_json_bytes(right)
    except (RecursionError, TypeError, ValueError):
        return False


def _valid_id(value: Any) -> bool:
    if not isinstance(value, str) or not value or len(value) > MAX_ID_LENGTH:
        return False
    return re.fullmatch(FACTORY_ID_PATTERN, value) is not None


def load_factory_portfolio(path: Path = EXAMPLE_PORTFOLIO_PATH) -> Any:
    return load_json_file(path)


def load_factory_portfolio_plan(path: Path = EXAMPLE_PORTFOLIO_PLAN_PATH) -> Any:
    return load_json_file(path)


def validate_factory_portfolio(data: Any) -> list[str]:
    """Validate the declarative closed registry and evidence-only routes."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["factory portfolio root must be an object"]
    if set(data) != PORTFOLIO_FIELDS:
        errors.append("factory portfolio must contain exactly the versioned fields")
    if data.get("contract_schema") != PORTFOLIO_SCHEMA_REFERENCE:
        errors.append("factory portfolio must reference its immutable project schema")
    if data.get("schema_version") != PORTFOLIO_SCHEMA_VERSION:
        errors.append(
            f"factory portfolio schema_version must equal {PORTFOLIO_SCHEMA_VERSION}"
        )

    metadata = data.get("portfolio")
    if not isinstance(metadata, dict):
        errors.append("factory portfolio metadata must be an object")
        metadata = {}
    elif set(metadata) != PORTFOLIO_METADATA_FIELDS:
        errors.append("factory portfolio metadata contains missing or unexpected fields")
    portfolio_id = metadata.get("id")
    if not _valid_id(portfolio_id):
        errors.append("factory portfolio id must be a lowercase kebab-case identifier")
    purpose = metadata.get("purpose")
    if (
        not isinstance(purpose, str)
        or not purpose.strip()
        or len(purpose) > MAX_PURPOSE_LENGTH
    ):
        errors.append("factory portfolio purpose must be non-empty and bounded")
    control_factory = metadata.get("control_factory")
    if not _valid_id(control_factory):
        errors.append("factory portfolio control_factory must be a valid identifier")

    factories = data.get("factories")
    if not isinstance(factories, list):
        return errors + ["factory portfolio factories must be a list"]
    if not MIN_FACTORIES <= len(factories) <= MAX_FACTORIES:
        errors.append(
            f"factory portfolio must contain between {MIN_FACTORIES} and "
            f"{MAX_FACTORIES} factories"
        )
        return errors
    valid_factories: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for index, factory in enumerate(factories):
        if not isinstance(factory, dict):
            errors.append(f"factory portfolio entry {index} must be an object")
            continue
        if set(factory) != FACTORY_FIELDS:
            errors.append(
                f"factory portfolio entry {index} contains missing or unexpected fields"
            )
        position = factory.get("position")
        if not _is_int(position) or position != index:
            errors.append(f"factory portfolio entry {index} has a noncanonical position")
        factory_id = factory.get("id")
        if not _valid_id(factory_id):
            errors.append(f"factory portfolio entry {index} has an invalid id")
            continue
        if factory_id in seen_ids:
            errors.append(f"duplicate factory portfolio id: {factory_id}")
        seen_ids.add(factory_id)
        factory_class = factory.get("class")
        if not isinstance(factory_class, str) or factory_class not in {
            "control_factory",
            "economic_factory",
        }:
            errors.append(f"{factory_id}: invalid factory class")
            continue
        valid_factories.append(factory)

    controls = [
        factory
        for factory in valid_factories
        if factory.get("class") == "control_factory"
    ]
    economics = [
        factory
        for factory in valid_factories
        if factory.get("class") == "economic_factory"
    ]
    if len(controls) != 1:
        errors.append("factory portfolio must contain exactly one control factory")
    elif control_factory != controls[0].get("id"):
        errors.append("factory portfolio control_factory must name the control entry")
    if not economics:
        errors.append("factory portfolio must contain at least one economic factory")

    routes = data.get("evidence_routes")
    if not isinstance(routes, list):
        return errors + ["factory portfolio evidence_routes must be a list"]
    if not 1 <= len(routes) <= MAX_FACTORIES - 1:
        errors.append(
            "factory portfolio must contain between 1 and "
            f"{MAX_FACTORIES - 1} evidence routes"
        )
        return errors
    if len(routes) != len(economics):
        errors.append("every economic factory must have exactly one evidence-return route")
    route_sources: list[str] = []
    valid_ids = {factory["id"] for factory in valid_factories}
    economic_ids = [factory["id"] for factory in economics]
    for index, route in enumerate(routes):
        if not isinstance(route, dict):
            errors.append(f"factory portfolio route {index} must be an object")
            continue
        if set(route) != ROUTE_FIELDS:
            errors.append(
                f"factory portfolio route {index} contains missing or unexpected fields"
            )
        if not _is_int(route.get("position")) or route.get("position") != index:
            errors.append(f"factory portfolio route {index} has a noncanonical position")
        source = route.get("from_factory")
        destination = route.get("to_factory")
        if not isinstance(source, str) or source not in valid_ids:
            errors.append(f"factory portfolio route {index} has an unknown source")
        else:
            route_sources.append(source)
            if source not in economic_ids:
                errors.append(
                    f"factory portfolio route {index} must originate at an economic factory"
                )
        if destination != control_factory:
            errors.append(
                f"factory portfolio route {index} must terminate at the control factory"
            )
        if source == destination:
            errors.append(f"factory portfolio route {index} may not be a self-route")
        if route.get("kind") != "evidence_return":
            errors.append(f"factory portfolio route {index} must return evidence")
        if route.get("payload_scope") != "evidence_only":
            errors.append(f"factory portfolio route {index} must be evidence-only")
        if route.get("grants_authority") is not False:
            errors.append(f"factory portfolio route {index} may not grant authority")
        if route.get("can_self_promote") is not False:
            errors.append(f"factory portfolio route {index} may not self-promote")
    if route_sources != economic_ids:
        errors.append(
            "factory portfolio evidence routes must follow economic-factory order exactly once"
        )

    if not _canonical_equal(data.get("policies"), EXPECTED_POLICIES):
        errors.append("factory portfolio policies must preserve the least-authority contract")
    return errors


def _verified_bundle_map(
    bundle_values: Any,
) -> tuple[list[str], dict[str, dict[str, Any]], dict[str, bytes]]:
    errors: list[str] = []
    verified: dict[str, dict[str, Any]] = {}
    bundle_bytes: dict[str, bytes] = {}
    if not isinstance(bundle_values, list):
        return ["factory portfolio bundles must be a list"], {}, {}
    if not MIN_FACTORIES <= len(bundle_values) <= MAX_FACTORIES:
        return [
            f"factory portfolio must receive between {MIN_FACTORIES} and "
            f"{MAX_FACTORIES} bundles"
        ], {}, {}
    for index, bundle in enumerate(bundle_values):
        if not isinstance(bundle, bytes):
            errors.append(f"factory portfolio bundle {index} must be bytes")
            continue
        bundle_errors, result = verify_factory_bundle(bundle)
        errors.extend(
            f"factory portfolio bundle {index}: {error}" for error in bundle_errors
        )
        if result is None:
            continue
        factory_id = result.get("factory_id")
        if not isinstance(factory_id, str):
            errors.append(f"factory portfolio bundle {index} has no factory id")
            continue
        if factory_id in verified:
            errors.append(f"duplicate factory portfolio bundle id: {factory_id}")
            continue
        verified[factory_id] = result
        bundle_bytes[factory_id] = bundle
    return errors, verified, bundle_bytes


def _bundle_alignment_errors(
    portfolio: dict[str, Any],
    verified: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    declared = {
        factory["id"]: factory
        for factory in portfolio["factories"]
        if isinstance(factory, dict) and isinstance(factory.get("id"), str)
    }
    missing = set(declared) - set(verified)
    extra = set(verified) - set(declared)
    if missing:
        errors.append("factory portfolio bundles missing ids: " + ", ".join(sorted(missing)))
    if extra:
        errors.append("factory portfolio bundles contain undeclared ids: " + ", ".join(sorted(extra)))
    for factory_id in sorted(set(declared) & set(verified)):
        manifest = verified[factory_id].get("manifest")
        actual_class = (
            manifest.get("factory", {}).get("class")
            if isinstance(manifest, dict)
            else None
        )
        if actual_class != declared[factory_id].get("class"):
            errors.append(f"{factory_id}: bundle class does not match portfolio registry")
    return errors


def verified_factory_portfolio_inputs(
    portfolio: Any,
    bundle_values: Any,
) -> tuple[
    list[str],
    dict[str, dict[str, Any]],
    dict[str, bytes],
]:
    """Verify a closed registry and return exact bundle results and bytes by ID."""
    portfolio_errors = validate_factory_portfolio(portfolio)
    if portfolio_errors or not isinstance(portfolio, dict):
        return list(portfolio_errors), {}, {}
    bundle_errors, verified, bundle_bytes = _verified_bundle_map(bundle_values)
    errors = list(bundle_errors)
    errors.extend(_bundle_alignment_errors(portfolio, verified))
    if errors:
        return errors, {}, {}
    return [], verified, bundle_bytes


def _factory_namespaces(factory_id: str) -> dict[str, str]:
    return {
        kind: f"factory/{factory_id}/{kind.replace('_', '-')}"
        for kind in NAMESPACE_KINDS
    }


def _selected_scheduler(result: dict[str, Any]) -> dict[str, str]:
    manifest = result["manifest"]
    selected = next(
        module
        for module in manifest["selected_modules"]
        if module["slot"] == "scheduling"
    )
    return {
        "id": selected["module"],
        "artifact_sha256": selected["artifact_sha256"],
    }


def build_factory_portfolio_plan(
    portfolio: dict[str, Any],
    verified: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Build the exact non-authorizing view from validated inputs."""
    factory_records: list[dict[str, Any]] = []
    bundle_set: list[dict[str, str]] = []
    all_namespaces: list[str] = []
    for factory in portfolio["factories"]:
        result = verified[factory["id"]]
        namespaces = _factory_namespaces(factory["id"])
        all_namespaces.extend(namespaces.values())
        bundle_set.append(
            {
                "factory_id": factory["id"],
                "bundle_sha256": result["bundle_sha256"],
            }
        )
        factory_records.append(
            {
                "position": factory["position"],
                "id": factory["id"],
                "class": factory["class"],
                "bundle_sha256": result["bundle_sha256"],
                "source": deepcopy(result["manifest"]["source"]),
                "selected_scheduler_module": _selected_scheduler(result),
                "namespaces": namespaces,
                "runtime_boundary": {
                    "bundle_verified": True,
                    "runtime_qualified": False,
                    "activation_authorized": False,
                    "execution_authorized": False,
                    "side_effect_authority": False,
                },
            }
        )

    control_factory = portfolio["portfolio"]["control_factory"]
    routes = [
        {
            **deepcopy(route),
            "from_bundle_sha256": verified[route["from_factory"]]["bundle_sha256"],
            "to_bundle_sha256": verified[route["to_factory"]]["bundle_sha256"],
        }
        for route in portfolio["evidence_routes"]
    ]
    plan_without_digest: dict[str, Any] = {
        "contract_schema": PORTFOLIO_PLAN_SCHEMA_REFERENCE,
        "schema_version": PORTFOLIO_PLAN_SCHEMA_VERSION,
        "portfolio": deepcopy(portfolio["portfolio"]),
        "source": {
            "portfolio_definition_sha256": sha256_json(portfolio),
            "factory_bundle_set_sha256": sha256_json(bundle_set),
        },
        "control_factory": {
            "id": control_factory,
            "bundle_sha256": verified[control_factory]["bundle_sha256"],
        },
        "factories": factory_records,
        "evidence_routes": routes,
        "isolation": {
            "closed_registry": True,
            "unknown_factories_fail_closed": True,
            "intended_namespaces_are_disjoint": len(all_namespaces)
            == len(set(all_namespaces)),
            "runtime_isolation_proved": False,
            "cross_factory_secret_access_granted": False,
            "cross_factory_worker_access_granted": False,
            "cross_factory_artifact_access_granted": False,
            "cross_factory_authority_granted": False,
            "evidence_routes_only": True,
        },
        "summary": {
            "factory_count": len(factory_records),
            "control_factory_count": 1,
            "economic_factory_count": len(factory_records) - 1,
            "evidence_route_count": len(routes),
            "intended_namespace_count": len(all_namespaces),
        },
        "control_claim": {
            "scope": "multi_factory_control_plan_only",
            "all_factory_bundles_verified": True,
            "contains_runtime_implementations": False,
            "proves_runtime_isolation": False,
            "deploys_infrastructure": False,
            "routes_secrets": False,
            "invokes_models": False,
            "executes_operations": False,
            "authorizes_activation": False,
            "authorizes_cross_factory_effects": False,
            "proves_runtime_recovery": False,
        },
    }
    plan = dict(plan_without_digest)
    plan["factory_portfolio_plan_sha256"] = sha256_json(plan_without_digest)
    return plan


def factory_portfolio_plan_for_bundles(
    portfolio: Any,
    bundle_values: Any,
) -> tuple[list[str], dict[str, Any] | None]:
    errors, verified, _ = verified_factory_portfolio_inputs(
        portfolio,
        bundle_values,
    )
    if errors:
        return errors, None
    assert isinstance(portfolio, dict)
    try:
        plan = build_factory_portfolio_plan(portfolio, verified)
    except (KeyError, StopIteration, TypeError, ValueError) as exc:
        return [f"cannot build factory portfolio plan: {exc}"], None
    if not _canonical_equal(
        plan,
        build_factory_portfolio_plan(portfolio, verified),
    ):
        return ["factory portfolio plan builder is not deterministic"], None
    return [], plan


def verify_factory_portfolio_plan_for_bundles(
    plan: Any,
    portfolio: Any,
    bundle_values: Any,
) -> list[str]:
    errors, verified, _ = verified_factory_portfolio_inputs(
        portfolio,
        bundle_values,
    )
    if errors:
        return errors
    assert isinstance(portfolio, dict)
    try:
        expected = build_factory_portfolio_plan(portfolio, verified)
    except (KeyError, StopIteration, TypeError, ValueError) as exc:
        return [f"cannot derive expected factory portfolio plan: {exc}"]
    if not _canonical_equal(plan, expected):
        return [
            "factory portfolio plan must exactly match its verified bundles and "
            "least-authority definition"
        ]
    return []
