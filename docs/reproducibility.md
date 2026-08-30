# Reproducibility

## Scope

This repository reproduces the **public architecture contract**, not the
private fleet. Validation is offline and checks that the published model still
enforces its core safety properties.

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

1. all submission documents exist;
2. the closed project allowlist and required component set are exact;
3. maturity labels cannot be promoted without an explicit evidence-policy
   change;
4. every probabilistic component has deterministic preconditions and
   postconditions;
5. probabilistic components cannot directly trigger external side effects;
6. every side-effecting deterministic component declares a policy gate;
7. required fail-closed invariants are true;
8. persistence and verification precede a controlled side effect;
9. every public repository file is inspected or rejected as an unapproved
   binary, and every repository symlink is denied;
10. public text contains no absolute home path, tailnet name, private or
    unapproved public address, or obvious inline credential;
11. repository-local documentation links resolve;
12. every submission gate remains required and dependency order is enforced;
13. submission readiness cannot become true while a required gate is pending
    or dependency-blocked.

The adversarial tests mutate valid architecture data and prove that the
validator rejects an unknown project, missing component, maturity inflation,
unbounded model exit, direct model publication, unguarded side effect, leaked
private detail, malformed contract data, dependency bypass, optionalized gate,
and premature submission-ready claim.

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

## Nix boundary

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
git clone --depth 1 --branch v1.0.1 https://github.com/adaliontech/Zaibatsu.git
cd Zaibatsu
make validate
```
