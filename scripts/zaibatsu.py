#!/usr/bin/env python3
"""Create and validate portable Zaibatsu software-factory definitions."""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

from factory_bundle import (
    build_factory_bundle,
    compare_factory_bundles,
    inspect_factory_bundle,
    MAX_BUNDLE_BYTES,
    sha256_bytes,
    verify_factory_bundle,
)
from factory_evidence_pack import (
    MAX_PACK_BYTES,
    runtime_evidence_pack_for_bundle,
    verify_runtime_evidence_pack_for_bundle,
)
from factory_evidence_return import (
    MAX_EVIDENCE_RETURN_JSON_BYTES,
    factory_evidence_return_for_inputs,
    verify_factory_evidence_return_for_inputs,
)
from factory_portfolio import (
    MAX_FACTORIES,
    MAX_PORTFOLIO_BYTES,
    MAX_PORTFOLIO_PLAN_BYTES,
    MIN_FACTORIES,
    factory_portfolio_plan_for_bundles,
    verify_factory_portfolio_plan_for_bundles,
)
from factory_composer import (
    MODULE_CATALOG_PATH,
    build_factory_plan,
    load_json_bytes,
    load_json_file,
    load_module_artifacts,
    rebuild_check,
    sha256_json,
    validate_factory_bindings,
    validate_factory_plan,
    validate_module_catalog,
)
from factory_qualification import (
    EXAMPLE_QUALIFICATION_EVIDENCE_PATH,
    EXAMPLE_QUALIFICATION_PLAN_PATH,
    QUALIFICATION_POLICY_PATH,
    qualification_assessment_for_bundle,
    qualification_evidence_for_bundle,
    qualification_plan_for_bundle,
    verify_qualification_assessment_for_bundle,
    verify_qualification_evidence_for_bundle,
    verify_qualification_plan_for_bundle,
)
from factory_rebuild import (
    factory_rebuild_plan_for_bundle,
    verify_factory_rebuild_plan_for_bundle,
)
from factory_runtime_evidence import (
    EXAMPLE_RUNTIME_ASSESSMENT_PATH,
    VERIFIER_REGISTRY_PATH,
    runtime_assessment_for_bundle,
    validate_runtime_evidence_set,
    verify_runtime_assessment_for_bundle,
)
from factory_source_lock import (
    EXAMPLE_SOURCE_LOCK_PATH,
    source_lock_for_bundle,
    verify_source_lock_for_bundle,
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
    descriptor = new_output_descriptor(path)
    if descriptor is None:
        return 2
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(rendered)
    except OSError as exc:
        print(f"cannot write output path {path}: {exc}", file=sys.stderr)
        return 2
    print(f"created {path}")
    return 0


def write_binary(value: bytes, output: str) -> int:
    path = Path(output)
    descriptor = new_output_descriptor(path)
    if descriptor is None:
        return 2
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(value)
    except OSError as exc:
        print(f"cannot write output path {path}: {exc}", file=sys.stderr)
        return 2
    print(f"created {path}")
    return 0


def new_output_descriptor(path: Path) -> int | None:
    """Create a new output without a check-then-open overwrite race."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        return os.open(
            path,
            os.O_WRONLY
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_NOFOLLOW", 0),
            0o644,
        )
    except FileExistsError:
        print(f"refusing to overwrite existing path: {path}", file=sys.stderr)
    except OSError as exc:
        print(f"cannot create output path {path}: {exc}", file=sys.stderr)
    return None


def load_json_document(path: str, label: str) -> Any | None:
    document_path = Path(path)
    try:
        return load_json_file(document_path)
    except (OSError, RecursionError, ValueError) as exc:
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


def load_bounded_binary(path: str, label: str, max_bytes: int) -> bytes | None:
    input_path = Path(path)
    descriptor: int | None = None
    try:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(input_path, flags)
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise OSError("input must be a regular file")
        if metadata.st_size <= 0 or metadata.st_size > max_bytes:
            raise OSError("input size is outside the accepted boundary")
        with os.fdopen(descriptor, "rb") as stream:
            descriptor = None
            value = stream.read(max_bytes + 1)
        if len(value) != metadata.st_size:
            raise OSError("input changed while it was being read")
    except OSError as exc:
        print(f"cannot load {label}: {exc}", file=sys.stderr)
        return None
    finally:
        if descriptor is not None:
            os.close(descriptor)
    return value


def load_bundle(path: str, label: str) -> bytes | None:
    return load_bounded_binary(path, label, MAX_BUNDLE_BYTES)


def load_bounded_json_document(
    path: str,
    label: str,
    max_bytes: int,
) -> Any | None:
    value = load_bounded_binary(path, label, max_bytes)
    if value is None:
        return None
    try:
        return load_json_bytes(value)
    except (RecursionError, UnicodeDecodeError, ValueError) as exc:
        print(f"cannot load {label}: {exc}", file=sys.stderr)
        return None


def command_verify_bundle(path: str) -> int:
    bundle = load_bundle(path, "factory bundle")
    if bundle is None:
        return 2
    bundle_path = Path(path)
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


def command_inspect_bundle(path: str, output: str | None) -> int:
    bundle = load_bundle(path, "factory bundle")
    if bundle is None:
        return 2
    errors, inspection = inspect_factory_bundle(bundle)
    if errors or inspection is None:
        print(f"factory bundle failed: {path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return write_document(inspection, output)


def command_compare_bundles(
    before_path: str,
    after_path: str,
    output: str | None,
) -> int:
    before = load_bundle(before_path, "before factory bundle")
    after = load_bundle(after_path, "after factory bundle")
    if before is None or after is None:
        return 2
    errors, comparison = compare_factory_bundles(before, after)
    if errors or comparison is None:
        print("factory bundle comparison failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return write_document(comparison, output)


def valid_portfolio_bundle_count(paths: list[str]) -> bool:
    if not MIN_FACTORIES <= len(paths) <= MAX_FACTORIES:
        print(
            f"factory portfolio requires between {MIN_FACTORIES} and "
            f"{MAX_FACTORIES} bundles",
            file=sys.stderr,
        )
        return False
    return True


def load_portfolio_bundles(paths: list[str]) -> list[bytes] | None:
    if not valid_portfolio_bundle_count(paths):
        return None
    bundles: list[bytes] = []
    for index, path in enumerate(paths):
        bundle = load_bundle(path, f"factory portfolio bundle {index}")
        if bundle is None:
            return None
        bundles.append(bundle)
    return bundles


def command_portfolio_plan(
    portfolio_path: str,
    bundle_paths: list[str],
    output: str | None,
) -> int:
    if not valid_portfolio_bundle_count(bundle_paths):
        return 2
    portfolio = load_bounded_json_document(
        portfolio_path,
        "factory portfolio",
        MAX_PORTFOLIO_BYTES,
    )
    if portfolio is None:
        return 2
    bundles = load_portfolio_bundles(bundle_paths)
    if bundles is None:
        return 2
    errors, plan = factory_portfolio_plan_for_bundles(portfolio, bundles)
    if errors or plan is None:
        print("cannot build factory portfolio plan", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return write_document(plan, output)


def command_verify_portfolio_plan(
    plan_path: str,
    portfolio_path: str,
    bundle_paths: list[str],
) -> int:
    if not valid_portfolio_bundle_count(bundle_paths):
        return 2
    plan = load_bounded_json_document(
        plan_path,
        "factory portfolio plan",
        MAX_PORTFOLIO_PLAN_BYTES,
    )
    portfolio = load_bounded_json_document(
        portfolio_path,
        "factory portfolio",
        MAX_PORTFOLIO_BYTES,
    )
    if plan is None or portfolio is None:
        return 2
    bundles = load_portfolio_bundles(bundle_paths)
    if bundles is None:
        return 2
    errors = verify_factory_portfolio_plan_for_bundles(plan, portfolio, bundles)
    if errors:
        print(f"factory portfolio plan failed: {plan_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    assert isinstance(plan, dict)
    print(f"factory portfolio plan passed: {plan_path}")
    print(
        "factory portfolio plan sha256: "
        f"{plan['factory_portfolio_plan_sha256']}"
    )
    print(f"factories: {plan['summary']['factory_count']}")
    print(f"evidence-only routes: {plan['summary']['evidence_route_count']}")
    print("runtime isolation proved: false")
    print("cross-factory authority granted: false")
    print("operations executed: false")
    return 0


def load_evidence_return_inputs(
    plan_path: str,
    portfolio_path: str,
    runtime_evidence_pack_path: str,
    qualification_plan_path: str,
    qualification_policy_path: str,
    bundle_paths: list[str],
) -> tuple[Any, Any, bytes, Any, Any, list[bytes]] | None:
    if not valid_portfolio_bundle_count(bundle_paths):
        return None
    plan = load_bounded_json_document(
        plan_path,
        "factory portfolio plan",
        MAX_PORTFOLIO_PLAN_BYTES,
    )
    portfolio = load_bounded_json_document(
        portfolio_path,
        "factory portfolio",
        MAX_PORTFOLIO_BYTES,
    )
    qualification_plan = load_bounded_json_document(
        qualification_plan_path,
        "qualification plan",
        MAX_EVIDENCE_RETURN_JSON_BYTES,
    )
    qualification_policy = load_bounded_json_document(
        qualification_policy_path,
        "qualification policy",
        MAX_EVIDENCE_RETURN_JSON_BYTES,
    )
    runtime_evidence_pack = load_bounded_binary(
        runtime_evidence_pack_path,
        "runtime-evidence pack",
        MAX_PACK_BYTES,
    )
    if any(
        value is None
        for value in (
            plan,
            portfolio,
            qualification_plan,
            qualification_policy,
            runtime_evidence_pack,
        )
    ):
        return None
    bundles = load_portfolio_bundles(bundle_paths)
    if bundles is None:
        return None
    assert isinstance(runtime_evidence_pack, bytes)
    return (
        plan,
        portfolio,
        runtime_evidence_pack,
        qualification_plan,
        qualification_policy,
        bundles,
    )


def command_evidence_return_record(
    plan_path: str,
    portfolio_path: str,
    source_factory_id: str,
    runtime_evidence_pack_path: str,
    qualification_plan_path: str,
    qualification_policy_path: str,
    bundle_paths: list[str],
    output: str | None,
) -> int:
    inputs = load_evidence_return_inputs(
        plan_path,
        portfolio_path,
        runtime_evidence_pack_path,
        qualification_plan_path,
        qualification_policy_path,
        bundle_paths,
    )
    if inputs is None:
        return 2
    plan, portfolio, pack, qualification_plan, qualification_policy, bundles = (
        inputs
    )
    errors, record = factory_evidence_return_for_inputs(
        plan,
        portfolio,
        bundles,
        source_factory_id,
        pack,
        qualification_plan,
        qualification_policy,
    )
    if errors or record is None:
        print("cannot build factory evidence-return record", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return write_document(record, output)


def command_verify_evidence_return_record(
    record_path: str,
    plan_path: str,
    portfolio_path: str,
    source_factory_id: str,
    runtime_evidence_pack_path: str,
    qualification_plan_path: str,
    qualification_policy_path: str,
    bundle_paths: list[str],
) -> int:
    if not valid_portfolio_bundle_count(bundle_paths):
        return 2
    record = load_bounded_json_document(
        record_path,
        "factory evidence-return record",
        MAX_EVIDENCE_RETURN_JSON_BYTES,
    )
    if record is None:
        return 2
    inputs = load_evidence_return_inputs(
        plan_path,
        portfolio_path,
        runtime_evidence_pack_path,
        qualification_plan_path,
        qualification_policy_path,
        bundle_paths,
    )
    if inputs is None:
        return 2
    plan, portfolio, pack, qualification_plan, qualification_policy, bundles = (
        inputs
    )
    errors = verify_factory_evidence_return_for_inputs(
        record,
        plan,
        portfolio,
        bundles,
        source_factory_id,
        pack,
        qualification_plan,
        qualification_policy,
    )
    if errors:
        print(f"factory evidence-return record failed: {record_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    assert isinstance(record, dict)
    print(f"factory evidence-return record passed: {record_path}")
    print(
        "factory evidence-return sha256: "
        f"{record['factory_evidence_return_sha256']}"
    )
    print(f"source factory: {record['factory']['id']}")
    print(f"destination factory: {record['route']['to_factory']}")
    print("transport observed: false")
    print("shared promotion eligible: false")
    print("cross-factory effects authorized: false")
    return 0


def command_source_lock(
    factory_path: str,
    bundle_path: str,
    repository_path: str,
    release_tag: str,
    catalog_path: str,
    repository_url: str,
    output: str | None,
) -> int:
    bundle = load_bundle(bundle_path, "factory bundle")
    if bundle is None:
        return 2
    errors, source_lock = source_lock_for_bundle(
        Path(repository_path),
        release_tag,
        factory_path,
        bundle,
        catalog_path,
        repository_url,
    )
    if errors or source_lock is None:
        print("cannot build factory source lock", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return write_document(source_lock, output)


def command_verify_source_lock(
    source_lock_path: str,
    bundle_path: str,
    repository_path: str,
) -> int:
    source_lock = load_json_document(source_lock_path, "factory source lock")
    bundle = load_bundle(bundle_path, "factory bundle")
    if source_lock is None or bundle is None:
        return 2
    errors = verify_source_lock_for_bundle(
        source_lock,
        Path(repository_path),
        bundle,
    )
    if errors:
        print(f"factory source lock failed: {source_lock_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"factory source lock passed: {source_lock_path}")
    print(
        "factory source lock sha256: "
        f"{source_lock['factory_source_lock_sha256']}"
    )
    print(f"release tag: {source_lock['repository']['release_tag']}")
    print(f"release commit: {source_lock['repository']['commit_oid']}")
    print(f"locked control inputs: {source_lock['rebuild']['input_count']}")
    print("qualification evidence granted: false")
    print("runtime eligible: false")
    print("activation authorized: false")
    return 0


def _load_rebuild_inputs(
    source_lock_path: str,
    runtime_assessment_path: str,
    contract_evidence_path: str,
    qualification_plan_path: str,
    policy_path: str,
) -> tuple[Any, Any, Any, Any, Any] | None:
    source_lock = load_json_document(source_lock_path, "factory source lock")
    runtime_assessment = load_json_document(
        runtime_assessment_path,
        "runtime assessment",
    )
    contract_evidence = load_json_document(
        contract_evidence_path,
        "qualification evidence",
    )
    qualification_plan = load_json_document(
        qualification_plan_path,
        "qualification plan",
    )
    policy = load_json_document(policy_path, "qualification policy")
    if any(
        document is None
        for document in (
            source_lock,
            runtime_assessment,
            contract_evidence,
            qualification_plan,
            policy,
        )
    ):
        return None
    return (
        source_lock,
        runtime_assessment,
        contract_evidence,
        qualification_plan,
        policy,
    )


def command_rebuild_plan(
    bundle_path: str,
    source_lock_path: str,
    runtime_assessment_path: str,
    runtime_evidence_pack_path: str,
    contract_evidence_path: str,
    qualification_plan_path: str,
    policy_path: str,
    repository_path: str,
    output: str | None,
) -> int:
    bundle = load_bundle(bundle_path, "factory bundle")
    runtime_evidence_pack = load_bounded_binary(
        runtime_evidence_pack_path,
        "runtime-evidence pack",
        MAX_PACK_BYTES,
    )
    documents = _load_rebuild_inputs(
        source_lock_path,
        runtime_assessment_path,
        contract_evidence_path,
        qualification_plan_path,
        policy_path,
    )
    if bundle is None or runtime_evidence_pack is None or documents is None:
        return 2
    (
        source_lock,
        runtime_assessment,
        contract_evidence,
        qualification_plan,
        policy,
    ) = documents
    errors, rebuild_plan = factory_rebuild_plan_for_bundle(
        source_lock,
        runtime_assessment,
        runtime_evidence_pack,
        contract_evidence,
        qualification_plan,
        bundle,
        policy,
        Path(repository_path),
    )
    if errors or rebuild_plan is None:
        print("cannot build factory rebuild plan", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return write_document(rebuild_plan, output)


def command_verify_rebuild_plan(
    rebuild_plan_path: str,
    bundle_path: str,
    source_lock_path: str,
    runtime_assessment_path: str,
    runtime_evidence_pack_path: str,
    contract_evidence_path: str,
    qualification_plan_path: str,
    policy_path: str,
    repository_path: str,
) -> int:
    rebuild_plan = load_json_document(rebuild_plan_path, "factory rebuild plan")
    bundle = load_bundle(bundle_path, "factory bundle")
    runtime_evidence_pack = load_bounded_binary(
        runtime_evidence_pack_path,
        "runtime-evidence pack",
        MAX_PACK_BYTES,
    )
    documents = _load_rebuild_inputs(
        source_lock_path,
        runtime_assessment_path,
        contract_evidence_path,
        qualification_plan_path,
        policy_path,
    )
    if (
        rebuild_plan is None
        or bundle is None
        or runtime_evidence_pack is None
        or documents is None
    ):
        return 2
    (
        source_lock,
        runtime_assessment,
        contract_evidence,
        qualification_plan,
        policy,
    ) = documents
    errors = verify_factory_rebuild_plan_for_bundle(
        rebuild_plan,
        source_lock,
        runtime_assessment,
        runtime_evidence_pack,
        contract_evidence,
        qualification_plan,
        bundle,
        policy,
        Path(repository_path),
    )
    if errors:
        print(f"factory rebuild plan failed: {rebuild_plan_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"factory rebuild plan passed: {rebuild_plan_path}")
    print(
        "factory rebuild plan sha256: "
        f"{rebuild_plan['factory_rebuild_plan_sha256']}"
    )
    print(f"rebuild actions: {rebuild_plan['summary']['action_count']}")
    print(
        "qualification-ready actions: "
        f"{rebuild_plan['summary']['qualification_ready_actions']}"
    )
    print(
        "missing evidence bindings: "
        f"{rebuild_plan['summary']['missing_evidence_bindings']}"
    )
    print(
        "qualification scope: "
        f"{rebuild_plan['source']['qualification_scope']}"
    )
    print("rebuild executed: false")
    print("factory rebuilt: false")
    print("activation authorized: false")
    return 0


def command_qualification_plan(
    bundle_path: str,
    policy_path: str,
    output: str | None,
) -> int:
    bundle = load_bundle(bundle_path, "factory bundle")
    policy = load_json_document(policy_path, "qualification policy")
    if bundle is None or policy is None:
        return 2
    errors, plan = qualification_plan_for_bundle(bundle, policy)
    if errors or plan is None:
        print("cannot build qualification plan", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return write_document(plan, output)


def command_verify_qualification_plan(
    plan_path: str,
    bundle_path: str,
    policy_path: str,
) -> int:
    plan = load_json_document(plan_path, "qualification plan")
    bundle = load_bundle(bundle_path, "factory bundle")
    policy = load_json_document(policy_path, "qualification policy")
    if plan is None or bundle is None or policy is None:
        return 2
    errors = verify_qualification_plan_for_bundle(plan, bundle, policy)
    if errors:
        print(f"qualification plan failed: {plan_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"qualification plan passed: {plan_path}")
    print(f"qualification plan sha256: {plan['qualification_plan_sha256']}")
    print("runtime eligible: false")
    print("activation authorized: false")
    return 0


def command_qualification_evidence(
    plan_path: str,
    bundle_path: str,
    policy_path: str,
    output: str | None,
) -> int:
    plan = load_json_document(plan_path, "qualification plan")
    bundle = load_bundle(bundle_path, "factory bundle")
    policy = load_json_document(policy_path, "qualification policy")
    if plan is None or bundle is None or policy is None:
        return 2
    errors, evidence = qualification_evidence_for_bundle(plan, bundle, policy)
    if errors or evidence is None:
        print("cannot build qualification evidence", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return write_document(evidence, output)


def command_verify_qualification_evidence(
    evidence_path: str,
    plan_path: str,
    bundle_path: str,
    policy_path: str,
) -> int:
    evidence = load_json_document(evidence_path, "qualification evidence")
    plan = load_json_document(plan_path, "qualification plan")
    bundle = load_bundle(bundle_path, "factory bundle")
    policy = load_json_document(policy_path, "qualification policy")
    if evidence is None or plan is None or bundle is None or policy is None:
        return 2
    errors = verify_qualification_evidence_for_bundle(
        evidence,
        plan,
        bundle,
        policy,
    )
    if errors:
        print(f"qualification evidence failed: {evidence_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"qualification evidence passed: {evidence_path}")
    print(
        "qualification evidence sha256: "
        f"{evidence['qualification_evidence_sha256']}"
    )
    print(
        "verified evidence bindings: "
        f"{evidence['summary']['verified_evidence_bindings']}"
    )
    print("runtime eligible: false")
    print("activation authorized: false")
    return 0


def command_qualification_assessment(
    evidence_path: str,
    plan_path: str,
    bundle_path: str,
    policy_path: str,
    output: str | None,
) -> int:
    evidence = load_json_document(evidence_path, "qualification evidence")
    plan = load_json_document(plan_path, "qualification plan")
    bundle = load_bundle(bundle_path, "factory bundle")
    policy = load_json_document(policy_path, "qualification policy")
    if evidence is None or plan is None or bundle is None or policy is None:
        return 2
    errors, assessment = qualification_assessment_for_bundle(
        evidence,
        plan,
        bundle,
        policy,
    )
    if errors or assessment is None:
        print("cannot build qualification assessment", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return write_document(assessment, output)


def command_verify_qualification_assessment(
    assessment_path: str,
    evidence_path: str,
    plan_path: str,
    bundle_path: str,
    policy_path: str,
) -> int:
    assessment = load_json_document(
        assessment_path,
        "qualification assessment",
    )
    evidence = load_json_document(evidence_path, "qualification evidence")
    plan = load_json_document(plan_path, "qualification plan")
    bundle = load_bundle(bundle_path, "factory bundle")
    policy = load_json_document(policy_path, "qualification policy")
    if any(
        value is None
        for value in (assessment, evidence, plan, bundle, policy)
    ):
        return 2
    errors = verify_qualification_assessment_for_bundle(
        assessment,
        evidence,
        plan,
        bundle,
        policy,
    )
    if errors:
        print(
            f"qualification assessment failed: {assessment_path}",
            file=sys.stderr,
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"qualification assessment passed: {assessment_path}")
    print(
        "qualification assessment sha256: "
        f"{assessment['qualification_assessment_sha256']}"
    )
    print(
        "missing evidence bindings: "
        f"{assessment['summary']['missing_evidence_bindings']}"
    )
    print("runtime eligible: false")
    print("activation authorized: false")
    return 0


def command_verify_runtime_evidence(
    runtime_evidence_path: str,
    bundle_path: str,
    qualification_plan_path: str,
    policy_path: str,
    verifier_registry_path: str,
) -> int:
    runtime_evidence = load_json_document(
        runtime_evidence_path,
        "runtime evidence",
    )
    bundle = load_bundle(bundle_path, "factory bundle")
    qualification_plan = load_json_document(
        qualification_plan_path,
        "qualification plan",
    )
    policy = load_json_document(policy_path, "qualification policy")
    verifier_registry = load_json_document(
        verifier_registry_path,
        "runtime evidence verifier registry",
    )
    if any(
        value is None
        for value in (
            runtime_evidence,
            bundle,
            qualification_plan,
            policy,
            verifier_registry,
        )
    ):
        return 2
    assert isinstance(bundle, bytes)
    bundle_errors, verified_bundle = verify_factory_bundle(bundle)
    errors = [f"factory bundle: {error}" for error in bundle_errors]
    if verified_bundle is not None:
        errors.extend(
            validate_runtime_evidence_set(
                runtime_evidence,
                verified_bundle,
                qualification_plan,
                policy,
                verifier_registry,
            )
        )
    if errors:
        print(
            f"runtime evidence failed: {runtime_evidence_path}",
            file=sys.stderr,
        )
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    assert isinstance(runtime_evidence, dict)
    print(f"runtime evidence passed: {runtime_evidence_path}")
    print(
        "runtime evidence sha256: "
        f"{runtime_evidence['runtime_evidence_set_sha256']}"
    )
    print(f"qualification scope: {runtime_evidence['qualification_scope']}")
    print(f"verified signatures: {runtime_evidence['summary']['signature_count']}")
    print("trusted verifier assertions reexecuted: false")
    print("runtime eligibility granted: false")
    print("activation authorized: false")
    print("execution authorized: false")
    return 0


def load_material_index(
    paths: list[str],
    label: str,
) -> dict[str, dict[str, Any]] | None:
    materials: dict[str, dict[str, Any]] = {}
    for path in paths:
        document = load_json_document(path, label)
        if not isinstance(document, dict):
            if document is not None:
                print(f"{label} must be a JSON object: {path}", file=sys.stderr)
            return None
        try:
            digest = sha256_json(document)
        except (RecursionError, TypeError, ValueError) as exc:
            print(f"cannot canonicalize {label} {path}: {exc}", file=sys.stderr)
            return None
        if digest in materials:
            print(f"duplicate {label} digest: {digest}", file=sys.stderr)
            return None
        materials[digest] = document
    return materials


def command_evidence_pack(
    runtime_evidence_path: str,
    bundle_path: str,
    qualification_plan_path: str,
    policy_path: str,
    verifier_registry_path: str,
    evidence_artifact_paths: list[str],
    verifier_implementation_paths: list[str],
    output: str,
) -> int:
    runtime_evidence = load_json_document(
        runtime_evidence_path,
        "runtime evidence",
    )
    verifier_registry = load_json_document(
        verifier_registry_path,
        "runtime evidence verifier registry",
    )
    qualification_plan = load_json_document(
        qualification_plan_path,
        "qualification plan",
    )
    policy = load_json_document(policy_path, "qualification policy")
    bundle = load_bundle(bundle_path, "factory bundle")
    evidence_artifacts = load_material_index(
        evidence_artifact_paths,
        "evidence artifact",
    )
    verifier_implementations = load_material_index(
        verifier_implementation_paths,
        "verifier implementation material",
    )
    if any(
        value is None
        for value in (
            runtime_evidence,
            verifier_registry,
            qualification_plan,
            policy,
            bundle,
            evidence_artifacts,
            verifier_implementations,
        )
    ):
        return 2
    assert isinstance(bundle, bytes)
    errors, pack, _ = runtime_evidence_pack_for_bundle(
        runtime_evidence,
        verifier_registry,
        evidence_artifacts,
        verifier_implementations,
        qualification_plan,
        bundle,
        policy,
    )
    if errors or pack is None:
        print("cannot build runtime-evidence pack", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    result = write_binary(pack, output)
    if result == 0:
        print(f"runtime-evidence pack sha256: {sha256_bytes(pack)}")
    return result


def command_verify_evidence_pack(
    pack_path: str,
    bundle_path: str,
    qualification_plan_path: str,
    policy_path: str,
    manifest_output: str | None,
) -> int:
    pack = load_bounded_binary(
        pack_path,
        "runtime-evidence pack",
        MAX_PACK_BYTES,
    )
    bundle = load_bundle(bundle_path, "factory bundle")
    qualification_plan = load_json_document(
        qualification_plan_path,
        "qualification plan",
    )
    policy = load_json_document(policy_path, "qualification policy")
    if any(
        value is None
        for value in (pack, bundle, qualification_plan, policy)
    ):
        return 2
    assert isinstance(pack, bytes)
    assert isinstance(bundle, bytes)
    errors, verified = verify_runtime_evidence_pack_for_bundle(
        pack,
        qualification_plan,
        bundle,
        policy,
    )
    if errors or verified is None:
        print(f"runtime-evidence pack failed: {pack_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if manifest_output is not None:
        result = write_document(verified["manifest"], manifest_output)
        if result != 0:
            return result
    manifest = verified["manifest"]
    print(f"runtime-evidence pack passed: {pack_path}")
    print(
        "runtime-evidence pack sha256: "
        f"{verified['runtime_evidence_pack_sha256']}"
    )
    print(f"signed receipts: {len(manifest['receipts'])}")
    print(
        "embedded evidence artifacts: "
        f"{sum(item['role'] == 'evidence_artifact' for item in manifest['files'])}"
    )
    print("trusted verifier assertions reexecuted: false")
    print("artifact semantic truth verified: false")
    print("runtime eligibility granted: false")
    print("activation authorized: false")
    print("execution authorized: false")
    return 0


def command_runtime_assessment(
    runtime_evidence_pack_path: str,
    contract_evidence_path: str,
    qualification_plan_path: str,
    bundle_path: str,
    policy_path: str,
    evaluated_at: str,
    output: str | None,
) -> int:
    runtime_evidence_pack = load_bounded_binary(
        runtime_evidence_pack_path,
        "runtime-evidence pack",
        MAX_PACK_BYTES,
    )
    contract_evidence = load_json_document(
        contract_evidence_path,
        "qualification evidence",
    )
    qualification_plan = load_json_document(
        qualification_plan_path,
        "qualification plan",
    )
    bundle = load_bundle(bundle_path, "factory bundle")
    policy = load_json_document(policy_path, "qualification policy")
    if any(
        value is None
        for value in (
            runtime_evidence_pack,
            contract_evidence,
            qualification_plan,
            bundle,
            policy,
        )
    ):
        return 2
    assert isinstance(bundle, bytes)
    errors, assessment = runtime_assessment_for_bundle(
        contract_evidence,
        runtime_evidence_pack,
        qualification_plan,
        bundle,
        policy,
        evaluated_at,
    )
    if errors or assessment is None:
        print("cannot build runtime assessment", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return write_document(assessment, output)


def command_verify_runtime_assessment(
    assessment_path: str,
    runtime_evidence_pack_path: str,
    contract_evidence_path: str,
    qualification_plan_path: str,
    bundle_path: str,
    policy_path: str,
) -> int:
    assessment = load_json_document(assessment_path, "runtime assessment")
    runtime_evidence_pack = load_bounded_binary(
        runtime_evidence_pack_path,
        "runtime-evidence pack",
        MAX_PACK_BYTES,
    )
    contract_evidence = load_json_document(
        contract_evidence_path,
        "qualification evidence",
    )
    qualification_plan = load_json_document(
        qualification_plan_path,
        "qualification plan",
    )
    bundle = load_bundle(bundle_path, "factory bundle")
    policy = load_json_document(policy_path, "qualification policy")
    if any(
        value is None
        for value in (
            assessment,
            runtime_evidence_pack,
            contract_evidence,
            qualification_plan,
            bundle,
            policy,
        )
    ):
        return 2
    assert isinstance(bundle, bytes)
    errors = verify_runtime_assessment_for_bundle(
        assessment,
        contract_evidence,
        runtime_evidence_pack,
        qualification_plan,
        bundle,
        policy,
    )
    if errors:
        print(f"runtime assessment failed: {assessment_path}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    assert isinstance(assessment, dict)
    print(f"runtime assessment passed: {assessment_path}")
    print(
        "runtime assessment sha256: "
        f"{assessment['runtime_assessment_sha256']}"
    )
    print(f"evaluated at: {assessment['source']['evaluated_at']}")
    print(f"qualification scope: {assessment['source']['qualification_scope']}")
    print(
        "runtime-eligible modules: "
        f"{assessment['summary']['runtime_eligible_modules']}"
    )
    print(
        "missing evidence bindings: "
        f"{assessment['summary']['missing_evidence_bindings']}"
    )
    print("activation authorized: false")
    print("execution authorized: false")
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

    inspect_bundle = commands.add_parser(
        "inspect-bundle", help="inspect a verified factory control bundle"
    )
    inspect_bundle.add_argument("path")
    inspect_bundle.add_argument("--output", help="write inspection JSON to a new file")

    compare_bundles = commands.add_parser(
        "compare-bundles", help="compare two verified factory control bundles"
    )
    compare_bundles.add_argument("before_path")
    compare_bundles.add_argument("after_path")
    compare_bundles.add_argument(
        "--output", help="write comparison JSON to a new file"
    )

    portfolio_plan = commands.add_parser(
        "portfolio-plan",
        help="compose verified bundles into a closed multi-factory control plan",
    )
    portfolio_plan.add_argument(
        "portfolio_path",
        help="schema-bound closed factory portfolio definition",
    )
    portfolio_plan.add_argument(
        "bundle_paths",
        nargs="+",
        help="verified factory control bundles in any input order",
    )
    portfolio_plan.add_argument(
        "--output",
        help="write the portfolio plan to a new file instead of stdout",
    )

    verify_portfolio_plan = commands.add_parser(
        "verify-portfolio-plan",
        help="verify a multi-factory plan against its registry and bundles",
    )
    verify_portfolio_plan.add_argument("plan_path")
    verify_portfolio_plan.add_argument("portfolio_path")
    verify_portfolio_plan.add_argument("bundle_paths", nargs="+")

    evidence_return_record = commands.add_parser(
        "evidence-return-record",
        help="bind a verified evidence pack to one declared portfolio route",
    )
    evidence_return_record.add_argument("plan_path")
    evidence_return_record.add_argument("portfolio_path")
    evidence_return_record.add_argument("source_factory_id")
    evidence_return_record.add_argument("runtime_evidence_pack_path")
    evidence_return_record.add_argument("qualification_plan_path")
    evidence_return_record.add_argument("qualification_policy_path")
    evidence_return_record.add_argument("bundle_paths", nargs="+")
    evidence_return_record.add_argument(
        "--output",
        help="write the evidence-return record to a new file instead of stdout",
    )

    verify_evidence_return_record = commands.add_parser(
        "verify-evidence-return-record",
        help="verify a route-bound evidence-return record against every input",
    )
    verify_evidence_return_record.add_argument("record_path")
    verify_evidence_return_record.add_argument("plan_path")
    verify_evidence_return_record.add_argument("portfolio_path")
    verify_evidence_return_record.add_argument("source_factory_id")
    verify_evidence_return_record.add_argument("runtime_evidence_pack_path")
    verify_evidence_return_record.add_argument("qualification_plan_path")
    verify_evidence_return_record.add_argument("qualification_policy_path")
    verify_evidence_return_record.add_argument("bundle_paths", nargs="+")

    source_lock = commands.add_parser(
        "source-lock",
        help="lock a verified bundle to exact sources in an annotated release",
    )
    source_lock.add_argument("factory_path")
    source_lock.add_argument("bundle_path")
    source_lock.add_argument(
        "--repository",
        default=".",
        help="Git repository containing the release objects",
    )
    source_lock.add_argument(
        "--release-tag",
        required=True,
        help="annotated vMAJOR.MINOR.PATCH tag to lock",
    )
    source_lock.add_argument(
        "--catalog-path",
        default="catalog/modules.json",
        help="repository-relative module catalog path",
    )
    source_lock.add_argument(
        "--repository-url",
        default="https://github.com/adaliontech/Zaibatsu",
        help="canonical credential-free HTTPS repository identity",
    )
    source_lock.add_argument(
        "--output", help="write source-lock JSON to a new file"
    )

    verify_source_lock = commands.add_parser(
        "verify-source-lock",
        help="rebuild and verify a source lock from immutable Git objects",
    )
    verify_source_lock.add_argument("source_lock_path")
    verify_source_lock.add_argument("bundle_path")
    verify_source_lock.add_argument(
        "--repository",
        default=".",
        help="Git repository containing the release objects",
    )

    rebuild_plan = commands.add_parser(
        "rebuild-plan",
        help="compile verified inputs into a non-executing factory rebuild DAG",
    )
    rebuild_plan.add_argument("bundle_path")
    rebuild_plan.add_argument(
        "--source-lock",
        default=str(EXAMPLE_SOURCE_LOCK_PATH),
        help="verified annotated-release source lock JSON",
    )
    rebuild_plan.add_argument(
        "--runtime-assessment",
        "--qualification-assessment",
        dest="runtime_assessment",
        default=str(EXAMPLE_RUNTIME_ASSESSMENT_PATH),
        help="signed-evidence runtime assessment JSON",
    )
    rebuild_plan.add_argument(
        "--runtime-evidence-pack",
        required=True,
        help="verified canonical runtime-evidence pack",
    )
    rebuild_plan.add_argument(
        "--qualification-evidence",
        default=str(EXAMPLE_QUALIFICATION_EVIDENCE_PATH),
        help="qualification evidence JSON",
    )
    rebuild_plan.add_argument(
        "--qualification-plan",
        default=str(EXAMPLE_QUALIFICATION_PLAN_PATH),
        help="qualification plan JSON",
    )
    rebuild_plan.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
        help="qualification policy JSON",
    )
    rebuild_plan.add_argument(
        "--repository",
        default=".",
        help="Git repository containing the locked release objects",
    )
    rebuild_plan.add_argument(
        "--output",
        help="write rebuild-plan JSON to a new file",
    )

    verify_rebuild_plan = commands.add_parser(
        "verify-rebuild-plan",
        help="rebuild and verify a non-executing factory rebuild DAG",
    )
    verify_rebuild_plan.add_argument("rebuild_plan_path")
    verify_rebuild_plan.add_argument("bundle_path")
    verify_rebuild_plan.add_argument(
        "--source-lock",
        default=str(EXAMPLE_SOURCE_LOCK_PATH),
    )
    verify_rebuild_plan.add_argument(
        "--runtime-assessment",
        "--qualification-assessment",
        dest="runtime_assessment",
        default=str(EXAMPLE_RUNTIME_ASSESSMENT_PATH),
    )
    verify_rebuild_plan.add_argument(
        "--runtime-evidence-pack",
        required=True,
    )
    verify_rebuild_plan.add_argument(
        "--qualification-evidence",
        default=str(EXAMPLE_QUALIFICATION_EVIDENCE_PATH),
    )
    verify_rebuild_plan.add_argument(
        "--qualification-plan",
        default=str(EXAMPLE_QUALIFICATION_PLAN_PATH),
    )
    verify_rebuild_plan.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
    )
    verify_rebuild_plan.add_argument("--repository", default=".")

    qualification_plan = commands.add_parser(
        "qualification-plan",
        help="list evidence required before bundle modules can be runtime-eligible",
    )
    qualification_plan.add_argument("bundle_path")
    qualification_plan.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
        help="qualification policy JSON",
    )
    qualification_plan.add_argument(
        "--output", help="write qualification-plan JSON to a new file"
    )

    verify_qualification_plan = commands.add_parser(
        "verify-qualification-plan",
        help="verify a qualification plan against its bundle and policy",
    )
    verify_qualification_plan.add_argument("plan_path")
    verify_qualification_plan.add_argument("bundle_path")
    verify_qualification_plan.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
        help="qualification policy JSON",
    )

    qualification_evidence = commands.add_parser(
        "qualification-evidence",
        help="derive contract-conformance receipts from a verified bundle",
    )
    qualification_evidence.add_argument("plan_path")
    qualification_evidence.add_argument("bundle_path")
    qualification_evidence.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
        help="qualification policy JSON",
    )
    qualification_evidence.add_argument(
        "--output", help="write qualification-evidence JSON to a new file"
    )

    verify_qualification_evidence = commands.add_parser(
        "verify-qualification-evidence",
        help="verify bundle-derived qualification evidence",
    )
    verify_qualification_evidence.add_argument("evidence_path")
    verify_qualification_evidence.add_argument("plan_path")
    verify_qualification_evidence.add_argument("bundle_path")
    verify_qualification_evidence.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
        help="qualification policy JSON",
    )

    qualification_assessment = commands.add_parser(
        "qualification-assessment",
        help="assess verified evidence without granting runtime eligibility",
    )
    qualification_assessment.add_argument("evidence_path")
    qualification_assessment.add_argument("plan_path")
    qualification_assessment.add_argument("bundle_path")
    qualification_assessment.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
        help="qualification policy JSON",
    )
    qualification_assessment.add_argument(
        "--output", help="write qualification-assessment JSON to a new file"
    )

    verify_qualification_assessment = commands.add_parser(
        "verify-qualification-assessment",
        help="verify a qualification assessment against every source input",
    )
    verify_qualification_assessment.add_argument("assessment_path")
    verify_qualification_assessment.add_argument("evidence_path")
    verify_qualification_assessment.add_argument("plan_path")
    verify_qualification_assessment.add_argument("bundle_path")
    verify_qualification_assessment.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
        help="qualification policy JSON",
    )

    verify_runtime_evidence = commands.add_parser(
        "verify-runtime-evidence",
        help="verify signed runtime evidence and its exact provenance",
    )
    verify_runtime_evidence.add_argument("runtime_evidence_path")
    verify_runtime_evidence.add_argument("bundle_path")
    verify_runtime_evidence.add_argument(
        "--qualification-plan",
        default=str(EXAMPLE_QUALIFICATION_PLAN_PATH),
    )
    verify_runtime_evidence.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
    )
    verify_runtime_evidence.add_argument(
        "--verifier-registry",
        default=str(VERIFIER_REGISTRY_PATH),
    )

    evidence_pack = commands.add_parser(
        "evidence-pack",
        help="build a canonical pack of signed evidence and referenced materials",
    )
    evidence_pack.add_argument("runtime_evidence_path")
    evidence_pack.add_argument("bundle_path")
    evidence_pack.add_argument(
        "--qualification-plan",
        default=str(EXAMPLE_QUALIFICATION_PLAN_PATH),
    )
    evidence_pack.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
    )
    evidence_pack.add_argument(
        "--verifier-registry",
        default=str(VERIFIER_REGISTRY_PATH),
    )
    evidence_pack.add_argument(
        "--evidence-artifact",
        action="append",
        required=True,
        dest="evidence_artifacts",
        help="JSON artifact whose canonical digest is referenced by a receipt",
    )
    evidence_pack.add_argument(
        "--verifier-implementation",
        action="append",
        required=True,
        dest="verifier_implementations",
        help="JSON verifier material whose canonical digest is referenced by a receipt",
    )
    evidence_pack.add_argument(
        "--output",
        required=True,
        help="write a new canonical uncompressed tar",
    )

    verify_evidence_pack = commands.add_parser(
        "verify-evidence-pack",
        help="verify a canonical runtime-evidence pack and every embedded digest",
    )
    verify_evidence_pack.add_argument("pack_path")
    verify_evidence_pack.add_argument("bundle_path")
    verify_evidence_pack.add_argument(
        "--qualification-plan",
        default=str(EXAMPLE_QUALIFICATION_PLAN_PATH),
    )
    verify_evidence_pack.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
    )
    verify_evidence_pack.add_argument(
        "--manifest-output",
        help="write the verified pack manifest to a new JSON file",
    )

    runtime_assessment = commands.add_parser(
        "runtime-assessment",
        help="assess a verified evidence pack at an explicit time without execution",
    )
    runtime_assessment.add_argument("runtime_evidence_pack_path")
    runtime_assessment.add_argument("contract_evidence_path")
    runtime_assessment.add_argument("qualification_plan_path")
    runtime_assessment.add_argument("bundle_path")
    runtime_assessment.add_argument(
        "--as-of",
        required=True,
        dest="evaluated_at",
        help="exact RFC3339 UTC assessment time",
    )
    runtime_assessment.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
    )
    runtime_assessment.add_argument(
        "--output",
        help="write runtime-assessment JSON to a new file",
    )

    verify_runtime_assessment = commands.add_parser(
        "verify-runtime-assessment",
        help="rebuild an assessment and reverify its complete evidence pack",
    )
    verify_runtime_assessment.add_argument("assessment_path")
    verify_runtime_assessment.add_argument("runtime_evidence_pack_path")
    verify_runtime_assessment.add_argument("contract_evidence_path")
    verify_runtime_assessment.add_argument("qualification_plan_path")
    verify_runtime_assessment.add_argument("bundle_path")
    verify_runtime_assessment.add_argument(
        "--policy",
        default=str(QUALIFICATION_POLICY_PATH),
    )

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
    if arguments.command == "inspect-bundle":
        return command_inspect_bundle(arguments.path, arguments.output)
    if arguments.command == "compare-bundles":
        return command_compare_bundles(
            arguments.before_path,
            arguments.after_path,
            arguments.output,
        )
    if arguments.command == "portfolio-plan":
        return command_portfolio_plan(
            arguments.portfolio_path,
            arguments.bundle_paths,
            arguments.output,
        )
    if arguments.command == "verify-portfolio-plan":
        return command_verify_portfolio_plan(
            arguments.plan_path,
            arguments.portfolio_path,
            arguments.bundle_paths,
        )
    if arguments.command == "evidence-return-record":
        return command_evidence_return_record(
            arguments.plan_path,
            arguments.portfolio_path,
            arguments.source_factory_id,
            arguments.runtime_evidence_pack_path,
            arguments.qualification_plan_path,
            arguments.qualification_policy_path,
            arguments.bundle_paths,
            arguments.output,
        )
    if arguments.command == "verify-evidence-return-record":
        return command_verify_evidence_return_record(
            arguments.record_path,
            arguments.plan_path,
            arguments.portfolio_path,
            arguments.source_factory_id,
            arguments.runtime_evidence_pack_path,
            arguments.qualification_plan_path,
            arguments.qualification_policy_path,
            arguments.bundle_paths,
        )
    if arguments.command == "source-lock":
        return command_source_lock(
            arguments.factory_path,
            arguments.bundle_path,
            arguments.repository,
            arguments.release_tag,
            arguments.catalog_path,
            arguments.repository_url,
            arguments.output,
        )
    if arguments.command == "verify-source-lock":
        return command_verify_source_lock(
            arguments.source_lock_path,
            arguments.bundle_path,
            arguments.repository,
        )
    if arguments.command == "rebuild-plan":
        return command_rebuild_plan(
            arguments.bundle_path,
            arguments.source_lock,
            arguments.runtime_assessment,
            arguments.runtime_evidence_pack,
            arguments.qualification_evidence,
            arguments.qualification_plan,
            arguments.policy,
            arguments.repository,
            arguments.output,
        )
    if arguments.command == "verify-rebuild-plan":
        return command_verify_rebuild_plan(
            arguments.rebuild_plan_path,
            arguments.bundle_path,
            arguments.source_lock,
            arguments.runtime_assessment,
            arguments.runtime_evidence_pack,
            arguments.qualification_evidence,
            arguments.qualification_plan,
            arguments.policy,
            arguments.repository,
        )
    if arguments.command == "qualification-plan":
        return command_qualification_plan(
            arguments.bundle_path,
            arguments.policy,
            arguments.output,
        )
    if arguments.command == "verify-qualification-plan":
        return command_verify_qualification_plan(
            arguments.plan_path,
            arguments.bundle_path,
            arguments.policy,
        )
    if arguments.command == "qualification-evidence":
        return command_qualification_evidence(
            arguments.plan_path,
            arguments.bundle_path,
            arguments.policy,
            arguments.output,
        )
    if arguments.command == "verify-qualification-evidence":
        return command_verify_qualification_evidence(
            arguments.evidence_path,
            arguments.plan_path,
            arguments.bundle_path,
            arguments.policy,
        )
    if arguments.command == "qualification-assessment":
        return command_qualification_assessment(
            arguments.evidence_path,
            arguments.plan_path,
            arguments.bundle_path,
            arguments.policy,
            arguments.output,
        )
    if arguments.command == "verify-qualification-assessment":
        return command_verify_qualification_assessment(
            arguments.assessment_path,
            arguments.evidence_path,
            arguments.plan_path,
            arguments.bundle_path,
            arguments.policy,
        )
    if arguments.command == "verify-runtime-evidence":
        return command_verify_runtime_evidence(
            arguments.runtime_evidence_path,
            arguments.bundle_path,
            arguments.qualification_plan,
            arguments.policy,
            arguments.verifier_registry,
        )
    if arguments.command == "evidence-pack":
        return command_evidence_pack(
            arguments.runtime_evidence_path,
            arguments.bundle_path,
            arguments.qualification_plan,
            arguments.policy,
            arguments.verifier_registry,
            arguments.evidence_artifacts,
            arguments.verifier_implementations,
            arguments.output,
        )
    if arguments.command == "verify-evidence-pack":
        return command_verify_evidence_pack(
            arguments.pack_path,
            arguments.bundle_path,
            arguments.qualification_plan,
            arguments.policy,
            arguments.manifest_output,
        )
    if arguments.command == "runtime-assessment":
        return command_runtime_assessment(
            arguments.runtime_evidence_pack_path,
            arguments.contract_evidence_path,
            arguments.qualification_plan_path,
            arguments.bundle_path,
            arguments.policy,
            arguments.evaluated_at,
            arguments.output,
        )
    if arguments.command == "verify-runtime-assessment":
        return command_verify_runtime_assessment(
            arguments.assessment_path,
            arguments.runtime_evidence_pack_path,
            arguments.contract_evidence_path,
            arguments.qualification_plan_path,
            arguments.bundle_path,
            arguments.policy,
        )
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
