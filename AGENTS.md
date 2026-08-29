# Zaibatsu repository guide

## Commands

- Full validation: `make validate`
- Architecture contract only: `python3 scripts/validate_repository.py`
- Tests only: `python3 -m unittest discover -s tests -v`
- Deferred local-model preflight: `make droid-preflight`

No dependency installation, network access, secret, cloud account, or
production connection is required.

## Repository purpose

This is a public-safe Factory Guild submission package. It explains and tests
the Zaibatsu architecture without exposing the private operations repository,
host inventory, credentials, or bootstrap procedures.

## Hard rules

- Do not add credentials, tokens, private keys, cookies, private network
  coordinates, machine fingerprints, personal data, or absolute home paths.
- Do not add commands that deploy, publish, enroll a device, alter a firewall,
  rotate a secret, or touch a production host.
- Do not describe a target component as operational beyond its evidenced
  scope. Use only the maturity values defined in `architecture/system.json`;
  when a narrow sub-scope is live but the full component is not, name both
  boundaries explicitly.
- Keep the distinction between deterministic control and probabilistic worker
  judgment explicit.
- Preserve the direct-owner recovery path. Dispatcher cannot be its own only
  recovery mechanism.
- Preserve the closed project allowlist and deny unknown project identities.
- Prefer Python standard-library validation; do not add a dependency unless it
  materially improves the public kit.
- Never commit `.factory/settings.local.json`; the local model identifier,
  endpoint port, local-model API key, and Factory API key are machine-local
  configuration.

## Completion evidence

Before calling any change complete:

1. Run `make validate`.
2. Review `git diff --check`.
3. Verify every new claim has a status and evidence source.
4. Verify no private operational detail entered the public package.
