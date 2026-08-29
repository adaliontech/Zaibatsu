# Changelog

## Unreleased

- Created the Zaibatsu public architecture and Guild submission package.
- Added a machine-readable component, maturity, task-flow, and invariant model.
- Added an offline validator and adversarial unit tests.
- Added architecture, implementation-status, threat-model, reproducibility,
  evidence, case-study, demo, Droid-session, Guild, and roadmap documents.
- Added a secret-free local-Qwen Droid configuration example, fail-closed
  preflight, and machine-readable submission gates.
- Corrected application and demo language so no completed Droid contribution
  is claimed before a real reviewed session exists.
- Hardened architecture and readiness validation against missing components,
  maturity inflation, optionalized gates, dependency bypasses, malformed data,
  and unscanned source files.
- Hardened local-model preflight against malformed or credential-bearing URLs,
  alternate inline credential fields, invalid model settings, and crash-only
  failures.
- Separated the Factory CLI API key from the local Qwen endpoint API key and
  made both explicit submission prerequisites.
- Connected authenticated Droid CLI `0.206.0` to the owner-operated Qwen model,
  recorded a native-tool canary, and accepted one reviewed two-file
  contribution after independent validation.
- Strengthened task-flow validation to require sandbox execution,
  verification, and policy decision in deterministic order before a controlled
  side effect; added the adversarial policy-before-verification test.
- Reconciled the static preflight with secure Factory CLI login receipts and
  authenticated tailnet-DNS model gateways without exposing credential values.
- Adopted Zaibatsu as the public submission brand and aligned the schemas,
  documentation, validator output, and local configuration example.
- Added a read-only, secret-free GitHub Actions gate for the offline validation
  suite and pinned the checkout action to its reviewed release commit.
