from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "droid_preflight.py"
SPEC = importlib.util.spec_from_file_location("droid_preflight", MODULE_PATH)
assert SPEC and SPEC.loader
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


class DroidPreflightTests(unittest.TestCase):
    def write_settings(self, settings: dict) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "settings.local.json"
        path.write_text(json.dumps(settings), encoding="utf-8")
        return path

    def valid_settings(self) -> dict:
        return {
            "customModels": [
                {
                    "model": "local-qwen-model-id",
                    "displayName": "Local Qwen 3.8 27B",
                    "baseUrl": "http://localhost:1234/v1",
                    "apiKey": "${LOCAL_TEST_KEY}",
                    "provider": "generic-chat-completion-api",
                }
            ]
        }

    def test_valid_local_settings_pass_without_exposing_key(self) -> None:
        path = self.write_settings(self.valid_settings())
        self.assertEqual(
            [], preflight.validate_settings(path, {"LOCAL_TEST_KEY": "not-printed"})
        )

    def test_missing_key_fails_closed(self) -> None:
        path = self.write_settings(self.valid_settings())
        errors = preflight.validate_settings(path, {})
        self.assertTrue(any("LOCAL_TEST_KEY" in error for error in errors))

    def test_non_loopback_endpoint_is_rejected(self) -> None:
        settings = self.valid_settings()
        settings["customModels"][0]["baseUrl"] = "https://model.example/v1"
        path = self.write_settings(settings)
        errors = preflight.validate_settings(path, {"LOCAL_TEST_KEY": "set"})
        self.assertTrue(any("loopback" in error for error in errors))

    def test_tailnet_dns_gateway_is_allowed(self) -> None:
        settings = self.valid_settings()
        settings["customModels"][0]["baseUrl"] = "http://gateway.example.ts.net:8443/v1"
        path = self.write_settings(settings)
        self.assertEqual(
            [], preflight.validate_settings(path, {"LOCAL_TEST_KEY": "set"})
        )

    def test_malformed_custom_model_fails_cleanly(self) -> None:
        path = self.write_settings({"customModels": [3]})
        errors = preflight.validate_settings(path, {})
        self.assertTrue(any("must be an object" in error for error in errors))

    def test_url_userinfo_is_rejected(self) -> None:
        settings = self.valid_settings()
        settings["customModels"][0]["baseUrl"] = (
            "http://user:password@localhost:1234/v1"
        )
        path = self.write_settings(settings)
        errors = preflight.validate_settings(path, {"LOCAL_TEST_KEY": "set"})
        self.assertTrue(any("userinfo" in error for error in errors))

    def test_invalid_port_is_rejected(self) -> None:
        settings = self.valid_settings()
        settings["customModels"][0]["baseUrl"] = "http://localhost:notaport/v1"
        path = self.write_settings(settings)
        errors = preflight.validate_settings(path, {"LOCAL_TEST_KEY": "set"})
        self.assertTrue(any("malformed" in error for error in errors))

    def test_url_query_and_fragment_are_rejected(self) -> None:
        settings = self.valid_settings()
        settings["customModels"][0]["baseUrl"] = (
            "http://localhost:1234/v1?token=value#fragment"
        )
        path = self.write_settings(settings)
        errors = preflight.validate_settings(path, {"LOCAL_TEST_KEY": "set"})
        self.assertTrue(any("query" in error for error in errors))

    def test_placeholder_with_leading_space_is_rejected(self) -> None:
        settings = self.valid_settings()
        settings["customModels"][0]["model"] = " REPLACE_WITH_MODEL_ID"
        path = self.write_settings(settings)
        errors = preflight.validate_settings(path, {"LOCAL_TEST_KEY": "set"})
        self.assertTrue(any("placeholder" in error for error in errors))

    def test_whitespace_only_key_is_rejected(self) -> None:
        path = self.write_settings(self.valid_settings())
        errors = preflight.validate_settings(path, {"LOCAL_TEST_KEY": "   "})
        self.assertTrue(any("LOCAL_TEST_KEY" in error for error in errors))

    def test_alternate_credential_fields_are_rejected(self) -> None:
        settings = self.valid_settings()
        settings["customModels"][0]["extraHeaders"] = {
            "Authorization": "not-a-real-secret"
        }
        path = self.write_settings(settings)
        errors = preflight.validate_settings(path, {"LOCAL_TEST_KEY": "set"})
        self.assertTrue(any("extraHeaders" in error for error in errors))

    def test_factory_authentication_is_a_separate_required_credential(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        missing = Path(temporary.name) / "missing.keyring"
        self.assertTrue(preflight.validate_factory_authentication({}, missing))
        self.assertTrue(
            preflight.validate_factory_authentication(
                {"FACTORY_API_KEY": "   "}, missing
            )
        )
        self.assertEqual(
            [],
            preflight.validate_factory_authentication(
                {"FACTORY_API_KEY": "present-but-never-printed"}, missing
            ),
        )

    def test_secure_factory_cli_login_receipt_is_accepted(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        auth_path = Path(temporary.name) / "auth.v2.keyring"
        auth_path.write_text("opaque-login-receipt", encoding="utf-8")
        auth_path.chmod(0o600)
        self.assertEqual([], preflight.validate_factory_authentication({}, auth_path))
        auth_path.chmod(0o644)
        self.assertTrue(preflight.validate_factory_authentication({}, auth_path))


if __name__ == "__main__":
    unittest.main()
