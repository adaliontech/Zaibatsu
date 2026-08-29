# Contributing

Zaibatsu welcomes small, evidence-backed improvements to its reference
architecture, validator, tests, and public documentation.

## Before changing anything

1. Read [`AGENTS.md`](AGENTS.md).
2. Preserve the deterministic-control and least-authority invariants.
3. Decide whether the change is operational, validated preproduction,
   designed, or planned; do not inflate maturity.
4. Keep operational infrastructure and personal data out of this repository.

## Validate

```bash
make validate
git diff --check
```

New validation behavior should include an adversarial test that demonstrates
the failure it prevents.

## Pull request evidence

Describe:

- the invariant or documentation gap being addressed;
- why the change belongs in deterministic code or probabilistic guidance;
- the exact verification run;
- any security, compatibility, or maturity impact;
- whether the change affects a public claim.

Do not include session transcripts, screenshots, fixtures, or logs containing
credentials or private infrastructure details.
