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
| Recursive improvement | Return evidence and improve shared factory patterns | Route-bound evidence return, non-authorizing proposal recording, structural observation normalization, and deterministic candidate classification for validation planning are operational in the public kit; transport, semantic truth, safety, validation execution, and shared promotion remain unproved or designed and owner-gated |
| Multi-factory portfolio plan | Join verified control bundles into one closed registry with evidence-only return routes and factory-scoped intended namespaces | Implemented and tested as a non-executing control plan; it proves bundle identity and declarative separation, not deployed runtime isolation or authority |
| Qualification planner | Bind a verified control bundle to mandatory runtime evidence requirements | Implemented and tested; the public plan contains no qualification evidence and grants no eligibility or activation |
| Signed runtime-evidence assessment | Combine bundle-derived contract receipts with fresh, allowlisted OpenSSH-signed verifier assertions | The public fixture verifies one signature in test-only scope: 10 of 67 bindings verified, 57 missing, zero runtime-eligible modules, and no activation or execution authority |
| Canonical runtime-evidence pack | Carry the signed evidence, verifier registry, exact evidence artifacts, verifier descriptors, and manifest schema as one reproducible archive | Implemented and tested; byte and digest integrity are verified, but verifier assertions are not rerun and artifact truth is not inferred |
| Route-bound factory evidence return | Bind one verified pack to its exact economic-factory bundle and declared evidence-only route into the control factory | Implemented and tested as a non-authorizing record; transport, content safety, classification, promotion, activation, execution, and cross-factory effects remain false |
| Evidence-bound improvement proposal | Bind one typed, untrusted shared-module, factory-template, or deterministic-gate suggestion to exact returned evidence | Implemented and tested as a review input; proposer authentication, safety, normalization, classification, merit, regression, rollback, approval, promotion, rollout, activation, execution, and cross-factory effects remain false |
| Evidence-bound observation normalization | Bind one typed, untrusted observation, failure, artifact outcome, or correction to exact returned evidence and a canonical subject | Implemented and tested as structural normalization only; content safety, reporter authentication, semantic truth, classification, merit, promotion, execution, and cross-factory effects remain false |
| Deterministic candidate classification | Join one exact proposal and normalized observation under a non-authorizing policy | Implemented and tested for workflow/type classification and validation-planning eligibility only; no safety, semantic truth, merit, validation execution, approval, promotion, rollout, activation, execution, or cross-factory effect is proved |
| Annotated-release source lock | Bind one verified control bundle to exact versioned source inputs | Sixteen Git blobs from immutable v1.6.0 rebuild the byte-identical bundle; no remote, signature, runtime-source, qualification, eligibility, or activation proof is claimed |
| Deterministic rebuild DAG | Join verified control provenance, module dependencies, qualification gaps, and activation gates | Implemented and tested as an inert nine-action plan; zero actions are qualification-ready, all nine remain blocked, and no execution or effect authority is granted |

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
- completed runtime qualification of any public bundle module;
- completed consolidation of every private product repository.

Source, tests, and a deployment plan are evidence classes—not proof that a
capability is running. See [Implementation status](docs/implementation-status.md)
for the full claim ledger.

## Quickstart

The public validator uses Python's standard library plus the OpenSSH
`ssh-keygen` binary for detached-signature verification:

```bash
git clone https://github.com/adaliontech/Zaibatsu.git
cd Zaibatsu
make validate
```

`make validate` checks the project-owned schemas, architecture contracts,
portable factory example, content-addressed module artifacts, resolved control
plan, portable bundle manifest, closed multi-factory portfolio plan,
annotated-release source lock, qualification
policy and plan, bundle-derived evidence, signed runtime evidence, runtime
assessment, route-bound evidence-return record, deterministic rebuild DAG,
evidence-bound improvement-proposal specification and record, structurally
normalized observation, validation-planning-only classification, sanitized
receipts, factory hierarchy
and lifecycle, maturity boundaries, submission gates, public-safety rules,
local links, and adversarial mutations. No model request, network access, cloud
account, secret, Ansible or Nix execution, or production system is required.

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

## Compose a factory control plan

The versioned [`catalog/modules.json`](catalog/modules.json) describes reusable
module implementations for the nine control slots and binds each one to a
SHA-256-addressed contract artifact under [`catalog/modules/`](catalog/modules/).
A binding is compatible when its declared policy value matches the factory
policy; the implementation ID itself is replaceable. Resolve the example,
verify the checked-in plan, and prove a second compilation is byte-identical:

```bash
python3 scripts/zaibatsu.py catalog-check
python3 scripts/zaibatsu.py plan examples/economic-factory.json \
  --output /tmp/example-product.plan.json
python3 scripts/zaibatsu.py verify-plan \
  /tmp/example-product.plan.json examples/economic-factory.json
python3 scripts/zaibatsu.py rebuild-check examples/economic-factory.json
```

The plan records canonical SHA-256 digests for both inputs, resolves dependency
order, preserves module implementation boundaries, and carries an explicit
least-authority claim. It proves reproducible **control-plan composition only**.
It does not install Ansible roles, build a Nix environment, create schedules,
contact a model, deploy infrastructure, or prove runtime recovery.

Package the complete selected control surface into a canonical archive and
verify it without extraction:

```bash
python3 scripts/zaibatsu.py bundle examples/economic-factory.json \
  --output /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py verify-bundle \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py inspect-bundle \
  /tmp/example-product.factory.tar
```

The uncompressed USTAR bundle is byte-reproducible and includes the canonical
factory definition, complete catalog, resolved plan, nine selected module
contract artifacts, five JSON Schemas, and a per-file digest manifest. The
verifier denies traversal paths, links, special files, duplicate or extra
members, noncanonical metadata or JSON, schema or payload tampering, and
trailing data. The bundle contains **contracts, not runtimes**: every module
artifact explicitly says that no implementation, entrypoint, environment lock,
deployment authority, or runtime-recovery proof is included.

To inspect a real module substitution, build the cron-scheduled public variant
and compare the two verified bundles:

```bash
python3 scripts/zaibatsu.py bundle examples/economic-factory-cron.json \
  --output /tmp/example-product-cron.factory.tar
python3 scripts/zaibatsu.py compare-bundles \
  /tmp/example-product.factory.tar \
  /tmp/example-product-cron.factory.tar
```

The comparison reports one `scheduling` implementation replacement from
`systemd-scheduler` to `cron-scheduler`. The module catalog and five schemas
remain unchanged, while the factory definition and resolved plan receive new
content digests. Both sides still report runtime ineligible: comparison proves
a modular control-contract change, not scheduler activation.

## Coordinate a closed portfolio of factories

Build separate control bundles for one control factory and two economic
factories, then compile them into one deterministic factory-of-factories view:

```bash
python3 scripts/zaibatsu.py bundle examples/control-factory.json \
  --output /tmp/example-control.factory.tar
python3 scripts/zaibatsu.py bundle examples/service-factory.json \
  --output /tmp/example-service.factory.tar
python3 scripts/zaibatsu.py portfolio-plan \
  examples/factory-portfolio.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar \
  --output /tmp/example-portfolio.plan.json
python3 scripts/zaibatsu.py verify-portfolio-plan \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar
```

The checked [portfolio](examples/factory-portfolio.json) declares exactly one
control factory, two economic factories, and one evidence-only return route
from each economic factory. The generated [portfolio
plan](examples/factory-portfolio.plan.json) fully verifies every bundle, binds
their exact digests and selected scheduler adapters, and generates 21 disjoint
intended authority, repository, secret, worker, artifact, and scheduler
namespaces. Bundle input order does not affect the plan; declared registry
order does.

This is the missing public control-layer join, not a deployment claim. The
namespaces are deterministic intended scopes rather than evidence of operating
system, network, process, credential, or database isolation. The plan contains
no runtime implementations, routes no secrets, invokes no model, executes no
operation, grants no cross-factory authority, and authorizes no activation.

## Lock bundle sources to an immutable release

Prove which exact versioned control inputs produced the verified bundle rather
than trusting files in the current checkout:

```bash
python3 scripts/zaibatsu.py source-lock \
  examples/economic-factory.json \
  /tmp/example-product.factory.tar \
  --release-tag v1.6.0 \
  --output /tmp/example-product.source-lock.json
python3 scripts/zaibatsu.py verify-source-lock \
  /tmp/example-product.source-lock.json \
  /tmp/example-product.factory.tar
```

The checked-in [source lock](examples/economic-factory.source-lock.json) binds
the definition, catalog, nine selected module contracts, and five schemas to
the annotated `v1.6.0` tag object, commit, tree, and individual Git blobs. It
records each repository-native object ID and a SHA-256 digest of every Git
object payload or file, rebuilds the bundle only from those immutable blobs,
and requires byte-identical output. Dirty working-tree files and Git
replacement objects cannot affect the result.

This is deliberately **control-source provenance only**. It does not contact a
remote repository, authenticate repository ownership, verify a tag signature,
contain runtime implementation source, satisfy a runtime qualification
binding, grant eligibility or activation, or deploy infrastructure. Because
the checked lock references an earlier release, verification requires full Git
history with the annotated `v1.6.0` tag available; a shallow `v1.7.0` clone is
not sufficient.

## Plan runtime qualification

Turn the verified bundle into a content-addressed list of evidence required
before its selected modules could become runtime-eligible:

```bash
python3 scripts/zaibatsu.py qualification-plan \
  /tmp/example-product.factory.tar \
  --output /tmp/example-product.qualification-plan.json
python3 scripts/zaibatsu.py verify-qualification-plan \
  /tmp/example-product.qualification-plan.json \
  /tmp/example-product.factory.tar
```

The default [qualification policy](policies/runtime-qualification-v1.json)
requires content-addressed implementation, source, environment, conformance,
and recovery evidence for every module, plus slot-specific proofs. For the
public example that resolves to 67 missing bindings across 27 requirement
types. The checked-in [qualification
plan](examples/economic-factory.qualification-plan.json) marks zero of nine
modules runtime-eligible. It is a reproducible request for missing evidence,
not evidence itself: self-attestation is rejected, qualification never grants
activation, and owner approval remains a separate prerequisite.

Derive the evidence the bundle can actually prove, then assess it against the
complete plan:

```bash
python3 scripts/zaibatsu.py qualification-evidence \
  /tmp/example-product.qualification-plan.json \
  /tmp/example-product.factory.tar \
  --output /tmp/example-product.qualification-evidence.json
python3 scripts/zaibatsu.py verify-qualification-evidence \
  /tmp/example-product.qualification-evidence.json \
  /tmp/example-product.qualification-plan.json \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py qualification-assessment \
  /tmp/example-product.qualification-evidence.json \
  /tmp/example-product.qualification-plan.json \
  /tmp/example-product.factory.tar \
  --output /tmp/example-product.qualification-assessment.json
python3 scripts/zaibatsu.py verify-qualification-assessment \
  /tmp/example-product.qualification-assessment.json \
  /tmp/example-product.qualification-evidence.json \
  /tmp/example-product.qualification-plan.json \
  /tmp/example-product.factory.tar
```

Bundle verification already proves that each selected module contract exactly
matches its catalog entry, project schema reference, and content digest. That
produces nine reproducible `contract_conformance_receipt` bindings. The public
[evidence set](examples/economic-factory.qualification-evidence.json) and
[assessment](examples/economic-factory.qualification-assessment.json) credit
only those facts: 9 of 67 bindings verified, 58 missing, and zero modules
runtime-eligible. They include no implementation, environment, isolation,
recovery, independent external-verifier, activation, or deployment proof.

Add externally supplied signed assertions through a separately hashed verifier
registry, package the exact referenced materials, then evaluate freshness at an
explicit timestamp:

```bash
python3 scripts/zaibatsu.py verify-runtime-evidence \
  examples/economic-factory.runtime-evidence.json \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py evidence-pack \
  examples/economic-factory.runtime-evidence.json \
  /tmp/example-product.factory.tar \
  --evidence-artifact examples/runtime-evidence/source-revision-fixture.json \
  --verifier-implementation examples/runtime-evidence/fixture-verifier-method.json \
  --output /tmp/example-product.runtime-evidence.tar
python3 scripts/zaibatsu.py verify-evidence-pack \
  /tmp/example-product.runtime-evidence.tar \
  /tmp/example-product.factory.tar \
  --manifest-output /tmp/example-product.runtime-evidence-pack-manifest.json
python3 scripts/zaibatsu.py runtime-assessment \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-evidence.json \
  examples/economic-factory.qualification-plan.json \
  /tmp/example-product.factory.tar \
  --as-of 2026-08-30T23:00:00Z \
  --output /tmp/example-product.runtime-assessment.json
python3 scripts/zaibatsu.py verify-runtime-assessment \
  /tmp/example-product.runtime-assessment.json \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-evidence.json \
  examples/economic-factory.qualification-plan.json \
  /tmp/example-product.factory.tar
```

The checked [verifier registry](policies/runtime-evidence-verifiers-v1.json)
contains a public key, exact factory/scope/requirement/method allowlists, a
verifier-implementation digest, and a maximum validity interval. Its one signed
[runtime-evidence receipt](examples/economic-factory.runtime-evidence.json) is
deliberately restricted to `public_test_fixture`; it demonstrates signature,
provenance, allowlist, replay, and freshness checks but can never make a module
runtime-eligible. The [checked pack
manifest](examples/economic-factory.runtime-evidence-pack-manifest.json) binds
that evidence and registry to the exact fixture artifact, verifier-method
descriptor, and manifest schema carried in the canonical archive. The resulting [runtime
assessment](examples/economic-factory.runtime-assessment.json) records 10 of 67
bindings verified, 57 missing, and zero eligible modules.

This trust boundary is intentionally narrow. The registry is an explicit
evaluator-selected trust input; its content digest proves which keys and rules
were selected, not who owns a key or whether its operator is organizationally
independent. A valid signature authenticates the exact assertion payload, not
the assertion's semantic truth. Zaibatsu retrieves the exact referenced
artifact and verifier descriptor from the verified pack, but does not rerun
the named verifier or infer that the artifact makes its assertion true. A production `factory_runtime` assessment
therefore requires a separately reviewed and pinned registry, a trusted
verifier allowed for every exact binding, and a current externally chosen
`--as-of` time. Even complete runtime qualification grants no activation,
execution, secret, deployment, or side-effect authority.

The v1 pack format accepts canonical JSON-object materials only, capped at
256 KiB per member, 16 MiB per archive, 256 receipts, and 516 archive members.
Binary artifacts or executable verifier implementations need a future typed
format; this release embeds JSON evidence and verifier descriptors, not code it
can execute.

## Bind returned evidence to its factory route

After building the three bundles, portfolio plan, and runtime-evidence pack
above, derive the exact non-authorizing record for the product factory's
declared route into the control factory:

```bash
python3 scripts/zaibatsu.py evidence-return-record \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar \
  --output /tmp/example-product.evidence-return.json
python3 scripts/zaibatsu.py verify-evidence-return-record \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar
```

The checked [evidence-return record](examples/economic-factory.evidence-return.json)
reverifies the closed portfolio, every bundle, the source factory and route,
the evidence pack, its embedded materials, signatures, allowlists, and content
digests. It then binds those exact identities into one canonical digest.

This is evidence provenance and routing intent, not transport telemetry or an
improvement decision. The record explicitly says it did not observe delivery,
scan content safety, prove secret absence, rerun verifier assertions, establish
artifact truth, classify an improvement, make it promotion-eligible, authorize
activation or execution, or grant any cross-factory effect.

## Record an evidence-bound improvement proposal

Use a typed proposal specification to record one suggestion against that exact
returned evidence:

```bash
python3 scripts/zaibatsu.py improvement-proposal-record \
  examples/economic-factory.improvement-proposal-spec.json \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar \
  --output /tmp/example-product.improvement-proposal.json
python3 scripts/zaibatsu.py verify-improvement-proposal-record \
  /tmp/example-product.improvement-proposal.json \
  examples/economic-factory.improvement-proposal-spec.json \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar
```

The checked [proposal specification](examples/economic-factory.improvement-proposal-spec.json)
names a deterministic-gate suggestion and requires every later review class.
The derived [proposal record](examples/economic-factory.improvement-proposal.json)
reverifies the complete evidence-return chain and binds the specification's
canonical JSON digest to its reporting factory, control factory, route, and
runtime-evidence pack.

This record is proposal intake, not recursive authority. By itself it does not
authenticate the proposer, trust or scan the narrative, normalize an
observation, classify the suggestion, establish merit, run reporting-factory
or independent regressions, verify rollback, change policy, obtain approval,
grant promotion or rollout eligibility, activate, execute, or authorize a
cross-factory effect.

## Normalize and classify an improvement candidate

Bind one typed, explicitly untrusted observation to the same returned evidence,
then classify the exact proposal/observation pair under a deterministic policy:

```bash
python3 scripts/zaibatsu.py improvement-observation-record \
  examples/economic-factory.improvement-observation-spec.json \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar \
  --output /tmp/example-product.improvement-observation.json
python3 scripts/zaibatsu.py verify-improvement-observation-record \
  /tmp/example-product.improvement-observation.json \
  examples/economic-factory.improvement-observation-spec.json \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar
python3 scripts/zaibatsu.py classify-improvement-proposal \
  policies/improvement-classification-v1.json \
  /tmp/example-product.improvement-proposal.json \
  examples/economic-factory.improvement-proposal-spec.json \
  /tmp/example-product.improvement-observation.json \
  examples/economic-factory.improvement-observation-spec.json \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar \
  --output /tmp/example-product.improvement-classification.json
python3 scripts/zaibatsu.py verify-improvement-classification \
  /tmp/example-product.improvement-classification.json \
  policies/improvement-classification-v1.json \
  /tmp/example-product.improvement-proposal.json \
  examples/economic-factory.improvement-proposal-spec.json \
  /tmp/example-product.improvement-observation.json \
  examples/economic-factory.improvement-observation-spec.json \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar
```

The checked observation is normalized only in the structural sense: its exact
canonical category, subject, narrative, source evidence, and digest are bound.
Zaibatsu does not call the report safe or true. The checked classification
reverifies the full proposal and observation chains, requires the same evidence
return and matching subject/target, and maps the target to a canonical candidate
class. `classified_for_validation_planning` means only that a later validation
plan may be created. It does not authorize that plan to run, establish merit,
approve promotion, change shared policy, roll out, activate, execute, or affect
another factory.

## Plan the factory rebuild

Compile the verified control and qualification state into an ordered,
machine-readable rebuild graph:

```bash
python3 scripts/zaibatsu.py rebuild-plan \
  /tmp/example-product.factory.tar \
  --runtime-evidence-pack /tmp/example-product.runtime-evidence.tar \
  --output /tmp/example-product.rebuild-plan.json
python3 scripts/zaibatsu.py verify-rebuild-plan \
  /tmp/example-product.rebuild-plan.json \
  /tmp/example-product.factory.tar \
  --runtime-evidence-pack /tmp/example-product.runtime-evidence.tar
```

Both commands fully reverify the bundle, annotated-release source lock,
qualification policy and plan, bundle-derived evidence, signed runtime-evidence
pack, embedded materials, verifier registry, and runtime assessment. The resulting [rebuild
plan](examples/economic-factory.rebuild-plan.json) binds their exact digests
and expresses the nine module slots as a dependency-ordered action DAG. Each
node records its intended operation, verified evidence, direct missing
evidence, upstream blockers, and false execution authority. Four gates keep
control-artifact verification, complete runtime qualification, explicit owner
approval, and factory activation separate.

For the public contracts, the graph reports 10 of 67 evidence bindings verified,
57 missing, zero qualification-ready actions, and all nine actions blocked.
Names such as `apply_host_configuration` and `realize_worker_environment` are
intents, not executed commands. Generation and verification read no secrets,
run no Ansible or Nix, install no scheduler, invoke no model, grant no approval,
activate nothing, deploy nothing, and prove no runtime recovery. Generated-key
tests prove that a complete, fresh `factory_runtime` evidence set can advance
one module to `qualified_not_authorized`; the same tests prove that this state
still carries false execution and side-effect authority and leaves the factory
activation gate blocked.

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
- [Portable factory definitions](examples/economic-factory.json) — reusable
  systemd and [cron](examples/economic-factory-cron.json) contract variants
  for a new control or economic factory.
- [Factory portfolio](examples/factory-portfolio.json) and [deterministic
  portfolio plan](examples/factory-portfolio.plan.json) — one verified control
  bundle plus two verified economic-factory bundles joined through a closed
  registry, disjoint intended namespaces, and non-authorizing evidence routes.
- [Reusable module catalog](catalog/modules.json), [module contract
  artifacts](catalog/modules/), [example control
  plan](examples/economic-factory.plan.json), and [bundle
  manifest](examples/economic-factory.bundle-manifest.json) — independently
  hashed module contracts resolved and packaged into a dependency-ordered,
  reproducible control bundle.
- [Annotated-release source lock](examples/economic-factory.source-lock.json)
  — the exact Git tag, commit, tree, and sixteen blobs that reproduce the
  verified control bundle, with explicit remote, signature, runtime,
  qualification, activation, and deployment nonclaims.
- [Qualification policy](policies/runtime-qualification-v1.json) and [example
  qualification plan](examples/economic-factory.qualification-plan.json) —
  content-addressed missing-evidence requirements with no runtime or activation
  authority.
- [Qualification evidence](examples/economic-factory.qualification-evidence.json)
  and [partial assessment](examples/economic-factory.qualification-assessment.json)
  — reproducible contract-only receipts, exact remaining gaps, and no runtime
  eligibility or activation authority.
- [Runtime verifier registry](policies/runtime-evidence-verifiers-v1.json),
  [signed evidence](examples/economic-factory.runtime-evidence.json), [pack
  manifest](examples/economic-factory.runtime-evidence-pack-manifest.json), and
  [runtime assessment](examples/economic-factory.runtime-assessment.json) —
  exact public keys, allowlists, provenance, freshness, embedded artifact and
  verifier-material digests, remaining gaps, and an explicitly fixture-only
  non-authorizing signature example.
- [Route-bound evidence-return record](examples/economic-factory.evidence-return.json)
  — the exact verified pack, source bundle, portfolio, and evidence-only route,
  with transport, classification, promotion, activation, execution, and
  cross-factory effects explicitly denied.
- [Improvement-proposal specification](examples/economic-factory.improvement-proposal-spec.json)
  and [evidence-bound record](examples/economic-factory.improvement-proposal.json)
  — one exact untrusted shared-change suggestion, its mandatory later review
  gates, and explicit denials of classification, validation, promotion,
  rollout, execution, and cross-factory authority.
- [Improvement-observation specification](examples/economic-factory.improvement-observation-spec.json)
  and [structurally normalized record](examples/economic-factory.improvement-observation.json)
  — one exact untrusted report bound to its evidence and canonical subject,
  without safety, truth, merit, or authority claims.
- [Classification policy](policies/improvement-classification-v1.json) and
  [checked classification](examples/economic-factory.improvement-classification.json)
  — deterministic workflow classification for validation planning only, with
  validation execution, approval, promotion, rollout, activation, execution,
  and cross-factory effects explicitly denied.
- [Factory rebuild plan](examples/economic-factory.rebuild-plan.json) — the
  exact nine-action dependency graph, evidence blockers, and four
  non-authorizing gates derived from fully reverified control inputs.
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
3. A portfolio has exactly one control factory; each economic factory retains
   separate intended authority, repository, secret, worker, artifact, and
   scheduler namespaces.
4. Cross-factory routes carry evidence only and grant no authority or
   self-promotion.
5. Every workload has exactly one scheduler of record.
6. Git versions intended state; plaintext secrets never enter Git.
7. Ansible and Nix serve different reproduction boundaries, and Nix remains
   planned until independently reproduced.
8. Agent skeletons are modular contracts, not autonomous production authority.
9. LLM harnesses are interchangeable workers behind deterministic entry and
   exit gates.
10. Module IDs select implementations; declared policy compatibility decides
   whether a module may fill a factory slot.
11. A module artifact, plan, or bundle is accepted only when every canonical
   digest, member, dependency, and least-authority boundary matches.
12. A qualification plan lists missing evidence; it is not evidence, runtime
    eligibility, activation authority, or owner approval.
13. Content addressing proves evidence identity, not truth; a signed assertion
    counts only under the exact evaluator-selected key, factory, scope,
    requirement, method, implementation digest, and validity interval.
14. A source lock proves exact local Git-object lineage for control contracts;
    it does not prove remote ownership, signature trust, or runtime source.
15. A signature authenticates an assertion; it does not prove key ownership,
    organizational independence, verifier correctness, or artifact truth.
16. A route-bound evidence-return record proves exact provenance and declared
    routing intent; it proves no transport, content safety, classification,
    promotion, activation, execution, or cross-factory effect.
17. An evidence-bound proposal proves which untrusted suggestion was recorded;
    it does not authenticate, normalize, classify, validate, approve, promote,
    roll out, activate, or execute that suggestion.
18. Structural observation normalization proves canonical form, evidence
    binding, and subject category; it does not prove safety or semantic truth.
19. Candidate classification permits validation planning only; it does not
    establish merit or authorize validation, mutation, promotion, or execution.
20. A rebuild plan reports intended actions and blockers; it executes no action
    and grants no qualification, approval, activation, deployment, or recovery
    authority.
21. Tests, schemas, linters, hashes, policy, receipts, and owner approval
    outrank model confidence.
22. Feedback may propose shared improvement but cannot self-promote.
23. Failed work remains inspectable, and the owner retains a recovery path
    outside Dispatcher.

## Factory Guild submission

The intended submission is an open-source project plus technical article and
short demo. Immutable `v1.1.0` passed a credential-disabled public-clone proof
and independent GitHub CI. Immutable `v1.1.1` added reusable contracts and
harder evidence validation and passed its own anonymous-clone and CI proof.
The `v1.1.2` candidate corrects the portable schema URI for definitions created
outside this repository and passed its own anonymous-clone and CI proof.
Immutable `v1.2.0` through `v1.4.0` then proved module composition, portable
bundles, and semantic comparison at their scoped public boundaries. The
qualification-plan candidate passed the same credential-disabled clone and
independent-CI boundary; immutable `v1.5.0` and its tag clone passed the full
release proof. The bundle-derived qualification-evidence candidate passed the
same 163-test credential-disabled clone and independent-CI boundary; immutable
`v1.6.0` and its tag clone passed the full release proof. The final demo and
applicant-owned form materials remain external submission gates. The `v1.7.0`
annotated-release control-source-lock candidate passed its own 173-test
full-history clone, schema, secret-scan, determinism, and independent-CI
boundary; immutable `v1.7.0` and its full-history tag clone passed the complete
release proof. The v1.8.0 rebuild-DAG candidate passed its 183-test
credential-disabled full-history clone, strict schema,
secret-scan, exact-regeneration, non-authorizing semantic, and independent-CI
boundary. Immutable `v1.8.0` and its full-history tag clone passed the complete
release proof. The v1.9.0 signed runtime-evidence candidate passed its 194-test,
87-file credential-disabled full-history clone, both Gitleaks modes, strict
Draft 2020-12 schema validation, exact artifact regeneration, signature and
non-authorizing semantic checks, and independent CI boundary. Its immutable
release uses annotated tag object `8667e6a104fa0e9fd44568847015d37de3c3e442`
over evidence roof `6502a2e6ade2ef3a6c6d6c4ad6656dbf8d7b889c`;
roof and tag CI, a credential-disabled full-history tag clone, four live-schema
byte checks, exact regeneration, and strict external schema validation all
passed. GitHub reports the release as immutable. The v1.10 candidate at
`359cc1bf4c28c4b8dc73f210c685820ee15475c4` adds the canonical
runtime-evidence pack and passed 203 tests, 90-file validation, exact artifact
regeneration, both Gitleaks modes, and five strict schemas from a
credential-disabled full-history clone; [candidate CI run
33342847863](https://github.com/adaliontech/Zaibatsu/actions/runs/33342847863)
also passed. Immutable [v1.10.0](https://github.com/adaliontech/Zaibatsu/releases/tag/v1.10.0)
uses annotated tag object `22e571aa87654a57b11a5038cfabdbc986432a85`
over evidence roof `535ebadec3fa15bf4cebddef96bad345371c62f3`;
[roof CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33342922185),
[tag CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33342972482),
a second credential-disabled full-history tag clone, three live-schema byte
checks, exact regeneration, both Gitleaks modes, and strict external schema
validation passed. GitHub reports v1.10.0 immutable, non-draft, and
non-prerelease. The v1.11 candidate at
`e4155072ec03f4eca502b12f5ca813e9cfaf0d8f` adds the closed multi-factory
portfolio plan and passed 212 tests, 97-file validation, both Gitleaks modes,
seven strict schemas, exact three-bundle plan regeneration, and independent
[candidate CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33355699088).
Immutable [v1.11.0](https://github.com/adaliontech/Zaibatsu/releases/tag/v1.11.0)
uses annotated tag object `ce1140db6fdcb85116ccb4ec6158b3751763a13b`
over evidence roof `b5d2b15911a34148df18bd49f94a3ced08e52ac9`;
[roof CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33355839619),
[tag CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33355871092),
a credential-disabled full-history tag clone, two live-schema byte checks,
exact portfolio regeneration, both Gitleaks modes, and strict external schema
validation passed. GitHub reports v1.11.0 immutable, non-draft, and
non-prerelease. The v1.12 route-bound evidence-return candidate at
`7eeb58ed132e8e32c395d0d6e2e81721cb0a83bd` passed 221 tests, 100-file
validation, a credential-disabled full-history clone, both Gitleaks modes,
eight strict schemas, exact regeneration, and independent
[candidate CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33356978139).
Immutable [v1.12.0](https://github.com/adaliontech/Zaibatsu/releases/tag/v1.12.0)
uses annotated tag object `d73fa379bb2db703e9775493bbd031d6199bc755`
over evidence roof `e1bed841c5d519426ef4fd36244ce0f366d58441`;
[roof CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33357109791),
[tag CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33357140454),
a credential-disabled full-history tag clone, eight strict schemas, exact
portfolio and evidence-return regeneration, both Gitleaks modes, and the live
tagged-schema byte check passed. GitHub reports v1.12.0 immutable, non-draft,
and non-prerelease.

The v1.13 evidence-bound improvement-proposal candidate at
`bc3381ac7889fef4b61f837d20a030cc28ee6f0a` passed 230 tests, 105-file
validation, strict Git, both checksum-pinned Gitleaks 8.30.1 modes, ten strict
Draft 2020-12 schemas, and byte-identical portfolio-plan, evidence-return, and
proposal regeneration from a credential-disabled full-history clone.
[Candidate CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33358242999)
passed independently. The proposal records exact untrusted intent while every
classification, validation, promotion, rollout, execution, and cross-factory
authority claim remains false. Immutable
[v1.13.0](https://github.com/adaliontech/Zaibatsu/releases/tag/v1.13.0) uses
annotated tag object `6ea9da6729475b275a65d564ab4dce585325384b` over evidence
roof `90921a43c2eb8fda3fe74a70db06ce52a617416c`;
[roof CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33358390313),
[tag CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33358425856), a
credential-disabled full-history tag clone, ten strict schemas, exact
portfolio/return/proposal regeneration, both Gitleaks modes, and two live
tagged-schema byte checks passed. GitHub reports v1.13.0 immutable, non-draft,
and non-prerelease.

The v1.14 structural-observation and deterministic-classification candidate at
`b4a34021ed6851c63f1ade291b5eb40128ea90f8` passed 241 tests, 115-file
validation, strict Git, both checksum-pinned Gitleaks 8.30.1 modes, fourteen
strict Draft 2020-12 schema/instance pairs, and byte-identical bundle, pack,
observation, and classification regeneration from a credential-disabled
full-history clone. [Candidate
CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33359925143) passed
independently. The classification proves workflow/type eligibility for
validation planning only; it grants no validation, approval, promotion,
rollout, execution, or cross-factory authority. Immutable
[v1.14.0](https://github.com/adaliontech/Zaibatsu/releases/tag/v1.14.0) uses
annotated tag object `c417b24070ccda8b08e707c3ec786094494629d1` over evidence
roof `aec013d84645b5d508bf914f9184e5fd34e96c28`;
[roof CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33360056494),
[tag CI](https://github.com/adaliontech/Zaibatsu/actions/runs/33360102500), a
credential-disabled full-history tag clone, fourteen strict schemas, exact
artifact regeneration, both Gitleaks modes, and four live tagged-schema byte
checks passed. GitHub reports v1.14.0 immutable, latest, non-draft, and
non-prerelease.

Zaibatsu is an independent project and is not affiliated with or endorsed by
Factory AI.

## License

[MIT](LICENSE)
