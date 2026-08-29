# Implementation status

Status date: **2026-08-28**

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
| Dispatcher API and policy engine | Designed | Contract and acceptance gates | No production Dispatcher service claim |
| PostgreSQL jobs and leases | Designed | State-machine and schema requirements | No deployed authoritative job database claim |
| Project sandboxes | Planned | Isolation requirements only | No environment is called a sandbox until its boundaries pass |
| Nix project environments | Planned | Tool-boundary design only | No current flake or cross-worker reproduction claim |
| Factory/Droid contribution | Validated preproduction | Authenticated local-Qwen session, reviewed two-file diff, pre-change adversarial proof, and independent validation | Droid strengthened the five-stage deterministic task-flow order and added its rejection test; this grants no production authority |

The current private source validation passed 96 operations tests and 34 pinned
newsroom regressions, in addition to infrastructure formatting, syntax, lint,
policy, shell, workflow, and leak checks. This supports the implemented and
validated-preproduction claims only; it does not promote designed components.

## Current authority

The existing systemd executor remains production authority. The Dispatcher is
a bounded implementation and preproduction target. Migration readiness is
explicitly separate from migration authorization.

## What is deliberately not claimed

- unattended model routing;
- a production PostgreSQL task engine;
- a deployed worker lease service;
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
