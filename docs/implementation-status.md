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
| Recursive shared improvement | Designed | Lifecycle and promotion contract | Automatic classification and cross-factory promotion are not deployed; improvement remains reviewed and owner-gated |

The sanitized meta-factory evidence is
[`evidence/meta-factory-foundations-v1.json`](../evidence/meta-factory-foundations-v1.json).
It binds current private-source observations while explicitly recording what is
not publicly reproducible or deployed.

## Public toolkit

| Capability | Status | Evidence strength | Exact claim |
| --- | --- | --- | --- |
| Portable factory definition | Operational in the public kit | Project-owned schema, example, CLI, and adversarial tests | A user can scaffold and validate a control or economic factory definition offline; this does not deploy that factory |
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
