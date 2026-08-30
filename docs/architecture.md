# Architecture

## Thesis

Zaibatsu separates the parts of software work that benefit from probabilistic
judgment from the parts that must be repeatable, auditable, and fail closed.

```text
                  control plane
  +-------------------------------------------+
  | intake -> policy -> durable job -> lease |
  +----------------------+--------------------+
                         |
                         v
                bounded execution plane
  +-------------------------------------------+
  | sandbox -> probabilistic worker -> result |
  +----------------------+--------------------+
                         |
                         v
                 verification plane
  +-------------------------------------------+
  | tests -> schema -> evidence -> risk gate  |
  +----------------------+--------------------+
                         |
                         v
                  side-effect plane
  +-------------------------------------------+
  | merge / deploy / publish / operate        |
  +-------------------------------------------+
```

The control plane may use agents as advisers, but its authority is conventional
software: transactions, explicit transitions, scoped capabilities, verified
artifacts, and policy decisions.

## Planes

### 1. Intake and control

Requests arrive from an owner, schedule, alert, API, or project service. The
Dispatcher assigns a stable job ID, project, priority, risk class, required
capabilities, acceptance checks, and idempotency key. Unknown projects and
invalid transitions fail closed.

The target job state machine is:

```text
queued -> eligible -> leased -> running -> verifying -> succeeded
   |          |          |          |           |
   +----------+----------+----------+-----------+-> failed / repair / exception
```

Every transition is explicit and transactional. A worker cannot promote its
own natural-language answer into terminal success.

### 2. Durable state

Workers are disposable; work is durable. PostgreSQL is the source of truth for
the bounded Dispatcher lane's jobs, leases, attempts, policy decisions,
evidence, and audit events. Kanban is a synchronized human-readable surface,
not the only record that work exists.

The private implementation runs PostgreSQL 16 over a Unix socket and a
deterministic read-only coordinator across the three allowlisted projects. The
coordinator invokes no model, is idempotent by time bucket, retries once, and
then blocks. `architecture/system.json` models this coordinator as its own
operational component. The broader Dispatcher API and policy surface remains
validated preproduction, while systemd retains authority for the existing
production workloads.

Operational state and knowledge stay separate:

| System | Question | Examples |
| --- | --- | --- |
| Operational database | What are we doing now? | jobs, leases, attempts, approvals, health |
| Git | What changed? | reviewed source, configuration, diffs |
| Artifact store | What can be shipped? | packages, manifests, reports |
| Logs and events | What happened? | commands, checks, transitions |
| Knowledge memory | What do we know? | decisions, runbooks, incidents, lessons |

### 3. Worker routing

Jobs declare capabilities rather than preferred personalities. A router can
choose any eligible implementation, research, planning, local-inference, or
review worker. Each worker receives only the repository, context, tools,
network, and credentials needed for that job.

```text
job requirements
      |
      v
capability + health + policy match
      |
      v
short-lived lease and bounded context
      |
      v
replaceable worker
```

A missing or failed optional model must not stop the Dispatcher. Lease expiry
returns abandoned work to a recoverable state.

### 4. Sandboxed execution

The intended execution boundary is one isolated workspace or worktree per job,
with project-scoped identity and deny-by-default network and secret access.
Failed workspaces remain available long enough for resumption or diagnosis.

Project sandboxes are planned, not currently deployed. The word “sandbox” is
reserved for an environment whose isolation, credentials, network policy,
lifecycle, and recovery have been proven.

### 5. Verification and policy

Verification starts with deterministic tools:

- unit, integration, regression, and acceptance tests;
- schema, type, lint, and format checks;
- stable hashes and signed or attributable manifests;
- policy evaluation against job risk and capability scope;
- idempotence, health, listener, and duplicate-execution checks.

An independent model may critique an artifact, but model judgment supplements
rather than replaces deterministic evidence. Only the policy engine authorizes
an external side effect.

### 6. Production boundary

Workers normally produce artifacts rather than changing production directly.

```text
worker result
    -> artifact
    -> deterministic checks
    -> risk policy
    -> controlled deploy or publish mechanism
    -> health verification
    -> durable evidence
```

Destructive infrastructure actions, sensitive blockchain operations, root
identity changes, secret rotation, and database migrations require stronger
policy and explicit owner authority.

## Infrastructure composition

Each tool answers a different question.

| Tool | Question | Zaibatsu role | Current maturity |
| --- | --- | --- | --- |
| OpenTofu | What cloud resources should exist? | reviewed resource lifecycle and cost gate | Validated preproduction |
| Tailscale | How does the management plane connect privately? | authenticated private administration fabric | Operational |
| Ansible | How should a host be configured? | identities, hardening, services, guards, monitoring | Validated preproduction |
| Nix | Which exact project tools should workers receive? | pinned development and runtime environments | Planned |
| systemd | What executes durably on a host? | current schedules and service supervision | Operational |
| PostgreSQL | What work exists and what state is it in? | durable bounded Dispatcher state plus broader validated contract | Validated preproduction |
| Bounded coordinator | Which fixed read-only collection is due? | allowlisted collect-only scheduling and receipt-bound completion | Operational |
| Factory Droid + local Qwen | Where can bounded AI repository work run? | optional public-kit contributor behind deterministic checks | Validated preproduction |

The order is intentional: private access and reproducible host configuration
are established before Nix is introduced. There is no current `flake.nix` in
the private operational source, so Zaibatsu does not claim Nix implementation.

## Network topology

The public model avoids hostnames and addresses:

```text
operator endpoints + bounded compute workers
                    |
              Tailscale fabric
                    |
               Dispatcher
              /          \
     project boundary A  project boundary B
```

Public applications expose only required service endpoints. SSH, management
APIs, metrics, databases, queues, dashboards, and deployment controls stay on
loopback or the private management network.

## Factory improvement loop

Zaibatsu closes the improvement loop by turning operational weakness into
durable improvement work:

```text
run -> failure evidence -> classified defect -> improvement job
    -> bounded implementation -> validation -> stronger future workflow
```

This is organizational feedback, not autonomous authority expansion. The same
policy and production gates apply to changes that improve the factory itself.

## Recovery invariant

The owner retains a direct recovery path outside the normal Dispatcher route.
Backups, configuration source, and operator access must permit rebuilding the
control plane when it is unavailable. Dispatcher must never be required to
recover Dispatcher.
