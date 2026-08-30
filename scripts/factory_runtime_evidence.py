#!/usr/bin/env python3
"""Verify signed runtime evidence and build scoped qualification assessments."""

from __future__ import annotations

import base64
import binascii
import os
import re
import stat
import subprocess
import tempfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from factory_bundle import verify_factory_bundle
from factory_composer import canonical_json_bytes, load_json_file, sha256_json
from factory_qualification import (
    validate_qualification_evidence,
    validate_qualification_plan,
)


ROOT = Path(__file__).resolve().parents[1]
VERIFIER_REGISTRY_PATH = (
    ROOT / "policies" / "runtime-evidence-verifiers-v1.json"
)
EXAMPLE_RUNTIME_EVIDENCE_PATH = (
    ROOT / "examples" / "economic-factory.runtime-evidence.json"
)
EXAMPLE_RUNTIME_ASSESSMENT_PATH = (
    ROOT / "examples" / "economic-factory.runtime-assessment.json"
)

VERIFIER_REGISTRY_SCHEMA_VERSION = (
    "zaibatsu.runtime-evidence-verifier-registry.v1"
)
RUNTIME_EVIDENCE_SCHEMA_VERSION = "zaibatsu.factory-runtime-evidence.v1"
RUNTIME_ASSESSMENT_SCHEMA_VERSION = (
    "zaibatsu.factory-runtime-assessment.v2"
)
VERIFIER_REGISTRY_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.9.0/schemas/runtime-evidence-verifier-registry.schema.json"
)
RUNTIME_EVIDENCE_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.9.0/schemas/factory-runtime-evidence.schema.json"
)
RUNTIME_ASSESSMENT_SCHEMA_REFERENCE = (
    "https://raw.githubusercontent.com/adaliontech/Zaibatsu/"
    "v1.10.0/schemas/factory-runtime-assessment.schema.json"
)

SIGNATURE_NAMESPACE = "zaibatsu-runtime-evidence-v1"
SSH_KEYGEN_PATH = Path("/usr/bin/ssh-keygen")
QUALIFICATION_SCOPES = {"factory_runtime", "public_test_fixture"}
NON_RUNTIME_SCOPE = "public_test_fixture"
MAX_RECEIPTS = 256

REGISTRY_FIELDS = {
    "contract_schema",
    "schema_version",
    "registry_id",
    "signature_namespace",
    "verifiers",
    "registry_boundary",
    "verifier_registry_sha256",
}
VERIFIER_FIELDS = {
    "position",
    "verifier_id",
    "public_key",
    "implementation_sha256",
    "allowed_factories",
    "allowed_scopes",
    "allowed_requirements",
    "allowed_methods",
    "max_validity_seconds",
    "trust_role",
    "active",
}
REGISTRY_BOUNDARY = {
    "public_keys_only": True,
    "private_keys_included": False,
    "exact_allowlists_required": True,
    "signatures_required": True,
    "self_attestation_accepted": False,
    "signature_grants_runtime_eligibility": False,
    "signature_grants_activation": False,
    "signature_grants_execution": False,
}

EVIDENCE_FIELDS = {
    "contract_schema",
    "schema_version",
    "factory",
    "source",
    "qualification_scope",
    "receipts",
    "summary",
    "evidence_boundary",
    "runtime_evidence_set_sha256",
}
RECEIPT_FIELDS = {"payload", "payload_sha256", "signature"}
PAYLOAD_FIELDS = {
    "factory_id",
    "bundle_sha256",
    "qualification_plan_sha256",
    "qualification_policy_sha256",
    "verifier_registry_sha256",
    "position",
    "slot",
    "module",
    "artifact_sha256",
    "requirement",
    "qualification_scope",
    "evidence_artifact_sha256",
    "verifier_id",
    "verification_method",
    "verifier_implementation_sha256",
    "observed_at",
    "valid_until",
    "result",
    "self_attested",
    "grants_activation",
    "grants_execution",
}
SIGNATURE_FIELDS = {"algorithm", "namespace", "value_base64"}
EVIDENCE_BOUNDARY = {
    "externally_supplied": True,
    "trusted_key_registry_required": True,
    "verifier_registry_selected_externally": True,
    "verifier_key_ownership_verified": False,
    "verifier_independence_verified": False,
    "requires_signature_verification": True,
    "verifier_assertions_reexecuted": False,
    "evidence_artifacts_embedded": False,
    "self_attestation_accepted": False,
    "signature_grants_runtime_eligibility": False,
    "activation_authorized": False,
    "execution_authorized": False,
}

ASSESSMENT_FIELDS = {
    "contract_schema",
    "schema_version",
    "factory",
    "source",
    "modules",
    "summary",
    "assessment_boundary",
    "runtime_assessment_sha256",
}
ASSESSMENT_BOUNDARY_BASE = {
    "cryptographic_signatures_verified": True,
    "verifier_registry_selected_externally": True,
    "verifier_key_ownership_verified": False,
    "verifier_independence_verified": False,
    "trusted_verifier_assertions_reexecuted": False,
    "evidence_artifacts_retrieved": True,
    "verifier_implementation_materials_retrieved": True,
    "artifact_semantic_truth_verified": False,
    "evaluation_time_externally_supplied": True,
    "trusted_current_clock_enforced": False,
    "self_attestation_accepted": False,
    "qualification_grants_activation": False,
    "owner_approval_required_for_activation": True,
    "activation_authorized": False,
    "execution_authorized": False,
}

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIREMENT_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
METHOD_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
RFC3339_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
SSH_ED25519_RE = re.compile(
    r"^ssh-ed25519 [A-Za-z0-9+/]+={0,2}$"
)


def load_verifier_registry(
    path: Path = VERIFIER_REGISTRY_PATH,
) -> dict[str, Any]:
    return load_json_file(path)


def load_runtime_evidence(
    path: Path = EXAMPLE_RUNTIME_EVIDENCE_PATH,
) -> dict[str, Any]:
    return load_json_file(path)


def load_runtime_assessment(
    path: Path = EXAMPLE_RUNTIME_ASSESSMENT_PATH,
) -> dict[str, Any]:
    return load_json_file(path)


def _json_exactly_equal(left: Any, right: Any) -> bool:
    try:
        return canonical_json_bytes(left) == canonical_json_bytes(right)
    except (RecursionError, TypeError, ValueError):
        return False


def _parse_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not RFC3339_RE.fullmatch(value):
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except ValueError:
        return None


def _valid_ed25519_public_key(value: Any) -> bool:
    if not isinstance(value, str) or not SSH_ED25519_RE.fullmatch(value):
        return False
    try:
        blob = base64.b64decode(value.split(" ", 1)[1], validate=True)
    except (binascii.Error, ValueError):
        return False
    if len(blob) != 51:
        return False
    algorithm_length = int.from_bytes(blob[0:4], "big")
    algorithm_end = 4 + algorithm_length
    if algorithm_length != 11 or blob[4:algorithm_end] != b"ssh-ed25519":
        return False
    key_length = int.from_bytes(blob[algorithm_end : algorithm_end + 4], "big")
    return key_length == 32 and algorithm_end + 4 + key_length == len(blob)


def _validate_sorted_strings(
    value: Any,
    label: str,
    pattern: re.Pattern[str],
) -> list[str]:
    if not isinstance(value, list) or not value:
        return [f"{label} must be a non-empty list"]
    if not all(
        isinstance(item, str) and pattern.fullmatch(item)
        for item in value
    ):
        return [f"{label} contains an invalid value"]
    errors: list[str] = []
    if len(value) != len(set(value)):
        errors.append(f"{label} values must be unique")
    if value != sorted(value):
        errors.append(f"{label} values must be sorted")
    return errors


def validate_verifier_registry(registry: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(registry, dict):
        return ["runtime evidence verifier registry root must be an object"]
    if set(registry) != REGISTRY_FIELDS:
        errors.append(
            "runtime evidence verifier registry has missing or unexpected fields"
        )
    if registry.get("contract_schema") != VERIFIER_REGISTRY_SCHEMA_REFERENCE:
        errors.append("runtime evidence verifier registry schema is invalid")
    if registry.get("schema_version") != VERIFIER_REGISTRY_SCHEMA_VERSION:
        errors.append(
            "runtime evidence verifier registry schema_version is invalid"
        )
    registry_id = registry.get("registry_id")
    if not isinstance(registry_id, str) or not SLUG_RE.fullmatch(registry_id):
        errors.append("runtime evidence verifier registry_id is invalid")
    if registry.get("signature_namespace") != SIGNATURE_NAMESPACE:
        errors.append("runtime evidence signature namespace is invalid")
    if not _json_exactly_equal(
        registry.get("registry_boundary"),
        REGISTRY_BOUNDARY,
    ):
        errors.append("runtime evidence verifier registry boundary is invalid")

    verifiers = registry.get("verifiers")
    if not isinstance(verifiers, list) or not verifiers:
        errors.append("runtime evidence verifier registry must contain verifiers")
    elif len(verifiers) > 64:
        errors.append("runtime evidence verifier registry is too large")
    else:
        ids: list[Any] = []
        keys: list[Any] = []
        for index, verifier in enumerate(verifiers):
            label = f"runtime evidence verifier {index}"
            if not isinstance(verifier, dict):
                errors.append(f"{label} must be an object")
                continue
            if set(verifier) != VERIFIER_FIELDS:
                errors.append(f"{label} has ambiguous fields")
            verifier_id = verifier.get("verifier_id")
            ids.append(verifier_id)
            if verifier.get("position") != index or isinstance(
                verifier.get("position"), bool
            ):
                errors.append(f"{label} position is invalid")
            if not isinstance(verifier_id, str) or not SLUG_RE.fullmatch(
                verifier_id
            ):
                errors.append(f"{label} verifier_id is invalid")
            public_key = verifier.get("public_key")
            keys.append(public_key)
            if not _valid_ed25519_public_key(public_key):
                errors.append(
                    f"{label} public key must be a valid exact ssh-ed25519 key"
                )
            if not isinstance(
                verifier.get("implementation_sha256"), str
            ) or not SHA256_RE.fullmatch(verifier["implementation_sha256"]):
                errors.append(f"{label} implementation digest is invalid")
            errors.extend(
                _validate_sorted_strings(
                    verifier.get("allowed_factories"),
                    f"{label} allowed factories",
                    SLUG_RE,
                )
            )
            scopes = verifier.get("allowed_scopes")
            errors.extend(
                _validate_sorted_strings(
                    scopes,
                    f"{label} allowed scopes",
                    REQUIREMENT_RE,
                )
            )
            if isinstance(scopes, list) and any(
                scope not in QUALIFICATION_SCOPES for scope in scopes
            ):
                errors.append(f"{label} contains an unsupported scope")
            errors.extend(
                _validate_sorted_strings(
                    verifier.get("allowed_requirements"),
                    f"{label} allowed requirements",
                    REQUIREMENT_RE,
                )
            )
            errors.extend(
                _validate_sorted_strings(
                    verifier.get("allowed_methods"),
                    f"{label} allowed methods",
                    METHOD_RE,
                )
            )
            max_validity = verifier.get("max_validity_seconds")
            if (
                not isinstance(max_validity, int)
                or isinstance(max_validity, bool)
                or not 60 <= max_validity <= 2_678_400
            ):
                errors.append(f"{label} max validity is invalid")
            trust_role = verifier.get("trust_role")
            if not isinstance(trust_role, str) or not SLUG_RE.fullmatch(
                trust_role
            ):
                errors.append(f"{label} trust role is invalid")
            if verifier.get("active") is not True:
                errors.append(f"{label} must be explicitly active")
        if len(ids) != len(set(map(str, ids))):
            errors.append("runtime evidence verifier ids must be unique")
        if len(keys) != len(set(map(str, keys))):
            errors.append("runtime evidence verifier public keys must be unique")

    supplied_digest = registry.get("verifier_registry_sha256")
    if not isinstance(supplied_digest, str) or not SHA256_RE.fullmatch(
        supplied_digest
    ):
        errors.append("runtime evidence verifier registry digest is invalid")
    else:
        without_digest = deepcopy(registry)
        without_digest.pop("verifier_registry_sha256", None)
        try:
            expected_digest = sha256_json(without_digest)
        except (RecursionError, TypeError, ValueError):
            expected_digest = None
        if supplied_digest != expected_digest:
            errors.append("runtime evidence verifier registry digest mismatch")
    return errors


def _verified_registry_by_id(
    registry: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    return {
        verifier["verifier_id"]: verifier
        for verifier in registry["verifiers"]
    }


def _ssh_keygen_available() -> bool:
    try:
        metadata = SSH_KEYGEN_PATH.stat()
    except OSError:
        return False
    return stat.S_ISREG(metadata.st_mode) and os.access(SSH_KEYGEN_PATH, os.X_OK)


def verify_receipt_signature(
    payload: dict[str, Any],
    signature: dict[str, Any],
    verifier: dict[str, Any],
) -> list[str]:
    if not _ssh_keygen_available():
        return ["OpenSSH ssh-keygen is required for runtime evidence signatures"]
    encoded = signature.get("value_base64")
    if not isinstance(encoded, str) or len(encoded) > 16_384:
        return ["runtime evidence signature encoding is invalid"]
    try:
        signature_bytes = base64.b64decode(encoded, validate=True)
    except (binascii.Error, ValueError):
        return ["runtime evidence signature is not strict base64"]
    if not signature_bytes.startswith(b"-----BEGIN SSH SIGNATURE-----\n"):
        return ["runtime evidence signature is not an armored SSH signature"]
    if len(signature_bytes) > 8_192:
        return ["runtime evidence signature exceeds the size boundary"]

    identity = verifier["verifier_id"]
    allowed_signer = f"{identity} {verifier['public_key']}\n"
    try:
        with tempfile.TemporaryDirectory(
            prefix="zaibatsu-runtime-evidence-"
        ) as temporary_directory:
            root = Path(temporary_directory)
            allowed_path = root / "allowed_signers"
            signature_path = root / "receipt.sig"
            allowed_path.write_text(allowed_signer, encoding="utf-8")
            signature_path.write_bytes(signature_bytes)
            result = subprocess.run(
                [
                    str(SSH_KEYGEN_PATH),
                    "-Y",
                    "verify",
                    "-f",
                    str(allowed_path),
                    "-I",
                    identity,
                    "-n",
                    SIGNATURE_NAMESPACE,
                    "-s",
                    str(signature_path),
                ],
                input=canonical_json_bytes(payload),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                env={"LANG": "C", "LC_ALL": "C"},
                timeout=5,
                check=False,
            )
    except (OSError, subprocess.SubprocessError) as exc:
        return [f"cannot verify runtime evidence signature: {exc}"]
    if result.returncode != 0:
        return ["runtime evidence signature verification failed"]
    return []


def _expected_evidence_source(
    verified_bundle: dict[str, Any],
    plan: dict[str, Any],
    policy: dict[str, Any],
    registry: dict[str, Any],
) -> dict[str, Any]:
    return {
        "bundle_sha256": verified_bundle["bundle_sha256"],
        "qualification_plan_sha256": plan["qualification_plan_sha256"],
        "qualification_policy_id": policy["policy_id"],
        "qualification_policy_sha256": sha256_json(policy),
        "verifier_registry_sha256": registry[
            "verifier_registry_sha256"
        ],
        "module_api_version": plan["source"]["module_api_version"],
    }


def validate_runtime_evidence_set(
    evidence: Any,
    verified_bundle: Any,
    plan: Any,
    policy: Any,
    registry: Any,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(evidence, dict):
        return ["runtime evidence set root must be an object"]
    if set(evidence) != EVIDENCE_FIELDS:
        errors.append("runtime evidence set has missing or unexpected fields")
    if evidence.get("contract_schema") != RUNTIME_EVIDENCE_SCHEMA_REFERENCE:
        errors.append("runtime evidence set schema is invalid")
    if evidence.get("schema_version") != RUNTIME_EVIDENCE_SCHEMA_VERSION:
        errors.append("runtime evidence set schema_version is invalid")
    if not _json_exactly_equal(
        evidence.get("evidence_boundary"),
        EVIDENCE_BOUNDARY,
    ):
        errors.append("runtime evidence set boundary is invalid")

    registry_errors = validate_verifier_registry(registry)
    errors.extend(f"verifier registry: {error}" for error in registry_errors)
    plan_errors = validate_qualification_plan(plan, verified_bundle, policy)
    errors.extend(f"qualification plan: {error}" for error in plan_errors)
    if registry_errors or plan_errors:
        return errors
    assert isinstance(verified_bundle, dict)
    assert isinstance(plan, dict)
    assert isinstance(policy, dict)
    assert isinstance(registry, dict)

    if not _json_exactly_equal(
        evidence.get("factory"),
        plan.get("factory"),
    ):
        errors.append("runtime evidence factory does not match the plan")
    try:
        expected_source = _expected_evidence_source(
            verified_bundle,
            plan,
            policy,
            registry,
        )
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return errors + [f"cannot derive runtime evidence source: {exc}"]
    if not _json_exactly_equal(evidence.get("source"), expected_source):
        errors.append("runtime evidence source does not match verified inputs")

    scope = evidence.get("qualification_scope")
    if scope not in QUALIFICATION_SCOPES:
        errors.append("runtime evidence qualification_scope is invalid")
    modules = {
        (module["position"], module["module"]): module
        for module in plan["modules"]
    }
    verifiers = _verified_registry_by_id(registry)
    receipts = evidence.get("receipts")
    bindings: list[tuple[Any, Any]] = []
    verified_signatures = 0
    if not isinstance(receipts, list) or not receipts:
        errors.append("runtime evidence set must contain receipts")
        receipts = []
    elif len(receipts) > MAX_RECEIPTS:
        errors.append("runtime evidence receipt count exceeds the boundary")
        receipts = []
    for index, receipt in enumerate(receipts):
        label = f"runtime evidence receipt {index}"
        if not isinstance(receipt, dict):
            errors.append(f"{label} must be an object")
            continue
        if set(receipt) != RECEIPT_FIELDS:
            errors.append(f"{label} has missing or unexpected fields")
        payload = receipt.get("payload")
        signature = receipt.get("signature")
        if not isinstance(payload, dict):
            errors.append(f"{label} payload must be an object")
            continue
        if set(payload) != PAYLOAD_FIELDS:
            errors.append(f"{label} payload has missing or unexpected fields")
        if not isinstance(signature, dict) or set(signature) != SIGNATURE_FIELDS:
            errors.append(f"{label} signature has invalid fields")
            signature = {}

        position = payload.get("position")
        module_id = payload.get("module")
        requirement = payload.get("requirement")
        binding = (position, requirement)
        bindings.append(binding)
        module = modules.get((position, module_id))
        expected_subject = {
            "factory_id": plan["factory"]["id"],
            "bundle_sha256": verified_bundle["bundle_sha256"],
            "qualification_plan_sha256": plan[
                "qualification_plan_sha256"
            ],
            "qualification_policy_sha256": sha256_json(policy),
            "verifier_registry_sha256": registry[
                "verifier_registry_sha256"
            ],
        }
        actual_subject = {
            field: payload.get(field) for field in expected_subject
        }
        if not _json_exactly_equal(actual_subject, expected_subject):
            errors.append(f"{label} signed source binding is invalid")
        if module is None:
            errors.append(f"{label} does not bind a selected module")
        else:
            expected_module = {
                "position": module["position"],
                "slot": module["slot"],
                "module": module["module"],
                "artifact_sha256": module["artifact_sha256"],
            }
            actual_module = {
                field: payload.get(field)
                for field in expected_module
            }
            if not _json_exactly_equal(actual_module, expected_module):
                errors.append(f"{label} module binding is invalid")
            if requirement not in module["required_evidence"]:
                errors.append(f"{label} requirement is not in the plan")
            if requirement == "contract_conformance_receipt":
                errors.append(
                    f"{label} cannot replace bundle-derived contract evidence"
                )

        if payload.get("qualification_scope") != scope:
            errors.append(f"{label} scope does not match the evidence set")
        for digest_field in (
            "evidence_artifact_sha256",
            "verifier_implementation_sha256",
        ):
            value = payload.get(digest_field)
            if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
                errors.append(f"{label} {digest_field} is invalid")
        method = payload.get("verification_method")
        if not isinstance(method, str) or not METHOD_RE.fullmatch(method):
            errors.append(f"{label} verification method is invalid")
        if payload.get("result") != "passed":
            errors.append(f"{label} result must be passed")
        if payload.get("self_attested") is not False:
            errors.append(f"{label} self-attestation is forbidden")
        if payload.get("grants_activation") is not False:
            errors.append(f"{label} cannot grant activation")
        if payload.get("grants_execution") is not False:
            errors.append(f"{label} cannot grant execution")

        observed = _parse_time(payload.get("observed_at"))
        valid_until = _parse_time(payload.get("valid_until"))
        if observed is None or valid_until is None:
            errors.append(f"{label} validity timestamps are invalid")
        elif valid_until <= observed:
            errors.append(f"{label} validity interval is not positive")

        verifier_id = payload.get("verifier_id")
        verifier = verifiers.get(verifier_id)
        if verifier is None:
            errors.append(f"{label} verifier is not trusted")
        else:
            factory_id = plan["factory"]["id"]
            if factory_id not in verifier["allowed_factories"]:
                errors.append(f"{label} verifier is not allowed for the factory")
            if scope not in verifier["allowed_scopes"]:
                errors.append(f"{label} verifier is not allowed for the scope")
            if requirement not in verifier["allowed_requirements"]:
                errors.append(
                    f"{label} verifier is not allowed for the requirement"
                )
            if method not in verifier["allowed_methods"]:
                errors.append(f"{label} verifier is not allowed for the method")
            if (
                payload.get("verifier_implementation_sha256")
                != verifier["implementation_sha256"]
            ):
                errors.append(f"{label} verifier implementation is not trusted")
            if observed is not None and valid_until is not None:
                lifetime = (valid_until - observed).total_seconds()
                if lifetime > verifier["max_validity_seconds"]:
                    errors.append(f"{label} validity exceeds verifier policy")

        try:
            expected_payload_digest = sha256_json(payload)
        except (RecursionError, TypeError, ValueError):
            expected_payload_digest = None
        if receipt.get("payload_sha256") != expected_payload_digest:
            errors.append(f"{label} payload digest mismatch")
        if signature.get("algorithm") != "ssh-ed25519":
            errors.append(f"{label} signature algorithm is invalid")
        if signature.get("namespace") != SIGNATURE_NAMESPACE:
            errors.append(f"{label} signature namespace is invalid")
        if verifier is not None and expected_payload_digest is not None:
            receipt_signature_errors = verify_receipt_signature(
                payload,
                signature,
                verifier,
            )
            if not receipt_signature_errors:
                verified_signatures += 1
            errors.extend(
                f"{label}: {error}" for error in receipt_signature_errors
            )

    if len(bindings) != len(set(bindings)):
        errors.append("runtime evidence bindings must be unique")
    sorted_bindings = sorted(bindings, key=lambda item: (str(item[0]), str(item[1])))
    if bindings != sorted_bindings:
        errors.append("runtime evidence receipts must be in binding order")

    expected_summary = {
        "receipt_count": len(receipts),
        "unique_bindings": len(set(bindings)),
        "signature_count": verified_signatures,
        "qualification_scope": scope,
    }
    if not _json_exactly_equal(evidence.get("summary"), expected_summary):
        errors.append("runtime evidence summary is invalid")

    supplied_digest = evidence.get("runtime_evidence_set_sha256")
    if not isinstance(supplied_digest, str) or not SHA256_RE.fullmatch(
        supplied_digest
    ):
        errors.append("runtime evidence set digest is invalid")
    else:
        without_digest = deepcopy(evidence)
        without_digest.pop("runtime_evidence_set_sha256", None)
        try:
            expected_digest = sha256_json(without_digest)
        except (RecursionError, TypeError, ValueError):
            expected_digest = None
        if supplied_digest != expected_digest:
            errors.append("runtime evidence set digest mismatch")
    return errors


def _assessment_source(
    verified_bundle: dict[str, Any],
    plan: dict[str, Any],
    policy: dict[str, Any],
    contract_evidence: dict[str, Any],
    runtime_evidence: dict[str, Any],
    registry: dict[str, Any],
    runtime_evidence_pack_sha256: str,
    evaluated_at: str,
) -> dict[str, Any]:
    return {
        **_expected_evidence_source(verified_bundle, plan, policy, registry),
        "qualification_evidence_sha256": contract_evidence[
            "qualification_evidence_sha256"
        ],
        "runtime_evidence_set_sha256": runtime_evidence[
            "runtime_evidence_set_sha256"
        ],
        "runtime_evidence_pack_sha256": runtime_evidence_pack_sha256,
        "evaluated_at": evaluated_at,
        "qualification_scope": runtime_evidence["qualification_scope"],
    }


def build_runtime_assessment(
    verified_bundle: dict[str, Any],
    plan: dict[str, Any],
    policy: dict[str, Any],
    contract_evidence: dict[str, Any],
    runtime_evidence: dict[str, Any],
    registry: dict[str, Any],
    runtime_evidence_pack_sha256: str,
    evaluated_at: str,
) -> dict[str, Any]:
    evaluation_time = _parse_time(evaluated_at)
    if evaluation_time is None:
        raise ValueError("assessment evaluated_at must be exact RFC3339 UTC")
    contract_by_module = {
        (receipt["position"], receipt["module"]): receipt["requirement"]
        for receipt in contract_evidence["receipts"]
    }
    runtime_by_module: dict[tuple[int, str], list[dict[str, Any]]] = {}
    for receipt in runtime_evidence["receipts"]:
        payload = receipt["payload"]
        runtime_by_module.setdefault(
            (payload["position"], payload["module"]),
            [],
        ).append(payload)

    scope = runtime_evidence["qualification_scope"]
    modules: list[dict[str, Any]] = []
    verified_bindings = 0
    fresh_runtime_bindings = 0
    stale_runtime_bindings = 0
    missing_bindings = 0
    runtime_eligible_modules = 0
    verified_requirement_types: set[str] = set()
    missing_requirement_types: set[str] = set()

    for module in plan["modules"]:
        key = (module["position"], module["module"])
        required = list(module["required_evidence"])
        verified_control = [contract_by_module[key]]
        fresh_runtime: list[str] = []
        stale_runtime: list[str] = []
        for payload in runtime_by_module.get(key, []):
            observed = _parse_time(payload["observed_at"])
            valid_until = _parse_time(payload["valid_until"])
            assert observed is not None and valid_until is not None
            if observed <= evaluation_time < valid_until:
                fresh_runtime.append(payload["requirement"])
            else:
                stale_runtime.append(payload["requirement"])
        fresh_runtime = sorted(fresh_runtime)
        stale_runtime = sorted(stale_runtime)
        verified = sorted(set(verified_control) | set(fresh_runtime))
        missing = [item for item in required if item not in verified]
        requirements_complete = not missing
        runtime_eligible = scope == "factory_runtime" and requirements_complete
        if scope != "factory_runtime":
            reason = "test_fixture_scope_not_runtime_eligible"
        elif missing and stale_runtime:
            reason = "runtime_evidence_missing_or_stale"
        elif missing:
            reason = "runtime_evidence_incomplete"
        else:
            reason = "qualified_not_authorized"
        runtime_eligible_modules += int(runtime_eligible)
        verified_bindings += len(verified)
        fresh_runtime_bindings += len(fresh_runtime)
        stale_runtime_bindings += len(stale_runtime)
        missing_bindings += len(missing)
        verified_requirement_types.update(verified)
        missing_requirement_types.update(missing)
        modules.append(
            {
                "position": module["position"],
                "slot": module["slot"],
                "module": module["module"],
                "artifact_sha256": module["artifact_sha256"],
                "required_evidence": required,
                "verified_control_evidence": verified_control,
                "verified_runtime_evidence": fresh_runtime,
                "stale_runtime_evidence": stale_runtime,
                "verified_evidence": verified,
                "missing_evidence": missing,
                "evidence_status": (
                    "complete" if requirements_complete else "partial"
                ),
                "qualification_scope": scope,
                "runtime_eligible": runtime_eligible,
                "reason": reason,
            }
        )

    assessment_without_digest: dict[str, Any] = {
        "contract_schema": RUNTIME_ASSESSMENT_SCHEMA_REFERENCE,
        "schema_version": RUNTIME_ASSESSMENT_SCHEMA_VERSION,
        "factory": deepcopy(plan["factory"]),
        "source": _assessment_source(
            verified_bundle,
            plan,
            policy,
            contract_evidence,
            runtime_evidence,
            registry,
            runtime_evidence_pack_sha256,
            evaluated_at,
        ),
        "modules": modules,
        "summary": {
            "module_count": len(modules),
            "runtime_eligible_modules": runtime_eligible_modules,
            "runtime_ineligible_modules": len(modules)
            - runtime_eligible_modules,
            "required_evidence_bindings": verified_bindings
            + missing_bindings,
            "verified_evidence_bindings": verified_bindings,
            "fresh_runtime_evidence_bindings": fresh_runtime_bindings,
            "stale_runtime_evidence_bindings": stale_runtime_bindings,
            "missing_evidence_bindings": missing_bindings,
            "verified_requirement_types": len(verified_requirement_types),
            "missing_requirement_types": len(missing_requirement_types),
            "all_requirements_satisfied": missing_bindings == 0,
            "qualification_scope": scope,
        },
        "assessment_boundary": {
            **deepcopy(ASSESSMENT_BOUNDARY_BASE),
            "fixture_scope_only": scope == NON_RUNTIME_SCOPE,
        },
    }
    assessment = dict(assessment_without_digest)
    assessment["runtime_assessment_sha256"] = sha256_json(
        assessment_without_digest
    )
    return assessment


def validate_runtime_assessment(
    assessment: Any,
    contract_evidence: Any,
    runtime_evidence: Any,
    verified_bundle: Any,
    plan: Any,
    policy: Any,
    registry: Any,
    runtime_evidence_pack_sha256: Any,
) -> list[str]:
    errors: list[str] = []
    if not isinstance(assessment, dict):
        return ["runtime assessment root must be an object"]
    if set(assessment) != ASSESSMENT_FIELDS:
        errors.append("runtime assessment has missing or unexpected fields")
    if assessment.get("contract_schema") != RUNTIME_ASSESSMENT_SCHEMA_REFERENCE:
        errors.append("runtime assessment schema is invalid")
    if assessment.get("schema_version") != RUNTIME_ASSESSMENT_SCHEMA_VERSION:
        errors.append("runtime assessment schema_version is invalid")

    contract_errors = validate_qualification_evidence(
        contract_evidence,
        verified_bundle,
        plan,
        policy,
    )
    errors.extend(
        f"contract evidence: {error}" for error in contract_errors
    )
    runtime_errors = validate_runtime_evidence_set(
        runtime_evidence,
        verified_bundle,
        plan,
        policy,
        registry,
    )
    errors.extend(f"runtime evidence: {error}" for error in runtime_errors)
    if contract_errors or runtime_errors:
        return errors
    try:
        evaluated_at = assessment["source"]["evaluated_at"]
        expected = build_runtime_assessment(
            verified_bundle,
            plan,
            policy,
            contract_evidence,
            runtime_evidence,
            registry,
            runtime_evidence_pack_sha256,
            evaluated_at,
        )
    except (KeyError, RecursionError, TypeError, ValueError) as exc:
        return errors + [f"cannot rebuild expected runtime assessment: {exc}"]
    if not _json_exactly_equal(assessment, expected):
        errors.append(
            "runtime assessment does not exactly match its verified inputs"
        )
    return errors


def runtime_assessment_for_bundle(
    contract_evidence: Any,
    runtime_evidence_pack: bytes,
    plan: Any,
    bundle: bytes,
    policy: Any,
    evaluated_at: str,
) -> tuple[list[str], dict[str, Any] | None]:
    from factory_evidence_pack import verify_runtime_evidence_pack_for_bundle

    bundle_errors, verified = verify_factory_bundle(bundle)
    if bundle_errors or verified is None:
        return [f"factory bundle: {error}" for error in bundle_errors], None
    pack_errors, verified_pack = verify_runtime_evidence_pack_for_bundle(
        runtime_evidence_pack,
        plan,
        bundle,
        policy,
    )
    if pack_errors or verified_pack is None:
        return [f"runtime-evidence pack: {error}" for error in pack_errors], None
    runtime_evidence = verified_pack["runtime_evidence"]
    registry = verified_pack["verifier_registry"]
    contract_errors = validate_qualification_evidence(
        contract_evidence,
        verified,
        plan,
        policy,
    )
    runtime_errors = validate_runtime_evidence_set(
        runtime_evidence,
        verified,
        plan,
        policy,
        registry,
    )
    errors = [f"contract evidence: {error}" for error in contract_errors]
    errors.extend(f"runtime evidence: {error}" for error in runtime_errors)
    if _parse_time(evaluated_at) is None:
        errors.append("assessment evaluated_at must be exact RFC3339 UTC")
    if errors:
        return errors, None
    return [], build_runtime_assessment(
        verified,
        plan,
        policy,
        contract_evidence,
        runtime_evidence,
        registry,
        verified_pack["runtime_evidence_pack_sha256"],
        evaluated_at,
    )


def verify_runtime_assessment_for_bundle(
    assessment: Any,
    contract_evidence: Any,
    runtime_evidence_pack: bytes,
    plan: Any,
    bundle: bytes,
    policy: Any,
) -> list[str]:
    from factory_evidence_pack import verify_runtime_evidence_pack_for_bundle

    bundle_errors, verified = verify_factory_bundle(bundle)
    if bundle_errors or verified is None:
        return [f"factory bundle: {error}" for error in bundle_errors]
    pack_errors, verified_pack = verify_runtime_evidence_pack_for_bundle(
        runtime_evidence_pack,
        plan,
        bundle,
        policy,
    )
    if pack_errors or verified_pack is None:
        return [f"runtime-evidence pack: {error}" for error in pack_errors]
    return validate_runtime_assessment(
        assessment,
        contract_evidence,
        verified_pack["runtime_evidence"],
        verified,
        plan,
        policy,
        verified_pack["verifier_registry"],
        verified_pack["runtime_evidence_pack_sha256"],
    )
