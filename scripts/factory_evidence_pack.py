#!/usr/bin/env python3
"""Build and verify canonical packs for signed runtime-evidence material."""

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
from factory_composer import (
    canonical_json_bytes,
    load_json_bytes,
    load_json_file,
    sha256_json,
)
from factory_runtime_evidence import validate_runtime_evidence_set


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_PACK_MANIFEST_PATH = (
    ROOT / "examples" / "economic-factory.runtime-evidence-pack-manifest.json"
)
PACK_SCHEMA_PATH = ROOT / "schemas" / "runtime-evidence-pack-manifest.schema.json"

PACK_MANIFEST_SCHEMA_VERSION = "zaibatsu.runtime-evidence-pack-manifest.v1"
PACK_MANIFEST_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.10.0/schemas/runtime-evidence-pack-manifest.schema.json"
)
PACK_MANIFEST_SCHEMA_SHA256 = (
    "1f843c1883dad7cd956ab29d255a48a7736e6b75d31f7baaf46c403635fea0f2"
)

MAX_PACK_BYTES = 16 * 1024 * 1024
MAX_MEMBER_BYTES = 256 * 1024
MAX_RECEIPTS = 256
MAX_MEMBERS = 2 * MAX_RECEIPTS + 4

MANIFEST_PATH = "MANIFEST.json"
RUNTIME_EVIDENCE_PATH = "runtime-evidence.json"
VERIFIER_REGISTRY_PATH = "verifier-registry.json"
PACKED_SCHEMA_PATH = "schemas/runtime-evidence-pack-manifest.schema.json"
ARTIFACT_PREFIX = "artifacts"
IMPLEMENTATION_PREFIX = "verifier-implementations"

MANIFEST_FIELDS = {
    "contract_schema",
    "schema_version",
    "factory",
    "source",
    "files",
    "receipts",
    "pack_boundary",
}
PACK_BOUNDARY = {
    "canonical_archive": True,
    "runtime_evidence_signatures_reverified": True,
    "evidence_artifacts_embedded": True,
    "evidence_artifact_digests_verified": True,
    "verifier_implementation_materials_embedded": True,
    "verifier_implementation_digests_verified": True,
    "verifier_assertions_reexecuted": False,
    "artifact_semantic_truth_verified": False,
    "verifier_key_ownership_verified": False,
    "verifier_independence_verified": False,
    "pack_grants_runtime_eligibility": False,
    "activation_authorized": False,
    "execution_authorized": False,
}


def load_pack_manifest(
    path: Path = EXAMPLE_PACK_MANIFEST_PATH,
) -> dict[str, Any]:
    return load_json_file(path)


def _artifact_path(digest: str) -> str:
    return f"{ARTIFACT_PREFIX}/{digest}.json"


def _implementation_path(digest: str) -> str:
    return f"{IMPLEMENTATION_PREFIX}/{digest}.json"


def _material_requirements(
    runtime_evidence: dict[str, Any],
) -> tuple[set[str], set[str]]:
    artifact_digests: set[str] = set()
    implementation_digests: set[str] = set()
    for receipt in runtime_evidence["receipts"]:
        payload = receipt["payload"]
        artifact_digests.add(payload["evidence_artifact_sha256"])
        implementation_digests.add(payload["verifier_implementation_sha256"])
    return artifact_digests, implementation_digests


def _validate_materials(
    runtime_evidence: dict[str, Any],
    evidence_artifacts: Any,
    verifier_implementations: Any,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(evidence_artifacts, dict):
        return ["evidence artifacts must be indexed by canonical SHA-256"]
    if not isinstance(verifier_implementations, dict):
        return ["verifier implementations must be indexed by canonical SHA-256"]
    try:
        required_artifacts, required_implementations = _material_requirements(
            runtime_evidence
        )
    except (KeyError, TypeError):
        return ["cannot derive material requirements from runtime evidence"]
    if set(evidence_artifacts) != required_artifacts:
        errors.append(
            "evidence artifacts must exactly match signed artifact digests"
        )
    if set(verifier_implementations) != required_implementations:
        errors.append(
            "verifier implementations must exactly match signed implementation digests"
        )
    for digest, document in evidence_artifacts.items():
        if not isinstance(document, dict):
            errors.append(f"evidence artifact must be a JSON object: {digest}")
            continue
        try:
            actual = sha256_json(document)
        except (RecursionError, TypeError, ValueError):
            actual = None
        if actual != digest:
            errors.append(f"evidence artifact digest mismatch: {digest}")
    for digest, document in verifier_implementations.items():
        if not isinstance(document, dict):
            errors.append(
                f"verifier implementation material must be a JSON object: {digest}"
            )
            continue
        try:
            actual = sha256_json(document)
        except (RecursionError, TypeError, ValueError):
            actual = None
        if actual != digest:
            errors.append(f"verifier implementation digest mismatch: {digest}")
    return errors


def _pack_payloads(
    runtime_evidence: dict[str, Any],
    verifier_registry: dict[str, Any],
    evidence_artifacts: dict[str, dict[str, Any]],
    verifier_implementations: dict[str, dict[str, Any]],
    schema: dict[str, Any],
) -> dict[str, bytes]:
    payloads = {
        RUNTIME_EVIDENCE_PATH: canonical_json_bytes(runtime_evidence),
        VERIFIER_REGISTRY_PATH: canonical_json_bytes(verifier_registry),
        PACKED_SCHEMA_PATH: canonical_json_bytes(schema),
    }
    payloads.update(
        {
            _artifact_path(digest): canonical_json_bytes(document)
            for digest, document in evidence_artifacts.items()
        }
    )
    payloads.update(
        {
            _implementation_path(digest): canonical_json_bytes(document)
            for digest, document in verifier_implementations.items()
        }
    )
    return payloads


def _file_role(path: str) -> str:
    if path == RUNTIME_EVIDENCE_PATH:
        return "runtime_evidence"
    if path == VERIFIER_REGISTRY_PATH:
        return "verifier_registry"
    if path == PACKED_SCHEMA_PATH:
        return "contract_schema"
    if path.startswith(f"{ARTIFACT_PREFIX}/"):
        return "evidence_artifact"
    if path.startswith(f"{IMPLEMENTATION_PREFIX}/"):
        return "verifier_implementation"
    raise ValueError(f"unexpected runtime-evidence pack path: {path}")


def build_pack_manifest(
    runtime_evidence: dict[str, Any],
    payloads: dict[str, bytes],
) -> dict[str, Any]:
    receipts = []
    for position, receipt in enumerate(runtime_evidence["receipts"]):
        payload = receipt["payload"]
        artifact_digest = payload["evidence_artifact_sha256"]
        implementation_digest = payload["verifier_implementation_sha256"]
        receipts.append(
            {
                "position": position,
                "module_position": payload["position"],
                "slot": payload["slot"],
                "module": payload["module"],
                "requirement": payload["requirement"],
                "payload_sha256": receipt["payload_sha256"],
                "evidence_artifact_path": _artifact_path(artifact_digest),
                "evidence_artifact_sha256": artifact_digest,
                "verifier_id": payload["verifier_id"],
                "verification_method": payload["verification_method"],
                "verifier_implementation_path": _implementation_path(
                    implementation_digest
                ),
                "verifier_implementation_sha256": implementation_digest,
            }
        )
    source = runtime_evidence["source"]
    return {
        "contract_schema": PACK_MANIFEST_SCHEMA_REFERENCE,
        "schema_version": PACK_MANIFEST_SCHEMA_VERSION,
        "factory": deepcopy(runtime_evidence["factory"]),
        "source": {
            "bundle_sha256": source["bundle_sha256"],
            "qualification_plan_sha256": source["qualification_plan_sha256"],
            "qualification_policy_id": source["qualification_policy_id"],
            "qualification_policy_sha256": source[
                "qualification_policy_sha256"
            ],
            "runtime_evidence_set_sha256": runtime_evidence[
                "runtime_evidence_set_sha256"
            ],
            "verifier_registry_sha256": source["verifier_registry_sha256"],
            "module_api_version": source["module_api_version"],
            "qualification_scope": runtime_evidence["qualification_scope"],
        },
        "files": [
            {
                "path": path,
                "role": _file_role(path),
                "sha256": sha256_bytes(payloads[path]),
                "size": len(payloads[path]),
            }
            for path in sorted(payloads)
        ],
        "receipts": receipts,
        "pack_boundary": deepcopy(PACK_BOUNDARY),
    }


def build_runtime_evidence_pack(
    runtime_evidence: dict[str, Any],
    verifier_registry: dict[str, Any],
    evidence_artifacts: dict[str, dict[str, Any]],
    verifier_implementations: dict[str, dict[str, Any]],
    schema: dict[str, Any] | None = None,
) -> tuple[bytes, dict[str, Any]]:
    checked_schema = schema or load_json_file(PACK_SCHEMA_PATH)
    if (
        not isinstance(checked_schema, dict)
        or checked_schema.get("$schema")
        != "https://json-schema.org/draft/2020-12/schema"
        or checked_schema.get("$id") != PACK_MANIFEST_SCHEMA_REFERENCE
        or sha256_json(checked_schema) != PACK_MANIFEST_SCHEMA_SHA256
    ):
        raise ValueError("runtime-evidence pack manifest schema is invalid")
    payloads = _pack_payloads(
        runtime_evidence,
        verifier_registry,
        evidence_artifacts,
        verifier_implementations,
        checked_schema,
    )
    manifest = build_pack_manifest(runtime_evidence, payloads)
    archive_payloads = dict(payloads)
    archive_payloads[MANIFEST_PATH] = canonical_json_bytes(manifest)
    if len(archive_payloads) > MAX_MEMBERS:
        raise ValueError("runtime-evidence pack member count exceeds the boundary")
    if any(
        not value or len(value) > MAX_MEMBER_BYTES
        for value in archive_payloads.values()
    ):
        raise ValueError("runtime-evidence pack member size exceeds the boundary")
    pack = canonical_tar_bytes(archive_payloads)
    if len(pack) > MAX_PACK_BYTES:
        raise ValueError("runtime-evidence pack size exceeds the boundary")
    return pack, manifest


def runtime_evidence_pack_for_bundle(
    runtime_evidence: Any,
    verifier_registry: Any,
    evidence_artifacts: Any,
    verifier_implementations: Any,
    qualification_plan: Any,
    bundle: bytes,
    qualification_policy: Any,
) -> tuple[list[str], bytes | None, dict[str, Any] | None]:
    bundle_errors, verified_bundle = verify_factory_bundle(bundle)
    errors = [f"factory bundle: {error}" for error in bundle_errors]
    if verified_bundle is None:
        return errors, None, None
    runtime_errors = validate_runtime_evidence_set(
        runtime_evidence,
        verified_bundle,
        qualification_plan,
        qualification_policy,
        verifier_registry,
    )
    errors.extend(f"runtime evidence: {error}" for error in runtime_errors)
    if runtime_errors:
        return errors, None, None
    assert isinstance(runtime_evidence, dict)
    assert isinstance(verifier_registry, dict)
    material_errors = _validate_materials(
        runtime_evidence,
        evidence_artifacts,
        verifier_implementations,
    )
    errors.extend(material_errors)
    if errors:
        return errors, None, None
    assert isinstance(evidence_artifacts, dict)
    assert isinstance(verifier_implementations, dict)
    try:
        pack, manifest = build_runtime_evidence_pack(
            runtime_evidence,
            verifier_registry,
            evidence_artifacts,
            verifier_implementations,
        )
    except (KeyError, OSError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot build runtime-evidence pack: {exc}"], None, None
    if len(pack) > MAX_PACK_BYTES:
        return ["runtime-evidence pack exceeds the size boundary"], None, None
    verification_errors, verified_pack = verify_runtime_evidence_pack_for_bundle(
        pack,
        qualification_plan,
        bundle,
        qualification_policy,
    )
    if verification_errors or verified_pack is None:
        return [
            f"built runtime-evidence pack: {error}"
            for error in verification_errors
        ], None, None
    return [], pack, manifest


def _parse_pack_payloads(
    payloads: dict[str, bytes],
) -> tuple[dict[str, Any], list[str]]:
    parsed: dict[str, Any] = {}
    errors: list[str] = []
    for path, value in payloads.items():
        try:
            document = load_json_bytes(value)
        except (RecursionError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"cannot parse runtime-evidence pack member {path}: {exc}")
            continue
        if not isinstance(document, dict):
            errors.append(
                f"runtime-evidence pack member must be a JSON object: {path}"
            )
            continue
        try:
            canonical = canonical_json_bytes(document)
        except (RecursionError, TypeError, ValueError) as exc:
            errors.append(
                f"cannot canonicalize runtime-evidence pack member {path}: {exc}"
            )
            continue
        if value != canonical:
            errors.append(f"runtime-evidence pack member is not canonical JSON: {path}")
        parsed[path] = document
    return parsed, errors


def verify_runtime_evidence_pack_for_bundle(
    pack: bytes,
    qualification_plan: Any,
    bundle: bytes,
    qualification_policy: Any,
) -> tuple[list[str], dict[str, Any] | None]:
    payloads, errors = read_bounded_archive_payloads(
        pack,
        label="runtime-evidence pack",
        max_archive_bytes=MAX_PACK_BYTES,
        max_member_bytes=MAX_MEMBER_BYTES,
        max_members=MAX_MEMBERS,
    )
    required_base = {
        MANIFEST_PATH,
        RUNTIME_EVIDENCE_PATH,
        VERIFIER_REGISTRY_PATH,
        PACKED_SCHEMA_PATH,
    }
    missing_base = required_base - set(payloads)
    if missing_base:
        errors.append(
            "runtime-evidence pack missing required members: "
            + ", ".join(sorted(missing_base))
        )
    parsed, parse_errors = _parse_pack_payloads(payloads)
    errors.extend(parse_errors)
    if errors or not required_base <= set(parsed):
        return errors, None

    manifest = parsed[MANIFEST_PATH]
    runtime_evidence = parsed[RUNTIME_EVIDENCE_PATH]
    verifier_registry = parsed[VERIFIER_REGISTRY_PATH]
    schema = parsed[PACKED_SCHEMA_PATH]
    if (
        schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema"
        or schema.get("$id") != PACK_MANIFEST_SCHEMA_REFERENCE
        or sha256_json(schema) != PACK_MANIFEST_SCHEMA_SHA256
    ):
        errors.append("packed runtime-evidence manifest schema is invalid")

    bundle_errors, verified_bundle = verify_factory_bundle(bundle)
    errors.extend(f"factory bundle: {error}" for error in bundle_errors)
    if verified_bundle is None:
        return errors, None
    runtime_errors = validate_runtime_evidence_set(
        runtime_evidence,
        verified_bundle,
        qualification_plan,
        qualification_policy,
        verifier_registry,
    )
    errors.extend(f"runtime evidence: {error}" for error in runtime_errors)
    if runtime_errors:
        return errors, None

    try:
        artifact_digests, implementation_digests = _material_requirements(
            runtime_evidence
        )
    except (KeyError, TypeError) as exc:
        return errors + [f"cannot derive packed material requirements: {exc}"], None
    expected_members = {
        *required_base,
        *(_artifact_path(digest) for digest in artifact_digests),
        *(_implementation_path(digest) for digest in implementation_digests),
    }
    missing = expected_members - set(payloads)
    extra = set(payloads) - expected_members
    if missing:
        errors.append(
            "runtime-evidence pack missing content-addressed materials: "
            + ", ".join(sorted(missing))
        )
    if extra:
        errors.append(
            "runtime-evidence pack contains unexpected members: "
            + ", ".join(sorted(extra))
        )

    evidence_artifacts = {
        digest: parsed.get(_artifact_path(digest))
        for digest in artifact_digests
    }
    verifier_implementations = {
        digest: parsed.get(_implementation_path(digest))
        for digest in implementation_digests
    }
    material_errors = _validate_materials(
        runtime_evidence,
        evidence_artifacts,
        verifier_implementations,
    )
    errors.extend(material_errors)
    if errors:
        return errors, None

    content_payloads = {
        path: value for path, value in payloads.items() if path != MANIFEST_PATH
    }
    try:
        expected_manifest = build_pack_manifest(runtime_evidence, content_payloads)
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return [f"cannot derive expected runtime-evidence pack manifest: {exc}"], None
    if set(manifest) != MANIFEST_FIELDS:
        errors.append("runtime-evidence pack manifest has ambiguous fields")
    if canonical_json_bytes(manifest) != canonical_json_bytes(expected_manifest):
        errors.append(
            "runtime-evidence pack manifest does not exactly match its payloads"
        )
    if canonical_json_bytes(manifest.get("pack_boundary")) != canonical_json_bytes(
        PACK_BOUNDARY
    ):
        errors.append("runtime-evidence pack boundary is invalid")
    if pack != canonical_tar_bytes(payloads):
        errors.append("runtime-evidence pack bytes are not canonical or reproducible")
    if errors:
        return errors, None
    return [], {
        "runtime_evidence_pack_sha256": sha256_bytes(pack),
        "manifest": manifest,
        "runtime_evidence": runtime_evidence,
        "verifier_registry": verifier_registry,
        "evidence_artifacts": evidence_artifacts,
        "verifier_implementations": verifier_implementations,
    }
