# Zaibatsu: deterministic control around probabilistic workers

## Summary

Zaibatsu is a small, self-hosted software-factory architecture for operating
multiple projects without turning an LLM into an infrastructure administrator.
It combines a private Tailscale management plane, reviewed OpenTofu and Ansible
automation, durable systemd execution, scoped identities, explicit readiness
gates, and a target PostgreSQL Dispatcher around replaceable AI workers.

The public artifact is an executable architecture kit. A machine-readable
contract distinguishes operational, validated-preproduction, designed, and
planned capabilities. A standard-library validator rejects unknown projects,
probabilistic components without deterministic entry and exit gates, direct
model-to-production paths, unguarded side effects, unsafe public details, and
broken documentation links.

## The problem

The starting environment had real automated products and recurring pipelines,
but its long-running schedules were tied to one workstation. The desired future
was broader: an always-on Dispatcher that could accept jobs, route work to
different model and compute workers, preserve progress across worker failure,
and coordinate two production project boundaries.

The obvious shortcut—give a capable model shell access and let it improvise—was
also the wrong architecture. Models are excellent at diagnosis, synthesis, and
implementation, but their output is probabilistic. Scheduling, identity,
authorization, deployment, secret scope, recovery, and audit must remain
explicit and repeatable.

The design question became:

> How can probabilistic workers do meaningful autonomous work while
> deterministic software retains authority over state and side effects?

## The architecture

Zaibatsu assigns one responsibility to each layer:

| Layer | Responsibility |
| --- | --- |
| Dispatcher | routing, durable state, policy, leases, audit, and authorization |
| Project boundary | business context, credentials, workflow, and production scope |
| Job | stable goal, state, risk, checks, attempts, evidence, and artifacts |
| Worker | temporary planning, research, implementation, or review |
| Sandbox | isolated per-project, preferably per-job execution |
| Verifier | tests, schemas, hashes, policy, health, and acceptance evidence |
| Deployment mechanism | the only controlled bridge to production |
| Knowledge system | durable decisions and small routed context packets |

The critical flow is:

```text
deterministic trigger
  -> deterministic eligibility and policy
  -> probabilistic worker judgment
  -> deterministic artifact validation
  -> optional independent model critique
  -> deterministic transition authorization
  -> deterministic external side effect
```

An agent can propose a deployment; it cannot make its own prose the deployment
authorization.

## Building beside the live system

The architecture was developed side by side with existing production rather
than by replacing its bootstrap or schedules.

1. The current executor remained authoritative.
2. The normal topology and three-project allowlist became machine-readable.
3. Private Tailscale administration and a default-deny host boundary were
   established and verified.
4. Ansible adapted a reviewed release to the always-on host using locked service
   identities and root-owned receipts.
5. A non-publishing shadow installed the workload definitions with all
   destination timers disabled and execution guarded.
6. Source, mutable state, credentials, and operational authority were split
   into separate transfer channels.
7. Snapshot and restore logic verified a manifest while refusing credentials,
   symlinks, active destination units, or a non-empty target.
8. Cutover gates stayed red for the missing job database, project sandboxes,
   production verification, rollback drills, and observation window.

This is the architecture’s core lesson in practice: preparation is not
authorization, and an artifact existing on a destination is not the same as
that destination owning production.

## Turning prose into an executable public artifact

The private program cannot safely be published in full. Host coordinates,
credential topology, recovery details, and production repositories belong
behind the control boundary. Zaibatsu therefore extracts the reusable
architecture while preserving claim provenance.

The public repository includes:

- `architecture/system.json`, a machine-readable component and invariant
  model;
- `scripts/validate_repository.py`, an offline contract and public-safety
  validator;
- adversarial tests that mutate the valid contract and prove rejection;
- an implementation-status ledger that prevents planned Nix and Dispatcher
  components from being described as operational;
- a threat model, reproduction guide, evidence ledger, demo, and application
  package.

This makes the architecture independently inspectable without publishing the
keys to the factory floor.

## Factory/Droid integration boundary

The core artifact remains useful without Droid. For the Guild contribution,
Factory Droid operated only on a sanitized public clone, never the private
fleet. The backend was the owner’s Qwen 3.8 27B GGUF 3-bit model through an
authenticated OpenAI-compatible gateway. Its endpoint and credential stayed
in ignored local configuration and the launch boundary, not in Git. Factory
authentication remained separate from model authentication.

The project-level `AGENTS.md` supplies exact commands and security boundaries.
One headless Droid task ran with low local autonomy. It strengthened the
validator from a partial task-flow order to `persist < execute_in_sandbox <
verify < policy_decision < controlled_side_effect`, added a test that moves
policy before verification, and ran the offline validation suite. The original
validator accepted that adversarial mutation. Because the custom model is
probabilistic, its self-report was not acceptance; the two-file diff was
reviewed and `make validate` was rerun independently.

The configuration seam, exact command, initial failed-auth observation,
successful session, reviewed diff, and independent evidence are recorded in
[Droid integration](droid-session.md).

## Results

The public kit converts architectural intent into properties a machine can
reject:

- an unrecognized project cannot enter the control model;
- a probabilistic worker without a deterministic precondition or postcondition
  fails validation;
- a probabilistic component cannot own an external side effect;
- a deterministic side-effecting component must declare its policy gate;
- the task flow must place sandbox execution, verification, and policy in the
  deterministic order required before a controlled side effect;
- a public document containing a private home path or address fails the safety
  scan;
- maturity is explicit, so Nix, leases, and sandboxes cannot silently become
  “done” in the narrative.

The private implementation separately carries its operational validation and
regression evidence. Exact results are recorded in [Evidence](evidence.md)
after the final clean run.

## What changed in my engineering workflow

Before Zaibatsu, architectural invariants existed across prose, playbooks,
runtime checks, and operator knowledge. The migration work made those
boundaries explicit, but the public extraction added a second layer: claims and
agent-control rules now have a small executable specification.

The most valuable pattern is not “let an agent run everything.” It is:

```text
give the agent a narrow problem
  -> require an artifact
  -> make deterministic checks cheap and local
  -> retain evidence independently of the agent
  -> expand authority only after the proof exists
```

## Limitations

- The Dispatcher job API and PostgreSQL state engine are designed, not
  deployed.
- Project sandboxes are planned, not proven.
- Nix is a deliberate next step and has no current flake implementation.
- The public validator tests architecture declarations, not the private fleet.
- Some business-level correctness will always require domain-specific tests or
  explicit owner judgment.
- The local Qwen/Droid result is one bounded contribution, not a general model
  benchmark or production-autonomy claim.
- A short Guild demo cannot substitute for recovery drills and operational
  observation.

## Takeaway

Autonomy becomes safer when AI workers are easy to replace and the surrounding
system is difficult to fool. Durable jobs, explicit capabilities, private
networking, reproducible configuration, deterministic verification, scoped
side effects, and honest maturity labels make probabilistic reasoning useful
without making it sovereign.
