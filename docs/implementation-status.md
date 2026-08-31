# Implementation status

Status date: **2026-08-30**

This ledger distinguishes the Zaibatsu meta-factory vision from deployed
runtime. Maturity is enforced by
[`architecture/factory-model.json`](../architecture/factory-model.json) and
[`architecture/system.json`](../architecture/system.json).

## Meta-factory capabilities

| Capability | Status | Evidence strength | Exact claim |
| --- | --- | --- | --- |
| Closed factory registry | Operational | Current control policy and worker/coordinator receipts | Orchestrator, SimbaPool, and FFN are the only factory identities; unknown factories fail closed |
| Git version control | Operational at reviewed scope | Reviewed source, diffs, immutable public releases | Source and intended state are versioned; complete canonical consolidation of every private product repository is not claimed |
| SOPS/age secret versioning | Validated preproduction | Ciphertext and recipient-policy checks passed privately | Static bootstrap material can remain encrypted in Git; universal factory adoption is not claimed |
| Bounded runtime machine secrets | Validated preproduction in this public ledger | Destination-scope, authorization, file-mode, and denial receipts | Runtime delivery excludes personal-vault sessions and cross-factory authority |
| Ansible host reproduction | Validated preproduction | Syntax, policy, apply, idempotence, service, and guard evidence | Reviewed host configuration has been exercised without making all factories disposable |
| Nix environment reproduction | Planned | Tool-boundary design only | No accepted flake, lock, or cross-node reproduction proof exists |
| systemd scheduling | Operational | Effective service/timer and authority evidence | Systemd is the primary durable scheduler for managed workloads |
| cron scheduling | Operational at selected downstream scope | Current scheduler inventory and workload authority register | Some downstream workloads still use cron; exactly one scheduler must own each workload |
| Modular agent skeletons | Validated preproduction source | 309 tests over a source-only scaffold with 21 modules, 6 flows, and 12 profiles | Reusable typed contracts exist; no scaffold runtime or production authority is deployed |
| LLM harness adapters | Validated preproduction at bounded scope | Model-independent source contracts plus reviewed Factory/Qwen contribution | Models can sit behind typed ports; general unattended multi-harness routing is not active |
| Deterministic output gates | Validated preproduction | Schemas, linters, tests, hashes, policies, receipts, adversarial mutations, and owner gates | Probabilistic output cannot declare itself verified or authorize an effect |
| Factory evidence return | Operational at bounded scope | Durable failures, artifacts, audit events, memory routing, and retained receipts | Factories can return evidence to the control layer |
| Recursive shared improvement | Proposal intake operational at bounded public-kit scope; broader loop designed | Evidence-bound proposal contract plus lifecycle and promotion contract | Exact untrusted proposals can be recorded against verified returned evidence; automatic normalization, classification, validation, promotion, and cross-factory rollout are not deployed |

The sanitized meta-factory evidence is
[`evidence/meta-factory-foundations-v1.json`](../evidence/meta-factory-foundations-v1.json).
It binds current private-source observations while explicitly recording what is
not publicly reproducible or deployed.

## Public toolkit

| Capability | Status | Evidence strength | Exact claim |
| --- | --- | --- | --- |
| Portable factory definition | Operational in the public kit | Project-owned schema, example, CLI, and adversarial tests | A user can scaffold and validate a control or economic factory definition offline; this does not deploy that factory |
| Reusable module catalog and artifacts | Operational in the public kit | Versioned catalog, ten independently hashed contract artifacts, schemas, alternate-artifact substitution, and compatibility/dependency/drift tests | A factory can replace an implementation ID only when the selected artifact preserves the declared slot policy and exact content digest; artifacts contain contracts rather than executable runtimes |
| Deterministic control-plan composition | Operational in the public kit | Canonical input digests, exact plan verification, byte-stable rebuild check, and drift/tamper tests | The same definition and catalog reproduce the same control plan independent of checkout path; infrastructure deployment and runtime recovery are explicitly not proved |
| Portable control bundle | Operational in the public kit | Canonical USTAR builder, in-memory verifier, stable inspection/comparison, public systemd/cron variants, per-file manifest, five bundled schemas, and archive/path/link/metadata/tamper adversarial tests | The same selected control inputs reproduce the same self-contained contract bundle; verified comparisons expose exact module changes, while no runtime implementation, environment realization, deployment, or recovery is included |
| Closed factory portfolio plan | Operational in the public kit | Three fully verified bundles, one schema-bound registry, exact plan reproduction, generated factory-scoped intended namespaces, evidence-only routes, and identity/class/order/replay/type/authority adversarial tests | One control factory and two economic factories compile into a deterministic multi-factory view. The plan proves bundle identity and declarative namespace separation only; it does not prove runtime isolation, route evidence, deployment, activation, execution, or cross-factory authority |
| Annotated-release control-source lock | Operational in the public kit | Exact annotated tag/commit/tree/blob derivation, native Git object IDs plus object-content SHA-256, byte-identical bundle rebuild, and moved-tag/lightweight-tag/worktree/replacement/replay/path/authority adversarial tests | Sixteen immutable local Git objects reproduce the selected control bundle; remote ownership, tag signatures, runtime implementation source, qualification, eligibility, activation, and deployment are not proved |
| Runtime-qualification planning | Operational in the public kit | Versioned minimum policy, two project-owned schemas, content-addressed systemd example, exact rebuild verification, and policy-weakening/staleness/authority adversarial tests | A verified bundle deterministically expands into 67 missing evidence bindings across 27 requirement types; zero modules become eligible, the plan contains no evidence, and qualification grants no activation authority |
| Bundle-derived qualification evidence | Operational in the public kit | Nine receipt digests, two project-owned schemas, exact evidence/assessment rebuilds, and forgery/replay/scope/authority adversarial tests | Complete bundle verification satisfies only the contract-conformance binding for each module: 9 of 67 bindings verified, 58 missing, no external independent verifier claimed, and zero runtime eligibility or activation |
| Signed runtime-evidence ingestion | Operational in the public kit | OpenSSH Ed25519 verification, content-addressed key registry and allowlists, exact provenance/freshness assessment, three project-owned schemas, checked fixture, generated-key positive path, and tamper/key/identity/namespace/replay/allowlist/staleness/type/malformed adversarial tests | The checked fixture authenticates one `source_revision` assertion only in `public_test_fixture` scope: 10 of 67 bindings verified, 57 missing, zero eligible modules. A signature authenticates an assertion but does not prove key ownership, independence, verifier correctness, or artifact truth; registry selection remains an explicit evaluator trust decision |
| Canonical runtime-evidence pack | Operational in the public kit | Reproducible USTAR, exact manifest and schema digest, embedded signed set/registry/artifacts/verifier descriptors, 256-receipt capacity, and archive/schema/material/replay/type/size adversarial tests | Verification proves the exact referenced bytes were retrieved intact and rechecks their signatures and bindings. It does not rerun verifier assertions, prove artifact truth, key ownership, or independence, or grant eligibility, activation, execution, or side-effect authority |
| Route-bound factory evidence return | Operational in the public kit | Exact portfolio/route/source-bundle/pack binding, full input re-verification, project-owned schema, bounded fast-fail parsing, and replay/forgery/type/size/authority adversarial tests | One verified pack is deterministically bound to the product factory's declared evidence-only route. No transport, content-safety or secret scan, semantic classification, promotion eligibility, policy change, activation, execution, or cross-factory effect is proved or authorized |
| Evidence-bound improvement proposal | Operational in the public kit | Two project-owned schemas, exact evidence-return re-verification, canonical proposal digest, mandatory later review gates, and replay/forgery/type/size/authority adversarial tests | One untrusted shared-module, factory-template, or deterministic-gate suggestion is bound to exact returned evidence. The proposer is not authenticated and no content safety, normalization, classification, merit, regression, rollback, approval, promotion, rollout, activation, execution, or cross-factory effect is proved or authorized |
| Deterministic factory rebuild DAG | Operational in the public kit | Fully reverified bundle/source/qualification/runtime-pack inputs, exact nine-action and four-gate rebuild, project-owned schema, and reorder/dependency/replay/shallow-history/type/authority adversarial tests | The checked graph records 0 of 9 actions qualification-ready and all 9 blocked. Generated-key tests prove a complete fresh `factory_runtime` evidence set can make exactly one module `qualified_not_authorized`, while execution, side effects, owner approval, activation, deployment, and recovery remain denied |
| Evidence receipt validation | Operational in the public kit | Four typed receipt classes plus malformed, contradictory, count, digest, scope, and limitation tests | Receipt files must contain enforceable evidence fields; their sanitized private observations are not independently reproduced by the public validator |
| Submission readiness validation | Operational in the public kit | Typed completion proof, exact dependency graph, and adversarial tests | Non-empty prose alone cannot complete a gate; final demo and applicant materials remain external |
| Public-safety scan | Operational in the public kit | Git-aware enumeration and adversarial path/content tests | Tracked and non-ignored public files are text-scanned; opaque files, symlinks, and Git submodules fail closed |

## Control-plane components

| Capability | Status | Evidence strength | Exact claim |
| --- | --- | --- | --- |
| Current systemd workload executor | Operational | Runtime and checked-in unit evidence | Existing managed schedules retain a declared owner until controlled migration |
| Private Tailscale administration | Operational | Connection, firewall, and identity checks recorded privately | Management remains outside the public application boundary |
| OpenTofu lifecycle controls | Validated preproduction | Offline validation and saved-plan policy tests | Apply remains owner-gated and CI has no apply authority |
| Provenance-aware knowledge retrieval | Operational | Local retrieval tests and receipts | Agents receive small routed context packets; prose is not task state |
| Dispatcher API and policy engine | Validated preproduction | 158 focused tests with sanitized private-source receipt | The broader side-effecting contract is implemented without general production authority |
| PostgreSQL jobs and leases | Validated preproduction | 104 assertions on two disposable PostgreSQL 16.15 clusters | State, lease, audit, replay, backup/restore, and continuation contracts are exercised privately |
| Bounded read-only coordinator | Operational | Live durable state, fixed time buckets, three eligible factory workers, retained failures, receipts | A narrow collect-only lane runs without a model; it does not authorize broader migration |
| Project/job sandboxes | Planned | Isolation requirements only | No environment is called a sandbox until identity, network, credential, lifecycle, and recovery boundaries pass |
| Probabilistic worker runtime | Designed | Contracts and source scaffold | General-purpose model workers are not activated in production |
| Artifact verification | Validated preproduction | Tests, schema/hash gates, and private acceptance evidence | Verified source contracts exist; the broad side-effecting runtime is not deployed |
| Factory Droid contribution | Validated preproduction | Authenticated local-Qwen session, reviewed diff, pre-change adversarial proof, independent validation | Droid strengthened the public task-flow contract and received no production authority |

Dispatcher and PostgreSQL results are bounded by
[`evidence/dispatcher-validation-v1.json`](../evidence/dispatcher-validation-v1.json).
The private implementation itself is not publicly reproducible.

## Current authority

- The always-on control host and downstream factories use conventional cron or
  systemd owners for current production workloads.
- PostgreSQL and the deterministic coordinator own one bounded read-only
  workflow family.
- Modular agent definitions, harness-independent implementations, and effect
  contracts remain source-only until qualification, isolated runtimes,
  independent alerts, recovery, and an observe-only canary pass.
- Migration readiness is separate from migration authorization.

## Deliberately unclaimed

- autonomous meta-factory self-improvement;
- automatic rollout of a shared pattern to economic factories;
- unattended model or harness routing;
- deployed modular agent profiles;
- completed runtime qualification of any public bundle module;
- execution of any action named by the public factory rebuild plan;
- deployed enforcement of namespaces named by the public factory portfolio
  plan;
- observed delivery, classification, or promotion of the public route-bound
  evidence-return record;
- authentication, classification, validation, or promotion of the public
  evidence-bound improvement proposal;
- direct model publication, deployment, commit, database apply, or secret use;
- Nix-based worker reconstruction;
- completed project/job sandboxes or separate sandbox hosts;
- general production execution through Dispatcher;
- complete private repository consolidation;
- a complete production cutover.

## Promotion rule

A capability moves to a stronger status only when evidence covers its complete
scope. Source tests cannot prove deployment, a running process cannot prove
recovery, one model contribution cannot prove general harness routing, and one
factory's success cannot authorize promotion into another factory.
