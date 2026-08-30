# Zaibatsu

[![Validate](https://github.com/adaliontech/Zaibatsu/actions/workflows/validate.yml/badge.svg)](https://github.com/adaliontech/Zaibatsu/actions/workflows/validate.yml)

**The factory of software factories.**

Zaibatsu is an evidence-gated architecture and toolkit for making software
factories reproducible: a control layer that defines, versions, coordinates,
observes, and improves multiple project-scoped factories. Each economic factory
produces software, data, research, content, or services for one business
boundary. Zaibatsu defines and governs the factories themselves.

The architecture combines conventional infrastructure and schedulers with
modular agent skeletons and interchangeable LLM harnesses. AI workers may
reason and build inside bounded tasks, but deterministic software owns durable
state, verification, policy, credentials, scheduling, and irreversible effects.

This repository is the public-safe executable architecture. It contains no
production inventory, private network coordinates, credentials, or deployment
access.

## The hierarchy

```text
Zaibatsu meta-factory
|
+-- control and factory registry
|   `-- Orchestrator control factory
|
+-- reproducible factory foundations
|   |-- Git + SOPS/age
|   |-- Ansible
|   `-- Nix after reproduction proof
|
+-- modular work and verification
|   |-- typed agent skeletons
|   |-- interchangeable LLM harnesses
|   `-- schemas, linters, tests, hashes, policy, receipts, owner gates
|
+-- economic software factories
    |-- FFN factory: fantasy data, tools, software, and publishing
    `-- SimbaPool factory: stake-pool operations, research, and publishing
```

An **economic factory** is a software factory attached to a business or product
boundary. It has its own identity, repositories, credentials, schedules, data,
agent profiles, acceptance rules, and production authority. The control factory
may coordinate it, but factories do not inherit one another's privileges.

## Factory lifecycle

Zaibatsu treats a factory as a versioned and improvable system, not merely a
directory containing prompts:

```text
define factory
  -> version in Git; encrypt static secrets with SOPS/age
  -> reproduce hosts with Ansible and environments with proven Nix definitions
  -> schedule through one declared cron or systemd owner
  -> execute bounded deterministic and probabilistic work
  -> verify artifacts with schemas, linters, tests, hashes, and policy
  -> authorize any external effect
  -> operate and observe the factory
  -> return evidence to Zaibatsu
  -> improve shared modules, templates, and gates
  -> promote only after review and deterministic acceptance
```

Feedback is recursive, but authority is not. A factory may report an incident
or propose a shared improvement; it cannot silently change its own policy or
promote that change into other factories.

## Control flow inside one factory

```text
intent / schedule / event
          |
          v
 deterministic Dispatcher
 jobs · policy · leases · audit
          |
          v
 modular bounded worker
 deterministic module or LLM harness
          |
          v
 deterministic verification
 schemas · linters · tests · hashes · policy
          |
          v
 controlled artifact / side effect
          |
          +---- evidence ----> Zaibatsu improvement input
```

Workers are replaceable. Jobs, evidence, factory definitions, and policy are
durable. An LLM response alone is never success and never authorization.

## Foundation and maturity

The target stack is intentionally boring at authority boundaries:

| Layer | Role | Current public claim |
| --- | --- | --- |
| Git | Version source, intended state, diffs, and releases | Operational at reviewed-source and public-release scope |
| SOPS/age | Keep static bootstrap material encrypted in Git | Validated preproduction |
| Bounded secret manager | Deliver runtime machine secrets without personal vault sessions | Validated preproduction in this public claim set |
| Ansible | Reproduce host configuration, identities, hardening, and services | Validated preproduction |
| Nix | Reproduce exact per-factory worker environments | Planned; no accepted flake or cross-node proof |
| systemd | Primary durable service and schedule owner | Operational |
| cron | Retained scheduler for selected downstream workloads | Operational with one scheduler of record per workload |
| PostgreSQL | Durable jobs, leases, attempts, policy, evidence, and audit | Validated preproduction broadly; a narrow read-only lane is operational |
| Modular agent skeletons | Reusable typed modules, flows, profiles, approvals, and effect fences | Implemented and tested source; not deployed |
| LLM harness adapters | Bind different models behind typed module contracts | Validated at bounded source/contribution scope; general unattended routing is not active |
| Recursive improvement | Return evidence and improve shared factory patterns | Evidence return is bounded and operational; shared automatic promotion remains designed and owner-gated |

The machine-readable source of this hierarchy is
[`architecture/factory-model.json`](architecture/factory-model.json). The
component-level control-plane contract remains in
[`architecture/system.json`](architecture/system.json).

## What is real today

As of 2026-08-30, the private program behind this public model has earned the
following bounded claims:

- Orchestrator, FFN, and SimbaPool are distinct factory identities with denied
  unknown-project routing.
- An always-on control host owns the managed production schedules through
  systemd; selected downstream cron schedules remain inventoried separately.
- Private administration, scoped machine-secret delivery, encrypted backups,
  and cross-host restore drills are active.
- PostgreSQL durable state and a deterministic read-only coordinator operate
  across the three registered factories without invoking a model.
- The broader Dispatcher API/policy and PostgreSQL contracts passed 158
  focused tests and 104 assertions on disposable PostgreSQL 16.15 clusters.
- The source-only modular agent scaffold passed 309 tests across 21 logical
  modules, 6 flows, and 12 deployment profiles. It is not installed or
  production-authorized.
- Factory Droid used an owner-operated local Qwen endpoint for one bounded
  public-repository contribution that was independently reviewed and tested.
- SOPS/age policy and Ansible-oriented operations contracts pass a private
  policy validator; Nix remains an explicit future boundary.

Sanitized scope and limitations are recorded in
[`evidence/meta-factory-foundations-v1.json`](evidence/meta-factory-foundations-v1.json).

## What is not claimed

Zaibatsu does not currently claim:

- deployed general-purpose modular agents;
- autonomous improvement or self-promotion;
- unattended multi-model routing;
- completed per-job or per-factory sandbox hosts;
- Nix-based worker reconstruction;
- general production execution through the PostgreSQL Dispatcher;
- direct model publication, deployment, secret use, or infrastructure control;
- completed consolidation of every private product repository.

Source, tests, and a deployment plan are evidence classes—not proof that a
capability is running. See [Implementation status](docs/implementation-status.md)
for the full claim ledger.

## Quickstart

The public validator uses only Python's standard library:

```bash
git clone https://github.com/adaliontech/Zaibatsu.git
cd Zaibatsu
make validate
```

`make validate` checks the project-owned schemas, architecture contracts,
portable factory example, evidence receipts, factory hierarchy and lifecycle,
maturity boundaries, submission gates, public-safety rules, local links, and
adversarial mutations. No model, network access, cloud account, secret, Nix
installation, or production system is required.

## Apply the contract to another factory

Create a safe starting definition and validate it with the same fail-closed
rules used by Zaibatsu:

```bash
python3 scripts/zaibatsu.py scaffold \
  --id example-product \
  --class economic_factory \
  --purpose "Produce a bounded software product" \
  --output examples/my-factory.json
python3 scripts/zaibatsu.py validate examples/my-factory.json
```

The scaffold starts at `planned`, denies plaintext Git secrets, requires one
cron or systemd scheduler of record, keeps model workers behind typed ports and
deterministic gates, and forbids self-promotion. Edit maturity only when the
corresponding content-addressed, independently verified evidence binding
exists; stronger factory and Nix maturity fail without it. A committed
[`examples/economic-factory.json`](examples/economic-factory.json) is ready to
inspect without creating a file.

## Factory AI and local Qwen

Zaibatsu is the meta-factory; Factory AI's Droid is one possible worker
harness. The core architecture does not depend on Droid or Qwen.

For the Guild case study, Droid used an authenticated OpenAI-compatible
endpoint serving an owner-operated GGUF. The loaded filename was labeled
`Qwen 3.8 27B` and the server reports `Q4_K - Small`; the public receipt does
not treat that filename as verified model identity, parameter count, or
weight-file provenance.

Droid strengthened the required task order to:

```text
persist < execute in sandbox < verify < policy decision < controlled side effect
```

Its self-report was not acceptance. The diff and adversarial test were reviewed
and the complete repository suite was rerun independently.

## Repository map

- [Meta-factory model](architecture/factory-model.json) — software factories,
  lifecycle, reproducibility, versioning, schedulers, skeletons, harnesses, and
  feedback.
- [Component architecture](architecture/system.json) — planes, components,
  task flow, and fail-closed invariants.
- [Portable factory definition](examples/economic-factory.json) — reusable
  contract for a new control or economic factory.
- [Project-owned schemas](schemas/) — JSON Schema contracts for architecture,
  readiness, portable factories, and sanitized evidence.
- [Architecture guide](docs/architecture.md) — how the two models compose.
- [Implementation status](docs/implementation-status.md) — operational versus
  validated, designed, and planned capabilities.
- [Case study](docs/case-study.md) — the Guild-ready technical narrative.
- [Security and threat model](docs/security-and-threat-model.md) — assets,
  trust boundaries, and mitigations.
- [Evidence](docs/evidence.md) and [sanitized receipts](evidence/) — provenance,
  results, and limitations.
- [Reproducibility](docs/reproducibility.md) — public validation and the Nix
  boundary.
- [Droid integration](docs/droid-session.md) — command, local-model seam, and
  reviewed contribution.
- [Roadmap](docs/roadmap.md) — bounded steps toward deployable factories.
- [Submission readiness](architecture/submission-readiness.json) — external
  gates that prevent premature submission claims.

## Core invariants

1. Zaibatsu is the meta-factory; economic factories remain project-scoped.
2. Unknown factories, identities, capabilities, and transitions fail closed.
3. Every workload has exactly one scheduler of record.
4. Git versions intended state; plaintext secrets never enter Git.
5. Ansible and Nix serve different reproduction boundaries, and Nix remains
   planned until independently reproduced.
6. Agent skeletons are modular contracts, not autonomous production authority.
7. LLM harnesses are interchangeable workers behind deterministic entry and
   exit gates.
8. Tests, schemas, linters, hashes, policy, receipts, and owner approval outrank
   model confidence.
9. Feedback may propose shared improvement but cannot self-promote.
10. Failed work remains inspectable, and the owner retains a recovery path
    outside Dispatcher.

## Factory Guild submission

The intended submission is an open-source project plus technical article and
short demo. Immutable `v1.1.0` passed a credential-disabled public-clone proof
and independent GitHub CI. The `v1.1.1` candidate adds reusable contracts and
harder evidence validation and passed its own anonymous-clone and CI proof. The
final demo and applicant-owned form materials remain external submission gates.

Zaibatsu is an independent project and is not affiliated with or endorsed by
Factory AI.

## License

[MIT](LICENSE)
