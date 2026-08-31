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

## Fourteen machine-readable views

Zaibatsu deliberately separates fourteen questions:

| Contract | Question |
| --- | --- |
| [`architecture/factory-model.json`](../architecture/factory-model.json) | What is a software factory, how is it reproduced and improved, and which factory instances exist? |
| [`architecture/system.json`](../architecture/system.json) | Which control-plane components execute the work, what is their maturity, and which invariants constrain them? |
| [`examples/economic-factory.json`](../examples/economic-factory.json) | Which policies and evidence bindings define one portable factory? |
| [`catalog/modules.json`](../catalog/modules.json) plus [`examples/economic-factory.plan.json`](../examples/economic-factory.plan.json) | Which compatible module implementations resolve into its deterministic control plan? |
| [`examples/economic-factory.bundle-manifest.json`](../examples/economic-factory.bundle-manifest.json) | Which exact definition, catalog, plan, selected module contracts, and schemas form its portable control bundle? |
| [`examples/factory-portfolio.json`](../examples/factory-portfolio.json) plus [`examples/factory-portfolio.plan.json`](../examples/factory-portfolio.plan.json) | Which verified factory bundles belong to one closed control portfolio, where may evidence return, and which intended namespaces remain factory-scoped? |
| [`examples/economic-factory.source-lock.json`](../examples/economic-factory.source-lock.json) | Which immutable annotated-release Git objects supplied the exact control files that reproduce that bundle? |
| [`policies/runtime-qualification-v1.json`](../policies/runtime-qualification-v1.json) plus [`examples/economic-factory.qualification-plan.json`](../examples/economic-factory.qualification-plan.json) | Which content-addressed evidence bindings are still required before those contracts can become runtime-eligible? |
| [`examples/economic-factory.qualification-evidence.json`](../examples/economic-factory.qualification-evidence.json) plus [`examples/economic-factory.qualification-assessment.json`](../examples/economic-factory.qualification-assessment.json) | Which requirements does the verified bundle itself actually prove, and exactly which runtime proofs remain missing? |
| [`policies/runtime-evidence-verifiers-v1.json`](../policies/runtime-evidence-verifiers-v1.json) plus [`examples/economic-factory.runtime-evidence.json`](../examples/economic-factory.runtime-evidence.json) | Which externally supplied assertions were signed by evaluator-selected keys under exact allowlists, provenance, scope, and freshness rules? |
| [`examples/economic-factory.runtime-evidence-pack-manifest.json`](../examples/economic-factory.runtime-evidence-pack-manifest.json) plus [`examples/economic-factory.runtime-assessment.json`](../examples/economic-factory.runtime-assessment.json) | Which exact evidence artifacts and verifier descriptors were retrieved and digest-verified, and what do those bytes still not prove or authorize? |
| [`examples/economic-factory.evidence-return.json`](../examples/economic-factory.evidence-return.json) | Which exact verified evidence pack is bound to which economic-factory bundle and declared evidence-only route, and which transport, interpretation, promotion, and effect claims remain false? |
| [`examples/economic-factory.improvement-proposal-spec.json`](../examples/economic-factory.improvement-proposal-spec.json) plus [`examples/economic-factory.improvement-proposal.json`](../examples/economic-factory.improvement-proposal.json) | Which exact untrusted shared-improvement suggestion is bound to that verified return, which later review gates are mandatory, and which classification, validation, promotion, rollout, and effect claims remain false? |
| [`examples/economic-factory.improvement-observation-spec.json`](../examples/economic-factory.improvement-observation-spec.json) plus [`examples/economic-factory.improvement-observation.json`](../examples/economic-factory.improvement-observation.json) | Which exact untrusted report is structurally normalized against returned evidence and a canonical subject, without claiming safety or semantic truth? |
| [`policies/improvement-classification-v1.json`](../policies/improvement-classification-v1.json) plus [`examples/economic-factory.improvement-classification.json`](../examples/economic-factory.improvement-classification.json) | Does the exact proposal/observation pair meet deterministic workflow/type rules for validation planning, and which validation, promotion, rollout, and effect authorities remain false? |
| [`examples/economic-factory.improvement-candidate-spec.json`](../examples/economic-factory.improvement-candidate-spec.json) plus [`examples/economic-factory.improvement-candidate.json`](../examples/economic-factory.improvement-candidate.json) | Which exact canonical non-executable candidate contract matches that eligible classification, and which safety, semantic, implementation, validation, promotion, and effect claims remain false? |
| [`examples/economic-factory.rebuild-plan.json`](../examples/economic-factory.rebuild-plan.json) | In which dependency order would a qualified factory be rebuilt, which direct and upstream blockers stop each action, and which separate gates still deny activation? |

The validator requires the factory registry and shared component maturities to
agree. A narrative edit cannot silently turn planned Nix reproduction or
source-only agents into operational capability.

## Multi-factory portfolio control

The portable factory contract proves one factory at a time. The portfolio
contract is the next control-layer join: it declares a closed registry with
exactly one control factory, at least one economic factory, and exactly one
evidence-only return route from every economic factory to the control factory.
Unknown or duplicate factories, class drift, missing routes, route reorder,
secret-bearing routes, authority grants, and self-promotion fail closed.

`portfolio-plan` receives the declarative portfolio and a set of canonical
factory bundles. It fully verifies every bundle before use, matches bundle
identity and class to the closed registry, and emits one deterministic plan in
declaration order. Bundle input order is irrelevant. Each factory record binds
the exact bundle, definition, catalog, factory-plan, module-API, and selected
scheduler-module digests. The example joins one control bundle and two
economic-factory bundles, including systemd and cron adapters.

The plan derives separate intended authority, repository, static-secret,
runtime-secret, worker-pool, artifact, and scheduler namespaces for every
factory. These 21 strings are disjoint by construction and make scope
collisions reviewable. They are not runtime isolation evidence: the plan does
not inspect process credentials, operating-system users, network policy,
databases, secret-manager ACLs, or scheduler state. It contains no runtime
implementations, routes no secret, invokes no model, executes no operation,
grants no cross-factory authority, authorizes no activation, and proves no
deployment or recovery.

## Route-bound evidence return

The portfolio declares where evidence may return; it does not carry any
evidence. The evidence-return contract joins that declared route to one
canonical runtime-evidence pack from the named economic factory. Before
deriving or accepting the record, the verifier rebuilds the portfolio plan,
fully verifies every bundle, matches the source factory and its single route,
and reverifies the pack against the exact source bundle, qualification plan,
policy, embedded materials, signatures, and allowlists.

The resulting digest makes route or source replay visible. It proves the exact
verified bytes were selected for the exact declared route. It does not observe
transport, scan the evidence for unsafe content or secrets, rerun verifier
assertions, prove artifact truth, classify an improvement candidate, change
shared policy, make anything promotion-eligible, or authorize activation,
execution, or cross-factory effects.

## Evidence-bound improvement proposal

The proposal contract is the next deliberately narrow recursive-improvement
join. Its first input is a typed but untrusted specification naming one shared
module, factory template, or deterministic gate and describing a proposed
addition, modification, or replacement. Its second input is the exact
route-bound evidence-return record. Before producing or accepting a proposal
record, the verifier repeats the complete evidence-return verification chain,
including the closed portfolio, every bundle, the source route, qualification
inputs, evidence pack, embedded materials, signatures, allowlists, and content
digests.

The resulting record binds the proposal specification's canonical JSON digest
to the evidence-return digest, runtime-evidence pack, reporting factory,
control factory, and route. The specification cannot omit content-safety,
candidate-classification, reporting-factory, independent-regression,
owner-policy, rollback, or cross-factory-privilege review requirements.

This records a suggestion; it does not accept one. The checked example does
not authenticate the proposer, scan the narrative, prove secret absence,
interpret source artifacts, normalize an observation, classify an improvement
candidate, establish merit, run a regression, verify rollback, change shared
policy, obtain owner approval, grant promotion or rollout eligibility,
activate anything, execute anything, or authorize a cross-factory effect.

## Structural normalization and candidate classification

The observation contract accepts one typed report—an observation, failure,
artifact outcome, or reported correction—and binds its canonical JSON digest to
the same fully reverified evidence return. Its subject vocabulary matches the
proposal target vocabulary. “Structurally normalized” means only that the
record has a bounded canonical category, subject, narrative, evidence source,
and digest. The reporter is not authenticated, the content is not safety- or
secret-scanned, and neither the source artifact nor report is called true.

The classification contract then reverifies the complete proposal and
observation chains under a separately hashed deterministic policy. It checks
same-source binding, subject/target alignment, allowed observation kind and
operation, complete later-review requirements, and non-authorizing input
boundaries in fixed order. A valid mismatch is retained as `not_classified`;
forged or unverifiable input is rejected before classification.

The checked result maps the aligned deterministic-gate target to
`deterministic_gate_candidate` and makes it eligible to create a validation
plan. This is workflow/type classification, not a judgment that the report is
safe, true, useful, or meritorious. It creates no validation plan, authorizes no
test execution or mutation, changes no policy, obtains no approval, and grants
no promotion, rollout, activation, execution, or cross-factory authority.

## Evidence-bound candidate contract

Classification alone names only a target and operation. The candidate contract
closes the next reproducibility gap by embedding one exact canonical shared
module, factory template, or deterministic-gate contract in a schema-bound
specification. Before producing or accepting its binding record, the verifier
repeats the complete classification, proposal, observation, evidence-return,
portfolio, bundle, qualification, evidence-pack, signature, and material chain.
It then requires the artifact target to exactly equal the classified target and
records the specification digest, artifact digest, and canonical byte count.

The checked artifact is a 1,130-byte deterministic-gate contract with typed
inputs, outputs, ordered checks, fail-closed behavior, and an explicit
contract-only authority boundary. It contains no executable implementation.
The binding proves identity, structure, lineage, and target alignment only. It
does not scan content or secrets, establish semantic correctness, create or run
a validation plan, pass either regression scope, verify rollback, obtain owner
approval, change shared policy, or authorize promotion, rollout, activation,
execution, or cross-factory effects.

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

`verify-runtime-evidence` adds a separate OpenSSH signature layer. Every signed
payload binds the factory, bundle, qualification plan and policy, verifier
registry, module position/slot/ID/artifact, requirement, scope, evidence-artifact
digest, verifier/method/implementation digest, validity interval, and false
activation/execution flags. The content-addressed registry restricts each key
to exact factories, scopes, requirements, methods, and maximum validity.
`evidence-pack` then places the signed set, registry, every referenced evidence
artifact and verifier descriptor, and the immutable manifest schema into a
canonical USTAR archive. `verify-evidence-pack` rejects unsafe or noncanonical
archives, exact-member drift, schema substitution, material digest mismatch,
registry replay, and signature failure before exposing any embedded document.
`runtime-assessment` combines fresh assertions from that verified pack with the
nine bundle-derived contract receipts at an explicit `evaluated_at` time.

The public key is intentionally fixture-only: its registry permits only
`public_test_fixture` and `source_revision`. The signature passes, but the scope
can never yield runtime eligibility. The checked assessment therefore records
10 verified bindings, 57 missing, and zero eligible modules. Signature validity
does not prove who owns the key, organizational independence, verifier
correctness, or artifact truth. The evaluator selects and must separately pin
and review the registry. v1.10 retrieves and digest-verifies the exact artifact
and verifier descriptor, but it neither reruns the verifier assertion nor
infers semantic truth from those bytes.

`rebuild-plan` then joins the fully reverified bundle, source lock,
qualification policy and plan, bundle-derived evidence, canonical
runtime-evidence pack, embedded materials, verifier registry, signed runtime
evidence, and runtime assessment. It converts the same
nine module slots into an action DAG, preserves their dependency edges, records
direct missing-evidence and upstream blockers separately, and terminates in
four gates: control artifacts reverified, all modules runtime-qualified, owner
activation approval, and factory activation. The public example has zero
qualification-ready actions and 57 missing evidence bindings. The first gate
passes because all control inputs were reverified; that pass grants no effect
authority and cannot satisfy the three later gates.

The action names describe intended future operations. The generator and
verifier do not run Ansible, realize Nix, read or materialize secrets, install
or enable a scheduler, invoke a model, create qualification evidence, obtain
owner approval, activate a factory, deploy infrastructure, or prove runtime
recovery. A reordered node, changed dependency, different input, inflated
status, or false authority bit makes exact verification fail.

Generated-key tests supply every non-contract requirement for the source module
under `factory_runtime` scope and prove that it becomes
`qualified_not_authorized`. They simultaneously prove that no action gains
execution or side-effect authority and that the overall factory gate remains
blocked. This demonstrates a reachable qualification path without implementing
promotion or execution.

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
  -> exact candidate contract binding
  -> change to shared module/template/gate
  -> deterministic and independent validation
  -> owner/policy promotion
  -> eligible factory rollout with rollback
```

Evidence return, non-authorizing proposal recording, structural observation
normalization, deterministic workflow/type classification, and exact
non-executable candidate-contract binding exist at bounded operational
public-kit scope. Semantic review, content-safety handling, implementation,
validation planning or execution, shared-template promotion, and rollout are
still designed. Recursive improvement therefore means the system learns
through reviewed, versioned artifacts—not that an agent recursively expands
its own authority.

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
