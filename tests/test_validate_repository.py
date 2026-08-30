from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_repository.py"
SPEC = importlib.util.spec_from_file_location("validate_repository", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ArchitectureValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.architecture = validator.load_architecture()

    def test_repository_architecture_passes(self) -> None:
        self.assertEqual([], validator.validate_architecture(self.architecture))

    def test_public_project_name_cannot_drift(self) -> None:
        mutated = copy.deepcopy(self.architecture)
        mutated["project"]["name"] = "renamed-without-contract-update"
        errors = validator.validate_architecture(mutated)
        self.assertTrue(any("project name" in error for error in errors))

    def test_unknown_project_identity_fails_closed(self) -> None:
        mutated = copy.deepcopy(self.architecture)
        mutated["project_allowlist"].append("unknown")
        errors = validator.validate_architecture(mutated)
        self.assertTrue(any("project_allowlist" in error for error in errors))

    def test_probabilistic_component_requires_deterministic_exit(self) -> None:
        mutated = copy.deepcopy(self.architecture)
        worker = next(
            item for item in mutated["components"] if item["id"] == "probabilistic-workers"
        )
        del worker["deterministic_postcondition"]
        errors = validator.validate_architecture(mutated)
        self.assertTrue(any("deterministic_postcondition" in error for error in errors))

    def test_probabilistic_component_cannot_publish_directly(self) -> None:
        mutated = copy.deepcopy(self.architecture)
        worker = next(
            item for item in mutated["components"] if item["id"] == "probabilistic-workers"
        )
        worker["can_trigger_external_side_effects"] = True
        worker["policy_gate"] = "model says yes"
        errors = validator.validate_architecture(mutated)
        self.assertTrue(any("cannot directly trigger" in error for error in errors))

    def test_side_effecting_component_requires_policy_gate(self) -> None:
        mutated = copy.deepcopy(self.architecture)
        executor = next(
            item
            for item in mutated["components"]
            if item["id"] == "current-systemd-executor"
        )
        del executor["policy_gate"]
        errors = validator.validate_architecture(mutated)
        self.assertTrue(any("lacks policy_gate" in error for error in errors))

    def test_required_component_cannot_be_removed(self) -> None:
        mutated = copy.deepcopy(self.architecture)
        mutated["components"] = [
            component
            for component in mutated["components"]
            if component["id"] != "factory-droid-contribution"
        ]
        errors = validator.validate_architecture(mutated)
        self.assertTrue(any("components missing required ids" in error for error in errors))

    def test_malformed_component_fails_cleanly(self) -> None:
        mutated = copy.deepcopy(self.architecture)
        mutated["components"][0] = "not-an-object"
        errors = validator.validate_architecture(mutated)
        self.assertTrue(any("must be an object" in error for error in errors))

    def test_task_flow_stages_must_be_unique(self) -> None:
        mutated = copy.deepcopy(self.architecture)
        mutated["task_flow"].append("verify")
        errors = validator.validate_architecture(mutated)
        self.assertTrue(any("must be unique" in error for error in errors))

    def test_policy_decision_cannot_precede_verify(self) -> None:
        mutated = copy.deepcopy(self.architecture)
        flow = mutated["task_flow"]
        flow.remove("policy_decision")
        flow.insert(flow.index("verify"), "policy_decision")
        errors = validator.validate_architecture(mutated)
        self.assertTrue(
            any("policy_decision" in error and "verify" in error for error in errors)
        )

    def test_maturity_cannot_be_inflated_without_policy_change(self) -> None:
        mutated = copy.deepcopy(self.architecture)
        droid = next(
            component
            for component in mutated["components"]
            if component["id"] == "factory-droid-contribution"
        )
        droid["maturity"] = "operational"
        errors = validator.validate_architecture(mutated)
        self.assertTrue(any("maturity must remain" in error for error in errors))

    def test_operational_coordinator_scope_is_machine_readable(self) -> None:
        coordinator = next(
            component
            for component in self.architecture["components"]
            if component["id"] == "bounded-readonly-coordinator"
        )
        self.assertEqual("operational", coordinator["maturity"])
        mutated = copy.deepcopy(self.architecture)
        mutated["components"] = [
            component
            for component in mutated["components"]
            if component["id"] != "bounded-readonly-coordinator"
        ]
        errors = validator.validate_architecture(mutated)
        self.assertTrue(any("components missing required ids" in error for error in errors))

    def test_unhashable_component_fields_fail_cleanly(self) -> None:
        mutated = copy.deepcopy(self.architecture)
        mutated["components"][0]["maturity"] = []
        mutated["components"][1]["kind"] = []
        errors = validator.validate_architecture(mutated)
        self.assertTrue(any("invalid maturity" in error for error in errors))
        self.assertTrue(any("invalid kind" in error for error in errors))

    def test_public_scan_rejects_absolute_home_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "docs").mkdir()
            (root / "architecture").mkdir()
            (root / "README.md").write_text(
                "Private path: /" + "home/example/private\n", encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("absolute home path" in error for error in errors))

    def test_public_scan_rejects_home_path_without_trailing_slash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "Private path: /" + "home/example\n", encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("absolute home path" in error for error in errors))

    def test_public_scan_rejects_macos_home_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "Private path: /" + "Users/example/private\n", encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("absolute home path" in error for error in errors))

    def test_public_scan_rejects_windows_home_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "Private path: C:" + "\\Users\\example\\private\n", encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("absolute home path" in error for error in errors))

    def test_public_scan_rejects_tailnet_dns_name(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "Private host: private-host.private-tailnet." + "ts.net\n",
                encoding="utf-8",
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("Tailscale DNS name" in error for error in errors))

    def test_public_scan_allows_documentation_tailnet_placeholder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "Example host: gateway.example." + "ts.net\n", encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertFalse(any("Tailscale DNS name" in error for error in errors))

    def test_public_scan_rejects_placeholder_embedded_in_private_hostname(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "Private host: privategateway.example." + "ts.net\n",
                encoding="utf-8",
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("Tailscale DNS name" in error for error in errors))

    def test_public_scan_rejects_placeholder_below_private_subdomain(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "Private host: evil.gateway.example." + "ts.net\n",
                encoding="utf-8",
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("Tailscale DNS name" in error for error in errors))

    def test_public_scan_rejects_public_ipv4_address(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "Private host: 8.8." + "8.8\n", encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("public IPv4 address" in error for error in errors))

    def test_public_scan_rejects_ipv6_address(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "Private host: 2606:4700:4700:" + ":1111\n", encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("IPv6 address" in error for error in errors))

    def test_public_scan_covers_arbitrary_text_extensions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "leak.js").write_text(
                'const endpoint = "8.8.' + '8.8";\n', encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("public IPv4 address" in error for error in errors))

    def test_public_scan_covers_environment_example_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / ".env.example").write_text(
                "API_" + "KEY=plaintext-example\n", encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("secret assignment" in error for error in errors))

    def test_public_scan_rejects_common_client_secret_assignment(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "client_" + "secret=plaintext-example\n", encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("secret assignment" in error for error in errors))

    def test_public_scan_rejects_inline_bearer_credential(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                'curl -H "Authorization: Bear' + 'er plaintext-example"\n',
                encoding="utf-8",
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("literal bearer credential" in error for error in errors))

    def test_public_scan_allows_descriptive_bearer_language(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "The client rejects inline bearer credential forms.\n",
                encoding="utf-8",
            )
            errors = validator.validate_public_safety(root)
        self.assertFalse(any("literal bearer credential" in error for error in errors))

    def test_public_scan_rejects_literal_json_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "docs").mkdir()
            (root / "architecture").mkdir()
            (root / "README.md").write_text(
                '"api' + 'Key": "plaintext-example"\n', encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("literal JSON API key" in error for error in errors))

    def test_public_scan_rejects_prefixed_environment_secret(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "ZAIBATSU_QWEN_" + "API_KEY=not-a-real-secret\n",
                encoding="utf-8",
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("secret assignment" in error for error in errors))

    def test_public_scan_rejects_legacy_pre_release_brand(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "README.md").write_text(
                "Old name: " + "Factory" + " Squared\n", encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("legacy pre-release brand" in error for error in errors))

    def test_public_scan_covers_prompt_and_python_source(self) -> None:
        scanned = {
            path.relative_to(validator.ROOT) for path in validator.public_files()
        }
        self.assertIn(Path(".factory/prompts/review.md"), scanned)
        self.assertIn(Path("scripts/droid_preflight.py"), scanned)
        self.assertIn(Path("tests/test_validate_repository.py"), scanned)

    def test_required_file_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            target = root / "target.md"
            target.write_text("safe\n", encoding="utf-8")
            (root / "README.md").symlink_to(target)
            errors = validator.validate_required_files(root)
        self.assertTrue(any("must not be a symlink" in error for error in errors))

    def test_non_required_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "docs").mkdir()
            target = root / "target.md"
            target.write_text("safe\n", encoding="utf-8")
            (root / "docs" / "extra.md").symlink_to(target)
            errors = validator.validate_public_paths(root)
        self.assertTrue(any("must not be symlinks" in error for error in errors))

    def test_unapproved_binary_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "opaque.bin").write_bytes(b"safe-prefix\x00opaque")
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("unapproved binary" in error for error in errors))


class SubmissionReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.architecture = validator.load_architecture()
        self.readiness = json.loads(validator.READINESS_PATH.read_text(encoding="utf-8"))

    def test_repository_readiness_ledger_passes(self) -> None:
        self.assertEqual([], validator.validate_submission_readiness(self.readiness))
        self.assertEqual(
            [],
            validator.validate_contract_consistency(
                self.architecture, self.readiness
            ),
        )

    def test_submission_cannot_be_ready_with_pending_gates(self) -> None:
        mutated = copy.deepcopy(self.readiness)
        mutated["submission_ready"] = True
        errors = validator.validate_submission_readiness(mutated)
        self.assertTrue(any("submission_ready" in error for error in errors))

    def test_blocked_gate_requires_named_dependency(self) -> None:
        mutated = copy.deepcopy(self.readiness)
        repository_gate = next(
            gate for gate in mutated["gates"] if gate["id"] == "public_repository"
        )
        demo_gate = next(
            gate for gate in mutated["gates"] if gate["id"] == "public_demo"
        )
        repository_gate["status"] = "pending_external"
        demo_gate["status"] = "blocked_by_dependency"
        demo_gate["blocked_by"] = []
        errors = validator.validate_submission_readiness(mutated)
        self.assertTrue(any("must exactly match" in error for error in errors))

    def test_pending_gate_cannot_be_made_optional(self) -> None:
        mutated = copy.deepcopy(self.readiness)
        for gate in mutated["gates"]:
            if gate["status"] != "complete":
                gate["required_for_submission"] = False
        mutated["submission_ready"] = True
        errors = validator.validate_submission_readiness(mutated)
        self.assertTrue(any("required_for_submission" in error for error in errors))
        self.assertTrue(any("submission_ready" in error for error in errors))

    def test_dependent_gate_cannot_complete_before_prerequisites(self) -> None:
        mutated = copy.deepcopy(self.readiness)
        repository_gate = next(
            gate for gate in mutated["gates"] if gate["id"] == "public_repository"
        )
        clone_gate = next(
            gate for gate in mutated["gates"] if gate["id"] == "fresh_clone_reproduction"
        )
        repository_gate["status"] = "pending_external"
        clone_gate["status"] = "complete"
        clone_gate.pop("blocked_by", None)
        errors = validator.validate_submission_readiness(mutated)
        self.assertTrue(any("must remain blocked" in error for error in errors))

    def test_malformed_gate_fails_cleanly(self) -> None:
        mutated = copy.deepcopy(self.readiness)
        mutated["gates"][0] = "not-an-object"
        errors = validator.validate_submission_readiness(mutated)
        self.assertTrue(any("must be an object" in error for error in errors))

    def test_unhashable_gate_status_fails_cleanly(self) -> None:
        mutated = copy.deepcopy(self.readiness)
        mutated["gates"][0]["status"] = []
        errors = validator.validate_submission_readiness(mutated)
        self.assertTrue(any("invalid gate status" in error for error in errors))

    def test_all_gates_can_progress_to_ready(self) -> None:
        mutated = copy.deepcopy(self.readiness)
        for gate in mutated["gates"]:
            gate["status"] = "complete"
            gate.pop("blocked_by", None)
            gate["evidence"] = "reviewed external evidence"
        mutated["submission_ready"] = True
        self.assertEqual([], validator.validate_submission_readiness(mutated))

    def test_completed_droid_gate_requires_maturity_promotion(self) -> None:
        architecture = copy.deepcopy(self.architecture)
        droid_component = next(
            component
            for component in architecture["components"]
            if component["id"] == "factory-droid-contribution"
        )
        droid_component["maturity"] = "pending_evidence"
        errors = validator.validate_contract_consistency(architecture, self.readiness)
        self.assertTrue(any("must be promoted" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
