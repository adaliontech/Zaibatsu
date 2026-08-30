# Reproducibility

## Scope

This repository reproduces the **public meta-factory and component contracts**,
not the private fleet. Validation is offline and checks that the factory
hierarchy, lifecycle, maturity, and safety properties remain congruent.

## Requirements

- Python 3.10 or later;
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
27. the qualification policy preserves every mandatory evidence class, and
    the checked-in plan exactly matches its verified bundle and policy while
    granting no runtime eligibility, activation, or owner approval;
28. bundle-derived qualification receipts and the partial assessment exactly
    rebuild from the verified bundle, plan, and policy; forged, replayed,
    duplicate, reordered, scope-inflated, or authority-inflated evidence fails
    closed.
29. the annotated-release source lock resolves exact tag, commit, tree, and
    blob objects with Git replacements disabled, reproduces the byte-identical
    bundle, and preserves explicit remote-ownership, signature, runtime-source,
    qualification, eligibility, activation, and deployment denials.

The adversarial tests mutate valid architecture data and prove that the
validator rejects meta-factory role drift, a missing or reclassified factory,
premature promotion, Nix inflation, plaintext Git secrets, model effect
authority, factory self-promotion, component/model divergence, an unknown
project, missing component, unbounded model exit, direct model publication,
unguarded side effect, leaked private detail, malformed contract data,
dependency bypass, optionalized gates, and premature readiness.

## Validate another factory

The reusable CLI uses the same standard-library contract implementation:

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
```

To create a new definition, run `python3 scripts/zaibatsu.py scaffold --help`.
The scaffold starts at planned maturity; it is a policy-safe definition, not
evidence that the new factory is deployed. Operational or
validated-preproduction maturity requires a scoped, content-addressed,
independently verified receipt binding.

The rebuild check and portable bundle cover the deterministic contract layer.
They are path-independent and offline, but do not run Ansible, realize Nix,
activate cron/systemd, contact a model, deploy a service, or demonstrate
recovery. Those are separate promotion gates.

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
git clone --branch v1.7.0 https://github.com/adaliontech/Zaibatsu.git
cd Zaibatsu
make validate
```

Use a full-history clone for `v1.7.0`: its checked source lock intentionally
reproduces the `v1.6.0` control bundle and therefore requires that annotated
tag and its objects. A shallow clone that omits the referenced release must
fail instead of silently weakening the lineage proof.
