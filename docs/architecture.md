# Architecture

## Thesis

Zaibatsu is the control factory above project-specific software factories. It
does not replace the products, repositories, schedules, or business rules
inside those factories. It gives them a common way to be defined, reproduced,
versioned, scheduled, observed, verified, and improved.

```text
                         Zaibatsu
                meta-factory control layer
        definitions · registry · policy · evidence
          reproduction · modules · shared learning
                         /       \
                        v         v
              FFN economic      SimbaPool economic
                 factory             factory
              data · tools       operations · research
              software · media   software · publishing
```

The shared layer controls factory contracts. Each economic factory retains its
own identity, data, credentials, repositories, schedules, acceptance rules,
budgets, and production authority.

## Eight machine-readable views

Zaibatsu deliberately separates eight questions:

| Contract | Question |
| --- | --- |
| [`architecture/factory-model.json`](../architecture/factory-model.json) | What is a software factory, how is it reproduced and improved, and which factory instances exist? |
| [`architecture/system.json`](../architecture/system.json) | Which control-plane components execute the work, what is their maturity, and which invariants constrain them? |
| [`examples/economic-factory.json`](../examples/economic-factory.json) | Which policies and evidence bindings define one portable factory? |
| [`catalog/modules.json`](../catalog/modules.json) plus [`examples/economic-factory.plan.json`](../examples/economic-factory.plan.json) | Which compatible module implementations resolve into its deterministic control plan? |
| [`examples/economic-factory.bundle-manifest.json`](../examples/economic-factory.bundle-manifest.json) | Which exact definition, catalog, plan, selected module contracts, and schemas form its portable control bundle? |
| [`examples/economic-factory.source-lock.json`](../examples/economic-factory.source-lock.json) | Which immutable annotated-release Git objects supplied the exact control files that reproduce that bundle? |
| [`policies/runtime-qualification-v1.json`](../policies/runtime-qualification-v1.json) plus [`examples/economic-factory.qualification-plan.json`](../examples/economic-factory.qualification-plan.json) | Which content-addressed evidence bindings are still required before those contracts can become runtime-eligible? |
| [`examples/economic-factory.qualification-evidence.json`](../examples/economic-factory.qualification-evidence.json) plus [`examples/economic-factory.qualification-assessment.json`](../examples/economic-factory.qualification-assessment.json) | Which requirements does the verified bundle itself actually prove, and exactly which runtime proofs remain missing? |

The validator requires the factory registry and shared component maturities to
agree. A narrative edit cannot silently turn planned Nix reproduction or
source-only agents into operational capability.

## Deterministic module composition

A portable factory selects exactly one implementation for each ordered slot:

```text
source versioning -> static secrets -> runtime secrets -> host reproduction
  -> worker environment -> scheduling -> execution -> verification -> feedback
```

The catalog gives every module a stable ID, interface version, typed inputs and
outputs, implementation boundary, dependency slots, and policy value. The
factory does not depend on the bundled ID: a replacement ID is accepted when
it belongs to the same slot and declares the same policy value. This keeps
implementations interchangeable without allowing a module swap to weaken Git,
SOPS/age, bounded runtime secrets, Ansible, Nix, scheduler, harness,
verification, or promotion policy.

The composer canonicalizes the complete factory definition and module catalog,
hashes both, resolves selected modules in dependency order, and hashes the
resulting plan. `verify-plan` rejects any definition drift, catalog drift,
module-policy mismatch, order change, or digest edit. `rebuild-check` compiles
the same inputs twice and requires identical canonical bytes.

Every catalog entry also names a module-local contract artifact and its
canonical SHA-256 digest. The artifact repeats the typed interface and policy
boundary in a portable unit while explicitly denying a bundled runtime,
entrypoint, environment lock, or effect authority. A replacement module needs
a compatible policy value and a distinct artifact whose content matches its
catalog contract and digest.

`bundle` packages the canonical definition, complete catalog, resolved plan,
nine selected module contracts, five project-owned schemas, and a digest
manifest into a deterministic uncompressed USTAR archive. `verify-bundle`
reads it entirely in memory and refuses traversal paths, links, special files,
duplicates, extras, noncanonical metadata or JSON, payload drift, schema drift,
and trailing bytes. It then reproduces the exact archive bytes.

`inspect-bundle` exposes only a stable projection of a fully verified bundle:
factory identity, source digests, selected modules, rebuild claims, and the
explicit reason it is not runtime-eligible. `compare-bundles` verifies both
archives before reporting definition, catalog, plan, module, or schema
changes. The public systemd and cron variants demonstrate that scheduler
selection is modular while leaving the shared catalog, schemas, and
least-authority boundary unchanged.

`source-lock` reads an annotated semantic-version tag, commit, tree, and the
sixteen bundle input blobs directly from local Git object storage with
replacement objects disabled. It records repository-native object IDs plus
SHA-256 hashes of the object content and canonical file content, rebuilds the
bundle from those blobs, and requires byte identity. `verify-source-lock`
repeats that derivation without trusting the working tree.

The source lock terminates at the control-contract boundary. It does not
contact or authenticate the stated remote, verify a tag signature, include
runtime implementation source, satisfy a qualification binding, grant runtime
eligibility or activation, or deploy infrastructure. Those stronger claims
remain separate evidence problems.

`qualification-plan` joins a fully verified bundle to a versioned minimum
policy and emits a content-addressed list of missing implementation, source,
environment, conformance, recovery, and slot-specific evidence. The public
systemd plan contains 67 missing bindings across 27 requirement types and
marks zero of nine modules eligible. `verify-qualification-plan` rebuilds the
expected plan from both inputs and denies bundle drift, policy drift, digest
drift, self-attestation, eligibility inflation, or activation authority. A
qualification plan contains no evidence and cannot substitute for owner
approval.

`qualification-evidence` reruns the same complete bundle, plan, and policy
verification before deriving nine content-addressed contract-conformance
receipts—one for each selected module. Those receipts prove only exact
contract/catalog/schema-reference/artifact-digest agreement. The corresponding
assessment verifies 9 of 67 bindings and leaves 58 missing. It claims no
runtime implementation, environment realization, recovery, isolation,
external independent verifier, eligibility, or activation. Replaying a receipt
against the cron bundle, another plan, policy, module, or artifact fails closed.

This boundary is deliberately narrower than infrastructure reproduction. The
plan and bundle own no side-effect authority and explicitly state that they
contain no runtime implementations, deploy no infrastructure, and prove no
runtime recovery. Ansible application, Nix realization, scheduler activation,
model execution, effect authorization, and recovery each require their own
evidence.

## Factory classes

### Control factory

The Orchestrator factory supplies the shared control layer: registry, policy,
durable state, scheduling contracts, evidence, reusable modules, deployment
patterns, recovery, and improvement proposals. Zaibatsu is the public model of
that meta-factory role.

### Economic factory

An economic factory produces outputs for one product or business boundary.
Current instances are FFN and SimbaPool. Their outputs differ, but each factory
has the same categories of control:

- project identity and repository lineage;
- static and runtime secret boundaries;
- host and environment reproduction;
- declared schedulers and workloads;
- deterministic and probabilistic worker modules;
- artifact contracts and verification;
- publication, deployment, and recovery policy;
- observations and evidence returned to Zaibatsu.

An unknown factory receives no routing, repository, credential, worker,
scheduler, or production authority.

## Factory lifecycle

```text
define
  -> version
  -> reproduce
  -> schedule
  -> execute bounded work
  -> verify artifacts
  -> authorize effect
  -> operate
  -> observe
  -> return evidence
  -> improve shared patterns
  -> promote reviewed change
```

Promotion is intentionally last. Evidence from one factory may reveal a better
module, prompt, linter, hook, policy, environment, or recovery procedure. That
evidence becomes an improvement candidate in Zaibatsu. It does not immediately
change the reporting factory or propagate to another factory.

## Versioning and secret boundary

Git versions reviewed source, intended state, diffs, release manifests, and
public releases. It is not a place for plaintext credentials or mutable runtime
state.

SOPS/age and a bounded runtime secret manager serve different purposes:

| Mechanism | Boundary |
| --- | --- |
| Git | reviewed source and intended state |
| SOPS/age | static encrypted bootstrap material and recipient policy that may be versioned safely |
| Bounded runtime secret manager | machine-scoped values delivered at runtime without a personal vault session |

The private operations layer has validated SOPS/age policy and ciphertext
checks. Complete canonical repository consolidation across every product
factory remains a separate owner-controlled gate.

## Reproducibility

Ansible and Nix solve different reproduction problems:

| Tool | Reproduces | Current maturity |
| --- | --- | --- |
| Ansible | host configuration, locked identities, hardening, packages, services, guards, and monitoring | Validated preproduction |
| Nix | exact per-factory or per-worker tool environments | Planned |

Ansible has review, syntax, policy, application, and idempotence evidence at
bounded scope. Nix is part of the required target architecture, but no accepted
flake or cross-node reproduction proof exists. A missing Nix environment must
eventually make a worker ineligible rather than inviting it to improvise a
toolchain.

## Scheduling and durable execution

The fleet contains both cron and systemd schedules. Zaibatsu does not pretend
that heterogeneity has already disappeared. Instead, it enforces one scheduler
of record per workload and requires inventory, failure handling, evidence, and
rollback before scheduler migration.

Systemd is the preferred durable default and owns the managed control-host
workloads. Selected downstream factory workloads still use cron. A duplicate
cron and systemd owner for the same effect is an architecture failure.

PostgreSQL is machine-level truth for the bounded Dispatcher lane's jobs,
leases, attempts, decisions, evidence, and audit events. Kanban and dashboards
are views, not the only record that work exists.

```text
trigger -> durable job -> eligibility -> lease -> run -> verify -> decision
                                                       |          |
                                                       v          v
                                                    evidence   effect gate
```

The current deterministic read-only coordinator invokes no model, uses fixed
time buckets, retains failures, and is operational across the closed factory
registry. General side-effecting Dispatcher execution remains validated
preproduction.

## Modular agent skeletons

The intended unit of reuse is a typed module, not an agent personality. Modules
can be composed into flows and assigned implementations per factory:

```text
factory profile
  -> flow recipe
  -> typed modules
  -> reviewed implementation for each module
  -> isolated execution plan
  -> deterministic evaluation and approval
```

Typical module classes include:

- deterministic heartbeat, readiness, evidence assembly, checkpoint, lint,
  test, schema validation, evaluation merge, and effect fencing;
- probabilistic research, analysis, writing, planning, building, and review;
- durable human approval;
- deterministic, idempotent commit, publication, or database-effect modules
  that require upstream authorization.

The private source-only scaffold currently contains 21 logical modules, 6
composed flows, 12 deployment profiles, and 23 implementation variants. Its
309-test suite passes. Those facts establish validated source, not deployment:
handlers, isolated pools, credentials, durable activation, qualification, and
an observe-only canary remain incomplete.

## LLM harnesses and deterministic verification

Logical modules bind to typed ports rather than one model vendor. A Codex,
Qwen, Factory Droid, or future harness may implement a compatible bounded
module after qualification. Harness selection does not grant authority.

```text
typed task + bounded context
            |
            v
     selected harness/model
            |
            v
      typed candidate artifact
            |
            v
schemas -> linters -> tests -> hashes -> policy -> receipt
            |
            v
       optional independent review
            |
            v
          owner/effect gate
```

Repository hooks are an explicit future extension to the deterministic gate
surface; they are not represented as universally deployed today. Model output
cannot waive a failed or unknown deterministic result, approve itself, publish,
deploy, commit, apply a database change, use a credential, or change policy.

## State and knowledge separation

| System | Question | Examples |
| --- | --- | --- |
| PostgreSQL | What work exists now? | jobs, leases, attempts, approvals, evidence |
| Git | What was reviewed and versioned? | source, configuration, diffs, releases |
| Artifact store | What exact output was produced? | packages, reports, manifests, candidates |
| Logs and receipts | What happened? | checks, transitions, effects, recovery |
| Knowledge memory | What have the factories learned? | decisions, incidents, runbooks, patterns |

Knowledge can inform a job but cannot become operational state merely because
an agent wrote persuasive prose.

## Recursive factory improvement

```text
factory run
  -> observation or failure
  -> retained evidence
  -> classified improvement candidate
  -> change to shared module/template/gate
  -> deterministic and independent validation
  -> owner/policy promotion
  -> eligible factory rollout with rollback
```

Evidence return exists at bounded operational scope. General automatic
classification, shared-template promotion, and rollout are still designed.
Recursive improvement therefore means the system learns through reviewed,
versioned artifacts—not that an agent recursively expands its own authority.

## Infrastructure composition

| Tool | Zaibatsu responsibility | Current maturity |
| --- | --- | --- |
| Git | source, intended state, history, releases | Operational at reviewed scope |
| SOPS/age | static encrypted secret material in Git | Validated preproduction |
| Bounded secret manager | runtime machine-secret delivery | Validated preproduction in the public ledger |
| OpenTofu | reviewed resource lifecycle and cost gate | Validated preproduction |
| Tailscale | private management fabric | Operational |
| Ansible | host reproduction and configuration | Validated preproduction |
| Nix | exact worker environments | Planned |
| cron | selected downstream schedules | Operational |
| systemd | primary durable services and schedules | Operational |
| PostgreSQL | durable jobs and bounded coordination | Validated preproduction broadly; narrow lane operational |
| Agent skeletons | reusable typed work graphs | Validated source only |
| LLM harnesses | replaceable probabilistic implementations | Bounded validation only |

## Production and recovery boundaries

Workers normally produce artifacts rather than changing production. Sensitive
publication, deployment, infrastructure, credentials, wallet or signing
operations, destructive changes, and data migrations require stronger policy
and explicit owner authority.

The owner retains a direct recovery path outside the normal Dispatcher route.
Backups, Git-defined configuration, encrypted recovery material, and operator
access must permit rebuilding the control layer when it is unavailable.
Dispatcher must never be required to recover Dispatcher.
