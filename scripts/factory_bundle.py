#!/usr/bin/env python3
"""Build and verify canonical, self-contained Zaibatsu control bundles."""

from __future__ import annotations

import hashlib
import io
import tarfile
from pathlib import Path, PurePosixPath
from typing import Any

from factory_composer import (
    MODULE_API_VERSION,
    build_factory_plan,
    canonical_json_bytes,
    load_json_bytes,
    load_json_file,
    sha256_json,
    validate_factory_bindings,
    validate_factory_plan,
    validate_module_artifact,
    validate_module_catalog,
)


BUNDLE_MANIFEST_SCHEMA_VERSION = "zaibatsu.factory-bundle-manifest.v1"
BUNDLE_MANIFEST_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.3.0/schemas/factory-bundle-manifest.schema.json"
)
MAX_BUNDLE_BYTES = 2 * 1024 * 1024
MAX_MEMBER_BYTES = 256 * 1024
MAX_MEMBERS = 32
ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = "MANIFEST.json"
DEFINITION_PATH = "factory/definition.json"
CATALOG_PATH = "factory/catalog.json"
PLAN_PATH = "factory/plan.json"
CONTRACT_SCHEMAS = {
    "schemas/factory-definition.schema.json": (
        "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
        "v1.2.0/schemas/factory-definition.schema.json",
        "f34cfd745da82c6db906e245844125fc0e6b6a26c136038ae8e6cacd93ed5144",
    ),
    "schemas/module-catalog.schema.json": (
        "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
        "v1.3.0/schemas/module-catalog.schema.json",
        "99086403632bfb2485811c355d47613b40226a9d5feb7ceb8dc26484de42940f",
    ),
    "schemas/module-artifact.schema.json": (
        "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
        "v1.3.0/schemas/module-artifact.schema.json",
        "2c04467de31db7bd68c710f4942239ba3d215dc2c9da7524e681fb60c0b0c0ef",
    ),
    "schemas/factory-plan.schema.json": (
        "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
        "v1.3.0/schemas/factory-plan.schema.json",
        "11576bb2f8bec6d554560ec9a2d3decdbea02edfe130cb66982b641a854f34b1",
    ),
    "schemas/factory-bundle-manifest.schema.json": (
        BUNDLE_MANIFEST_SCHEMA_REFERENCE,
        "5eb51f5f7bbcc7806ed0b28906f22a6c994fdfdbfb3af0db711431651e564ab4",
    ),
}


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe_member_name(value: Any) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(
        part not in {"", ".", ".."} for part in path.parts
    )


def _strict_json_bytes(value: bytes) -> Any:
    return load_json_bytes(value)


def selected_artifacts(
    plan: dict[str, Any], artifacts: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    return {module["module"]: artifacts[module["module"]] for module in plan["modules"]}


def load_contract_schemas(root: Path = ROOT) -> dict[str, dict[str, Any]]:
    schemas: dict[str, dict[str, Any]] = {}
    for path, (expected_id, expected_digest) in CONTRACT_SCHEMAS.items():
        schema = load_json_file(root / path)
        if (
            not isinstance(schema, dict)
            or schema.get("$id") != expected_id
            or sha256_json(schema) != expected_digest
        ):
            raise ValueError(f"local contract schema does not match immutable release: {path}")
        schemas[path] = schema
    return schemas


def build_bundle_payloads(
    definition: dict[str, Any],
    catalog: dict[str, Any],
    plan: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
    schemas: dict[str, dict[str, Any]] | None = None,
) -> dict[str, bytes]:
    payloads = {
        DEFINITION_PATH: canonical_json_bytes(definition),
        CATALOG_PATH: canonical_json_bytes(catalog),
        PLAN_PATH: canonical_json_bytes(plan),
    }
    for module in plan["modules"]:
        module_id = module["module"]
        artifact_path = module["artifact"]["path"]
        payloads[artifact_path] = canonical_json_bytes(artifacts[module_id])
    for schema_path, schema in (schemas or load_contract_schemas()).items():
        payloads[schema_path] = canonical_json_bytes(schema)
    return payloads


def build_bundle_manifest(
    definition: dict[str, Any],
    catalog: dict[str, Any],
    plan: dict[str, Any],
    payloads: dict[str, bytes],
) -> dict[str, Any]:
    return {
        "contract_schema": BUNDLE_MANIFEST_SCHEMA_REFERENCE,
        "schema_version": BUNDLE_MANIFEST_SCHEMA_VERSION,
        "factory": {
            "id": definition["factory"]["id"],
            "class": definition["factory"]["class"],
        },
        "source": {
            "factory_definition_sha256": sha256_json(definition),
            "module_catalog_sha256": sha256_json(catalog),
            "factory_plan_sha256": plan["plan_sha256"],
            "module_api_version": MODULE_API_VERSION,
        },
        "files": [
            {
                "path": path,
                "sha256": sha256_bytes(payloads[path]),
                "size": len(payloads[path]),
            }
            for path in sorted(payloads)
        ],
        "selected_modules": [
            {
                "position": module["position"],
                "slot": module["slot"],
                "module": module["module"],
                "artifact_sha256": module["artifact"]["sha256"],
            }
            for module in plan["modules"]
        ],
        "rebuild_claim": {
            "scope": "portable_control_bundle",
            "byte_reproducible": True,
            "contains_selected_module_contracts": True,
            "contains_contract_schemas": True,
            "contains_runtime_implementations": False,
            "deploys_infrastructure": False,
            "proves_runtime_recovery": False,
        },
    }


def canonical_tar_bytes(payloads: dict[str, bytes]) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for name in sorted(payloads):
            data = payloads[name]
            member = tarfile.TarInfo(name)
            member.size = len(data)
            member.mode = 0o644
            member.mtime = 0
            member.uid = 0
            member.gid = 0
            member.uname = ""
            member.gname = ""
            archive.addfile(member, io.BytesIO(data))
    return output.getvalue()


def build_factory_bundle(
    definition: dict[str, Any],
    catalog: dict[str, Any],
    artifacts: dict[str, dict[str, Any]],
    schemas: dict[str, dict[str, Any]] | None = None,
) -> tuple[bytes, dict[str, Any]]:
    plan = build_factory_plan(definition, catalog)
    chosen = selected_artifacts(plan, artifacts)
    payloads = build_bundle_payloads(definition, catalog, plan, chosen, schemas)
    manifest = build_bundle_manifest(definition, catalog, plan, payloads)
    archive_payloads = dict(payloads)
    archive_payloads[MANIFEST_PATH] = canonical_json_bytes(manifest)
    return canonical_tar_bytes(archive_payloads), manifest


def validate_bundle_manifest(
    manifest: Any,
    definition: Any,
    catalog: Any,
    plan: Any,
    payloads: dict[str, bytes],
) -> list[str]:
    if not all(isinstance(value, dict) for value in (manifest, definition, catalog, plan)):
        return ["bundle manifest and control documents must be objects"]
    try:
        expected = build_bundle_manifest(definition, catalog, plan, payloads)
    except (KeyError, TypeError, ValueError) as exc:
        return [f"cannot derive expected bundle manifest: {exc}"]
    if manifest != expected:
        return ["bundle manifest does not exactly match its content-addressed payloads"]
    return []


def _read_archive_payloads(bundle: bytes) -> tuple[dict[str, bytes], list[str]]:
    errors: list[str] = []
    payloads: dict[str, bytes] = {}
    if not isinstance(bundle, bytes):
        return {}, ["factory bundle must be bytes"]
    if not bundle or len(bundle) > MAX_BUNDLE_BYTES:
        return {}, ["factory bundle size is outside the accepted boundary"]
    try:
        with tarfile.open(fileobj=io.BytesIO(bundle), mode="r:") as archive:
            if archive.pax_headers:
                errors.append("factory bundle must not contain global PAX metadata")
            members = archive.getmembers()
            if not members or len(members) > MAX_MEMBERS:
                errors.append("factory bundle member count is outside the accepted boundary")
            seen: set[str] = set()
            for member in members:
                name = member.name
                if not _safe_member_name(name):
                    errors.append(f"unsafe factory bundle member path: {name!r}")
                    continue
                if name in seen:
                    errors.append(f"duplicate factory bundle member: {name}")
                    continue
                seen.add(name)
                if not member.isfile():
                    errors.append(f"factory bundle member must be a regular file: {name}")
                    continue
                if member.size <= 0 or member.size > MAX_MEMBER_BYTES:
                    errors.append(f"factory bundle member size is invalid: {name}")
                    continue
                if (
                    member.mode != 0o644
                    or member.mtime != 0
                    or member.uid != 0
                    or member.gid != 0
                    or member.uname
                    or member.gname
                    or member.pax_headers
                ):
                    errors.append(f"factory bundle member metadata is not canonical: {name}")
                extracted = archive.extractfile(member)
                if extracted is None:
                    errors.append(f"cannot read factory bundle member: {name}")
                    continue
                data = extracted.read(MAX_MEMBER_BYTES + 1)
                if len(data) != member.size:
                    errors.append(f"factory bundle member length is inconsistent: {name}")
                    continue
                payloads[name] = data
    except (tarfile.TarError, EOFError, OSError, ValueError) as exc:
        return {}, [f"cannot read factory bundle: {exc}"]
    return payloads, errors


def verify_factory_bundle(bundle: bytes) -> tuple[list[str], dict[str, Any] | None]:
    payloads, errors = _read_archive_payloads(bundle)
    required = {
        MANIFEST_PATH,
        DEFINITION_PATH,
        CATALOG_PATH,
        PLAN_PATH,
        *CONTRACT_SCHEMAS,
    }
    missing = required - set(payloads)
    if missing:
        errors.append("factory bundle missing control members: " + ", ".join(sorted(missing)))
        return errors, None
    parsed: dict[str, Any] = {}
    for path in required:
        try:
            parsed[path] = _strict_json_bytes(payloads[path])
        except (UnicodeDecodeError, ValueError) as exc:
            errors.append(f"cannot parse {path}: {exc}")
    if errors:
        return errors, None
    manifest = parsed[MANIFEST_PATH]
    definition = parsed[DEFINITION_PATH]
    catalog = parsed[CATALOG_PATH]
    plan = parsed[PLAN_PATH]

    for schema_path, (expected_id, expected_digest) in CONTRACT_SCHEMAS.items():
        try:
            schema = _strict_json_bytes(payloads[schema_path])
        except (UnicodeDecodeError, ValueError) as exc:
            errors.append(f"cannot parse bundled schema {schema_path}: {exc}")
            continue
        if not isinstance(schema, dict):
            errors.append(f"bundled schema must be an object: {schema_path}")
        elif (
            schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
            or schema.get("$id") != expected_id
            or schema.get("type") != "object"
        ):
            errors.append(f"bundled schema identity or root contract is invalid: {schema_path}")
        elif sha256_json(schema) != expected_digest:
            errors.append(
                f"bundled schema does not match immutable content digest: {schema_path}"
            )

    from validate_repository import validate_factory_definition

    errors.extend(validate_factory_definition(definition))
    errors.extend(validate_module_catalog(catalog))
    errors.extend(validate_factory_bindings(definition, catalog))
    errors.extend(validate_factory_plan(plan, definition, catalog))
    if errors:
        return errors, None

    modules = {module["id"]: module for module in catalog["modules"]}
    expected_members = set(required)
    for resolved in plan["modules"]:
        module_id = resolved["module"]
        artifact_path = resolved["artifact"]["path"]
        expected_members.add(artifact_path)
        data = payloads.get(artifact_path)
        if data is None:
            errors.append(f"factory bundle missing selected module artifact: {module_id}")
            continue
        try:
            artifact = _strict_json_bytes(data)
        except (UnicodeDecodeError, ValueError) as exc:
            errors.append(f"cannot parse module artifact {module_id}: {exc}")
            continue
        errors.extend(validate_module_artifact(artifact, modules.get(module_id)))
        if sha256_json(artifact) != resolved["artifact"]["sha256"]:
            errors.append(f"factory bundle module artifact digest mismatch: {module_id}")
    extra = set(payloads) - expected_members
    if extra:
        errors.append("factory bundle contains unexpected members: " + ", ".join(sorted(extra)))
    if errors:
        return errors, None

    content_payloads = {path: data for path, data in payloads.items() if path != MANIFEST_PATH}
    errors.extend(
        validate_bundle_manifest(manifest, definition, catalog, plan, content_payloads)
    )
    if errors:
        return errors, None
    for path, data in payloads.items():
        try:
            parsed_value = _strict_json_bytes(data)
        except (UnicodeDecodeError, ValueError) as exc:
            return [f"cannot canonicalize factory bundle member {path}: {exc}"], None
        if data != canonical_json_bytes(parsed_value):
            return [f"factory bundle member is not canonical JSON: {path}"], None
    expected_bundle = canonical_tar_bytes(payloads)
    if bundle != expected_bundle:
        return ["factory bundle bytes are not canonical or reproducible"], None
    return [], {
        "bundle_sha256": sha256_bytes(bundle),
        "plan_sha256": plan["plan_sha256"],
        "factory_id": definition["factory"]["id"],
        "manifest": manifest,
    }
