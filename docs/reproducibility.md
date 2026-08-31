# Reproducibility

## Scope

This repository reproduces the **public meta-factory and component contracts**,
not the private fleet. Validation is offline and checks that the factory
hierarchy, lifecycle, maturity, and safety properties remain congruent.

## Requirements

- Python 3.10 or later;
- OpenSSH `ssh-keygen` with `-Y verify` support;
- GNU Make for the convenience target (optional);
- no third-party Python package;
- no network access;
- no credentials or infrastructure account.

## Run

```bash
make validate
```

Equivalent commands:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/validate_repository.py
```

The validator confirms:

1. all submission documents, project-owned JSON Schemas, and sanitized receipts
   exist and reference the correct contract;
2. Zaibatsu remains the meta-factory control layer rather than one economic
   factory;
3. the closed factory registry contains the control factory and both economic
   factories with exact roles;
4. the factory lifecycle preserves versioning, reproduction, scheduling,
   verification, evidence return, improvement, and reviewed promotion order;
5. Git/SOPS, Ansible/Nix, cron/systemd, skeleton, harness, gate, and feedback
   maturity cannot be inflated;
6. plaintext secrets remain forbidden in Git and SOPS/age remains the static
   ciphertext boundary;
7. agent skeletons remain source-only and repository hooks remain a planned
   gate extension;
8. factories cannot self-promote feedback and models cannot authorize effects;
9. the factory registry and shared capability maturities agree with the
   component architecture;
10. every probabilistic component has deterministic preconditions and
   postconditions;
11. probabilistic components cannot directly trigger external side effects;
12. every side-effecting deterministic component declares a policy gate;
13. required fail-closed invariants are true;
14. persistence and verification precede a controlled side effect;
15. every tracked or non-ignored public repository file is inspected, every
   opaque or invalid-UTF-8 file fails closed regardless of suffix, and every
   repository symlink or Git submodule is denied;
16. public text contains no absolute home path, tailnet name, private or
    unapproved public address, or obvious inline credential;
17. repository-local documentation links resolve;
18. every sanitized evidence receipt has the required status, counts, digests,
    scope restrictions, redactions, and limitations for its evidence class;
19. every completed submission gate has typed proof, every gate remains
    required, and dependency order is enforced;
20. submission readiness cannot become true while a required gate is pending
    or dependency-blocked;
21. the portable example preserves the same Git/SOPS, Ansible/Nix,
    scheduler-of-record, deterministic-gate, no-model-effect, and
    no-self-promotion boundaries;
22. reusable modules fill every ordered factory slot, preserve the declared
    policy rather than a hard-coded implementation ID, and cannot introduce a
    forward dependency or side-effect authority;
23. the checked-in control plan exactly matches the canonical definition and
    catalog digests, and compiling those inputs twice produces identical bytes;
24. every catalog module binds a module-local, symlink-free artifact whose
    canonical digest and complete contract agree with the catalog and plan;
25. the portable bundle includes all selected module contracts and five
    schemas, rejects unsafe or ambiguous archive forms without extraction, and
    reproduces identical canonical USTAR bytes.
26. inspection and comparison accept only fully verified canonical bundles,
    report a scheduler substitution at the module slot, and preserve the
    explicit no-runtime and no-deployment boundary;
27. the closed factory portfolio accepts only fully verified bundles, exactly
    one control factory, ordered economic factories, disjoint intended
    namespaces, and evidence-only non-authorizing return routes;
28. the qualification policy preserves every mandatory evidence class, and
    the checked-in plan exactly matches its verified bundle and policy while
    granting no runtime eligibility, activation, or owner approval;
29. bundle-derived qualification receipts and the partial assessment exactly
    rebuild from the verified bundle, plan, and policy; forged, replayed,
    duplicate, reordered, scope-inflated, or authority-inflated evidence fails
    closed.
30. the annotated-release source lock resolves exact tag, commit, tree, and
    blob objects with Git replacements disabled, reproduces the byte-identical
    bundle, and preserves explicit remote-ownership, signature, runtime-source,
    qualification, eligibility, activation, and deployment denials.
31. the signed runtime-evidence registry and receipts bind exact public keys,
    allowlists, provenance, scope, verifier implementation, validity, and false
    authority flags; tampering, replay, wrong keys, duplicates, stale evidence,
    type confusion, and missing OpenSSH fail closed;
32. the canonical runtime-evidence pack embeds the signed set, registry, exact
    evidence artifacts, verifier descriptors, and immutable manifest schema;
    archive, schema, digest, replay, size, and authority mutations fail closed,
    while verifier reexecution and artifact truth remain explicit nonclaims;
33. the public signature is restricted to fixture scope, while an ephemeral-key
    positive test proves a complete `factory_runtime` set can qualify one module
    without granting execution, side effects, owner approval, or activation;
34. the factory rebuild plan fully reverifies the bundle, source lock, policy,
    qualification plan, both evidence classes, runtime-evidence pack, embedded
    materials, registry, and assessment;
    preserves exact action and
    gate order, dependencies, blockers, and digests; and grants no execution,
    qualification, owner approval, activation, deployment, or recovery
    authority.
35. the route-bound evidence-return record fully reverifies the portfolio,
    bundles, source route, qualification inputs, runtime-evidence pack,
    signatures, allowlists, and digests; source/route replay, forgery, scalar
    confusion, oversize input, and every transport, interpretation, promotion,
    activation, execution, or cross-factory authority inflation fail closed.
36. the improvement-proposal record fully reverifies that evidence return and
    every source input, binds one strict proposal specification by canonical
    digest, preserves all mandatory later review gates, and rejects target,
    replay, forgery, scalar, malformed, size, classification, promotion,
    rollout, execution, and cross-factory authority mutations.
37. the improvement-observation record separately reverifies the return,
    preserves a bounded canonical category and subject, and rejects safety,
    truth, authority, replay, forgery, type, size, and ordering inflation.
38. the classification record reverifies both complete chains under a hashed
    policy, emits deterministic rejection for valid mismatches, and permits
    validation planning only without creating or executing a plan.
39. the candidate binding accepts only an eligible classification, requires an
    exact target match, content-addresses one canonical non-executable contract,
    and rejects implementation, validation, promotion, execution, or
    cross-factory authority inflation.
40. the improvement validation plan fully reverifies that candidate chain,
    reproduces eight fixed `not_run` stages and twelve `missing` evidence
    bindings, and rejects implementation, execution, validation-success,
    promotion, or cross-factory authority inflation.

The adversarial tests mutate valid architecture data and prove that the
validator rejects meta-factory role drift, a missing or reclassified factory,
premature promotion, Nix inflation, plaintext Git secrets, model effect
authority, factory self-promotion, component/model divergence, an unknown
project, missing component, unbounded model exit, direct model publication,
unguarded side effect, leaked private detail, malformed contract data,
dependency bypass, optionalized gates, and premature readiness.

## Validate another factory

The reusable CLI uses the same standard-library contract implementation and
OpenSSH verifier:

```bash
python3 scripts/zaibatsu.py validate examples/economic-factory.json
python3 scripts/zaibatsu.py catalog-check
python3 scripts/zaibatsu.py verify-plan \
  examples/economic-factory.plan.json examples/economic-factory.json
python3 scripts/zaibatsu.py rebuild-check examples/economic-factory.json
python3 scripts/zaibatsu.py bundle examples/economic-factory.json \
  --output /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py verify-bundle \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py inspect-bundle \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py bundle examples/economic-factory-cron.json \
  --output /tmp/example-product-cron.factory.tar
python3 scripts/zaibatsu.py compare-bundles \
  /tmp/example-product.factory.tar \
  /tmp/example-product-cron.factory.tar
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
python3 scripts/zaibatsu.py source-lock \
  examples/economic-factory.json \
  /tmp/example-product.factory.tar \
  --release-tag v1.6.0 \
  --output /tmp/example-product.source-lock.json
python3 scripts/zaibatsu.py verify-source-lock \
  /tmp/example-product.source-lock.json \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py qualification-plan \
  /tmp/example-product.factory.tar \
  --output /tmp/example-product.qualification-plan.json
python3 scripts/zaibatsu.py verify-qualification-plan \
  /tmp/example-product.qualification-plan.json \
  /tmp/example-product.factory.tar
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
  /tmp/example-product.factory.tar
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
python3 scripts/zaibatsu.py bind-improvement-candidate \
  examples/economic-factory.improvement-candidate-spec.json \
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
  /tmp/example-service.factory.tar \
  --output /tmp/example-product.improvement-candidate.json
python3 scripts/zaibatsu.py verify-improvement-candidate \
  /tmp/example-product.improvement-candidate.json \
  examples/economic-factory.improvement-candidate-spec.json \
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
python3 scripts/zaibatsu.py rebuild-plan \
  /tmp/example-product.factory.tar \
  --runtime-evidence-pack /tmp/example-product.runtime-evidence.tar \
  --output /tmp/example-product.rebuild-plan.json
python3 scripts/zaibatsu.py verify-rebuild-plan \
  /tmp/example-product.rebuild-plan.json \
  /tmp/example-product.factory.tar \
  --runtime-evidence-pack /tmp/example-product.runtime-evidence.tar
```

To create a new definition, run `python3 scripts/zaibatsu.py scaffold --help`.
The scaffold starts at planned maturity; it is a policy-safe definition, not
evidence that the new factory is deployed. Operational or
validated-preproduction maturity requires a scoped, content-addressed,
trusted-verifier receipt binding whose trust root is separately reviewed.

The rebuild check and portable bundle cover the deterministic contract layer.
They are path-independent and offline, but do not run Ansible, realize Nix,
activate cron/systemd, contact a model, deploy a service, or demonstrate
recovery. Those are separate promotion gates.

The portfolio plan adds the public factory-of-factories join. It verifies one
control bundle and two economic-factory bundles, matches them to a closed
ordered registry, binds their exact source and scheduler-module digests, and
derives 21 disjoint intended namespaces. Both economic factories may return
evidence only through their declared return routes; no declared route permits
secrets, grants authority, or self-promotion. The names are declarative scopes,
not proof that runtime
users, processes, networks, credentials, databases, workers, or schedulers are
isolated.

The source lock strengthens that contract-layer proof by ignoring the working
tree and rebuilding from sixteen exact blobs reachable through an annotated
release tag. It records both the repository's native Git object identifiers
and SHA-256 hashes of the tag, commit, tree, and file object content. It does not
contact a remote, authenticate repository ownership, verify a tag signature,
contain runtime implementations, or satisfy qualification, activation,
deployment, or recovery gates.

The qualification plan closes none of those gates. It binds the control bundle
and minimum policy by digest and enumerates missing evidence. The public
example contains 67 missing bindings across 27 requirement types, marks zero
of nine modules eligible, accepts no self-attestation, and grants no activation.

The bundle verifier can independently reproduce one narrow evidence type from
the public inputs: every selected module contract matches its catalog record,
schema reference, and artifact digest. The generated evidence set binds nine
contract-conformance receipts to the exact bundle, plan, policy, module, and
artifact. The assessment therefore reports 9 verified and 58 missing bindings.
It explicitly contains no runtime implementation, environment, recovery,
isolation, external independent-verifier, eligibility, or activation proof.

The checked signed receipt adds one fresh `source_revision` binding at the
recorded assessment time. Its registry permits only `public_test_fixture`, so
the combined assessment reports 10 verified and 57 missing bindings while all
nine modules remain ineligible. OpenSSH proves that the exact payload matches
the selected public key and namespace. The canonical pack retrieves and
digest-verifies the exact evidence artifact and verifier descriptor named by
that payload. It does not rerun the verifier, infer the artifact's semantic
truth, authenticate the key owner, or establish organizational independence.
Registry selection and the assessment clock are explicit trust inputs that a
production caller must separately review and pin.

The evidence-return record then binds that exact verified pack to the product
bundle's single declared evidence-only route in the rebuilt portfolio plan.
It does not claim that transport happened, inspect the content for secrets or
safety, rerun the verifier, classify an improvement, modify shared policy, make
a change promotion-eligible, or authorize activation, execution, or any
cross-factory effect.

The improvement-proposal record then rechecks that entire chain and binds one
typed, untrusted shared-change suggestion to it by canonical JSON digest. The
specification requires content-safety, classification, reporting-factory,
independent-regression, owner-policy, rollback, and cross-factory-privilege
review. Recording it does not authenticate the proposer, inspect or trust the
narrative, normalize an observation, classify a candidate, establish merit,
run a test, verify rollback, change policy, approve promotion, authorize
rollout, activate, execute, or grant any cross-factory effect.

The improvement-observation record separately rechecks that chain and binds
one typed, explicitly untrusted report to a canonical subject and digest.
Structural normalization means bounded canonical JSON, source binding, and a
known category; it does not authenticate the reporter, scan content safety or
secrets, or establish the semantic truth of the report or source artifact.

The improvement-classification record then reverifies both complete chains and
the separately hashed classification policy. It deterministically checks source
and target alignment, allowed workflow types, preserved later-review gates, and
non-authorizing boundaries. The checked pair is eligible only for validation
planning. Classification itself creates no validation plan, no validation or mutation may run, and
no merit, approval, promotion, rollout, activation, execution, or cross-factory
effect follows from the classification.

The improvement-candidate record then binds one exact canonical contract to
that eligible classification. The checked artifact declares typed inputs,
outputs, ordered fail-closed checks, and a contract-only authority boundary;
it contains no executable implementation. Reproducible bytes and a matching
digest do not establish content safety, secret absence, semantic correctness,
implementation, validation planning or execution, regression safety,
rollback, approval, promotion, rollout, activation, execution, or any
cross-factory effect.

The separate improvement-validation planner reverifies that exact candidate
and its complete source chain before reproducing eight fixed validation stages
and twelve required evidence bindings. The checked record remains wholly
inert: all stages are `not_run`, all evidence is `missing`, no implementation
exists, and executed, passed, and failed counts are zero. Its policy forbids
network access, production credentials or state, model output as verification,
and overwrite. It proves planning identity and order only—not that content is
safe, an implementation exists, validation ran or passed, rollback works,
approval was obtained, or promotion, rollout, activation, execution, or any
cross-factory effect is authorized.

The rebuild plan consumes those fully reverified inputs and emits an inert
nine-action dependency graph plus four gates. The public result has zero
qualification-ready actions, all nine blocked, and 57 missing evidence
bindings. It reports future action intents and blockers; it does not read
secrets, run Ansible, realize Nix, install a scheduler, invoke a model, produce
qualification evidence, obtain owner approval, activate or deploy anything, or
prove that a runtime can be recovered. Generated-key tests exercise the
reachable `qualified_not_authorized` state for one fully evidenced source
module; no checked public module is currently qualified, and qualification
still grants no execution or activation authority.

## Optional Droid preflight

Droid is not required for repository validation. On a machine with the local
Qwen endpoint, model credential, and separate Factory authentication, follow
[Factory Droid integration](droid-session.md) and run:

```bash
make droid-preflight
```

This is a static, fail-closed check. It does not contact the endpoint. The
recorded live canary and bounded contribution are separate evidence that the
configured model can stream native tool calls and complete this narrow task.

## Expected result

The command exits zero and prints `Zaibatsu validation passed`. Any failure is
reported as a concrete contract violation.

## Infrastructure reproduction boundary

The private evidence behind this public model distinguishes:

- Git for source and intended state;
- SOPS/age for static encrypted material that may be versioned;
- bounded secret-manager identities for runtime values;
- Ansible for host configuration;
- Nix for exact worker environments.

Nix is part of the target architecture for cross-worker toolchain pinning, but
it is not required by or implemented in this public validation kit. Adding a
flake before the private implementation uses and verifies one would create a
demonstration-only claim. The roadmap preserves Nix as planned until an actual
worker environment is reproduced on more than one eligible node.

## Clean-checkout proof

Before publication, run the commands from a fresh clone in a temporary
directory, record the commit and output in [Evidence](evidence.md), and retain
the complete receipt outside the human documentation tree. For an immutable
release reproduction, clone the named tag rather than the moving default
branch:

```bash
git clone --branch v1.15.0 https://github.com/adaliontech/Zaibatsu.git
cd Zaibatsu
make validate
```

Use a full-history clone for `v1.15.0`: its checked source lock intentionally
reproduces the `v1.6.0` control bundle and therefore requires that annotated
tag and its objects. A shallow clone that omits the referenced release must
fail instead of silently weakening the lineage proof.
