# Security policy

## Scope

Zaibatsu is a reference architecture and offline validation kit. It contains no
production access, credential material, network enrollment, or deployment
mechanism.

## Reporting

Do not open a public issue containing a credential, private address, machine
identity, production topology, or exploitable operational detail. Use the
repository's private vulnerability-reporting form under **Security →
Advisories → Report a vulnerability** so the report remains non-public.

## Supported version

Only the latest release on the default branch is maintained.

## Security expectations

- `make validate` must run without secrets or network access.
- Probabilistic components cannot directly own external side effects.
- Every side-effecting deterministic component declares a policy gate.
- Unknown project identities fail closed.
- Public documentation must pass the built-in safety scan.

This repository is not a substitute for a security review of any system that
adopts the pattern.
