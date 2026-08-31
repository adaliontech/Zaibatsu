# Factory Guild requirements

Research date: **2026-08-29**

Authoritative source: [The Factory Guild](https://factory.ai/ambassador).

## Official process

The current Guild page gives three steps:

1. build something with Factory;
2. post it publicly;
3. submit the link.

New candidates are reviewed by the Guild Council and, if selected, proceed to
an interview. Factory states that it curates for quality and does not accept
every submission. The page does not publish a submission deadline.

## Chosen format

**Open-source project**, supported by a technical article and short demo.

Factory’s open-source guidance asks for:

- a public repository with a clear README and license;
- an explanation of what the project does and how it uses Factory/Droid;
- a quickstart others can run;
- a project maintained well enough to work today;
- meaningful added value rather than an empty or copied experiment.

The article guidance adds:

- a concrete task from start to finish;
- exact Droid features, commands, or setup;
- screenshots, diffs, or a short clip;
- a real before/after result or metric where available;
- no generic hype, thin paywalled copy, invented benchmark, or unverifiable
  claim.

The demo guidance favors a real task on screen, quick reproduction steps, the
shipped outcome, and a shareable recording or repository.

## Application fields

For a new applicant, the current form requires:

- first name;
- last name;
- email;
- resume in PDF, DOC, or DOCX format, up to 10 MB;
- timezone;
- a submission narrative describing what was built and where it is published;
- agreement to Factory’s review/reposting terms.

LinkedIn is visible but not marked required. Social-profile and Guild-profile
sections are optional, and the form also offers a separate existing-member
path.

## Zaibatsu compliance matrix

| Requirement | Artifact | Status |
| --- | --- | --- |
| Real public project | This repository | Public and anonymously reachable |
| Clear README | [`README.md`](../README.md) | Complete |
| License | [`LICENSE`](../LICENSE) | Complete |
| Runnable quickstart | [`docs/reproducibility.md`](reproducibility.md) | Immutable v1.14.0 passed 241-test, 115-file credential-disabled full-history candidate and tag clones, candidate/roof/tag CI, both Gitleaks modes, four live-v1.14-schema byte checks, fourteen strict schemas, exact bundle, pack, observation, and classification regeneration, and planning-only semantic proof |
| Reusable value | [`examples/economic-factory.json`](../examples/economic-factory.json), [cron variant](../examples/economic-factory-cron.json), [factory portfolio](../examples/factory-portfolio.json), [evidence-return record](../examples/economic-factory.evidence-return.json), [improvement-proposal specification](../examples/economic-factory.improvement-proposal-spec.json), [evidence-bound proposal](../examples/economic-factory.improvement-proposal.json), [observation specification](../examples/economic-factory.improvement-observation-spec.json), [normalized observation](../examples/economic-factory.improvement-observation.json), [classification policy](../policies/improvement-classification-v1.json), [checked classification](../examples/economic-factory.improvement-classification.json), [candidate-contract specification](../examples/economic-factory.improvement-candidate-spec.json), [bound candidate](../examples/economic-factory.improvement-candidate.json), [`catalog/modules.json`](../catalog/modules.json), [source lock](../examples/economic-factory.source-lock.json), [qualification policy](../policies/runtime-qualification-v1.json), [signed runtime evidence](../examples/economic-factory.runtime-evidence.json), [evidence-pack manifest](../examples/economic-factory.runtime-evidence-pack-manifest.json), [runtime assessment](../examples/economic-factory.runtime-assessment.json), [rebuild plan](../examples/economic-factory.rebuild-plan.json), and [`scripts/zaibatsu.py`](../scripts/zaibatsu.py) | Another project can scaffold a fail-closed definition, reproduce and inspect self-verifying control bundles, join them into a closed evidence-only multi-factory view, bind a verified pack to its exact source and route, record typed untrusted intent, structurally normalize an evidence-bound report, deterministically classify an aligned pair for validation planning, bind exact non-executable candidate-contract bytes without granting validation or promotion authority, bind one bundle to exact annotated-release control sources, compare a policy-compatible module substitution, generate a missing-evidence plan, verify scoped signed assertions, package every referenced artifact and verifier descriptor, assess exact gaps and freshness, and compile verified inputs into a non-executing rebuild DAG offline |
| Explain Factory/Droid role | [`docs/droid-session.md`](droid-session.md) | Authenticated session, scoped diff, and independent validation recorded |
| End-to-end case study | [`docs/case-study.md`](case-study.md) | Factory-of-software-factories narrative and real Droid result complete |
| Exact command/setup | [`docs/droid-session.md`](droid-session.md) | Local-Qwen command, prompt, and redacted credential boundaries recorded |
| Screenshots/diff/clip | [`docs/demo-script.md`](demo-script.md) | Reviewed diff ready; final public clip pending |
| Real result or metric | [`docs/evidence.md`](evidence.md) | Two-file contribution, pre-change gap, and passing validation recorded |
| Public link in submission narrative | [`docs/guild-application.md`](guild-application.md) | Public URL verified |
| Required resume | Applicant-owned file | Required at form submission |

## Submission gate

Do not submit a private URL, call designed components operational, claim
Factory work without a real session, or treat a locally passing checkout as a
public clean-clone proof. The exact release checklist is in
[Guild application](guild-application.md).

The bounded local-Qwen Droid run supplies reviewable “build something with
Factory” evidence. The v1.1.0 through v1.4.0 candidates passed their scoped
clean-clone gates, and v1.4.0 is now an immutable public release. The v1.5.0
qualification-planning candidate and immutable release passed the same public
proof. The v1.6.0 bundle-derived qualification-evidence candidate passed that
proof, and its immutable release passed tag CI and clone reproduction. The
v1.7.0 source-lock candidate and immutable release passed the complete public
boundary. The v1.8.0 rebuild-DAG candidate and immutable release passed the
same complete public boundary. The v1.9.0 signed runtime-evidence candidate
passed the 194-test clean-clone, schema, signature, exact-regeneration,
Gitleaks, and independent-CI boundary; its immutable release passed roof and
tag CI, live-schema byte checks, and full-history tag-clone reproduction. The
v1.10 runtime-evidence-pack candidate passed 203 tests, 90-file validation,
exact pack/assessment/rebuild regeneration, both Gitleaks modes, five strict
schemas, and independent CI from a credential-disabled full-history clone. Its
immutable release passed roof and tag CI, three live-schema byte checks, exact
tag-clone regeneration, both Gitleaks modes, and strict schema validation. The
v1.11 closed-portfolio working candidate passes 212 local tests, 97-file
validation, two strict schemas, exact three-bundle regeneration, seeded
malformed and forged-plan controls, and least-authority adversarial tests. The
exact candidate also passed a credential-disabled full-history clone, both
Gitleaks modes, seven strict schemas, exact plan regeneration, non-authorizing
assertions, and independent CI. Its immutable release passed roof and tag CI,
two live-schema byte checks, full-history tag-clone reproduction, strict schema
validation, and exact plan regeneration. The v1.12 route-bound evidence-return
candidate passes 221 tests, 100-file validation, a credential-disabled
full-history clone, both Gitleaks modes, eight strict schemas, exact
regeneration, replay/forgery/type/size/authority tests, and independent CI.
Its immutable release passed roof and tag CI, a live tagged-schema byte check,
full-history tag-clone reproduction, exact regeneration, both Gitleaks modes,
and strict schema validation. The v1.13 evidence-bound improvement-proposal
candidate passes 230 tests, 105-file validation, a credential-disabled
full-history clone, both Gitleaks modes, ten strict schemas, exact
portfolio/return/proposal regeneration, explicit non-authorizing output, and
independent CI. Its immutable release and full-history tag clone passed
roof/tag CI, two live-schema byte checks, exact regeneration, strict external
validation, and both Gitleaks modes. The final clip and applicant-owned form
submission remain.

The v1.14 structural-observation and deterministic-classification candidate
passed 241 tests, 115-file validation, a credential-disabled full-history
clone, both Gitleaks modes, fourteen strict schemas, exact observation and
classification regeneration, explicit planning-only output, and independent
CI. Its evidence roof, annotated immutable release, roof/tag CI, four
live-schema byte checks, and full-history tag-clone reproduction also passed.
The final clip and applicant-owned form submission remain external.

The v1.15 evidence-bound candidate-contract candidate passed 247 tests,
120-file validation, a credential-disabled full-history clone, both Gitleaks
modes, sixteen strict schemas, exact candidate regeneration, explicit
contract-only output, and independent CI. Its evidence roof and immutable
release are the remaining release steps; the final clip and applicant-owned
form submission remain external.
