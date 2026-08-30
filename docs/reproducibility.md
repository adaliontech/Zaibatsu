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

1. all submission documents and sanitized receipts exist;
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
15. every public repository file is inspected or rejected as an unapproved
   binary, and every repository symlink is denied;
16. public text contains no absolute home path, tailnet name, private or
    unapproved public address, or obvious inline credential;
17. repository-local documentation links resolve;
18. every submission gate remains required and dependency order is enforced;
19. submission readiness cannot become true while a required gate is pending
    or dependency-blocked.

The adversarial tests mutate valid architecture data and prove that the
validator rejects meta-factory role drift, a missing or reclassified factory,
premature promotion, Nix inflation, plaintext Git secrets, model effect
authority, factory self-promotion, component/model divergence, an unknown
project, missing component, unbounded model exit, direct model publication,
unguarded side effect, leaked private detail, malformed contract data,
dependency bypass, optionalized gates, and premature readiness.

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
git clone --depth 1 --branch v1.1.0 https://github.com/adaliontech/Zaibatsu.git
cd Zaibatsu
make validate
```
