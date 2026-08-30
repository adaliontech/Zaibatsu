# Zaibatsu repository guide

## Commands

- Full validation: `make validate`
- Architecture contract only: `python3 scripts/validate_repository.py`
- Portable example: `python3 scripts/zaibatsu.py validate examples/economic-factory.json`
- Module catalog: `python3 scripts/zaibatsu.py catalog-check`
- Plan proof: `python3 scripts/zaibatsu.py verify-plan examples/economic-factory.plan.json examples/economic-factory.json`
- Byte-stable rebuild: `python3 scripts/zaibatsu.py rebuild-check examples/economic-factory.json`
- Portable bundle: `python3 scripts/zaibatsu.py bundle examples/economic-factory.json --output /tmp/example-product.factory.tar`
- Bundle proof: `python3 scripts/zaibatsu.py verify-bundle /tmp/example-product.factory.tar`
- Bundle inspection: `python3 scripts/zaibatsu.py inspect-bundle /tmp/example-product.factory.tar`
- Module-change comparison: build the cron example, then run `python3 scripts/zaibatsu.py compare-bundles /tmp/example-product.factory.tar /tmp/example-product-cron.factory.tar`
- Qualification requirements: `python3 scripts/zaibatsu.py qualification-plan /tmp/example-product.factory.tar --output /tmp/example-product.qualification-plan.json`
- Qualification-plan proof: `python3 scripts/zaibatsu.py verify-qualification-plan /tmp/example-product.qualification-plan.json /tmp/example-product.factory.tar`
- Bundle-derived evidence: `python3 scripts/zaibatsu.py qualification-evidence /tmp/example-product.qualification-plan.json /tmp/example-product.factory.tar --output /tmp/example-product.qualification-evidence.json`
- Partial assessment: `python3 scripts/zaibatsu.py qualification-assessment /tmp/example-product.qualification-evidence.json /tmp/example-product.qualification-plan.json /tmp/example-product.factory.tar --output /tmp/example-product.qualification-assessment.json`
- Tests only: `python3 -m unittest discover -s tests -v`
- Deferred local-model preflight: `make droid-preflight`

No dependency installation, network access, secret, cloud account, or
production connection is required.

## Repository purpose

This is the public-safe executable architecture for Zaibatsu, the factory of
software factories, and its Factory Guild submission package. It explains and
tests the meta-factory, economic-factory, component, agent, verification, and
feedback boundaries without exposing private operations, inventory,
credentials, or bootstrap procedures.

## Hard rules

- Do not add credentials, tokens, private keys, cookies, private network
  coordinates, machine fingerprints, personal data, or absolute home paths.
- Do not add commands that deploy, publish, enroll a device, alter a firewall,
  rotate a secret, or touch a production host.
- Do not describe a target capability as operational beyond its evidenced
  scope. Keep `architecture/factory-model.json` and `architecture/system.json`
  aligned; when a narrow sub-scope is live but the full capability is not,
  name both boundaries explicitly.
- Preserve Zaibatsu's role as the meta-factory control layer, the control versus
  economic factory classes, and the complete factory lifecycle.
- Preserve Git/SOPS, Ansible/Nix, and cron/systemd as distinct boundaries. Do
  not represent Nix, repository hooks, modular-agent deployment, unattended
  multi-harness routing, or shared recursive promotion as complete.
- Keep the distinction between deterministic control and probabilistic worker
  judgment explicit.
- Returned factory evidence may propose an improvement but may not self-promote
  into shared policy or another factory.
- Preserve the direct-owner recovery path. Dispatcher cannot be its own only
  recovery mechanism.
- Preserve the closed factory/project registry and deny unknown identities.
- Keep every JSON instance bound to its project-owned schema. Evidence receipts
  and completed submission gates require typed fields, not prose alone.
- Treat a qualification plan only as a content-addressed list of missing
  evidence. It may not accept self-attestation, mark a bundled contract
  runtime-eligible, authorize activation, or replace owner approval.
- Treat bundle-derived qualification evidence only as proof of the exact
  contract/catalog/schema/digest checks the bundle verifier reruns. It may not
  claim an external independent verifier, runtime implementation evidence,
  full qualification, eligibility, activation, or deployment.
- Treat every tracked or non-ignored path as public. Opaque files, symlinks,
  and Git submodules are outside the scanner's inspectable boundary and must
  fail closed.
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
