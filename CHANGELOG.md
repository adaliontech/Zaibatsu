# Changelog

## 1.17.0 - 2026-08-31

- Added a canonical improvement-validation input pack that carries every exact
  input needed to independently reverify the v1.16 validation plan: its full
  proposal-to-candidate chain, portfolio and qualification contracts, nested
  runtime-evidence pack, and three verified factory bundles.
- Added a strict, digest-pinned Draft 2020-12 manifest schema. The checked
  example is a byte-reproducible 296,960-byte USTAR with 21 members and exact
  path, role, media type, size, digest, factory-order, and validation-summary
  bindings.
- Added self-contained pack verification that requires no network or external
  input files, recursively reverifies both nested archive classes, rebuilds the
  manifest, and requires byte-identical canonical archive reconstruction.
- Kept the boundary deliberately narrow: the pack contains portable inputs,
  not a validation executor, verifier runtime, candidate implementation, stage
  evidence, or authority. Verification requires no live production credential
  or state, but does not content-scan arbitrary embedded evidence or prove
  secret absence. All stages remain `not_run`, all twelve evidence items remain
  `missing`, and validation, approval, promotion, rollout, activation,
  execution, and cross-factory authority remain false.
- Added `improvement-validation-pack` and
  `verify-improvement-validation-pack` plus archive, nested-payload, schema,
  replay, authority, malformed-input, bounds, ordering, deterministic rebuild,
  and safe-I/O tests. The integrated suite now contains 260 tests and the
  validator requires 128 files.

## 1.16.0 - 2026-08-30

- Added a schema-bound improvement-validation-plan specification and exact
  deterministic plan record that consume the bound candidate only after
  reverifying its complete classification, proposal, observation,
  evidence-return, portfolio, bundle, qualification, runtime-pack, and source
  chain.
- Enumerated eight fixed validation stages and twelve required evidence
  artifacts without running commands, reading production credentials or
  state, using the network, or treating model output as verification.
- Kept the boundary deliberately narrow: every stage is `not_run`, every
  evidence item is `missing`, executed/passed/failed counts are zero, no
  candidate implementation exists, and readiness, execution authorization,
  approval, promotion, rollout, activation, and cross-factory effects remain
  false.
- Added `plan-improvement-validation` and
  `verify-improvement-validation-plan`, two strict Draft 2020-12 schemas,
  checked examples, complete repository re-verification, and fail-closed CLI
  input bounds.
- Added stage/order/requirement weakening, candidate-chain replay,
  authority-forgery, scalar, malformed, recursive, size, bundle-order, and CLI
  round-trip tests. The integrated suite now contains 252 tests and the
  validator requires 125 files.

## 1.15.0 - 2026-08-30

- Added a schema-bound improvement-candidate specification that embeds one
  exact canonical shared-module, factory-template, or deterministic-gate
  contract and preserves every later safety, semantic, regression, rollback,
  approval, and privilege-review requirement.
- Added an evidence-bound candidate record that fully reverifies the
  classification, proposal, observation, evidence-return, portfolio, bundle,
  qualification, evidence-pack, signature, allowlist, and material chain before
  requiring exact classified-target alignment and recording the candidate
  artifact digest and canonical byte count.
- Kept the boundary deliberately narrow: the checked 1,130-byte gate artifact
  is an explicitly untrusted, non-executable contract. Content safety, secret
  absence, semantic correctness, an implementation, validation planning or
  execution, regressions, rollback, approval, promotion, rollout, activation,
  execution, and cross-factory effects remain false.
- Added `bind-improvement-candidate` and `verify-improvement-candidate`, two
  strict Draft 2020-12 schemas, checked examples, complete repository
  re-verification, and fail-closed CLI input bounds.
- Added requirement-weakening, authority-inflation, target-mismatch,
  noneligible-classification, replay, refreshed-digest forgery, scalar,
  malformed, recursive, size, order, and CLI round-trip tests. The integrated
  suite now contains 247 tests and the validator requires 120 files.

## 1.14.0 - 2026-08-30

- Added a schema-bound untrusted improvement-observation specification and
  evidence-bound record for observations, failures, artifact outcomes, and
  corrections. The complete evidence-return chain is reverified before the
  canonical category, subject, narrative, and digest are recorded.
- Defined structural normalization narrowly: exact form and provenance are
  proved, while reporter identity, content safety, secret absence, source or
  report semantic truth, merit, promotion, execution, and cross-factory effects
  remain false.
- Added a separately hashed deterministic classification policy and exact
  classification record. Fixed-order checks join the complete proposal and
  observation chains, require source and subject alignment, preserve later
  review gates, and map valid targets to canonical candidate classes.
- Made classification scope explicit: a positive result is eligible only for
  validation planning. No validation plan is created; validation execution,
  mutation, approval, promotion, rollout, activation, execution, and
  cross-factory effects remain false. Valid policy or target mismatches produce
  deterministic `not_classified` records; forged inputs fail verification.
- Added `improvement-observation-record`,
  `verify-improvement-observation-record`, `classify-improvement-proposal`, and
  `verify-improvement-classification` CLI workflows plus four strict Draft
  2020-12 schemas and checked examples.
- Added gate-weakening, noncanonical policy, type-confusion, evidence-replay,
  target-mismatch, restrictive-policy, digest-refresh authority forgery,
  recursive, size, input-order, and CLI round-trip tests. The integrated suite
  now contains 241 tests and the validator requires 115 files.

## 1.13.0 - 2026-08-30

- Added a schema-bound, untrusted factory improvement-proposal specification
  for shared modules, factory templates, and deterministic gates. Every
  specification requires content-safety, classification, reporting-factory,
  independent-regression, owner-policy, rollback, and cross-factory-privilege
  review gates.
- Added a deterministic proposal record that fully reverifies the route-bound
  evidence return and its complete portfolio, bundle, qualification,
  evidence-pack, material, signature, and allowlist chain before binding the
  exact canonical proposal content to it.
- Added `improvement-proposal-record` and
  `verify-improvement-proposal-record` CLI workflows. The checked fixture
  records one proposal for control-layer review without authenticating its
  proposer or interpreting its narrative.
- Made the review boundary explicit: proposal structure, canonical content,
  source evidence, and route bindings are verified; content safety, secret
  absence, semantic truth, observation normalization, classification, merit,
  regression results, rollback, approval, eligibility, rollout, activation,
  execution, and cross-factory effects remain false.
- Added weakened-gate, unsupported-target, replay, digest-refresh forgery,
  scalar-confusion, malformed, recursive, size, input-order, and CLI boundary
  tests. The integrated suite now contains 230 tests and the validator requires
  105 files.

## 1.12.0 - 2026-08-30

- Added a schema-bound factory evidence-return record that binds one fully
  verified canonical runtime-evidence pack to the exact economic-factory
  bundle, closed portfolio plan, and declared evidence-only route that may
  return it to the control factory.
- Added `evidence-return-record` and `verify-evidence-return-record` CLI
  workflows. They fully reverify every supplied factory bundle, the portfolio
  plan, source route, qualification policy and plan, evidence-pack archive,
  embedded materials, signatures, allowlists, and content digests before
  accepting the exact derived record.
- Made the review boundary machine-readable: route and byte bindings are true,
  while transport observation, content-safety scanning, secret absence,
  verifier reexecution, artifact truth, classification, improvement-candidate
  status, shared-promotion eligibility, activation, execution, and
  cross-factory effects remain false.
- Added fast bounded record prechecks plus route/source/bundle/pack replay,
  digest-refresh forgery, authority-inflation, scalar-confusion, malformed,
  size, input-order, and CLI overwrite tests. The integrated suite now
  contains 221 tests and the validator requires 100 files.

## 1.11.0 - 2026-08-30

- Added schema-bound factory-portfolio definitions and deterministic portfolio
  plans so Zaibatsu can join multiple verified factory bundles into one
  machine-verifiable factory-of-factories control view.
- Added `portfolio-plan` and `verify-portfolio-plan` CLI workflows. They fully
  verify every canonical bundle, match identity and class to an ordered closed
  registry, bind exact bundle/source/scheduler-module digests, and remain
  independent of bundle argument order.
- Added a public three-factory example with exactly one control factory, two
  economic factories, systemd and cron module choices, 21 disjoint intended
  namespaces, and one evidence-only return route per economic factory.
- Preserved the authority boundary: intended namespaces do not prove runtime
  isolation; the plan contains no runtime implementations, routes no secrets,
  invokes no model, executes no operation, grants no cross-factory authority,
  authorizes no activation, and proves no deployment or recovery.
- Added duplicate, missing, tampered, replacement, class-drift, route,
  namespace-collision, authority-inflation, scalar-confusion, malformed-input,
  input-order, and CLI overwrite tests. The integrated suite now contains 212
  tests and the validator requires 97 files.

## 1.10.0 - 2026-08-30

- Added a canonical, self-verifying runtime-evidence pack that embeds the
  signed evidence set, verifier registry, every content-addressed evidence
  artifact, every referenced verifier-implementation descriptor, and its
  immutable manifest schema.
- Added `evidence-pack` and `verify-evidence-pack` CLI workflows. Pack
  verification rechecks archive safety and byte reproducibility, JSON
  canonicalization, schema identity and digest, exact member inventory,
  material digests, registry rules, and every OpenSSH signature.
- Upgraded runtime assessments to v2 and rebuild plans to v3. Both now bind and
  reverify the exact pack rather than accepting detached evidence and registry
  inputs; rebuild planning retrieves the signed materials before compiling its
  still-inert nine-action DAG.
- Preserved the trust boundary: embedded bytes and digests are verified, but
  verifier assertions are not reexecuted, artifact semantic truth is not
  inferred, key ownership and independence are not proved, and a pack alone
  grants no runtime eligibility, activation, execution, or side-effect
  authority.
- Extracted the bounded canonical archive reader for bundle and evidence-pack
  verification, made builders reject archives their verifiers would reject,
  and covered the full 256-receipt/516-member contract ceiling.
- Added traversal, link, special-file, duplicate, extra-member, metadata,
  trailing-byte, noncanonical-JSON, schema/material tamper, replay, size,
  authority-inflation, scalar-confusion, malformed-input, and CLI tests. The
  integrated suite now contains 203 tests and the validator requires 90 files.

## 1.9.0 - 2026-08-30

- Added OpenSSH Ed25519 verification for externally supplied runtime-evidence
  assertions. Every payload binds the exact factory, bundle, qualification
  policy and plan, verifier registry, module artifact, requirement, scope,
  evidence-artifact digest, verifier method and implementation, validity
  interval, and false activation/execution authority.
- Added a content-addressed verifier public-key registry with exact
  factory/scope/requirement/method allowlists and maximum validity intervals,
  plus `verify-runtime-evidence`, `runtime-assessment`, and
  `verify-runtime-assessment` CLI workflows.
- Added a fixture-only signed public receipt and combined runtime assessment.
  The signature verifies, but `public_test_fixture` scope can never grant
  runtime eligibility: the checked state is 10 of 67 bindings verified, 57
  missing, zero eligible modules, and zero activation or execution authority.
- Upgraded the deterministic rebuild DAG to bind and reverify the registry,
  signed evidence, explicit assessment time, and combined evidence state. The
  checked graph remains fully inert with all nine actions blocked.
- Added generated-key positive-path coverage proving that complete, fresh
  `factory_runtime` evidence can move one module to
  `qualified_not_authorized` while every execution, side-effect, approval, and
  activation boundary remains denied.
- Added tamper, wrong-key, identity, algorithm, namespace, allowlist, replay,
  freshness, duplicate, reorder, type-confusion, malformed-input, missing-tool,
  strict-schema, and fuzz coverage. The integrated public suite now contains
  194 tests and the validator requires 87 files.
- Documented that a signature authenticates an assertion rather than its
  semantic truth: registry selection is an evaluator trust decision, key
  ownership and independence are not inferred, verifier assertions are not
  rerun, and evidence artifacts are not retrieved in this release.

## 1.8.0 - 2026-08-30

- Added a deterministic, content-addressed factory rebuild plan that turns the
  verified control bundle, annotated-release source lock, qualification policy,
  evidence, and assessment into a nine-action dependency graph with four
  explicit gates.
- Added `rebuild-plan` and `verify-rebuild-plan` CLI workflows. Both fully
  reverify every input before emitting or accepting a plan, bind the exact
  input digests and module DAG, and reject replay, reorder, dependency, intent,
  status, gate, and authority forgery.
- Kept the rebuild plan deliberately inert: it runs no Ansible or Nix, reads no
  secrets, installs no scheduler, invokes no model, grants no qualification or
  owner approval, activates nothing, deploys nothing, and proves no runtime
  recovery.
- Recorded the public example's honest state: 9 contract-conformance receipts,
  58 missing runtime-evidence bindings, zero qualification-ready actions, and
  all nine actions blocked before owner and activation gates.
- Added a project-owned Draft 2020-12 schema plus boolean/integer-confusion,
  replay, shallow-history, malformed-input, and CLI adversarial coverage.
- Hardened shared CLI and bundle JSON parsing so recursion-depth attacks fail
  with a validation error instead of escaping as an unhandled exception.
- Expanded the public adversarial suite from 173 to 183 tests.

## 1.7.0 - 2026-08-30

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
