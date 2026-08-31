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
- Multi-factory portfolio: build `examples/control-factory.json`, `examples/economic-factory.json`, and `examples/service-factory.json`, then run `python3 scripts/zaibatsu.py portfolio-plan examples/factory-portfolio.json /tmp/example-control.factory.tar /tmp/example-product.factory.tar /tmp/example-service.factory.tar --output /tmp/example-portfolio.plan.json`
- Portfolio proof: `python3 scripts/zaibatsu.py verify-portfolio-plan /tmp/example-portfolio.plan.json examples/factory-portfolio.json /tmp/example-control.factory.tar /tmp/example-product.factory.tar /tmp/example-service.factory.tar`
- Route-bound evidence return: `python3 scripts/zaibatsu.py evidence-return-record /tmp/example-portfolio.plan.json examples/factory-portfolio.json example-product /tmp/example-product.runtime-evidence.tar examples/economic-factory.qualification-plan.json policies/runtime-qualification-v1.json /tmp/example-control.factory.tar /tmp/example-product.factory.tar /tmp/example-service.factory.tar --output /tmp/example-product.evidence-return.json`
- Evidence-return proof: `python3 scripts/zaibatsu.py verify-evidence-return-record /tmp/example-product.evidence-return.json /tmp/example-portfolio.plan.json examples/factory-portfolio.json example-product /tmp/example-product.runtime-evidence.tar examples/economic-factory.qualification-plan.json policies/runtime-qualification-v1.json /tmp/example-control.factory.tar /tmp/example-product.factory.tar /tmp/example-service.factory.tar`
- Candidate-contract binding: after creating the checked proposal, observation, and classification chain, run `python3 scripts/zaibatsu.py bind-improvement-candidate examples/economic-factory.improvement-candidate-spec.json /tmp/example-product.improvement-classification.json policies/improvement-classification-v1.json /tmp/example-product.improvement-proposal.json examples/economic-factory.improvement-proposal-spec.json /tmp/example-product.improvement-observation.json examples/economic-factory.improvement-observation-spec.json /tmp/example-product.evidence-return.json /tmp/example-portfolio.plan.json examples/factory-portfolio.json example-product /tmp/example-product.runtime-evidence.tar examples/economic-factory.qualification-plan.json policies/runtime-qualification-v1.json /tmp/example-control.factory.tar /tmp/example-product.factory.tar /tmp/example-service.factory.tar --output /tmp/example-product.improvement-candidate.json`
- Improvement validation plan: after binding the candidate, run `python3 scripts/zaibatsu.py plan-improvement-validation examples/economic-factory.improvement-validation-plan-spec.json /tmp/example-product.improvement-candidate.json examples/economic-factory.improvement-candidate-spec.json /tmp/example-product.improvement-classification.json policies/improvement-classification-v1.json /tmp/example-product.improvement-proposal.json examples/economic-factory.improvement-proposal-spec.json /tmp/example-product.improvement-observation.json examples/economic-factory.improvement-observation-spec.json /tmp/example-product.evidence-return.json /tmp/example-portfolio.plan.json examples/factory-portfolio.json example-product /tmp/example-product.runtime-evidence.tar examples/economic-factory.qualification-plan.json policies/runtime-qualification-v1.json /tmp/example-control.factory.tar /tmp/example-product.factory.tar /tmp/example-service.factory.tar --output /tmp/example-product.improvement-validation-plan.json`
- Annotated-release source lock: `python3 scripts/zaibatsu.py source-lock examples/economic-factory.json /tmp/example-product.factory.tar --release-tag v1.6.0 --output /tmp/example-product.source-lock.json`
- Source-lock proof: `python3 scripts/zaibatsu.py verify-source-lock /tmp/example-product.source-lock.json /tmp/example-product.factory.tar`
- Qualification requirements: `python3 scripts/zaibatsu.py qualification-plan /tmp/example-product.factory.tar --output /tmp/example-product.qualification-plan.json`
- Qualification-plan proof: `python3 scripts/zaibatsu.py verify-qualification-plan /tmp/example-product.qualification-plan.json /tmp/example-product.factory.tar`
- Bundle-derived evidence: `python3 scripts/zaibatsu.py qualification-evidence /tmp/example-product.qualification-plan.json /tmp/example-product.factory.tar --output /tmp/example-product.qualification-evidence.json`
- Partial assessment: `python3 scripts/zaibatsu.py qualification-assessment /tmp/example-product.qualification-evidence.json /tmp/example-product.qualification-plan.json /tmp/example-product.factory.tar --output /tmp/example-product.qualification-assessment.json`
- Signed runtime-evidence proof: `python3 scripts/zaibatsu.py verify-runtime-evidence examples/economic-factory.runtime-evidence.json /tmp/example-product.factory.tar`
- Runtime-evidence pack: `python3 scripts/zaibatsu.py evidence-pack examples/economic-factory.runtime-evidence.json /tmp/example-product.factory.tar --evidence-artifact examples/runtime-evidence/source-revision-fixture.json --verifier-implementation examples/runtime-evidence/fixture-verifier-method.json --output /tmp/example-product.runtime-evidence.tar`
- Runtime-evidence-pack proof: `python3 scripts/zaibatsu.py verify-evidence-pack /tmp/example-product.runtime-evidence.tar /tmp/example-product.factory.tar`
- Combined runtime assessment: `python3 scripts/zaibatsu.py runtime-assessment /tmp/example-product.runtime-evidence.tar examples/economic-factory.qualification-evidence.json examples/economic-factory.qualification-plan.json /tmp/example-product.factory.tar --as-of 2026-08-30T23:00:00Z --output /tmp/example-product.runtime-assessment.json`
- Factory rebuild DAG: `python3 scripts/zaibatsu.py rebuild-plan /tmp/example-product.factory.tar --runtime-evidence-pack /tmp/example-product.runtime-evidence.tar --output /tmp/example-product.rebuild-plan.json`
- Rebuild-DAG proof: `python3 scripts/zaibatsu.py verify-rebuild-plan /tmp/example-product.rebuild-plan.json /tmp/example-product.factory.tar --runtime-evidence-pack /tmp/example-product.runtime-evidence.tar`
- Tests only: `python3 -m unittest discover -s tests -v`
- Deferred local-model preflight: `make droid-preflight`

No dependency installation, network access, secret, cloud account, or
production connection is required. OpenSSH `ssh-keygen` is required to verify
signed runtime evidence.

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
- Treat a runtime-evidence signature only as authentication of the exact
  assertion under the evaluator-selected registry and timestamp. It does not
  prove key ownership, organizational independence, verifier correctness,
  artifact truth, activation, or execution. Never commit a verifier private
  key. Production trust roots and clocks require separate review and pinning.
- Treat a factory source lock only as proof that exact JSON blobs in one local
  annotated release rebuild the verified control bundle. It does not contact
  or authenticate the named remote, verify a tag signature or repository
  owner, include runtime implementation source, satisfy a qualification
  binding, grant eligibility or activation, or deploy anything.
- Treat a factory rebuild plan only as a deterministic graph of intended
  actions, direct evidence gaps, upstream blockers, and non-authorizing gates.
  It must fully reverify every bound input and may not run Ansible, realize Nix,
  read secrets, install a scheduler, invoke a model, manufacture qualification
  evidence or owner approval, activate a factory, deploy infrastructure, or
  claim runtime recovery.
- Treat a factory portfolio plan only as a deterministic join over fully
  verified control bundles, an ordered closed registry, intended namespaces,
  and evidence-only routes. It does not prove runtime isolation, carry
  evidence, route secrets, grant cross-factory authority, activate a factory,
  or execute or deploy anything.
- Treat a factory evidence-return record only as proof that one verified pack
  is bound to one declared economic-factory route. It does not prove transport,
  content safety, secret absence, verifier reexecution, artifact truth,
  classification, improvement value, promotion eligibility or authorization,
  activation, execution, or cross-factory effects.
- Treat an improvement-candidate binding only as proof that one exact canonical
  non-executable contract matches an eligible classification target and its
  fully reverified evidence chain. It does not prove content safety, secret
  absence, semantic correctness, an implementation, a validation plan or
  result, regression safety, rollback, owner approval, promotion, rollout,
  activation, execution, or cross-factory effects.
- Treat an improvement validation plan only as a deterministic inventory of
  fixed future stages and missing content-addressed evidence. It may not run
  validation, use production credentials or state, accept model output as
  verification, claim an implementation or result, or grant approval,
  promotion, rollout, activation, execution, or cross-factory effects.
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
