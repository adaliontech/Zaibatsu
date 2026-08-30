from __future__ import annotations

import copy
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_repository.py"
if str(MODULE_PATH.parent) not in sys.path:
    sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("validate_repository", MODULE_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
import factory_bundle as bundler
import factory_composer as composer
import factory_qualification as qualification


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


class ModuleCompositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = validator.load_factory_definition()
        self.catalog = composer.load_module_catalog()
        self.plan = composer.load_factory_plan()

    def test_repository_catalog_bindings_and_plan_pass(self) -> None:
        self.assertEqual([], composer.validate_module_catalog(self.catalog))
        self.assertEqual(
            [], composer.validate_factory_bindings(self.factory, self.catalog)
        )
        self.assertEqual(
            [], composer.validate_factory_plan(self.plan, self.factory, self.catalog)
        )

    def test_compatible_alternate_module_id_is_interchangeable(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        factory = copy.deepcopy(self.factory)
        module = next(item for item in catalog["modules"] if item["id"] == "git-source")
        module["id"] = "alternate-git-source"
        module["artifact"]["path"] = "modules/alternate-git-source/module.json"
        binding = next(
            item
            for item in factory["module_bindings"]
            if item["slot"] == "source_versioning"
        )
        binding["module"] = "alternate-git-source"
        self.assertEqual([], composer.validate_module_catalog(catalog))
        self.assertEqual([], composer.validate_factory_bindings(factory, catalog))

    def test_compatible_alternate_artifact_builds_verified_bundle(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        factory = copy.deepcopy(self.factory)
        module = next(item for item in catalog["modules"] if item["id"] == "git-source")
        module["id"] = "alternate-git-source"
        module["artifact"]["path"] = "modules/alternate-git-source/module.json"
        artifact = composer.expected_module_artifact(module)
        module["artifact"]["sha256"] = composer.sha256_json(artifact)
        binding = next(
            item
            for item in factory["module_bindings"]
            if item["slot"] == "source_versioning"
        )
        binding["module"] = "alternate-git-source"
        with tempfile.TemporaryDirectory() as temporary_directory:
            base = Path(temporary_directory)
            shutil.copytree(validator.ROOT / "catalog" / "modules", base / "modules")
            artifact_path = base / module["artifact"]["path"]
            artifact_path.parent.mkdir()
            artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
            artifacts, errors = composer.load_module_artifacts(catalog, base)
        self.assertEqual([], composer.validate_module_catalog(catalog))
        self.assertEqual([], composer.validate_factory_bindings(factory, catalog))
        self.assertEqual([], errors)
        bundle, _ = bundler.build_factory_bundle(factory, catalog, artifacts)
        verification_errors, _ = bundler.verify_factory_bundle(bundle)
        self.assertEqual([], verification_errors)

    def test_module_policy_mismatch_fails_closed(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        module = next(item for item in catalog["modules"] if item["id"] == "git-source")
        module["policy_value"] = "not-git"
        errors = composer.validate_factory_bindings(self.factory, catalog)
        self.assertTrue(any("does not preserve" in error for error in errors))

    def test_duplicate_module_id_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][1]["id"] = catalog["modules"][0]["id"]
        errors = composer.validate_module_catalog(catalog)
        self.assertTrue(any("duplicate module id" in error for error in errors))

    def test_invalid_module_id_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][0]["id"] = "Ambiguous module id"
        errors = composer.validate_module_catalog(catalog)
        self.assertTrue(any("must have an id" in error for error in errors))

    def test_missing_module_slot_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"] = [
            module for module in catalog["modules"] if module["slot"] != "feedback"
        ]
        errors = composer.validate_module_catalog(catalog)
        self.assertTrue(any("missing slots" in error for error in errors))

    def test_forward_module_dependency_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][0]["requires_slots"] = ["feedback"]
        errors = composer.validate_module_catalog(catalog)
        self.assertTrue(any("must precede" in error for error in errors))

    def test_duplicate_typed_output_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][0]["provides"].append(
            catalog["modules"][0]["provides"][0]
        )
        errors = composer.validate_module_catalog(catalog)
        self.assertTrue(any("provides must be unique" in error for error in errors))

    def test_malformed_catalog_and_binding_fail_cleanly(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][0]["policy_value"] = ["valid", []]
        errors = composer.validate_module_catalog(catalog)
        self.assertTrue(any("policy_value" in error for error in errors))
        factory = copy.deepcopy(self.factory)
        factory["module_bindings"][0]["slot"] = []
        errors = composer.validate_factory_bindings(factory, self.catalog)
        self.assertTrue(any("invalid slot" in error for error in errors))

    def test_repository_module_artifacts_are_content_addressed(self) -> None:
        artifacts, errors = composer.load_module_artifacts(self.catalog)
        self.assertEqual([], errors)
        self.assertEqual(10, len(artifacts))
        for module in self.catalog["modules"]:
            artifact = artifacts[module["id"]]
            self.assertEqual([], composer.validate_module_artifact(artifact, module))
            self.assertEqual(
                module["artifact"]["sha256"], composer.sha256_json(artifact)
            )

    def test_module_artifact_digest_drift_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][0]["artifact"]["sha256"] = "0" * 64
        _, errors = composer.load_module_artifacts(catalog)
        self.assertTrue(any("digest does not match" in error for error in errors))

    def test_module_artifact_contract_drift_is_rejected(self) -> None:
        module = self.catalog["modules"][0]
        artifact = composer.expected_module_artifact(module)
        artifact["provides"].append("undeclared_output")
        errors = composer.validate_module_artifact(artifact, module)
        self.assertTrue(any("exactly match" in error for error in errors))

    def test_module_artifact_path_traversal_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][0]["artifact"]["path"] = "../outside/module.json"
        errors = composer.validate_module_catalog(catalog)
        self.assertTrue(any("module-local" in error for error in errors))

    def test_module_artifact_symlink_is_rejected(self) -> None:
        module = copy.deepcopy(self.catalog["modules"][0])
        with tempfile.TemporaryDirectory() as temporary_directory:
            base = Path(temporary_directory)
            artifact_path = base / module["artifact"]["path"]
            artifact_path.parent.mkdir(parents=True)
            target = base / "target.json"
            target.write_text("{}\n", encoding="utf-8")
            artifact_path.symlink_to(target)
            _, errors = composer.load_module_artifacts({"modules": [module]}, base)
        self.assertTrue(any("must not be a symlink" in error for error in errors))

    def test_plan_binds_every_selected_module_artifact(self) -> None:
        catalog_modules = {module["id"]: module for module in self.catalog["modules"]}
        for resolved in self.plan["modules"]:
            self.assertEqual(
                catalog_modules[resolved["module"]]["artifact"],
                resolved["artifact"],
            )

    def test_definition_drift_invalidates_recorded_plan(self) -> None:
        factory = copy.deepcopy(self.factory)
        factory["factory"]["purpose"] += " after a reviewed change"
        errors = composer.validate_factory_plan(self.plan, factory, self.catalog)
        self.assertTrue(any("content-addressed inputs" in error for error in errors))

    def test_catalog_drift_invalidates_recorded_plan(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][0]["description"] += " with a revised contract"
        errors = composer.validate_factory_plan(self.plan, self.factory, catalog)
        self.assertTrue(any("content-addressed inputs" in error for error in errors))

    def test_plan_digest_tampering_is_rejected(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["plan_sha256"] = "0" * 64
        errors = composer.validate_factory_plan(plan, self.factory, self.catalog)
        self.assertTrue(any("content-addressed inputs" in error for error in errors))

    def test_rebuild_is_byte_stable_and_path_independent(self) -> None:
        stable, digest = composer.rebuild_check(self.factory, self.catalog)
        self.assertTrue(stable)
        self.assertEqual(self.plan["plan_sha256"], digest)
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            factory_path = root / "nested" / "factory.json"
            catalog_path = root / "elsewhere" / "catalog.json"
            factory_path.parent.mkdir()
            catalog_path.parent.mkdir()
            factory_path.write_text(json.dumps(self.factory), encoding="utf-8")
            catalog_path.write_text(json.dumps(self.catalog), encoding="utf-8")
            relocated = composer.build_factory_plan(
                json.loads(factory_path.read_text(encoding="utf-8")),
                json.loads(catalog_path.read_text(encoding="utf-8")),
            )
        self.assertEqual(self.plan, relocated)

    def test_plan_cannot_claim_deployment_or_runtime_recovery(self) -> None:
        claim = self.plan["rebuild_claim"]
        self.assertEqual("control_plan_only", claim["scope"])
        self.assertFalse(claim["deploys_infrastructure"])
        self.assertFalse(claim["proves_runtime_recovery"])
        rendered = json.dumps(self.plan)
        self.assertNotIn("/home/", rendered)
        self.assertNotIn("C:\\Users\\", rendered)

    def test_plan_mutation_cannot_modify_source_inputs(self) -> None:
        factory_before = copy.deepcopy(self.factory)
        catalog_before = copy.deepcopy(self.catalog)
        plan = composer.build_factory_plan(self.factory, self.catalog)
        plan["deterministic_gates"].append("untrusted")
        plan["modules"][0]["provides"].append("untrusted_output")
        plan["modules"][7]["policy_value"].append("untrusted")
        self.assertEqual(factory_before, self.factory)
        self.assertEqual(catalog_before, self.catalog)

    def test_cli_plan_verify_and_rebuild_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "factory.plan.json"
            cli = [sys.executable, str(validator.ROOT / "scripts" / "zaibatsu.py")]
            plan_result = subprocess.run(
                cli
                + [
                    "plan",
                    str(validator.EXAMPLE_FACTORY_PATH),
                    "--output",
                    str(output),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(0, plan_result.returncode, plan_result.stderr)
            self.assertEqual(self.plan, json.loads(output.read_text(encoding="utf-8")))
            verify_result = subprocess.run(
                cli
                + [
                    "verify-plan",
                    str(output),
                    str(validator.EXAMPLE_FACTORY_PATH),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(0, verify_result.returncode, verify_result.stderr)
            rebuild_result = subprocess.run(
                cli + ["rebuild-check", str(validator.EXAMPLE_FACTORY_PATH)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(0, rebuild_result.returncode, rebuild_result.stderr)
            self.assertIn(self.plan["plan_sha256"], rebuild_result.stdout)

    def test_cli_rejects_stale_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            factory_path = Path(temporary_directory) / "factory.json"
            factory = copy.deepcopy(self.factory)
            factory["factory"]["purpose"] += " changed"
            factory_path.write_text(json.dumps(factory), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(validator.ROOT / "scripts" / "zaibatsu.py"),
                    "verify-plan",
                    str(composer.EXAMPLE_PLAN_PATH),
                    str(factory_path),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        self.assertEqual(1, result.returncode)
        self.assertIn("content-addressed inputs", result.stderr)

    def test_cli_rejects_duplicate_json_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            factory_path = Path(temporary_directory) / "factory.json"
            factory_path.write_text(
                '{"contract_schema":"first","contract_schema":"second"}\n',
                encoding="utf-8",
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(validator.ROOT / "scripts" / "zaibatsu.py"),
                    "validate",
                    str(factory_path),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        self.assertEqual(2, result.returncode)
        self.assertIn("duplicate JSON object key", result.stderr)

    def test_cli_refuses_dangling_output_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            output = root / "factory.plan.json"
            target = root / "missing-target.json"
            output.symlink_to(target)
            result = subprocess.run(
                [
                    sys.executable,
                    str(validator.ROOT / "scripts" / "zaibatsu.py"),
                    "plan",
                    str(validator.EXAMPLE_FACTORY_PATH),
                    "--output",
                    str(output),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        self.assertEqual(2, result.returncode)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertFalse(target.exists())


class FactoryBundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = validator.load_factory_definition()
        self.cron_factory = composer.load_json_file(
            validator.ROOT / "examples" / "economic-factory-cron.json"
        )
        self.catalog = composer.load_module_catalog()
        self.plan = composer.load_factory_plan()
        self.artifacts, errors = composer.load_module_artifacts(self.catalog)
        self.assertEqual([], errors)
        self.bundle, self.manifest = bundler.build_factory_bundle(
            self.factory, self.catalog, self.artifacts
        )

    def _alternate_source_bundle(self) -> bytes:
        factory = copy.deepcopy(self.factory)
        catalog = copy.deepcopy(self.catalog)
        artifacts = copy.deepcopy(self.artifacts)
        module = next(item for item in catalog["modules"] if item["id"] == "git-source")
        module["id"] = "alternate-git-source"
        module["artifact"]["path"] = (
            "modules/alternate-git-source/module.json"
        )
        artifact = composer.expected_module_artifact(module)
        module["artifact"]["sha256"] = composer.sha256_json(artifact)
        binding = next(
            item
            for item in factory["module_bindings"]
            if item["slot"] == "source_versioning"
        )
        binding["module"] = "alternate-git-source"
        artifacts.pop("git-source")
        artifacts["alternate-git-source"] = artifact
        bundle, _ = bundler.build_factory_bundle(factory, catalog, artifacts)
        return bundle

    def test_bundle_round_trip_passes(self) -> None:
        errors, result = bundler.verify_factory_bundle(self.bundle)
        self.assertEqual([], errors)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertEqual("example-product", result["factory_id"])
        self.assertEqual(self.plan["plan_sha256"], result["plan_sha256"])
        self.assertEqual(bundler.sha256_bytes(self.bundle), result["bundle_sha256"])

    def test_bundle_is_byte_reproducible(self) -> None:
        second, second_manifest = bundler.build_factory_bundle(
            copy.deepcopy(self.factory),
            copy.deepcopy(self.catalog),
            copy.deepcopy(self.artifacts),
        )
        self.assertEqual(self.bundle, second)
        self.assertEqual(self.manifest, second_manifest)

    def test_repository_bundle_manifest_matches_builder(self) -> None:
        recorded = composer.load_json_file(validator.EXAMPLE_BUNDLE_MANIFEST_PATH)
        self.assertEqual(self.manifest, recorded)

    def test_bundle_inspection_is_stable_and_non_authorizing(self) -> None:
        errors, inspection = bundler.inspect_factory_bundle(self.bundle)
        self.assertEqual([], errors)
        self.assertIsNotNone(inspection)
        assert inspection is not None
        second_errors, second = bundler.inspect_factory_bundle(self.bundle)
        self.assertEqual([], second_errors)
        self.assertEqual(inspection, second)
        self.assertEqual(
            bundler.BUNDLE_INSPECTION_SCHEMA_VERSION,
            inspection["schema_version"],
        )
        schema = composer.load_json_file(
            validator.ROOT / "schemas" / "factory-bundle-inspection.schema.json"
        )
        self.assertEqual(bundler.BUNDLE_INSPECTION_SCHEMA_REFERENCE, schema["$id"])
        self.assertEqual(
            bundler.BUNDLE_INSPECTION_SCHEMA_REFERENCE,
            inspection["contract_schema"],
        )
        self.assertEqual(set(schema["required"]), set(inspection))
        self.assertEqual(self.manifest["selected_modules"], inspection["selected_modules"])
        self.assertFalse(inspection["runtime_eligibility"]["eligible"])
        self.assertFalse(inspection["rebuild_claim"]["deploys_infrastructure"])

    def test_same_bundle_comparison_has_no_changes(self) -> None:
        errors, comparison = bundler.compare_factory_bundles(
            self.bundle, self.bundle
        )
        self.assertEqual([], errors)
        self.assertIsNotNone(comparison)
        assert comparison is not None
        self.assertFalse(comparison["changed"])
        self.assertEqual([], comparison["changes"]["modules"])
        self.assertEqual([], comparison["changes"]["schemas"])
        self.assertFalse(comparison["changes"]["factory_identity_changed"])
        self.assertFalse(comparison["changes"]["factory_definition_changed"])
        self.assertFalse(comparison["changes"]["module_catalog_changed"])
        self.assertFalse(comparison["changes"]["factory_plan_changed"])
        self.assertTrue(comparison["runtime_boundary_preserved"])
        schema = composer.load_json_file(
            validator.ROOT / "schemas" / "factory-bundle-comparison.schema.json"
        )
        self.assertEqual(bundler.BUNDLE_COMPARISON_SCHEMA_REFERENCE, schema["$id"])
        self.assertEqual(
            bundler.BUNDLE_COMPARISON_SCHEMA_REFERENCE,
            comparison["contract_schema"],
        )
        self.assertEqual(set(schema["required"]), set(comparison))

    def test_compatible_substitution_comparison_is_narrow(self) -> None:
        alternate = self._alternate_source_bundle()
        errors, comparison = bundler.compare_factory_bundles(self.bundle, alternate)
        self.assertEqual([], errors)
        self.assertIsNotNone(comparison)
        assert comparison is not None
        self.assertTrue(comparison["changed"])
        self.assertFalse(comparison["changes"]["factory_identity_changed"])
        self.assertTrue(comparison["changes"]["factory_definition_changed"])
        self.assertTrue(comparison["changes"]["module_catalog_changed"])
        self.assertTrue(comparison["changes"]["factory_plan_changed"])
        self.assertEqual([], comparison["changes"]["schemas"])
        self.assertEqual(1, len(comparison["changes"]["modules"]))
        module_change = comparison["changes"]["modules"][0]
        self.assertEqual("source_versioning", module_change["slot"])
        self.assertEqual("implementation_replaced", module_change["change"])
        self.assertEqual("git-source", module_change["before"]["module"])
        self.assertEqual("alternate-git-source", module_change["after"]["module"])
        self.assertTrue(comparison["runtime_boundary_preserved"])

    def test_public_scheduler_variant_comparison_is_narrow(self) -> None:
        cron_bundle, _ = bundler.build_factory_bundle(
            self.cron_factory,
            self.catalog,
            self.artifacts,
        )
        errors, comparison = bundler.compare_factory_bundles(
            self.bundle, cron_bundle
        )
        self.assertEqual([], errors)
        self.assertIsNotNone(comparison)
        assert comparison is not None
        self.assertTrue(comparison["changes"]["factory_definition_changed"])
        self.assertFalse(comparison["changes"]["module_catalog_changed"])
        self.assertTrue(comparison["changes"]["factory_plan_changed"])
        self.assertEqual([], comparison["changes"]["schemas"])
        self.assertEqual(1, len(comparison["changes"]["modules"]))
        module_change = comparison["changes"]["modules"][0]
        self.assertEqual("scheduling", module_change["slot"])
        self.assertEqual("systemd-scheduler", module_change["before"]["module"])
        self.assertEqual("cron-scheduler", module_change["after"]["module"])
        self.assertTrue(comparison["runtime_boundary_preserved"])

    def test_bundle_comparison_rejects_a_tampered_side(self) -> None:
        tampered = self.bundle.replace(b"Git lineage", b"Git lineagf", 1)
        errors, comparison = bundler.compare_factory_bundles(
            self.bundle, tampered
        )
        self.assertTrue(any(error.startswith("after bundle:") for error in errors))
        self.assertIsNone(comparison)

    def test_bundle_tar_metadata_and_order_are_canonical(self) -> None:
        with tarfile.open(fileobj=io.BytesIO(self.bundle), mode="r:") as archive:
            members = archive.getmembers()
        self.assertEqual(
            sorted(member.name for member in members),
            [member.name for member in members],
        )
        for member in members:
            self.assertTrue(member.isfile())
            self.assertEqual(0o644, member.mode)
            self.assertEqual(0, member.mtime)
            self.assertEqual(0, member.uid)
            self.assertEqual(0, member.gid)
            self.assertEqual("", member.uname)
            self.assertEqual("", member.gname)

    def test_bundle_contains_only_selected_module_contracts(self) -> None:
        with tarfile.open(fileobj=io.BytesIO(self.bundle), mode="r:") as archive:
            names = {member.name for member in archive.getmembers()}
        self.assertNotIn("modules/cron-scheduler/module.json", names)
        self.assertIn("modules/systemd-scheduler/module.json", names)
        claim = self.manifest["rebuild_claim"]
        self.assertTrue(claim["contains_selected_module_contracts"])
        self.assertTrue(claim["contains_contract_schemas"])
        self.assertFalse(claim["contains_runtime_implementations"])
        self.assertFalse(claim["deploys_infrastructure"])
        self.assertFalse(claim["proves_runtime_recovery"])

    def test_bundle_payload_tampering_is_rejected(self) -> None:
        tampered = self.bundle.replace(b"Git lineage", b"Git lineagf", 1)
        self.assertNotEqual(self.bundle, tampered)
        errors, _ = bundler.verify_factory_bundle(tampered)
        self.assertTrue(errors)

    def test_bundled_schema_body_tampering_is_rejected_after_manifest_rebuild(self) -> None:
        payloads, read_errors = bundler._read_archive_payloads(self.bundle)
        self.assertEqual([], read_errors)
        schema_path = "schemas/factory-bundle-manifest.schema.json"
        schema = composer.load_json_bytes(payloads[schema_path])
        schema["description"] = "attacker-controlled rule change"
        payloads[schema_path] = composer.canonical_json_bytes(schema)

        content_payloads = {
            path: data
            for path, data in payloads.items()
            if path != bundler.MANIFEST_PATH
        }
        malicious_manifest = bundler.build_bundle_manifest(
            self.factory,
            self.catalog,
            self.plan,
            content_payloads,
        )
        payloads[bundler.MANIFEST_PATH] = composer.canonical_json_bytes(
            malicious_manifest
        )
        malicious_bundle = bundler.canonical_tar_bytes(payloads)

        errors, _ = bundler.verify_factory_bundle(malicious_bundle)
        self.assertTrue(any("immutable content digest" in error for error in errors))

    def test_bundle_trailing_bytes_are_rejected(self) -> None:
        errors, _ = bundler.verify_factory_bundle(self.bundle + b"unexpected")
        self.assertTrue(any("not canonical" in error for error in errors))

    def test_bundle_path_traversal_is_rejected(self) -> None:
        malicious = bundler.canonical_tar_bytes({"../escape.json": b"{}\n"})
        errors, _ = bundler.verify_factory_bundle(malicious)
        self.assertTrue(any("unsafe" in error for error in errors))

    def test_bundle_symlink_member_is_rejected(self) -> None:
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            member = tarfile.TarInfo("unsafe-link")
            member.type = tarfile.SYMTYPE
            member.linkname = "outside"
            member.mode = 0o644
            member.mtime = 0
            archive.addfile(member)
        errors, _ = bundler.verify_factory_bundle(output.getvalue())
        self.assertTrue(any("regular file" in error for error in errors))

    def test_bundle_duplicate_member_is_rejected(self) -> None:
        output = io.BytesIO()
        with tarfile.open(fileobj=output, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for _ in range(2):
                member = tarfile.TarInfo(bundler.MANIFEST_PATH)
                member.size = 3
                member.mode = 0o644
                member.mtime = 0
                archive.addfile(member, io.BytesIO(b"{}\n"))
        errors, _ = bundler.verify_factory_bundle(output.getvalue())
        self.assertTrue(any("duplicate" in error for error in errors))

    def test_bundle_extra_member_is_rejected(self) -> None:
        payloads, read_errors = bundler._read_archive_payloads(self.bundle)
        self.assertEqual([], read_errors)
        payloads["unexpected.json"] = b"{}\n"
        errors, _ = bundler.verify_factory_bundle(
            bundler.canonical_tar_bytes(payloads)
        )
        self.assertTrue(any("unexpected members" in error for error in errors))

    def test_malformed_bundle_fails_cleanly(self) -> None:
        for value in (b"", b"not a tar", b"\0" * 512, b"x" * 1024):
            errors, result = bundler.verify_factory_bundle(value)
            self.assertTrue(errors)
            self.assertIsNone(result)

    def test_cli_bundle_and_verify_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "factory.tar"
            cli = [sys.executable, str(validator.ROOT / "scripts" / "zaibatsu.py")]
            built = subprocess.run(
                cli
                + [
                    "bundle",
                    str(validator.EXAMPLE_FACTORY_PATH),
                    "--output",
                    str(output),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(0, built.returncode, built.stderr)
            self.assertEqual(self.bundle, output.read_bytes())
            verified = subprocess.run(
                cli + ["verify-bundle", str(output)],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(0, verified.returncode, verified.stderr)
            self.assertIn(bundler.sha256_bytes(self.bundle), verified.stdout)

    def test_cli_inspect_and_compare_bundle_round_trip(self) -> None:
        alternate = self._alternate_source_bundle()
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            before_path = root / "before.tar"
            after_path = root / "after.tar"
            inspection_path = root / "inspection.json"
            comparison_path = root / "comparison.json"
            before_path.write_bytes(self.bundle)
            after_path.write_bytes(alternate)
            cli = [sys.executable, str(validator.ROOT / "scripts" / "zaibatsu.py")]
            inspected = subprocess.run(
                cli
                + [
                    "inspect-bundle",
                    str(before_path),
                    "--output",
                    str(inspection_path),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            compared = subprocess.run(
                cli
                + [
                    "compare-bundles",
                    str(before_path),
                    str(after_path),
                    "--output",
                    str(comparison_path),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(0, inspected.returncode, inspected.stderr)
            self.assertEqual(0, compared.returncode, compared.stderr)
            for command in (
                [
                    "inspect-bundle",
                    str(before_path),
                    "--output",
                    str(inspection_path),
                ],
                [
                    "compare-bundles",
                    str(before_path),
                    str(after_path),
                    "--output",
                    str(comparison_path),
                ],
            ):
                repeated = subprocess.run(
                    cli + command,
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                self.assertEqual(2, repeated.returncode)
                self.assertIn("refusing to overwrite", repeated.stderr)
            inspection = json.loads(inspection_path.read_text(encoding="utf-8"))
            comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
        self.assertEqual(bundler.sha256_bytes(self.bundle), inspection["bundle_sha256"])
        self.assertEqual(1, len(comparison["changes"]["modules"]))

    def test_cli_bundle_refuses_dangling_output_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            output = root / "factory.tar"
            target = root / "missing.tar"
            output.symlink_to(target)
            result = subprocess.run(
                [
                    sys.executable,
                    str(validator.ROOT / "scripts" / "zaibatsu.py"),
                    "bundle",
                    str(validator.EXAMPLE_FACTORY_PATH),
                    "--output",
                    str(output),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        self.assertEqual(2, result.returncode)
        self.assertIn("refusing to overwrite", result.stderr)
        self.assertFalse(target.exists())

    def test_cli_bundle_readers_reject_symlinks_and_oversized_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            valid = root / "valid.tar"
            linked = root / "linked.tar"
            oversized = root / "oversized.tar"
            valid.write_bytes(self.bundle)
            linked.symlink_to(valid)
            oversized.write_bytes(b"x" * (bundler.MAX_BUNDLE_BYTES + 1))
            cli = [sys.executable, str(validator.ROOT / "scripts" / "zaibatsu.py")]
            for command, path in (
                ("verify-bundle", linked),
                ("inspect-bundle", oversized),
            ):
                with self.subTest(command=command):
                    result = subprocess.run(
                        cli + [command, str(path)],
                        check=False,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    self.assertEqual(2, result.returncode)
                    self.assertIn("cannot load", result.stderr)


class QualificationPlanningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.factory = validator.load_factory_definition()
        self.catalog = composer.load_module_catalog()
        self.artifacts, errors = composer.load_module_artifacts(self.catalog)
        self.assertEqual([], errors)
        self.bundle, _ = bundler.build_factory_bundle(
            self.factory,
            self.catalog,
            self.artifacts,
        )
        self.policy = qualification.load_qualification_policy()
        self.recorded = qualification.load_qualification_plan()

    def test_repository_qualification_policy_and_plan_pass(self) -> None:
        self.assertEqual([], qualification.validate_qualification_policy(self.policy))
        bundle_errors, verified = bundler.verify_factory_bundle(self.bundle)
        self.assertEqual([], bundle_errors)
        self.assertIsNotNone(verified)
        assert verified is not None
        self.assertEqual(
            [],
            qualification.validate_qualification_plan(
                self.recorded,
                verified,
                self.policy,
            ),
        )
        self.assertEqual(
            self.recorded,
            qualification.build_qualification_plan(verified, self.policy),
        )

    def test_qualification_plan_is_stable_and_non_authorizing(self) -> None:
        errors, first = qualification.qualification_plan_for_bundle(
            self.bundle,
            self.policy,
        )
        second_errors, second = qualification.qualification_plan_for_bundle(
            self.bundle,
            copy.deepcopy(self.policy),
        )
        self.assertEqual([], errors)
        self.assertEqual([], second_errors)
        self.assertEqual(first, second)
        self.assertIsNotNone(first)
        assert first is not None
        without_digest = copy.deepcopy(first)
        digest = without_digest.pop("qualification_plan_sha256")
        self.assertEqual(composer.sha256_json(without_digest), digest)
        self.assertEqual(9, first["summary"]["module_count"])
        self.assertEqual(0, first["summary"]["runtime_eligible_modules"])
        self.assertEqual(67, first["summary"]["missing_evidence_bindings"])
        self.assertEqual(27, first["summary"]["unique_requirement_types"])
        self.assertFalse(first["summary"]["all_requirements_satisfied"])
        self.assertFalse(first["qualification_boundary"]["activation_authorized"])
        self.assertFalse(
            first["qualification_boundary"]["runtime_eligibility_granted"]
        )
        self.assertTrue(
            first["qualification_boundary"][
                "owner_approval_required_for_activation"
            ]
        )
        self.assertTrue(all(not module["runtime_eligible"] for module in first["modules"]))
        policy_schema = composer.load_json_file(
            validator.ROOT
            / "schemas"
            / "module-qualification-policy.schema.json"
        )
        plan_schema = composer.load_json_file(
            validator.ROOT
            / "schemas"
            / "factory-qualification-plan.schema.json"
        )
        self.assertEqual(
            qualification.QUALIFICATION_POLICY_SCHEMA_REFERENCE,
            policy_schema["$id"],
        )
        self.assertEqual(
            qualification.QUALIFICATION_PLAN_SCHEMA_REFERENCE,
            plan_schema["$id"],
        )
        self.assertEqual(set(plan_schema["required"]), set(first))

    def test_policy_cannot_accept_self_attestation_or_grant_activation(self) -> None:
        for field, unsafe_value in (
            ("self_attestation_accepted", True),
            ("qualification_plan_is_evidence", True),
            ("qualification_grants_activation", True),
            ("owner_approval_required_for_activation", False),
        ):
            with self.subTest(field=field):
                mutated = copy.deepcopy(self.policy)
                mutated["decision_boundary"][field] = unsafe_value
                errors = qualification.validate_qualification_policy(mutated)
                self.assertTrue(any("fail-closed" in error for error in errors))

        type_confused = copy.deepcopy(self.policy)
        type_confused["decision_boundary"][
            "owner_approval_required_for_activation"
        ] = 1
        errors = qualification.validate_qualification_policy(type_confused)
        self.assertTrue(any("fail-closed" in error for error in errors))

    def test_policy_cannot_remove_mandatory_requirements(self) -> None:
        missing_base = copy.deepcopy(self.policy)
        missing_base["base_requirements"].remove("implementation_artifact_digest")
        errors = qualification.validate_qualification_policy(missing_base)
        self.assertTrue(any("base qualification requirements" in error for error in errors))

        missing_slot = copy.deepcopy(self.policy)
        execution = next(
            entry
            for entry in missing_slot["slot_requirements"]
            if entry["slot"] == "execution"
        )
        execution["requirements"].remove("fixed_fixture_evaluation_receipt")
        errors = qualification.validate_qualification_policy(missing_slot)
        self.assertTrue(any("execution qualification requirements" in error for error in errors))

    def test_policy_rejects_duplicate_or_reordered_requirements(self) -> None:
        reordered = copy.deepcopy(self.policy)
        reordered["base_requirements"].reverse()
        errors = qualification.validate_qualification_policy(reordered)
        self.assertTrue(any("must be sorted" in error for error in errors))

        duplicate = copy.deepcopy(self.policy)
        source = duplicate["slot_requirements"][0]["requirements"]
        source.append("contract_conformance_receipt")
        source.sort()
        errors = qualification.validate_qualification_policy(duplicate)
        self.assertTrue(any("globally unique" in error for error in errors))

    def test_stale_plan_is_rejected_after_bundle_or_policy_change(self) -> None:
        cron_factory = composer.load_json_file(
            validator.ROOT / "examples" / "economic-factory-cron.json"
        )
        cron_bundle, _ = bundler.build_factory_bundle(
            cron_factory,
            self.catalog,
            self.artifacts,
        )
        errors = qualification.verify_qualification_plan_for_bundle(
            self.recorded,
            cron_bundle,
            self.policy,
        )
        self.assertTrue(any("does not exactly match" in error for error in errors))

        stronger = copy.deepcopy(self.policy)
        stronger["base_requirements"].append("additional_runtime_receipt")
        stronger["base_requirements"].sort()
        self.assertEqual([], qualification.validate_qualification_policy(stronger))
        errors = qualification.verify_qualification_plan_for_bundle(
            self.recorded,
            self.bundle,
            stronger,
        )
        self.assertTrue(any("does not exactly match" in error for error in errors))

    def test_plan_authority_inflation_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.recorded)
        mutated["qualification_boundary"]["activation_authorized"] = True
        errors = qualification.verify_qualification_plan_for_bundle(
            mutated,
            self.bundle,
            self.policy,
        )
        self.assertTrue(any("non-authorizing boundary" in error for error in errors))

        type_confused = copy.deepcopy(self.recorded)
        type_confused["qualification_boundary"]["activation_authorized"] = 0
        errors = qualification.verify_qualification_plan_for_bundle(
            type_confused,
            self.bundle,
            self.policy,
        )
        self.assertTrue(any("non-authorizing boundary" in error for error in errors))

        numeric_position = copy.deepcopy(self.recorded)
        numeric_position["modules"][1]["position"] = True
        errors = qualification.verify_qualification_plan_for_bundle(
            numeric_position,
            self.bundle,
            self.policy,
        )
        self.assertTrue(any("does not exactly match" in error for error in errors))

    def test_qualification_rejects_tampered_bundle_before_plan(self) -> None:
        tampered = self.bundle.replace(b"Git lineage", b"Git lineagf", 1)
        errors, plan = qualification.qualification_plan_for_bundle(
            tampered,
            self.policy,
        )
        self.assertTrue(any(error.startswith("factory bundle:") for error in errors))
        self.assertIsNone(plan)

    def test_malformed_qualification_inputs_fail_cleanly(self) -> None:
        for malformed in (None, [], {}, {"slot_requirements": [None]}):
            with self.subTest(malformed=malformed):
                errors, plan = qualification.qualification_plan_for_bundle(
                    self.bundle,
                    malformed,
                )
                self.assertTrue(errors)
                self.assertIsNone(plan)
        errors = qualification.validate_qualification_plan(
            {"qualification_boundary": []},
            [],
            self.policy,
        )
        self.assertTrue(errors)

    def test_cli_qualification_plan_round_trip_and_overwrite_refusal(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            bundle_path = root / "factory.tar"
            output = root / "qualification-plan.json"
            bundle_path.write_bytes(self.bundle)
            cli = [sys.executable, str(validator.ROOT / "scripts" / "zaibatsu.py")]
            command = cli + [
                "qualification-plan",
                str(bundle_path),
                "--output",
                str(output),
            ]
            generated = subprocess.run(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(0, generated.returncode, generated.stderr)
            self.assertEqual(self.recorded, json.loads(output.read_text(encoding="utf-8")))
            verified = subprocess.run(
                cli
                + [
                    "verify-qualification-plan",
                    str(output),
                    str(bundle_path),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(0, verified.returncode, verified.stderr)
            self.assertIn("runtime eligible: false", verified.stdout)
            repeated = subprocess.run(
                command,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            self.assertEqual(2, repeated.returncode)
            self.assertIn("refusing to overwrite", repeated.stderr)


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
