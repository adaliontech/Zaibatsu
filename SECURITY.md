# Security policy

## Scope

Zaibatsu is a public meta-factory architecture and offline validation kit. It
contains factory contracts and sanitized evidence, but no production access,
credential material, network enrollment, or deployment mechanism.

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
- Factory feedback cannot self-promote into shared policy.
- Plaintext secrets are forbidden in Git; SOPS/age is the modeled static
  ciphertext boundary and runtime machine secrets remain separate.
- Each workload has one cron or systemd scheduler of record.
- Source-only agent skeletons and planned Nix environments cannot be presented
  as deployed.
- Public documentation must pass the built-in safety scan.
- Git-tracked and non-ignored paths are scanned; opaque binaries, invalid UTF-8,
  symlinks, and Git submodules are rejected because their contents cannot be
  inspected by the offline public-safety gate.
- CI runs checksum-pinned Gitleaks against full Git history and the release
  tree; GitHub secret scanning and push protection are enabled separately.
- Published release tags are protected by release immutability.

This repository is not a substitute for a security review of any system that
adopts the pattern.
