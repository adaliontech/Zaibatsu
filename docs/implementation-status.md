# Implementation status

Status date: **2026-08-29**

This ledger prevents target architecture from being presented as deployed
runtime. The maturity labels are enforced by
[`architecture/system.json`](../architecture/system.json).

| Capability | Status | Evidence strength | What the claim means |
| --- | --- | --- | --- |
| Current systemd workload executor | Operational | Runtime and checked-in unit evidence | Existing schedules remain authoritative until controlled migration |
| Private Tailscale administration | Operational | Connection, firewall, and identity checks recorded privately | The management path is private; public recovery access has a separate removal gate |
| Ansible host configuration | Validated preproduction | Syntax, check, apply, idempotence, service, and guard evidence | Configuration has been exercised without granting production authority |
| OpenTofu lifecycle controls | Validated preproduction | Offline validation and saved-plan policy tests | Apply remains review-gated and is not a CI authority |
| Non-publishing workload shadow | Validated preproduction | Disabled timers, execution guards, regression, and dry-run evidence | Shadow execution cannot publish or become a duplicate scheduler |
| Scoped machine-secret delivery | Validated preproduction | Destination scope, file-mode, and deny-all authorization receipts | Personal-vault or cross-project authority is not part of the design |
| Provenance-aware knowledge retrieval | Operational | Local retrieval tests and receipts | Agents receive small routed context packets; prose is not task state |
| Dispatcher API and policy engine | Validated preproduction | 158 focused tests covering contracts, replay protection, coordinator behavior, recovery, and local transport | The broader side-effecting API surface is implemented and evidenced without general production authority |
| PostgreSQL jobs and leases | Validated preproduction | 104 live assertions on two disposable PostgreSQL 16.15 clusters, including leases, privilege denial, audit chains, backup/restore equivalence, and continuation after restore | The full state contract is implemented and independently exercised |
| Bounded read-only coordinator lane | Operational | Live durable job state, deterministic time-bucket scheduling, three eligible project workers, retained failures, and receipt-bound completion | The live lane performs fixed read-only collection without a model; it does not authorize broader workload migration |
| Project sandboxes | Planned | Isolation requirements only | No environment is called a sandbox until its boundaries pass |
| Nix project environments | Planned | Tool-boundary design only | No current flake or cross-worker reproduction claim |
| Factory/Droid contribution | Validated preproduction | Authenticated local-Qwen session, reviewed two-file diff, pre-change adversarial proof, and independent validation | Droid strengthened the five-stage deterministic task-flow order and added its rejection test; this grants no production authority |

The current private Dispatcher source validation passed 158 focused tests. Its
standalone acceptance harness passed 104 live assertions against two
disposable, socket-only PostgreSQL 16.15 clusters with production data
explicitly excluded. These results support the bounded claims above; they do
not promote untested side-effecting workflows or project sandboxes.

## Current authority

The existing systemd executor remains production workload authority. The
Dispatcher database and deterministic read-only coordinator are live for one
bounded workflow family; the broader API/policy and worker architecture remain
validated preproduction. Migration readiness is explicitly separate from
migration authorization.

## What is deliberately not claimed

- unattended model routing;
- general production job execution through Dispatcher;
- side-effecting Dispatcher transitions outside the bounded read-only lane;
- completed project sandboxes;
- Nix-based reconstruction;
- unattended or production-authorized Qwen/Droid operation;
- direct agent publication or deployment;
- autonomous secret or infrastructure administration;
- a complete production cutover.

## Promotion rule

A capability moves to a stronger status only when the evidence required at its
full scope exists. A passing local test cannot prove a remote service, a running
process cannot prove recovery, and a design document cannot prove an
implementation.
