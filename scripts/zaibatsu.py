#!/usr/bin/env python3
"""Create and validate portable Zaibatsu software-factory definitions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from factory_bundle import build_factory_bundle, sha256_bytes, verify_factory_bundle
from factory_composer import (
    MODULE_CATALOG_PATH,
    build_factory_plan,
    load_json_file,
    load_module_artifacts,
    rebuild_check,
    validate_factory_bindings,
    validate_factory_plan,
    validate_module_catalog,
)
from validate_repository import (
    FACTORY_DEFINITION_SCHEMA_VERSION,
    PORTABLE_FACTORY_SCHEMA_REFERENCE,
    REQUIRED_DETERMINISTIC_GATES,
    validate_factory_definition,
)


def factory_template(
    factory_id: str,
    factory_class: str,
    purpose: str,
    scheduler: str,
) -> dict[str, Any]:
    return {
        "contract_schema": PORTABLE_FACTORY_SCHEMA_REFERENCE,
        "schema_version": FACTORY_DEFINITION_SCHEMA_VERSION,
        "factory": {
            "id": factory_id,
            "class": factory_class,
            "maturity": "planned",
            "purpose": purpose,
        },
        "versioning_policy": {
            "source_and_intended_state": "git",
            "encrypted_static_secrets": "sops_age",
            "runtime_secrets": "bounded_secret_manager",
            "plaintext_secrets_in_git": False,
        },
        "reproducibility_policy": {
            "host_configuration": "ansible",
            "worker_environments": "nix",
            "nix_maturity": "planned",
            "nix_cross_node_proof": False,
        },
        "scheduling_policy": {
            "scheduler_of_record": scheduler,
            "one_scheduler_of_record_per_workload": True,
        },
        "agent_policy": {
            "skeleton_status": "planned",
            "harness_binding": "model_independent_typed_ports",
            "deterministic_gates": list(REQUIRED_DETERMINISTIC_GATES),
            "model_may_authorize_external_effect": False,
        },
        "feedback_policy": {
            "return_evidence": True,
            "promotion_authority": "reviewed_deterministic_policy_and_owner_gate",
            "factory_may_self_promote": False,
        },
        "module_bindings": [
            {"slot": "source_versioning", "module": "git-source"},
            {"slot": "static_secrets", "module": "sops-age-static-secrets"},
            {"slot": "runtime_secrets", "module": "bounded-runtime-secrets"},
            {"slot": "host_reproduction", "module": "ansible-host-reproduction"},
            {"slot": "worker_environment", "module": "nix-worker-environment"},
            {"slot": "scheduling", "module": f"{scheduler}-scheduler"},
            {"slot": "execution", "module": "typed-agent-execution"},
            {"slot": "verification", "module": "deterministic-verification"},
            {"slot": "feedback", "module": "owner-gated-feedback"},
        ],
        "evidence_bindings": [],
    }


def write_document(document: dict[str, Any], output: str | None) -> int:
    rendered = json.dumps(document, indent=2) + "\n"
    if output is None:
        sys.stdout.write(rendered)
        return 0
    path = Path(output)
    if path.exists() or path.is_symlink():
        print(f"refusing to overwrite existing path: {path}", file=sys.stderr)
        return 2
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    print(f"created {path}")
    return 0


def write_binary(value: bytes, output: str) -> int:
    path = Path(output)
    if path.exists() or path.is_symlink():
        print(f"refusing to overwrite existing path: {path}", file=sys.stderr)
        return 2
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(value)
    print(f"created {path}")
    return 0


def load_json_document(path: str, label: str) -> Any | None:
    document_path = Path(path)
    try:
        return load_json_file(document_path)
    except (OSError, ValueError) as exc:
        print(f"cannot load {label}: {exc}", file=sys.stderr)
        return None


def factory_and_catalog_errors(
    document: Any,
    catalog: Any,
    catalog_base: Path,
) -> list[str]:
    errors = validate_factory_definition(document)
    errors.extend(validate_module_catalog(catalog))
    _, artifact_errors = load_module_artifacts(catalog, catalog_base)
    errors.extend(artifact_errors)
    errors.extend(validate_factory_bindings(document, catalog))
    return errors


def command_validate(path: str, catalog_path: str) -> int:
    document_path = Path(path)
    document = load_json_document(path, "factory definition")
    catalog = load_json_document(catalog_path, "module catalog")
    if document is None or catalog is None:
        return 2
    errors = factory_and_catalog_errors(document, catalog, Path(catalog_path).parent)
    if errors:
        print(f"factory definition failed: {document_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"factory definition passed: {document_path}")
    return 0


def command_catalog_check(path: str) -> int:
    catalog = load_json_document(path, "module catalog")
    if catalog is None:
        return 2
    errors = validate_module_catalog(catalog)
    _, artifact_errors = load_module_artifacts(catalog, Path(path).parent)
    errors.extend(artifact_errors)
    if errors:
        print(f"module catalog failed: {path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"module catalog passed: {path}")
    return 0


def command_plan(path: str, catalog_path: str, output: str | None) -> int:
    definition = load_json_document(path, "factory definition")
    catalog = load_json_document(catalog_path, "module catalog")
    if definition is None or catalog is None:
        return 2
    errors = factory_and_catalog_errors(definition, catalog, Path(catalog_path).parent)
    if errors:
        print("cannot compose invalid factory inputs", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return write_document(build_factory_plan(definition, catalog), output)


def command_verify_plan(plan_path: str, factory_path: str, catalog_path: str) -> int:
    plan = load_json_document(plan_path, "factory plan")
    definition = load_json_document(factory_path, "factory definition")
    catalog = load_json_document(catalog_path, "module catalog")
    if plan is None or definition is None or catalog is None:
        return 2
    errors = factory_and_catalog_errors(definition, catalog, Path(catalog_path).parent)
    errors.extend(validate_factory_plan(plan, definition, catalog))
    if errors:
        print(f"factory plan failed: {plan_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"factory plan passed: {plan_path}")
    print(f"plan sha256: {plan['plan_sha256']}")
    return 0


def command_rebuild_check(path: str, catalog_path: str) -> int:
    definition = load_json_document(path, "factory definition")
    catalog = load_json_document(catalog_path, "module catalog")
    if definition is None or catalog is None:
        return 2
    errors = factory_and_catalog_errors(definition, catalog, Path(catalog_path).parent)
    if errors:
        print("cannot rebuild invalid factory inputs", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    stable, digest = rebuild_check(definition, catalog)
    if not stable:
        print("factory control plan was not byte-reproducible", file=sys.stderr)
        return 1
    print("factory control plan rebuild passed")
    print(f"plan sha256: {digest}")
    return 0


def command_bundle(path: str, catalog_path: str, output: str) -> int:
    definition = load_json_document(path, "factory definition")
    catalog = load_json_document(catalog_path, "module catalog")
    if definition is None or catalog is None:
        return 2
    catalog_base = Path(catalog_path).parent
    errors = validate_factory_definition(definition)
    errors.extend(validate_module_catalog(catalog))
    errors.extend(validate_factory_bindings(definition, catalog))
    artifacts, artifact_errors = load_module_artifacts(catalog, catalog_base)
    errors.extend(artifact_errors)
    if errors:
        print("cannot bundle invalid factory inputs", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    bundle, _ = build_factory_bundle(definition, catalog, artifacts)
    result = write_binary(bundle, output)
    if result == 0:
        print(f"bundle sha256: {sha256_bytes(bundle)}")
    return result


def command_verify_bundle(path: str) -> int:
    bundle_path = Path(path)
    try:
        bundle = bundle_path.read_bytes()
    except OSError as exc:
        print(f"cannot load factory bundle: {exc}", file=sys.stderr)
        return 2
    errors, result = verify_factory_bundle(bundle)
    if errors or result is None:
        print(f"factory bundle failed: {bundle_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"factory bundle passed: {bundle_path}")
    print(f"factory id: {result['factory_id']}")
    print(f"plan sha256: {result['plan_sha256']}")
    print(f"bundle sha256: {result['bundle_sha256']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zaibatsu",
        description="Scaffold and validate evidence-gated software factories.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="validate a factory JSON file")
    validate.add_argument("path")
    validate.add_argument("--catalog", default=str(MODULE_CATALOG_PATH))

    catalog_check = commands.add_parser(
        "catalog-check", help="validate a reusable module catalog"
    )
    catalog_check.add_argument("path", nargs="?", default=str(MODULE_CATALOG_PATH))

    plan = commands.add_parser(
        "plan", help="resolve a factory and module catalog into a deterministic plan"
    )
    plan.add_argument("path")
    plan.add_argument("--catalog", default=str(MODULE_CATALOG_PATH))
    plan.add_argument("--output", help="write the plan to a new file instead of stdout")

    verify_plan = commands.add_parser(
        "verify-plan", help="verify a plan against its content-addressed inputs"
    )
    verify_plan.add_argument("plan_path")
    verify_plan.add_argument("factory_path")
    verify_plan.add_argument("--catalog", default=str(MODULE_CATALOG_PATH))

    rebuild = commands.add_parser(
        "rebuild-check", help="compile twice and prove a byte-stable control plan"
    )
    rebuild.add_argument("path")
    rebuild.add_argument("--catalog", default=str(MODULE_CATALOG_PATH))

    bundle = commands.add_parser(
        "bundle", help="build a canonical self-contained factory control bundle"
    )
    bundle.add_argument("path")
    bundle.add_argument("--catalog", default=str(MODULE_CATALOG_PATH))
    bundle.add_argument("--output", required=True, help="write a new uncompressed tar")

    verify_bundle = commands.add_parser(
        "verify-bundle", help="verify and reproduce a factory control bundle"
    )
    verify_bundle.add_argument("path")

    scaffold = commands.add_parser("scaffold", help="create a safe factory skeleton")
    scaffold.add_argument("--id", required=True, dest="factory_id")
    scaffold.add_argument(
        "--class",
        required=True,
        dest="factory_class",
        choices=("control_factory", "economic_factory"),
    )
    scaffold.add_argument("--purpose", required=True)
    scaffold.add_argument("--scheduler", choices=("systemd", "cron"), default="systemd")
    scaffold.add_argument("--output", help="write to a new file instead of stdout")
    return parser


def main() -> int:
    arguments = build_parser().parse_args()
    if arguments.command == "validate":
        return command_validate(arguments.path, arguments.catalog)
    if arguments.command == "catalog-check":
        return command_catalog_check(arguments.path)
    if arguments.command == "plan":
        return command_plan(arguments.path, arguments.catalog, arguments.output)
    if arguments.command == "verify-plan":
        return command_verify_plan(
            arguments.plan_path, arguments.factory_path, arguments.catalog
        )
    if arguments.command == "rebuild-check":
        return command_rebuild_check(arguments.path, arguments.catalog)
    if arguments.command == "bundle":
        return command_bundle(arguments.path, arguments.catalog, arguments.output)
    if arguments.command == "verify-bundle":
        return command_verify_bundle(arguments.path)
    document = factory_template(
        arguments.factory_id,
        arguments.factory_class,
        arguments.purpose,
        arguments.scheduler,
    )
    catalog = load_json_document(str(MODULE_CATALOG_PATH), "bundled module catalog")
    if catalog is None:
        return 2
    errors = factory_and_catalog_errors(
        document, catalog, MODULE_CATALOG_PATH.parent
    )
    if errors:
        for error in errors:
            print(f"internal scaffold error: {error}", file=sys.stderr)
        return 2
    return write_document(document, arguments.output)


if __name__ == "__main__":
    sys.exit(main())
