# Changelog

## 1.7.0 - Unreleased

- Added deterministic `source-lock` and `verify-source-lock` workflows that
  rebuild a verified control bundle entirely from an annotated release's Git
  objects rather than the working tree.
- Bound the factory definition, module catalog, nine selected module contracts,
  and five bundled schemas to exact release tag, commit, tree, blob, raw-file,
  canonical-JSON, and bundle identities.
- Added SHA-256 digests for annotated-tag, commit, and tree object content in
  addition to the repository's native Git object IDs, and disabled Git
  replacement-object substitution and repository-redirection environment
  overrides during verification.
- Denied lightweight or moved tags, forged/reordered/duplicate inputs, bundle
  replay, unsafe paths, credential-bearing repository URLs, overwrite races,
  scalar type confusion, and authority inflation.
- Kept the source lock outside runtime qualification: it contains control
  sources only and grants no implementation evidence, eligibility, activation,
  deployment, repository-ownership, remote-contact, or signature claim.
- Expanded the public adversarial suite from 163 to 173 tests.

## 1.6.0 - 2026-08-30

- Added deterministic bundle-derived contract-conformance receipts for every
  selected module in a fully verified factory bundle.
- Added `qualification-evidence`, `verify-qualification-evidence`,
  `qualification-assessment`, and `verify-qualification-assessment` workflows.
- Published a partial public assessment that verifies 9 of 67 evidence
  bindings, leaves 58 missing, and marks zero of nine modules runtime-eligible.
- Bound every receipt, evidence set, and assessment by canonical SHA-256 to the
  exact bundle, plan, policy, module identity, and artifact digest.
- Denied forged/replayed/duplicate evidence, false independent-verifier scope,
  eligibility inflation, activation authority, and scalar type confusion.
- Expanded the public adversarial suite from 153 to 163 tests.

## 1.5.0 - 2026-08-30

- Added a versioned runtime-qualification policy with mandatory base and
  slot-specific evidence requirements for every selected factory module.
- Added deterministic `qualification-plan` and `verify-qualification-plan`
  workflows. Plans bind a fully verified bundle and policy by SHA-256.
- Published a systemd example plan with 67 missing evidence bindings across 27
  requirement types and zero of nine modules marked runtime-eligible.
- Denied self-attestation, missing-evidence success, runtime eligibility,
  activation authority, and owner-approval bypass at both schema and semantic
  validation layers.
- Expanded the public adversarial suite from 143 to 153 tests.

## 1.4.0 - 2026-08-30

- Added stable `inspect-bundle` output for verified bundle identity, source
  digests, selected modules, rebuild claims, and explicit runtime ineligibility.
- Added `compare-bundles` semantic comparison for factory, input, module, and
  schema changes. Both inputs must pass full canonical bundle verification.
- Added a public cron-scheduled variant of the example factory. Comparing it
  with the systemd variant reports one scheduling implementation replacement,
  an unchanged catalog and schemas, and the preserved no-runtime boundary.
- Bounded bundle reads before allocation and rejected symlink, non-regular,
  changing, empty, or oversized CLI inputs.
- Made CLI output creation OS-exclusive so existing paths cannot be overwritten
  through a check-then-open race.
- Expanded the public adversarial suite from 136 to 143 tests.

## 1.3.0 - 2026-08-30

- Added individually content-addressed module contract artifacts for every
  catalog implementation. Catalog validation denies missing, drifting,
  symlinked, escaping, or digest-mismatched artifacts.
- Added deterministic `bundle` and `verify-bundle` CLI workflows. The canonical
  USTAR bundle contains the factory definition, catalog, resolved plan, all
  selected module contracts, and the five contract schemas.
- Made the bundle self-verifying without extraction: unsafe paths, links,
  special files, duplicate or extra members, noncanonical metadata or JSON,
  malformed archives, payload/schema tampering, schema-body substitution even
  after manifest recomputation, and trailing data fail closed.
- Proved a differently named, independently hashed compatible module artifact
  can replace a bundled implementation and still produce a verified bundle.
- Preserved the evidence boundary: bundles contain no runtime implementation,
  entrypoint, environment lock, infrastructure deployment, or recovery proof.
- Expanded the public adversarial suite from 114 to 136 tests.

## 1.2.0 - 2026-08-30

- Added a versioned reusable module catalog and policy-compatible module
  bindings for Git, SOPS/age, bounded runtime secrets, Ansible, Nix,
  cron/systemd, typed worker execution, deterministic verification, and
  owner-gated feedback.
- Added deterministic `plan`, `verify-plan`, and `rebuild-check` CLI commands.
  Plans bind the canonical factory definition and catalog digests, resolve
  modules in dependency order, and explicitly prove only byte-reproducible
  control-plan composition—not infrastructure deployment or runtime recovery.
- Rejected duplicate JSON keys, non-standard JSON numbers, ambiguous fields,
  module-policy mismatch, forward dependencies, duplicate outputs, stale input
  plans, and digest tampering.
- Expanded the public adversarial suite from 95 to 114 tests.

## 1.1.2 - 2026-08-30

- Changed portable factory definitions from a repository-relative schema path
  to the immutable v1.1.2 schema URI. Definitions scaffolded into another
  directory now resolve correctly in standard JSON Schema tooling, while the
  offline Zaibatsu validator maps the canonical URI to its bundled copy.

## 1.1.1 - 2026-08-30

- Added a portable factory-definition contract, project-owned JSON Schemas,
  reusable economic-factory example, and `zaibatsu scaffold` / `validate` CLI
  so adopters can apply the control model outside Zaibatsu's own registry.
- Made all four sanitized evidence receipts executable contracts: empty,
  malformed, contradictory, zero-count, unbounded, or digest-invalid receipts
  now fail validation.
- Replaced prose-only completion with typed submission-gate proof and fixed
  malformed or missing gate status handling to fail cleanly.
- Closed ignored-directory, force-added local-settings, misleading media-suffix,
  invalid-UTF-8, and Git-submodule public-scan gaps. Opaque files now fail
  closed because their contents cannot be inspected.
- Expanded the public adversarial suite from 70 to 95 tests and tightened the
  Guild, demo, security, and maturity wording around what is reusable today
  versus validated privately, source-only, designed, or planned.

## 1.1.0 - 2026-08-29

- Reframed Zaibatsu around its intended role as the factory of software
  factories: a meta-factory control layer above project-scoped economic
  factories.
- Added `architecture/factory-model.json` with the closed factory registry,
  complete lifecycle, capability maturities, reproducibility, versioning,
  scheduler, modular-agent, harness, deterministic-gate, and feedback policy.
- Added adversarial enforcement for meta-factory role drift, factory
  reclassification, premature promotion, false Nix maturity, plaintext Git
  secrets, model effect authority, factory self-promotion, and cross-contract
  maturity drift.
- Made Git/SOPS, Ansible/Nix, cron/systemd, bounded runtime secrets, modular
  skeletons, LLM harness adapters, and recursive improvement first-class while
  preserving their actual operational, validated, designed, or planned scope.
- Added a sanitized foundations receipt binding a fresh private SOPS/Ansible
  policy pass and a 309-test source-only modular-agent scaffold with 21 modules,
  6 flows, and 12 deployment profiles.
- Rewrote the README, architecture, case study, implementation ledger, threat
  model, reproduction guide, roadmap, application, and demo around the same
  meta-factory hierarchy.
- Expanded the public adversarial suite from 59 to 70 tests, including malformed
  meta-factory input handling.
- Tightened the local-model receipt so a server filename is recorded only as an
  observed label, not verified model identity or parameter count.

## 1.0.1 - 2026-08-29

- Closed the documentation-host placeholder substring bypass and added
  adversarial coverage for embedded and subdomain forms.
- Expanded public-safety validation to every repository file, global and
  private IPv6, common client-secret and inline bearer forms, environment
  example files, unapproved binary content, and all repository symlinks.
- Required the exact `ZAIBATSU_QWEN_API_KEY` reference and safe metadata for
  ignored local Droid settings.
- Added checksum-pinned Gitleaks history and tree scans to CI, using a full
  checkout so removed secrets cannot disappear from the validation boundary.
- Added sanitized Dispatcher, Droid-contribution, and Qwen-observation receipts
  with explicit public-reproducibility and model-identity limitations.
- Added the operational bounded read-only coordinator as a distinct
  machine-readable component while preserving the broader Dispatcher and
  PostgreSQL contracts at validated preproduction.
- Expanded the integrated adversarial suite from 46 to 59 tests.

## 1.0.0 - 2026-08-29

- Created the Zaibatsu public architecture and Guild submission package.
- Added a machine-readable component, maturity, task-flow, and invariant model.
- Added an offline validator and adversarial unit tests.
- Added architecture, implementation-status, threat-model, reproducibility,
  evidence, case-study, demo, Droid-session, Guild, and roadmap documents.
- Added a secret-free local-Qwen Droid configuration example, fail-closed
  preflight, and machine-readable submission gates.
- Corrected the hosted model description from stale 3-bit wording to its
  authenticated `Q4_K - Small` llama.cpp metadata.
- Promoted the implemented Dispatcher API/policy and PostgreSQL state
  contracts to validated preproduction while documenting the narrow live
  read-only coordinator lane and preserving systemd workload authority.
- Hardened the public-safety validator for tailnet DNS names, Linux/macOS and
  Windows home paths, and public IPv4 addresses, with adversarial tests and a
  fixed documentation-placeholder allowlist.
- Added current 158-test Dispatcher and 104-assertion PostgreSQL 16.15
  acceptance evidence without publishing private coordinates.
- Corrected application and demo language so no completed Droid contribution
  is claimed before a real reviewed session exists.
- Hardened architecture and readiness validation against missing components,
  maturity inflation, optionalized gates, dependency bypasses, malformed data,
  and unscanned source files.
- Hardened local-model preflight against malformed or credential-bearing URLs,
  alternate inline credential fields, invalid model settings, and crash-only
  failures.
- Separated the Factory CLI API key from the local Qwen endpoint API key and
  made both explicit submission prerequisites.
- Connected authenticated Droid CLI `0.206.0` to the owner-operated Qwen model,
  recorded a native-tool canary, and accepted one reviewed two-file
  contribution after independent validation.
- Strengthened task-flow validation to require sandbox execution,
  verification, and policy decision in deterministic order before a controlled
  side effect; added the adversarial policy-before-verification test.
- Reconciled the static preflight with secure Factory CLI login receipts and
  authenticated tailnet-DNS model gateways without exposing credential values.
- Adopted Zaibatsu as the public submission brand and aligned the schemas,
  documentation, validator output, and local configuration example.
- Added a read-only, secret-free GitHub Actions gate for the offline validation
  suite and pinned the checkout action to its reviewed release commit.
