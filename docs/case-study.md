# Zaibatsu: the factory of software factories

## Summary

Zaibatsu is an evidence-gated architecture and toolkit for making multiple
project-specific software factories reproducible. An economic factory produces
software, data, research, content, or services for one business boundary.
Zaibatsu defines and governs the common machinery: factory identity,
versioning, reproduction, scheduling, modular work, deterministic verification,
evidence, recovery, and reviewed improvement.

The system combines Git and SOPS/age, Ansible and planned Nix environments,
cron and systemd, PostgreSQL durable state, modular agent skeletons, and
interchangeable LLM harnesses. Models provide bounded judgment. Conventional
software retains authority over state, secrets, policy, scheduling,
verification, deployment, publication, and other irreversible effects.

## The problem

The starting environment contained real automated products, data pipelines,
content systems, schedules, and production services. Each had grown its own
scripts, credentials, models, schedulers, recovery procedures, and operational
knowledge. Long-running shared schedules were also tied too closely to one
owner workstation.

Moving timers to an always-on server solved only part of the problem. The
larger challenge was to make each business boundary into a repeatable software
factory without merging its authority with every other factory. A useful
system needed to answer:

- What exactly defines one factory?
- How can it be versioned and reproduced?
- Which scheduler owns each workload?
- How can modules and model harnesses be reused without sharing credentials?
- How does evidence return to the shared control layer?
- How can a lesson improve multiple factories without allowing self-promotion?

The design question became:

> How can one control factory build and improve several economic software
> factories while each remains reproducible, modular, recoverable, and
> independently authorized?

## Meta-factory hierarchy

```text
Zaibatsu control factory
  -> registry, templates, infrastructure, policy, evidence, recovery
  -> modular deterministic and probabilistic work contracts
  -> reviewed shared improvement
       |
       +-- FFN economic factory
       |     data · tools · software · editorial · distribution
       |
       `-- SimbaPool economic factory
             operations · research · software · publishing
```

The economic factories can reuse a module or infrastructure pattern without
sharing their identities, secrets, data, schedules, or deployment rights.
Unknown factory identities fail closed.

## The factory contract

Zaibatsu assigns one responsibility to each layer:

| Layer | Responsibility |
| --- | --- |
| Factory registry | closed identity, business class, ownership, and project boundary |
| Git and release layer | reviewed source, intended state, diffs, manifests, and release history |
| Static secret layer | SOPS/age ciphertext and recipient policy; no plaintext in Git |
| Runtime secret layer | bounded machine identities and factory-scoped delivery |
| Reproduction layer | Ansible host state and eventually Nix worker environments |
| Scheduler layer | exactly one cron or systemd owner for each workload |
| Dispatcher | durable jobs, routing, policy, leases, evidence, audit, and authorization |
| Agent skeleton | reusable typed modules, flows, implementations, and deployment profiles |
| Harness implementation | temporary deterministic tool or probabilistic model worker |
| Verifier | schemas, linters, tests, hashes, policy, receipts, and independent checks |
| Effect mechanism | the only controlled bridge to Git, publication, databases, or production |
| Knowledge and feedback | decisions, incidents, runbooks, observations, and improvement candidates |

The complete lifecycle is:

```text
define -> version -> reproduce -> schedule -> execute -> verify -> authorize
       -> operate -> observe -> return evidence -> improve -> reviewed promotion
```

## Reproduction and versioning

Git is the source/history boundary, not the runtime database. SOPS/age permits
static encrypted bootstrap material to be reviewed and versioned without
placing plaintext secrets in Git. Runtime machine credentials remain scoped to
their factory and delivered separately.

Ansible reproduces hosts: identities, hardening, packages, services, guards,
and monitoring. Nix is intended to reproduce the narrower worker toolchain and
environment. The two are complementary. Ansible has bounded evidence; Nix
remains planned until a real flake reproduces on more than one eligible node.

## Scheduling beside the live system

The architecture was built beside existing production rather than pretending
all scheduler diversity had already disappeared.

1. Every current workload was inventoried with one scheduler of record.
2. Managed shared schedules moved to the always-on control host under systemd.
3. Selected downstream cron workloads remained with their factories.
4. Private networking, locked identities, guards, and receipts were added
   before wider authority.
5. A non-publishing shadow proved configuration without becoming a duplicate
   scheduler.
6. Backups and restore drills preserved a recovery path independent of the
   normal control flow.

Systemd is the durable default, but cron remains a supported adapter while it
owns real downstream workloads. Migration requires equivalent failure,
monitoring, retry, rollback, and ownership evidence.

## Durable control and modular agents

PostgreSQL provides durable state for the bounded Dispatcher lane. The broader
contract covers jobs, transitions, attempts, leases, idempotency, policy,
evidence, audit events, and recovery. The current fixed read-only coordinator
runs across the three factory identities without invoking a model.

The reusable unit above that state is a typed module rather than an agent
persona. Modules compose into flows, and deployment profiles select reviewed
implementations for each factory. A research module could use one harness in
FFN and another in SimbaPool while preserving identical typed inputs, outputs,
budgets, denied capabilities, and evaluation rules.

The private source-only scaffold currently has 21 logical modules, 6 flows, 12
deployment profiles, 23 implementation variants, and a 309-test pass. It
contains deterministic quality modules, probabilistic work modules, durable
approval, and idempotent effect contracts. It remains source-only: dedicated
pools, handler qualification, activation, credentials, alerts, and an
observe-only canary are not complete.

## LLM harness boundary

```text
typed task and bounded context
  -> selected deterministic or LLM harness implementation
  -> typed candidate artifact
  -> schemas, linters, tests, hashes, policy, receipts
  -> optional independent critique
  -> durable owner or effect gate
```

Codex, Qwen, Factory Droid, or a future model can implement a module only after
its adapter and behavior qualify. A model cannot waive a deterministic failure,
approve itself, use credentials, change policy, or trigger an effect merely by
returning confident prose.

## Recursive improvement without recursive authority

Factory outcomes return evidence to Zaibatsu:

```text
run -> observation/failure -> evidence -> classified improvement candidate
    -> shared module/template/gate change -> deterministic validation
    -> owner-reviewed promotion -> eligible factory rollout with rollback
```

Today, evidence capture and some improvement work are operational at bounded
scope. General automatic classification, shared-template promotion, and
cross-factory rollout are not deployed. Recursive improvement means reviewed
versioned learning, not self-modifying production authority.

## Factory/Droid contribution

Factory AI's Droid is one possible harness inside the larger Zaibatsu model.
For the Guild contribution, Droid operated only on a sanitized public clone.
It used an owner-operated GGUF through an authenticated OpenAI-compatible
gateway; the loaded filename was labeled `Qwen 3.8 27B` and the server reports
`Q4_K - Small`. Official identity and parameter count remain unverified.

The bounded task strengthened the public validator from a partial task-flow
check to:

```text
persist < execute_in_sandbox < verify < policy_decision < controlled_side_effect
```

It added an adversarial test that the original validator accepted. Droid's
self-report was not acceptance: the two-file diff was reviewed and the suite
was rerun independently.

## Executable public artifact

The private implementation cannot be published in full. Zaibatsu extracts the
reusable contracts while preserving evidence and limitations:

- `architecture/factory-model.json` defines factories, lifecycle,
  reproducibility, versioning, schedulers, skeletons, harnesses, and feedback;
- `architecture/system.json` defines control-plane components, maturity, task
  order, and fail-closed invariants;
- `examples/economic-factory.json` and `scripts/zaibatsu.py` let another
  project scaffold and validate a portable factory definition;
- `catalog/modules.json` defines policy-compatible implementations for every
  factory control slot, while `examples/economic-factory.plan.json` proves a
  content-addressed, dependency-ordered composition;
- `zaibatsu plan`, `verify-plan`, and `rebuild-check` reject module-policy
  mismatch, definition or catalog drift, and plan tampering without claiming
  infrastructure deployment or recovery;
- project-owned JSON Schemas describe the architecture, factory, readiness,
  and evidence documents;
- `scripts/validate_repository.py` checks all contracts, evidence semantics,
  readiness proof, and public safety;
- adversarial tests prove that hierarchy, lifecycle, maturity, secret,
  scheduler, model-authority, and feedback rules reject unsafe mutations;
- sanitized receipts bind private observations without publishing operational
  access.

## Results

The public package can now reject claims or architectures in which:

- Zaibatsu drifts from meta-factory to a single project factory;
- an economic factory becomes the shared control factory;
- an unknown factory enters the registry;
- promotion happens before evidence returns;
- Nix becomes “operational” without a flake and cross-node proof;
- plaintext secrets become allowed in Git;
- cron and systemd both own the same workload;
- a source-only skeleton is described as deployed;
- a model authorizes an external effect;
- a factory promotes its own feedback into shared policy;
- component and meta-factory maturity ledgers diverge.

## Limitations

- The modular agent scaffold is source-only and not production-authorized.
- Nix environments and repository-hook extensions remain planned.
- General unattended multi-model routing is not active.
- Project/job sandboxes and future separate sandbox hosts are not proven.
- Only the deterministic read-only Dispatcher lane is operational; broader
  side-effect authority remains validated preproduction.
- Complete canonical private repository consolidation remains gated.
- Public receipts describe private validation but do not make the private
  implementation independently reproducible.
- A Guild demo cannot substitute for recovery drills and operational evidence.

## Takeaway

Zaibatsu is not one AI agent and not one software factory. It is the control
architecture and toolkit for making factories repeatable and governable:
versioned definitions, bounded reproduction, modular work, interchangeable
harnesses, deterministic verification, explicit effects, retained evidence,
and reviewed recursive improvement. The maturity ledger identifies which of
those layers are operational, validated privately, source-only, or still
planned.
