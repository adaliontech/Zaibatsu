#!/usr/bin/env python3
"""Create and validate portable Zaibatsu software-factory definitions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from validate_repository import (
    FACTORY_DEFINITION_SCHEMA_VERSION,
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
        "contract_schema": "../schemas/factory-definition.schema.json",
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
        "evidence_bindings": [],
    }


def write_document(document: dict[str, Any], output: str | None) -> int:
    rendered = json.dumps(document, indent=2) + "\n"
    if output is None:
        sys.stdout.write(rendered)
        return 0
    path = Path(output)
    if path.exists():
        print(f"refusing to overwrite existing path: {path}", file=sys.stderr)
        return 2
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(rendered, encoding="utf-8")
    print(f"created {path}")
    return 0


def command_validate(path: str) -> int:
    document_path = Path(path)
    try:
        document = json.loads(document_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot load factory definition: {exc}", file=sys.stderr)
        return 2
    errors = validate_factory_definition(document)
    if errors:
        print(f"factory definition failed: {document_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"factory definition passed: {document_path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="zaibatsu",
        description="Scaffold and validate evidence-gated software factories.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="validate a factory JSON file")
    validate.add_argument("path")

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
        return command_validate(arguments.path)
    document = factory_template(
        arguments.factory_id,
        arguments.factory_class,
        arguments.purpose,
        arguments.scheduler,
    )
    errors = validate_factory_definition(document)
    if errors:
        for error in errors:
            print(f"internal scaffold error: {error}", file=sys.stderr)
        return 2
    return write_document(document, arguments.output)


if __name__ == "__main__":
    sys.exit(main())
