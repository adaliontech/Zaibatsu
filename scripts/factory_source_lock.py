#!/usr/bin/env python3
"""Bind a verified control bundle to exact files in an annotated Git release."""

from __future__ import annotations

import hashlib
import os
import re
import subprocess
from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import urlsplit

from factory_bundle import (
    CONTRACT_SCHEMAS,
    build_factory_bundle,
    sha256_bytes,
    verify_factory_bundle,
)
from factory_composer import (
    MODULE_API_VERSION,
    build_factory_plan,
    canonical_json_bytes,
    load_json_bytes,
    sha256_json,
    validate_factory_bindings,
    validate_factory_plan,
    validate_module_artifact,
    validate_module_catalog,
)
ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_SOURCE_LOCK_PATH = ROOT / "examples" / "economic-factory.source-lock.json"
SOURCE_LOCK_SCHEMA_VERSION = "zaibatsu.factory-source-lock.v1"
SOURCE_LOCK_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.7.0/schemas/factory-source-lock.schema.json"
)
PUBLIC_REPOSITORY_URL = "https://github.com/adaliontech/Zaibatsu"
MAX_SOURCE_FILE_BYTES = 256 * 1024
MAX_GIT_OUTPUT_BYTES = 1024 * 1024
RELEASE_TAG_RE = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+$")
HEX_40_RE = re.compile(r"^[0-9a-f]{40}$")
HEX_64_RE = re.compile(r"^[0-9a-f]{64}$")
REPOSITORY_PATH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")
REPOSITORY_HOST_LABEL = r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
REPOSITORY_URL_RE = re.compile(
    rf"^https://{REPOSITORY_HOST_LABEL}(?:\.{REPOSITORY_HOST_LABEL})*"
    r"/(?!\.{1,2}(?:/|$))[A-Za-z0-9._~-]+"
    r"(?:/(?!\.{1,2}(?:/|$))[A-Za-z0-9._~-]+)*$"
)
SOURCE_LOCK_FIELDS = {
    "contract_schema",
    "schema_version",
    "factory",
    "repository",
    "source",
    "inputs",
    "rebuild",
    "source_lock_boundary",
    "factory_source_lock_sha256",
}
SOURCE_LOCK_BOUNDARY = {
    "locks_control_sources_only": True,
    "reads_immutable_git_objects_not_worktree": True,
    "remote_repository_contacted": False,
    "repository_ownership_verified": False,
    "tag_signature_verification_included": False,
    "contains_runtime_implementation_source": False,
    "grants_qualification_evidence": False,
    "runtime_eligibility_granted": False,
    "activation_authorized": False,
    "deploys_infrastructure": False,
}
GIT_ENVIRONMENT_DENY = {
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CEILING_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_DIR",
    "GIT_EXEC_PATH",
    "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_REPLACE_REF_BASE",
    "GIT_SHALLOW_FILE",
    "GIT_WORK_TREE",
}


def load_source_lock(path: Path = EXAMPLE_SOURCE_LOCK_PATH) -> dict[str, Any]:
    return load_json_bytes(path.read_bytes())


def _safe_repository_path(value: Any) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or len(value) > 240
        or "\\" in value
        or REPOSITORY_PATH_RE.fullmatch(value) is None
    ):
        return False
    path = PurePosixPath(value)
    return (
        not path.is_absolute()
        and all(part not in {"", ".", "..", ".git"} for part in path.parts)
        and str(path) == value
    )


def _run_git(repository: Path, arguments: list[str]) -> bytes:
    environment = os.environ.copy()
    for key in list(environment):
        if (
            key in GIT_ENVIRONMENT_DENY
            or key == "GIT_CONFIG_COUNT"
            or key.startswith("GIT_CONFIG_KEY_")
            or key.startswith("GIT_CONFIG_VALUE_")
        ):
            environment.pop(key, None)
    environment.update(
        {
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_LITERAL_PATHSPECS": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    try:
        result = subprocess.run(
            ["git", "--no-replace-objects", "-C", str(repository), *arguments],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"cannot run Git: {exc}") from exc
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        if len(detail) > 240:
            detail = detail[:240] + "..."
        raise ValueError(detail or "Git command failed")
    if len(result.stdout) > MAX_GIT_OUTPUT_BYTES:
        raise ValueError("Git output exceeds the source-lock boundary")
    return result.stdout


def _git_text(repository: Path, arguments: list[str]) -> str:
    try:
        value = _run_git(repository, arguments).decode("ascii").strip()
    except UnicodeDecodeError as exc:
        raise ValueError("Git object identity is not ASCII") from exc
    if not value or "\n" in value or "\r" in value:
        raise ValueError("Git object identity is ambiguous")
    return value


def _valid_oid(value: Any, object_format: str) -> bool:
    if not isinstance(value, str):
        return False
    if object_format == "sha1":
        return HEX_40_RE.fullmatch(value) is not None
    if object_format == "sha256":
        return HEX_64_RE.fullmatch(value) is not None
    return False


def _valid_repository_url(value: Any) -> bool:
    if (
        not isinstance(value, str)
        or len(value) > 240
        or REPOSITORY_URL_RE.fullmatch(value) is None
    ):
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    return (
        parsed.scheme == "https"
        and parsed.hostname is not None
        and parsed.username is None
        and parsed.password is None
        and port is None
        and bool(parsed.path.strip("/"))
        and parsed.query == ""
        and parsed.fragment == ""
        and value == value.rstrip("/")
    )


def _git_object_content(repository: Path, oid: str, kind: str) -> bytes:
    if _git_text(repository, ["cat-file", "-t", oid]) != kind:
        raise ValueError(f"release {kind} object has an unexpected type")
    try:
        size = int(_git_text(repository, ["cat-file", "-s", oid]))
    except ValueError as exc:
        raise ValueError(f"cannot inspect release {kind} object size: {exc}") from exc
    if size <= 0 or size > MAX_GIT_OUTPUT_BYTES:
        raise ValueError(f"release {kind} object exceeds the source-lock boundary")
    value = _run_git(repository, ["cat-file", kind, oid])
    if len(value) != size:
        raise ValueError(f"release {kind} object size changed while reading")
    return value


def _release_identity(
    repository: Path,
    release_tag: str,
    repository_url: str,
) -> dict[str, Any]:
    if not RELEASE_TAG_RE.fullmatch(release_tag):
        raise ValueError("release tag must be an exact vMAJOR.MINOR.PATCH tag")
    if not _valid_repository_url(repository_url):
        raise ValueError("repository URL must be a credential-free canonical HTTPS URL")
    object_format = _git_text(repository, ["rev-parse", "--show-object-format"])
    if object_format not in {"sha1", "sha256"}:
        raise ValueError("Git object format is unsupported")
    reference = f"refs/tags/{release_tag}"
    tag_object = _git_text(
        repository,
        ["rev-parse", "--verify", f"{reference}^{{tag}}"],
    )
    try:
        tag_object_value = _git_object_content(repository, tag_object, "tag")
    except ValueError as exc:
        raise ValueError(f"release tag must be an annotated Git tag: {exc}") from exc
    commit = _git_text(
        repository,
        ["rev-parse", "--verify", f"{reference}^{{commit}}"],
    )
    tree = _git_text(
        repository,
        ["rev-parse", "--verify", f"{reference}^{{tree}}"],
    )
    for label, value in (
        ("tag object", tag_object),
        ("commit", commit),
        ("tree", tree),
    ):
        if not _valid_oid(value, object_format):
            raise ValueError(f"{label} does not match the repository object format")
    commit_object_value = _git_object_content(repository, commit, "commit")
    tree_object_value = _git_object_content(repository, tree, "tree")
    return {
        "url": repository_url,
        "object_format": object_format,
        "release_tag": release_tag,
        "tag_object_oid": tag_object,
        "tag_object_sha256": hashlib.sha256(tag_object_value).hexdigest(),
        "commit_oid": commit,
        "commit_object_sha256": hashlib.sha256(commit_object_value).hexdigest(),
        "tree_oid": tree,
        "tree_object_sha256": hashlib.sha256(tree_object_value).hexdigest(),
        "annotated_tag_verified": True,
        "tag_signature_verification_included": False,
    }


def _git_blob(
    repository: Path,
    commit_oid: str,
    path: str,
    object_format: str,
) -> tuple[bytes, dict[str, Any]]:
    if not _safe_repository_path(path):
        raise ValueError(f"unsafe source-lock path: {path!r}")
    output = _run_git(
        repository,
        ["ls-tree", "-z", "--full-tree", commit_oid, "--", path],
    )
    entries = [entry for entry in output.split(b"\0") if entry]
    if len(entries) != 1:
        raise ValueError(f"release must contain exactly one source path: {path}")
    try:
        metadata, returned_path = entries[0].split(b"\t", 1)
        mode, kind, oid = metadata.decode("ascii").split(" ", 2)
        decoded_path = returned_path.decode("utf-8")
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError(f"cannot parse Git tree entry: {path}") from exc
    if decoded_path != path:
        raise ValueError(f"Git returned an unexpected source path for {path}")
    if mode != "100644" or kind != "blob" or not _valid_oid(oid, object_format):
        raise ValueError(f"source-lock input must be a regular non-executable blob: {path}")
    try:
        size = int(_git_text(repository, ["cat-file", "-s", oid]))
    except ValueError as exc:
        raise ValueError(f"cannot inspect Git blob size: {path}: {exc}") from exc
    if size <= 0 or size > MAX_SOURCE_FILE_BYTES:
        raise ValueError(f"Git blob size is outside the source-lock boundary: {path}")
    value = _run_git(repository, ["cat-file", "blob", oid])
    if len(value) != size:
        raise ValueError(f"Git blob size changed while reading: {path}")
    try:
        document = load_json_bytes(value)
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError(f"source-lock input must be strict JSON: {path}: {exc}") from exc
    return value, {
        "path": path,
        "mode": mode,
        "git_blob_oid": oid,
        "file_sha256": hashlib.sha256(value).hexdigest(),
        "canonical_json_sha256": sha256_json(document),
    }


def _artifact_repository_path(catalog_path: str, artifact_path: str) -> str:
    catalog_parent = PurePosixPath(catalog_path).parent
    joined = str(catalog_parent / PurePosixPath(artifact_path))
    if not _safe_repository_path(joined):
        raise ValueError(f"unsafe module artifact source path: {artifact_path!r}")
    return joined


def _tagged_control_sources(
    repository: Path,
    release: dict[str, Any],
    factory_definition_path: str,
    catalog_path: str,
) -> tuple[
    list[dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
]:
    # Imported lazily so the repository validator can import this module
    # without creating an import cycle.
    from validate_repository import validate_factory_definition

    for path in (factory_definition_path, catalog_path):
        if not _safe_repository_path(path):
            raise ValueError(f"unsafe source-lock path: {path!r}")
    commit_oid = release["commit_oid"]
    object_format = release["object_format"]
    blob_values: dict[str, bytes] = {}
    input_by_path: dict[str, dict[str, Any]] = {}

    def read(path: str) -> Any:
        if path not in blob_values:
            value, entry = _git_blob(
                repository,
                commit_oid,
                path,
                object_format,
            )
            blob_values[path] = value
            input_by_path[path] = entry
        return load_json_bytes(blob_values[path])

    definition = read(factory_definition_path)
    catalog = read(catalog_path)
    errors = validate_factory_definition(definition)
    errors.extend(validate_module_catalog(catalog))
    errors.extend(validate_factory_bindings(definition, catalog))
    if errors:
        raise ValueError("tagged control source is invalid: " + "; ".join(errors))
    plan = build_factory_plan(definition, catalog)
    plan_errors = validate_factory_plan(plan, definition, catalog)
    if plan_errors:
        raise ValueError("tagged factory plan is invalid: " + "; ".join(plan_errors))

    catalog_modules = {module["id"]: module for module in catalog["modules"]}
    artifacts: dict[str, dict[str, Any]] = {}
    for selected in plan["modules"]:
        module_id = selected["module"]
        artifact_path = _artifact_repository_path(
            catalog_path,
            catalog_modules[module_id]["artifact"]["path"],
        )
        artifact = read(artifact_path)
        artifact_errors = validate_module_artifact(
            artifact,
            catalog_modules[module_id],
        )
        if artifact_errors:
            raise ValueError(
                f"tagged module artifact is invalid ({module_id}): "
                + "; ".join(artifact_errors)
            )
        artifacts[module_id] = artifact

    schemas = {path: read(path) for path in sorted(CONTRACT_SCHEMAS)}
    return (
        [input_by_path[path] for path in sorted(input_by_path)],
        definition,
        catalog,
        artifacts,
        schemas,
    )


def build_source_lock(
    repository: Path,
    release_tag: str,
    factory_definition_path: str,
    bundle: bytes,
    catalog_path: str = "catalog/modules.json",
    repository_url: str = PUBLIC_REPOSITORY_URL,
) -> dict[str, Any]:
    """Rebuild a verified bundle entirely from immutable Git objects."""
    bundle_errors, verified_bundle = verify_factory_bundle(bundle)
    if bundle_errors or verified_bundle is None:
        raise ValueError("factory bundle: " + "; ".join(bundle_errors))
    release = _release_identity(repository, release_tag, repository_url)
    inputs, definition, catalog, artifacts, schemas = _tagged_control_sources(
        repository,
        release,
        factory_definition_path,
        catalog_path,
    )
    rebuilt_bundle, rebuilt_manifest = build_factory_bundle(
        definition,
        catalog,
        artifacts,
        schemas,
    )
    if rebuilt_bundle != bundle:
        raise ValueError("annotated release sources do not rebuild the exact bundle")
    if rebuilt_manifest != verified_bundle["manifest"]:
        raise ValueError("annotated release sources do not rebuild the exact manifest")

    manifest = verified_bundle["manifest"]
    source = manifest["source"]
    lock_without_digest: dict[str, Any] = {
        "contract_schema": SOURCE_LOCK_SCHEMA_REFERENCE,
        "schema_version": SOURCE_LOCK_SCHEMA_VERSION,
        "factory": deepcopy(manifest["factory"]),
        "repository": release,
        "source": {
            "factory_definition_path": factory_definition_path,
            "module_catalog_path": catalog_path,
            "bundle_sha256": verified_bundle["bundle_sha256"],
            "factory_definition_sha256": source["factory_definition_sha256"],
            "module_catalog_sha256": source["module_catalog_sha256"],
            "factory_plan_sha256": source["factory_plan_sha256"],
            "module_api_version": source["module_api_version"],
        },
        "inputs": inputs,
        "rebuild": {
            "input_count": len(inputs),
            "selected_module_count": len(manifest["selected_modules"]),
            "bundle_rebuilt_byte_identically": True,
            "manifest_rebuilt_exactly": True,
        },
        "source_lock_boundary": deepcopy(SOURCE_LOCK_BOUNDARY),
    }
    lock = dict(lock_without_digest)
    lock["factory_source_lock_sha256"] = sha256_json(lock_without_digest)
    return lock


def validate_source_lock(
    lock: Any,
    repository: Path,
    bundle: bytes,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(lock, dict):
        return ["factory source lock root must be an object"]
    if set(lock) != SOURCE_LOCK_FIELDS:
        errors.append("factory source lock contains missing or unexpected fields")
    if lock.get("contract_schema") != SOURCE_LOCK_SCHEMA_REFERENCE:
        errors.append("factory source lock must reference its immutable schema")
    if lock.get("schema_version") != SOURCE_LOCK_SCHEMA_VERSION:
        errors.append("factory source lock schema_version is invalid")
    try:
        boundary_matches = canonical_json_bytes(
            lock.get("source_lock_boundary")
        ) == canonical_json_bytes(SOURCE_LOCK_BOUNDARY)
    except (TypeError, ValueError):
        boundary_matches = False
    if not boundary_matches:
        errors.append("factory source lock must preserve the non-authorizing boundary")
    release = lock.get("repository")
    source = lock.get("source")
    if not isinstance(release, dict) or not isinstance(source, dict):
        return errors + ["factory source lock repository and source must be objects"]
    release_tag = release.get("release_tag")
    factory_path = source.get("factory_definition_path")
    catalog_path = source.get("module_catalog_path")
    if not isinstance(release_tag, str) or not RELEASE_TAG_RE.fullmatch(release_tag):
        return errors + ["factory source lock release tag is invalid"]
    if not _safe_repository_path(factory_path) or not _safe_repository_path(catalog_path):
        return errors + ["factory source lock contains an unsafe source path"]
    try:
        expected = build_source_lock(
            repository,
            release_tag,
            factory_path,
            bundle,
            catalog_path,
            release["url"],
        )
    except (KeyError, TypeError, ValueError) as exc:
        return errors + [f"cannot rebuild expected factory source lock: {exc}"]
    try:
        exact = canonical_json_bytes(lock) == canonical_json_bytes(expected)
    except (TypeError, ValueError):
        exact = False
    if not exact:
        errors.append(
            "factory source lock does not exactly match its Git release and bundle"
        )
    return errors


def source_lock_for_bundle(
    repository: Path,
    release_tag: str,
    factory_definition_path: str,
    bundle: bytes,
    catalog_path: str = "catalog/modules.json",
    repository_url: str = PUBLIC_REPOSITORY_URL,
) -> tuple[list[str], dict[str, Any] | None]:
    try:
        lock = build_source_lock(
            repository,
            release_tag,
            factory_definition_path,
            bundle,
            catalog_path,
            repository_url,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return [str(exc)], None
    return [], lock


def verify_source_lock_for_bundle(
    lock: Any,
    repository: Path,
    bundle: bytes,
) -> list[str]:
    return validate_source_lock(lock, repository, bundle)
