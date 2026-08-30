# Zaibatsu

[![Validate](https://github.com/adaliontech/Zaibatsu/actions/workflows/validate.yml/badge.svg)](https://github.com/adaliontech/Zaibatsu/actions/workflows/validate.yml)

**Deterministic control around probabilistic workers.**

Zaibatsu is a reference architecture and executable policy kit for a small,
self-hosted software factory. A conventional control
plane owns durable jobs, state transitions, policy, leases, evidence, and
external side effects. AI agents are bounded, replaceable workers: they may
reason and propose artifacts, but they do not become the system of record or
the final authority at an irreversible boundary.

This repository is the public-safe architecture package. It deliberately
contains no credentials, private network coordinates, production inventory,
or deployment access.

## Why Zaibatsu?

The name describes a coordinated group of specialized project factories. Each
project keeps its own identity, credentials, data, and production boundary,
while a shared deterministic control plane routes work and enforces policy.
Failed runs become evidence, evidence becomes a durable improvement job, and
the improved control plane makes later work more reliable.

```text
intent / schedule / event
          |
          v
  deterministic Dispatcher
  jobs · policy · leases · audit
          |
          v
 probabilistic bounded worker
  plan · diagnose · implement
          |
          v
 deterministic verification
 tests · schemas · hashes · policy
          |
          v
 controlled artifact / side effect
          |
          +---- evidence ----> factory improvement job
```

## Quickstart

The validation kit uses only Python’s standard library.

```bash
git clone https://github.com/adaliontech/Zaibatsu.git
cd Zaibatsu
make validate
```

`make validate` checks the architecture contract, public-safety rules, local
documentation links, every public repository path, and adversarial test cases.
No network access, cloud account, secrets, Nix installation, or production
system is required.

The core kit does not depend on Droid. Its optional Factory integration used
an owner-operated GGUF whose server-reported loaded filename identifies Qwen
3.8 27B and whose server reports `Q4_K - Small`, through an authenticated
OpenAI-compatible gateway. Droid produced one reviewed two-file contract
improvement and adversarial test; independent validation accepted the result.

## What is real today

The architecture is derived from a working private operations program, but its
parts have different maturity levels. As of 2026-08-29:

- a Tailscale private administration path is operational;
- Ansible configuration, host hardening, non-publishing shadow execution,
  disabled-by-default schedules, scoped secret delivery, and idempotence have
  preproduction evidence;
- the bounded Qwen-backed Droid contribution has reviewed preproduction
  evidence and independent repository validation;
- the Dispatcher API/policy contract and PostgreSQL job engine have validated
  preproduction evidence from 158 focused tests and a 104-assertion disposable
  PostgreSQL 16.15 two-cluster acceptance run;
- a distinct machine-readable, deterministic read-only coordinator component
  uses the durable database for the three allowlisted projects without
  invoking a model;
- systemd remains the authoritative production scheduler;
- broader Dispatcher side-effect authority, project sandboxes, and Nix flakes
  remain unclaimed or planned work.

See [Implementation status](docs/implementation-status.md) for the exact
claim ledger.

## Repository map

- [Architecture](docs/architecture.md) — components, task flow, and boundaries.
- [Case study](docs/case-study.md) — the Guild-ready technical narrative.
- [Implementation status](docs/implementation-status.md) — implemented versus
  validated, designed, and planned.
- [Security and threat model](docs/security-and-threat-model.md) — assets,
  trust boundaries, failure modes, and mitigations.
- [Reproducibility](docs/reproducibility.md) — how to validate this package.
- [Evidence](docs/evidence.md) — provenance and verification ledger.
- [Sanitized evidence receipts](evidence/) — bounded machine-readable results
  and their limitations.
- [Factory Droid integration](docs/droid-session.md) — local-Qwen setup, exact
  command, reviewed contribution, and redacted evidence.
- [Demo script](docs/demo-script.md) — a concise screen-recording plan.
- [Guild requirements](docs/guild-requirements.md) — current official rubric.
- [Guild application](docs/guild-application.md) — truthful current draft and
  remaining publication, demo, and applicant-owned gates.
- [Roadmap](docs/roadmap.md) — next increments without inflated claims.
- [Machine-readable architecture](architecture/system.json) — contract checked
  by the validator.
- [Submission readiness](architecture/submission-readiness.json) —
  machine-readable external gates that prevent premature submission claims.

## Core invariants

1. Workers are disposable; jobs and evidence are durable.
2. Probabilistic reasoning is enclosed by deterministic entry and exit gates.
3. An LLM response alone is never verification.
4. No agent can publish, deploy, rotate secrets, or mutate production without
   deterministic policy authorization.
5. Project identities, credentials, data, networks, and deployment rights are
   separated and denied by default.
6. Git defines intended state; PostgreSQL owns durable state for the bounded
   Dispatcher lane; Kanban is a synchronized view.
7. Tailscale carries private management traffic.
8. OpenTofu creates infrastructure, Ansible configures hosts, Nix will pin
   project tool environments, and systemd executes durable services.
9. Failed work remains inspectable and recoverable.
10. Dispatcher must never be required to recover Dispatcher.

## Factory Guild submission

The intended format is an **open-source project** backed by a technical article
and short demo. Factory’s Guild asks builders to build with Factory, publish the
work, and submit a public link. The bounded local-Qwen Droid contribution is
complete and independently validated. The repository is public; the hardened
`v1.0.1` candidate passed its credential-free clone gate. The final demo and
applicant-owned form materials remain explicit gates in
[Submission readiness](architecture/submission-readiness.json).

Zaibatsu is an independent project and is not affiliated with or endorsed by
Factory AI.

## License

[MIT](LICENSE)
