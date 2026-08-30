#!/usr/bin/env python3
"""Fail-closed local preflight for the Droid/Qwen integration."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Mapping
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
SETTINGS_PATH = ROOT / ".factory" / "settings.local.json"
EXPECTED_DISPLAY_NAME = "Local Qwen 3.8 27B"
MODEL_API_KEY_ENV = "ZAIBATSU_QWEN_API_KEY"
MODEL_API_KEY_REFERENCE = f"${{{MODEL_API_KEY_ENV}}}"
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}
TAILNET_DNS_SUFFIX = ".ts.net"
FACTORY_API_KEY_ENV = "FACTORY_API_KEY"
FACTORY_AUTH_PATH = Path.home() / ".factory" / "auth.v2.keyring"


def validate_settings(
    path: Path = SETTINGS_PATH, environment: Mapping[str, str] | None = None
) -> list[str]:
    """Validate configuration shape without contacting the model or printing a key."""
    errors: list[str] = []
    environment = os.environ if environment is None else environment

    try:
        metadata = path.lstat()
    except OSError:
        return [
            "missing .factory/settings.local.json; copy the tracked example and fill local values"
        ]
    if (
        not stat.S_ISREG(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or metadata.st_uid != os.getuid()
        or metadata.st_nlink != 1
        or stat.S_IMODE(metadata.st_mode) & 0o022
    ):
        return ["local settings file has unsafe metadata"]

    try:
        settings = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot load local settings: {exc}"]

    if not isinstance(settings, dict):
        return ["local settings root must be an object"]

    models = settings.get("customModels")
    if not isinstance(models, list):
        return ["customModels must be a list"]

    valid_models = []
    for index, item in enumerate(models):
        if not isinstance(item, dict):
            errors.append(f"custom model at index {index} must be an object")
            continue
        valid_models.append(item)

    matches = [
        item for item in valid_models if item.get("displayName") == EXPECTED_DISPLAY_NAME
    ]
    if len(matches) != 1:
        errors.append(
            f"customModels must contain exactly one {EXPECTED_DISPLAY_NAME!r} entry"
        )
        return errors

    model = matches[0]
    model_id = model.get("model")
    if not isinstance(model_id, str) or not model_id.strip():
        errors.append("local model id is missing")
    elif model_id.strip().startswith("REPLACE_WITH_"):
        errors.append("local model id still contains the example placeholder")
    elif model_id != model_id.strip():
        errors.append("local model id must not have leading or trailing whitespace")

    if model.get("provider") != "generic-chat-completion-api":
        errors.append("local model provider must be generic-chat-completion-api")

    base_url = model.get("baseUrl")
    if not isinstance(base_url, str) or not base_url.strip():
        errors.append("local model baseUrl is missing")
    elif any(character.isspace() for character in base_url):
        errors.append("local model baseUrl must not contain whitespace")
    else:
        try:
            parsed = urlparse(base_url)
            hostname = parsed.hostname
            parsed.port
        except ValueError:
            errors.append("local model baseUrl is malformed")
        else:
            private_host = isinstance(hostname, str) and hostname.endswith(
                TAILNET_DNS_SUFFIX
            )
            if parsed.scheme != "http" or (
                hostname not in LOOPBACK_HOSTS and not private_host
            ):
                errors.append(
                    "local model baseUrl must use HTTP on loopback or a tailnet DNS host"
                )
            if parsed.username is not None or parsed.password is not None:
                errors.append("local model baseUrl must not contain userinfo")
            if parsed.query or parsed.fragment or parsed.params:
                errors.append("local model baseUrl must not contain params, query, or fragment")
            if not parsed.path.rstrip("/").endswith("/v1"):
                errors.append("local model baseUrl must end in /v1")

    max_output_tokens = model.get("maxOutputTokens")
    if max_output_tokens is not None and (
        type(max_output_tokens) is not int or max_output_tokens <= 0
    ):
        errors.append("maxOutputTokens must be a positive integer")
    no_image_support = model.get("noImageSupport")
    if no_image_support is not None and not isinstance(no_image_support, bool):
        errors.append("noImageSupport must be boolean")
    for forbidden_field in ("apiKeyHelper", "extraHeaders"):
        if forbidden_field in model:
            errors.append(
                f"{forbidden_field} is not allowed; use the apiKey environment reference"
            )

    key_reference = model.get("apiKey")
    if key_reference != MODEL_API_KEY_REFERENCE:
        errors.append(f"apiKey must equal {MODEL_API_KEY_REFERENCE}")
    else:
        key_value = environment.get(MODEL_API_KEY_ENV)
        if not isinstance(key_value, str) or not key_value.strip():
            errors.append(f"required environment variable is unset: {MODEL_API_KEY_ENV}")

    return errors


def droid_version() -> tuple[str | None, str | None]:
    binary = shutil.which("droid")
    if not binary:
        return None, "droid executable is not on PATH"
    try:
        result = subprocess.run(
            [binary, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        return None, "droid --version timed out"
    except OSError:
        return None, "droid --version could not start"
    if result.returncode != 0:
        return None, "droid --version failed"
    version = result.stdout.strip() or result.stderr.strip()
    if not version:
        return None, "droid --version returned no version text"
    return version, None


def validate_factory_authentication(
    environment: Mapping[str, str] | None = None,
    auth_path: Path = FACTORY_AUTH_PATH,
) -> list[str]:
    """Require an API key or a metadata-safe Factory CLI login receipt."""
    environment = os.environ if environment is None else environment
    value = environment.get(FACTORY_API_KEY_ENV)
    if isinstance(value, str) and value.strip():
        return []
    try:
        metadata = auth_path.lstat()
    except OSError:
        return [
            f"Factory authentication is unavailable: set {FACTORY_API_KEY_ENV} "
            "or complete droid login"
        ]
    if (
        not stat.S_ISREG(metadata.st_mode)
        or stat.S_ISLNK(metadata.st_mode)
        or metadata.st_uid != os.getuid()
        or metadata.st_nlink != 1
        or stat.S_IMODE(metadata.st_mode) != 0o600
        or not 0 < metadata.st_size <= 64 * 1024
    ):
        return ["Factory CLI authentication receipt has unsafe metadata"]
    return []


def main() -> int:
    errors = validate_settings()
    errors.extend(validate_factory_authentication())
    version, version_error = droid_version()
    if version_error:
        errors.append(version_error)

    if errors:
        print("Droid/Qwen preflight pending:")
        for error in errors:
            print(f"- {error}")
        print("- no model request was sent and no secret value was printed")
        return 2

    print("Droid/Qwen static preflight passed")
    print(f"- Droid CLI: {version}")
    print("- custom-model shape and both credential prerequisites are present")
    print("- endpoint behavior is outside this static check; see the evidence ledger")
    return 0


if __name__ == "__main__":
    sys.exit(main())
