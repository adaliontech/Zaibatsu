from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
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
        self.assertTrue(any("opaque binary" in error for error in errors))

    def test_media_extension_does_not_bypass_binary_scan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "claim.png").write_bytes(b"safe-prefix\x00private-content")
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("opaque binary" in error for error in errors))

    def test_invalid_utf8_media_file_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "claim.jpg").write_bytes(b"\xff\xfeprivate-content")
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("cannot scan public text" in error for error in errors))

    def test_runtime_and_pycache_names_do_not_bypass_scan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "runtime").mkdir()
            (root / "__pycache__").mkdir()
            (root / "runtime" / "leak.txt").write_text(
                "Private host: 8.8." + "8.8\n", encoding="utf-8"
            )
            (root / "__pycache__" / "leak.txt").write_text(
                "Private path: /" + "home/example/private\n", encoding="utf-8"
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("runtime/leak.txt" in error for error in errors))
        self.assertTrue(any("__pycache__/leak.txt" in error for error in errors))

    def test_force_added_ignored_settings_are_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / ".factory").mkdir()
            (root / ".gitignore").write_text(
                ".factory/settings.local.json\n", encoding="utf-8"
            )
            settings = root / ".factory" / "settings.local.json"
            settings.write_text(
                '{\n  "api' + 'Key": "plaintext-example"\n}\n', encoding="utf-8"
            )
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(
                ["git", "-C", str(root), "add", "-f", ".factory/settings.local.json"],
                check=True,
            )
            errors = validator.validate_public_safety(root)
        self.assertTrue(any("literal JSON API key" in error for error in errors))

    def test_git_submodule_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            nested = root / "module"
            subprocess.run(["git", "init", "-q", str(nested)], check=True)
            (nested / "README.md").write_text("nested\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(nested), "add", "README.md"], check=True)
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(nested),
                    "-c",
                    "user.name=Test",
                    "-c",
                    "user.email=test@example.invalid",
                    "commit",
                    "-qm",
                    "nested",
                ],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(root), "add", "module"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            shutil.rmtree(nested)
            errors = validator.validate_public_paths(root)
        self.assertTrue(any("submodules" in error for error in errors))

    def test_staged_content_is_scanned_even_when_worktree_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            path = root / "settings.json"
            path.write_text(
                '{\n  "api' + 'Key": "plaintext-example"\n}\n', encoding="utf-8"
            )
            subprocess.run(["git", "-C", str(root), "add", "settings.json"], check=True)
            path.write_text('{"safe": true}\n', encoding="utf-8")
            errors = validator.validate_public_safety(root)
        self.assertTrue(
            any("settings.json (Git index)" in error for error in errors)
        )


class FactoryModelValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.architecture = validator.load_architecture()
        self.factory_model = validator.load_factory_model()

    def test_repository_factory_model_passes(self) -> None:
        self.assertEqual([], validator.validate_factory_model(self.factory_model))
        self.assertEqual(
            [],
            validator.validate_factory_consistency(
                self.architecture, self.factory_model
            ),
        )

    def test_meta_factory_role_cannot_drift(self) -> None:
        mutated = copy.deepcopy(self.factory_model)
        mutated["project"]["role"] = "single_software_factory"
        errors = validator.validate_factory_model(mutated)
        self.assertTrue(any("meta-factory control layer" in error for error in errors))

    def test_required_factory_instance_cannot_be_removed(self) -> None:
        mutated = copy.deepcopy(self.factory_model)
        mutated["factory_instances"] = mutated["factory_instances"][:-1]
        errors = validator.validate_factory_model(mutated)
        self.assertTrue(any("closed project registry" in error for error in errors))

    def test_economic_factory_cannot_become_control_factory(self) -> None:
        mutated = copy.deepcopy(self.factory_model)
        economic_factory = next(
            instance
            for instance in mutated["factory_instances"]
            if instance["id"] == "ffn"
        )
        economic_factory["class"] = "control_factory"
        errors = validator.validate_factory_model(mutated)
        self.assertTrue(any("class and maturity" in error for error in errors))

    def test_factory_lifecycle_cannot_promote_before_evidence_return(self) -> None:
        mutated = copy.deepcopy(self.factory_model)
        lifecycle = mutated["factory_lifecycle"]
        lifecycle.remove("promote_reviewed_change")
        lifecycle.insert(lifecycle.index("return_evidence"), "promote_reviewed_change")
        errors = validator.validate_factory_model(mutated)
        self.assertTrue(any("meta-factory order" in error for error in errors))

    def test_nix_maturity_cannot_be_inflated(self) -> None:
        mutated = copy.deepcopy(self.factory_model)
        nix = next(
            capability
            for capability in mutated["capabilities"]
            if capability["id"] == "nix-environment-reproduction"
        )
        nix["maturity"] = "operational"
        mutated["reproducibility_policy"]["nix_currently_deployed"] = True
        errors = validator.validate_factory_model(mutated)
        self.assertTrue(any("nix-environment-reproduction" in error for error in errors))
        self.assertTrue(any("Ansible/Nix boundary" in error for error in errors))

    def test_plaintext_secrets_cannot_be_allowed_in_git(self) -> None:
        mutated = copy.deepcopy(self.factory_model)
        mutated["versioning_policy"]["plaintext_secrets_in_git"] = True
        errors = validator.validate_factory_model(mutated)
        self.assertTrue(any("no plaintext" in error for error in errors))

    def test_model_cannot_authorize_external_effect(self) -> None:
        mutated = copy.deepcopy(self.factory_model)
        mutated["agent_policy"]["model_may_authorize_external_effect"] = True
        errors = validator.validate_factory_model(mutated)
        self.assertTrue(any("may not authorize" in error for error in errors))

    def test_factory_feedback_cannot_self_promote(self) -> None:
        mutated = copy.deepcopy(self.factory_model)
        mutated["feedback_policy"]["factory_may_self_promote"] = True
        errors = validator.validate_factory_model(mutated)
        self.assertTrue(any("feedback policy" in error for error in errors))

    def test_component_and_factory_maturities_cannot_diverge(self) -> None:
        mutated = copy.deepcopy(self.factory_model)
        ansible = next(
            capability
            for capability in mutated["capabilities"]
            if capability["id"] == "ansible-reproduction"
        )
        ansible["maturity"] = "operational"
        errors = validator.validate_factory_consistency(self.architecture, mutated)
        self.assertTrue(any("ansible-configuration" in error for error in errors))

    def test_malformed_factory_model_fails_cleanly(self) -> None:
        malformed = {
            "schema_version": validator.FACTORY_MODEL_SCHEMA_VERSION,
            "project": [],
            "factory_classes": [],
            "factory_instances": [None],
            "factory_lifecycle": None,
            "capabilities": [None],
            "reproducibility_policy": [],
            "versioning_policy": [],
            "scheduling_policy": [],
            "agent_policy": [],
            "feedback_policy": [],
            "invariants": [],
        }
        errors = validator.validate_factory_model(malformed)
        self.assertGreaterEqual(len(errors), 11)
        self.assertTrue(any("factory model project" in error for error in errors))
        self.assertTrue(any("factory instance at index 0" in error for error in errors))
        self.assertTrue(any("factory capability at index 0" in error for error in errors))


class PortableFactoryDefinitionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = validator.load_factory_definition()

    def test_repository_example_passes(self) -> None:
        self.assertEqual([], validator.validate_factory_definition(self.factory))

    def test_unknown_factory_class_fails_closed(self) -> None:
        mutated = copy.deepcopy(self.factory)
        mutated["factory"]["class"] = "unbounded_factory"
        errors = validator.validate_factory_definition(mutated)
        self.assertTrue(any("factory class" in error for error in errors))

    def test_model_cannot_authorize_effect(self) -> None:
        mutated = copy.deepcopy(self.factory)
        mutated["agent_policy"]["model_may_authorize_external_effect"] = True
        errors = validator.validate_factory_definition(mutated)
        self.assertTrue(any("may not authorize" in error for error in errors))

    def test_feedback_cannot_self_promote(self) -> None:
        mutated = copy.deepcopy(self.factory)
        mutated["feedback_policy"]["factory_may_self_promote"] = True
        errors = validator.validate_factory_definition(mutated)
        self.assertTrue(any("without self-promotion" in error for error in errors))

    def test_nix_claim_requires_cross_node_proof(self) -> None:
        mutated = copy.deepcopy(self.factory)
        mutated["reproducibility_policy"]["nix_maturity"] = "operational"
        errors = validator.validate_factory_definition(mutated)
        self.assertTrue(any("cross-node" in error for error in errors))

    def test_strong_factory_maturity_requires_bound_receipt(self) -> None:
        mutated = copy.deepcopy(self.factory)
        mutated["factory"]["maturity"] = "operational"
        errors = validator.validate_factory_definition(mutated)
        self.assertTrue(any("factory-definition receipt" in error for error in errors))

    def test_cli_validates_repository_example(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(validator.ROOT / "scripts" / "zaibatsu.py"),
                "validate",
                str(validator.EXAMPLE_FACTORY_PATH),
            ],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)

    def test_cli_scaffold_round_trip_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "factory.json"
            command = [
                sys.executable,
                str(validator.ROOT / "scripts" / "zaibatsu.py"),
                "scaffold",
                "--id",
                "test-product",
                "--class",
                "economic_factory",
                "--purpose",
                "Produce a bounded test product",
                "--output",
                str(output),
            ]
            first = subprocess.run(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(0, first.returncode, first.stderr)
            document = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual([], validator.validate_factory_definition(document))
            self.assertEqual(
                validator.PORTABLE_FACTORY_SCHEMA_REFERENCE,
                document["contract_schema"],
            )
            second = subprocess.run(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(2, second.returncode)
            self.assertIn("refusing to overwrite", second.stderr)

    def test_unhashable_factory_fields_fail_cleanly(self) -> None:
        mutated = copy.deepcopy(self.factory)
        mutated["factory"]["class"] = []
        mutated["factory"]["maturity"] = []
        mutated["reproducibility_policy"]["nix_maturity"] = []
        mutated["scheduling_policy"]["scheduler_of_record"] = []
        mutated["agent_policy"]["skeleton_status"] = []
        errors = validator.validate_factory_definition(mutated)
        self.assertGreaterEqual(len(errors), 5)


class EvidenceReceiptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.receipts = {
            relative: json.loads((validator.ROOT / relative).read_text(encoding="utf-8"))
            for relative in validator.EVIDENCE_CONTRACTS
        }

    def test_repository_receipts_pass(self) -> None:
        self.assertEqual([], validator.validate_evidence_receipts())

    def test_empty_receipt_fails_closed(self) -> None:
        relative = "evidence/dispatcher-validation-v1.json"
        errors = validator.validate_evidence_receipt(relative, {})
        self.assertGreaterEqual(len(errors), 6)

    def test_dispatcher_zero_test_claim_is_rejected(self) -> None:
        relative = "evidence/dispatcher-validation-v1.json"
        mutated = copy.deepcopy(self.receipts[relative])
        mutated["focused_suite"]["tests_passed"] = 0
        errors = validator.validate_evidence_receipt(relative, mutated)
        self.assertTrue(any("focused suite counts" in error for error in errors))

    def test_dispatcher_invalid_digest_is_rejected(self) -> None:
        relative = "evidence/dispatcher-validation-v1.json"
        mutated = copy.deepcopy(self.receipts[relative])
        mutated["source"]["source_tree_sha256"] = "not-a-digest"
        errors = validator.validate_evidence_receipt(relative, mutated)
        self.assertTrue(any("source_tree_sha256" in error for error in errors))

    def test_droid_self_report_cannot_become_verification(self) -> None:
        relative = "evidence/droid-contribution-v1.json"
        mutated = copy.deepcopy(self.receipts[relative])
        mutated["acceptance"]["model_self_report_is_verification"] = True
        errors = validator.validate_evidence_receipt(relative, mutated)
        self.assertTrue(any("independent review" in error for error in errors))

    def test_qwen_identity_limitations_cannot_be_removed(self) -> None:
        relative = "evidence/qwen-model-observation-v1.json"
        mutated = copy.deepcopy(self.receipts[relative])
        mutated["limitations"] = []
        errors = validator.validate_evidence_receipt(relative, mutated)
        self.assertTrue(any("identity limitations" in error for error in errors))

    def test_unhashable_qwen_redaction_fails_cleanly(self) -> None:
        relative = "evidence/qwen-model-observation-v1.json"
        mutated = copy.deepcopy(self.receipts[relative])
        mutated["redactions"] = [{}]
        errors = validator.validate_evidence_receipt(relative, mutated)
        self.assertTrue(any("must stay redacted" in error for error in errors))


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

    def test_missing_gate_status_fails_cleanly(self) -> None:
        mutated = copy.deepcopy(self.readiness)
        del mutated["gates"][0]["status"]
        errors = validator.validate_submission_readiness(mutated)
        self.assertTrue(any("invalid gate status" in error for error in errors))

    def test_complete_gate_rejects_prose_only_evidence(self) -> None:
        mutated = copy.deepcopy(self.readiness)
        gate = next(item for item in mutated["gates"] if item["id"] == "public_package")
        gate.pop("proof")
        gate["evidence"] = "reviewed external evidence"
        errors = validator.validate_submission_readiness(mutated)
        self.assertTrue(any("structured proof" in error for error in errors))

    def test_unhashable_receipt_reference_fails_cleanly(self) -> None:
        mutated = copy.deepcopy(self.readiness)
        gate = next(item for item in mutated["gates"] if item["id"] == "droid_cli_install")
        gate["proof"]["receipt"] = []
        errors = validator.validate_submission_readiness(mutated)
        self.assertTrue(any("validated receipt" in error for error in errors))

    def test_all_gates_can_progress_to_ready(self) -> None:
        mutated = copy.deepcopy(self.readiness)
        completion_proofs = {
            "fresh_clone_reproduction": {
                "candidate_commit": "a" * 40,
                "tests_passed": validator.INTEGRATED_TEST_COUNT,
                "gitleaks_version": "8.30.1",
                "github_actions_run": "https://github.com/example/project/actions/runs/1",
            },
            "public_demo": {
                "url": "https://example.com/demo",
                "release_tag": "v1.1.2",
            },
            "applicant_materials": {
                "submitted_by_applicant": True,
                "resume_provided_privately": True,
            },
        }
        for gate in mutated["gates"]:
            gate["status"] = "complete"
            gate.pop("blocked_by", None)
            if gate["id"] in completion_proofs:
                gate["proof"] = completion_proofs[gate["id"]]
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
