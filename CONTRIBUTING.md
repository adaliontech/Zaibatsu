# Contributing

Zaibatsu welcomes small, evidence-backed improvements to its reference
architecture, validator, tests, and public documentation.

## Before changing anything

1. Read [`AGENTS.md`](AGENTS.md).
2. Preserve the meta-factory, deterministic-control, and least-authority
invariants across the machine-readable architecture, portable factory,
readiness, and evidence contracts.
3. Keep control-factory and economic-factory identities, credentials,
   schedulers, data, and production authority project-scoped.
4. Decide whether the change is operational, validated preproduction,
   designed, or planned; do not inflate maturity.
5. Keep operational infrastructure and personal data out of this repository.

## Validate

```bash
make validate
git diff --check
```

New validation behavior should include an adversarial test that demonstrates
the failure it prevents.

Changes to factory lifecycle, reproduction, versioning, scheduling, worker
harnesses, verification, or feedback must keep
[`architecture/factory-model.json`](architecture/factory-model.json) and
[`architecture/system.json`](architecture/system.json) consistent.
Changes to a module policy, dependency, interface, or implementation boundary
must also update the catalog, regenerate the example plan, and add a drift or
compatibility test. Regenerate the example bundle manifest and exercise
`bundle` plus `verify-bundle` whenever a selected artifact, plan, or bundled
schema changes; do not commit generated tar archives.
Changes to inspection or comparison behavior must prove that invalid bundles
are rejected before a semantic result is emitted and that the result preserves
the bundle's non-authorizing runtime boundary.
Qualification-policy changes may add requirements but may not remove the
mandatory minimum, accept self-attestation, treat a plan as evidence, grant
runtime eligibility or activation, or bypass owner approval. Regenerate and
verify the checked-in qualification plan after any bundle or policy change.
Qualification-evidence or assessment changes must remain exact rebuilds from a
fully verified bundle, plan, and policy. Content addressing alone may not be
called semantic verification; every credited binding must name the precise
deterministic verifier and scope, and no partial result may grant eligibility
or activation.
Source-lock changes must read immutable Git objects rather than working-tree
files, require an annotated semantic-version tag, dual-hash release objects,
rebuild the exact verified bundle, and reject replacement-object or
repository-redirection environment substitution.
A source lock may not be presented as remote ownership, tag-signature,
implementation-source, runtime-qualification, eligibility, or deployment proof.

## Pull request evidence

Describe:

- the invariant or documentation gap being addressed;
- why the change belongs in deterministic code or probabilistic guidance;
- the exact verification run;
- any security, compatibility, or maturity impact;
- whether the change affects a public claim.

Do not include session transcripts, screenshots, fixtures, or logs containing
credentials or private infrastructure details.
