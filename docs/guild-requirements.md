# Factory Guild requirements

Research date: **2026-08-28**

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
| Real public project | This repository | Ready locally; public remote pending owner-authorized publication |
| Clear README | [`README.md`](../README.md) | Complete |
| License | [`LICENSE`](../LICENSE) | Complete |
| Runnable quickstart | [`docs/reproducibility.md`](reproducibility.md) | Complete locally without Droid |
| Explain Factory/Droid role | [`docs/droid-session.md`](droid-session.md) | Authenticated session, scoped diff, and independent validation recorded |
| End-to-end case study | [`docs/case-study.md`](case-study.md) | Architecture narrative and real Droid result complete |
| Exact command/setup | [`docs/droid-session.md`](droid-session.md) | Local-Qwen command, prompt, and redacted credential boundaries recorded |
| Screenshots/diff/clip | [`docs/demo-script.md`](demo-script.md) | Reviewed diff ready; final public clip pending |
| Real result or metric | [`docs/evidence.md`](evidence.md) | Two-file contribution, pre-change gap, and passing validation recorded |
| Public link in submission narrative | [`docs/guild-application.md`](guild-application.md) | URL reserved; public visibility pending |
| Required resume | Applicant-owned file | Required at form submission |

## Submission gate

Do not submit a private URL, call designed components operational, claim
Factory work without a real session, or treat a locally passing checkout as a
public clean-clone proof. The exact release checklist is in
[Guild application](guild-application.md).

The bounded local-Qwen Droid run now supplies reviewable “build something with
Factory” evidence. A public repository URL, fresh-clone proof, final clip, and
applicant-owned form materials are still required before submission.
