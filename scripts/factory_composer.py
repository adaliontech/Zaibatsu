#!/usr/bin/env python3
"""Deterministically compose portable factory definitions into control plans."""

from __future__ import annotations

import hashlib
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MODULE_CATALOG_PATH = ROOT / "catalog" / "modules.json"
EXAMPLE_PLAN_PATH = ROOT / "examples" / "economic-factory.plan.json"

MODULE_CATALOG_SCHEMA_VERSION = "zaibatsu.module-catalog.v1"
FACTORY_PLAN_SCHEMA_VERSION = "zaibatsu.factory-plan.v1"
MODULE_API_VERSION = "zaibatsu.module.v1"
MODULE_CATALOG_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.2.0/schemas/module-catalog.schema.json"
)
FACTORY_PLAN_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.2.0/schemas/factory-plan.schema.json"
)

REQUIRED_MODULE_SLOTS = (
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

ALLOWED_IMPLEMENTATION_STATUSES = {"contract_only", "source_only", "planned"}
ALLOWED_MODULE_KINDS = {"deterministic", "probabilistic_adapter"}
MODULE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CATALOG_FIELDS = {
    "contract_schema",
    "schema_version",
    "module_api_version",
    "modules",
}
MODULE_FIELDS = {
    "id",
    "slot",
    "interface_version",
    "kind",
    "implementation_status",
    "side_effect_authority",
    "policy_value",
    "description",
    "rebuild_boundary",
    "requires_slots",
    "provides",
}


def canonical_json_bytes(value: Any) -> bytes:
    """Return one stable UTF-8 representation used for every plan digest."""
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        + "\n"
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def _reject_nonstandard_number(value: str) -> None:
    raise ValueError(f"non-standard JSON number: {value}")


def load_json_file(path: Path) -> Any:
    return json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonstandard_number,
    )


def load_module_catalog(path: Path = MODULE_CATALOG_PATH) -> dict[str, Any]:
    return load_json_file(path)


def load_factory_plan(path: Path = EXAMPLE_PLAN_PATH) -> dict[str, Any]:
    return load_json_file(path)


def validate_module_catalog(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["module catalog root must be an object"]
    if set(data) != CATALOG_FIELDS:
        errors.append("module catalog must contain exactly the versioned catalog fields")
    if data.get("contract_schema") != MODULE_CATALOG_SCHEMA_REFERENCE:
        errors.append("module catalog must reference its immutable project schema")
    if data.get("schema_version") != MODULE_CATALOG_SCHEMA_VERSION:
        errors.append(
            f"module catalog schema_version must equal {MODULE_CATALOG_SCHEMA_VERSION}"
        )
    if data.get("module_api_version") != MODULE_API_VERSION:
        errors.append(f"module_api_version must equal {MODULE_API_VERSION}")

    modules = data.get("modules")
    if not isinstance(modules, list):
        return errors + ["module catalog modules must be a list"]

    seen_ids: set[str] = set()
    by_slot: dict[str, list[dict[str, Any]]] = {
        slot: [] for slot in REQUIRED_MODULE_SLOTS
    }
    slot_position = {slot: index for index, slot in enumerate(REQUIRED_MODULE_SLOTS)}
    for index, module in enumerate(modules):
        if not isinstance(module, dict):
            errors.append(f"module at index {index} must be an object")
            continue
        if set(module) != MODULE_FIELDS:
            errors.append(f"module at index {index} contains missing or unexpected fields")
        module_id = module.get("id")
        if not isinstance(module_id, str) or not MODULE_ID_RE.fullmatch(module_id):
            errors.append(f"module at index {index} must have an id")
            continue
        if module_id in seen_ids:
            errors.append(f"duplicate module id: {module_id}")
        seen_ids.add(module_id)
        slot = module.get("slot")
        if not isinstance(slot, str) or slot not in by_slot:
            errors.append(f"{module_id}: invalid module slot {slot!r}")
            continue
        by_slot[slot].append(module)
        if module.get("interface_version") != MODULE_API_VERSION:
            errors.append(f"{module_id}: interface_version must match the catalog")
        kind = module.get("kind")
        if not isinstance(kind, str) or kind not in ALLOWED_MODULE_KINDS:
            errors.append(f"{module_id}: invalid module kind {kind!r}")
        status = module.get("implementation_status")
        if not isinstance(status, str) or status not in ALLOWED_IMPLEMENTATION_STATUSES:
            errors.append(f"{module_id}: invalid implementation_status {status!r}")
        if module.get("side_effect_authority") is not False:
            errors.append(f"{module_id}: catalog modules may not own side-effect authority")
        for field in ("description", "rebuild_boundary"):
            if not isinstance(module.get(field), str) or not module[field].strip():
                errors.append(f"{module_id}: {field} must be non-empty")
        policy_value = module.get("policy_value")
        if not (
            (isinstance(policy_value, str) and policy_value.strip())
            or (
                isinstance(policy_value, list)
                and policy_value
                and all(isinstance(item, str) and item.strip() for item in policy_value)
                and len(policy_value) == len(set(policy_value))
            )
        ):
            errors.append(
                f"{module_id}: policy_value must be a non-empty string or unique string list"
            )
        requires = module.get("requires_slots")
        if not isinstance(requires, list) or not all(
            isinstance(required, str) for required in requires
        ):
            errors.append(f"{module_id}: requires_slots must be a list of slots")
            continue
        if len(requires) != len(set(requires)):
            errors.append(f"{module_id}: requires_slots must be unique")
        for required in requires:
            if required not in slot_position:
                errors.append(f"{module_id}: unknown required slot {required}")
            elif slot_position[required] >= slot_position[slot]:
                errors.append(
                    f"{module_id}: required slot {required} must precede {slot}"
                )
        provides = module.get("provides")
        if not isinstance(provides, list) or not provides or not all(
            isinstance(item, str) and item.strip() for item in provides
        ):
            errors.append(f"{module_id}: provides must contain typed outputs")
        elif len(provides) != len(set(provides)):
            errors.append(f"{module_id}: provides must be unique")

    missing_slots = [slot for slot, entries in by_slot.items() if not entries]
    if missing_slots:
        errors.append("module catalog missing slots: " + ", ".join(missing_slots))
    return errors


def validate_factory_bindings(definition: Any, catalog: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(definition, dict) or not isinstance(catalog, dict):
        return ["factory definition and module catalog must be objects"]
    modules = catalog.get("modules")
    if not isinstance(modules, list):
        return ["module catalog modules must be a list"]
    by_id = {
        module.get("id"): module
        for module in modules
        if isinstance(module, dict) and isinstance(module.get("id"), str)
    }
    bindings = definition.get("module_bindings")
    if not isinstance(bindings, list):
        return ["factory module_bindings must be a list"]
    seen_slots: set[str] = set()
    for index, binding in enumerate(bindings):
        if not isinstance(binding, dict):
            errors.append(f"factory module binding at index {index} must be an object")
            continue
        if set(binding) != {"slot", "module"}:
            errors.append(
                f"factory module binding at index {index} must contain only slot and module"
            )
        slot = binding.get("slot")
        module_id = binding.get("module")
        if not isinstance(slot, str) or slot not in REQUIRED_MODULE_SLOTS:
            errors.append(f"factory module binding at index {index} has invalid slot")
            continue
        if slot in seen_slots:
            errors.append(f"duplicate factory module slot: {slot}")
        seen_slots.add(slot)
        if not isinstance(module_id, str) or module_id not in by_id:
            errors.append(f"{slot}: selected module is not in the catalog")
            continue
        if by_id[module_id].get("slot") != slot:
            errors.append(f"{slot}: selected module belongs to another slot")
    if seen_slots != set(REQUIRED_MODULE_SLOTS):
        errors.append("factory module bindings must select every required slot exactly once")

    versioning = definition.get("versioning_policy")
    reproduction = definition.get("reproducibility_policy")
    scheduling = definition.get("scheduling_policy")
    agent = definition.get("agent_policy")
    feedback = definition.get("feedback_policy")
    if not all(
        isinstance(policy, dict)
        for policy in (versioning, reproduction, scheduling, agent, feedback)
    ):
        return errors + ["factory policies must be objects before modules can be bound"]
    expected_policy_values = {
        "source_versioning": versioning.get("source_and_intended_state"),
        "static_secrets": versioning.get("encrypted_static_secrets"),
        "runtime_secrets": versioning.get("runtime_secrets"),
        "host_reproduction": reproduction.get("host_configuration"),
        "worker_environment": reproduction.get("worker_environments"),
        "scheduling": scheduling.get("scheduler_of_record"),
        "execution": agent.get("harness_binding"),
        "verification": agent.get("deterministic_gates"),
        "feedback": feedback.get("promotion_authority"),
    }
    selected = {
        binding["slot"]: binding["module"]
        for binding in bindings
        if isinstance(binding, dict)
        and isinstance(binding.get("slot"), str)
        and isinstance(binding.get("module"), str)
    }
    for slot, expected_value in expected_policy_values.items():
        module = by_id.get(selected.get(slot))
        if isinstance(module, dict) and module.get("policy_value") != expected_value:
            errors.append(f"{slot}: selected module does not preserve declared policy")
    return errors


def build_factory_plan(
    definition: dict[str, Any], catalog: dict[str, Any]
) -> dict[str, Any]:
    """Resolve one validated definition into a path-independent control plan."""
    catalog_modules = {module["id"]: module for module in catalog["modules"]}
    bindings = {
        binding["slot"]: binding["module"]
        for binding in definition["module_bindings"]
    }
    resolved_modules: list[dict[str, Any]] = []
    for position, slot in enumerate(REQUIRED_MODULE_SLOTS):
        module = catalog_modules[bindings[slot]]
        resolved_modules.append(
            {
                "position": position,
                "slot": slot,
                "module": module["id"],
                "policy_value": deepcopy(module["policy_value"]),
                "interface_version": module["interface_version"],
                "kind": module["kind"],
                "implementation_status": module["implementation_status"],
                "side_effect_authority": False,
                "requires_slots": list(module["requires_slots"]),
                "provides": list(module["provides"]),
                "rebuild_boundary": module["rebuild_boundary"],
            }
        )
    factory = definition["factory"]
    plan_without_digest: dict[str, Any] = {
        "contract_schema": FACTORY_PLAN_SCHEMA_REFERENCE,
        "schema_version": FACTORY_PLAN_SCHEMA_VERSION,
        "factory": {
            "id": factory["id"],
            "class": factory["class"],
            "maturity": factory["maturity"],
            "purpose": factory["purpose"],
        },
        "source": {
            "factory_definition_sha256": sha256_json(definition),
            "module_catalog_sha256": sha256_json(catalog),
            "module_api_version": MODULE_API_VERSION,
        },
        "module_order": list(REQUIRED_MODULE_SLOTS),
        "modules": resolved_modules,
        "deterministic_gates": list(
            definition["agent_policy"]["deterministic_gates"]
        ),
        "rebuild_claim": {
            "scope": "control_plan_only",
            "byte_reproducible": True,
            "deploys_infrastructure": False,
            "proves_runtime_recovery": False,
        },
    }
    plan = dict(plan_without_digest)
    plan["plan_sha256"] = sha256_json(plan_without_digest)
    return plan


def validate_factory_plan(
    plan: Any,
    definition: Any,
    catalog: Any,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["factory plan root must be an object"]
    if plan.get("contract_schema") != FACTORY_PLAN_SCHEMA_REFERENCE:
        errors.append("factory plan must reference its immutable project schema")
    if plan.get("schema_version") != FACTORY_PLAN_SCHEMA_VERSION:
        errors.append(
            f"factory plan schema_version must equal {FACTORY_PLAN_SCHEMA_VERSION}"
        )
    if not isinstance(definition, dict) or not isinstance(catalog, dict):
        return errors + ["factory definition and module catalog must be objects"]
    try:
        expected = build_factory_plan(definition, catalog)
    except (KeyError, TypeError, ValueError) as exc:
        return errors + [f"cannot rebuild expected factory plan: {exc}"]
    if plan != expected:
        errors.append("factory plan does not exactly match its content-addressed inputs")
    return errors


def rebuild_check(
    definition: dict[str, Any],
    catalog: dict[str, Any],
) -> tuple[bool, str]:
    first = build_factory_plan(definition, catalog)
    serialized = canonical_json_bytes(first)
    reparsed = json.loads(serialized.decode("utf-8"))
    second = build_factory_plan(definition, catalog)
    stable = serialized == canonical_json_bytes(second) and reparsed == second
    return stable, first["plan_sha256"]
