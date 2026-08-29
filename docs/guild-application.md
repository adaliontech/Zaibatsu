# Guild application package

## Current submission state

**Submission type:** Open-source project

**Link to submission:** `https://github.com/adaliontech/Zaibatsu`

The application is prepared but must not be submitted yet. The official Guild
path requires real Factory work and a public link. The local package is ready;
publication, fresh-clone proof, the final demo, and applicant materials remain
explicit gates in
[`architecture/submission-readiness.json`](../architecture/submission-readiness.json).

## Current project description

Zaibatsu is an executable reference architecture for putting deterministic
control around probabilistic AI workers. It models durable jobs, scoped
capabilities, private Tailscale administration, Ansible configuration,
artifact gates, and recovery boundaries, then validates the safety invariants
offline. The case study distinguishes operational, preproduction, designed,
planned, and pending-evidence components—including Nix, the PostgreSQL
Dispatcher, and project sandboxes.

The core repository works without a model or Droid credentials. For the Guild
case study, authenticated Factory Droid used an owner-operated Qwen 3.8 27B
GGUF 3-bit model on a clean sanitized clone. Its reviewed change strengthened the
contract from a three-stage check to the full ordering `persist <
execute_in_sandbox < verify < policy_decision < controlled_side_effect` and
added an adversarial test that the old validator accepted. Independent
validation passed before the contribution was promoted.

## Factory contribution paragraph

Factory Droid `0.206.0`, backed by the local Qwen model through an authenticated
OpenAI-compatible gateway, changed exactly
`scripts/validate_repository.py` and `tests/test_validate_repository.py`. The
new test moves `policy_decision` before `verify`; the pre-change validator
accepted that unsafe ordering, while the shipped validator rejects it with a
deterministic adjacent-stage error. Droid reported 36 passing tests, and an
independent run reproduced all 36 before later integration and branding checks
brought the package to 40 passing tests. No model or Factory credential is
published.

## One-line description

An executable reference architecture for durable, auditable software factories
where deterministic systems govern probabilistic workers.

## Optional public Guild bio

Independent builder working on self-hosted agentic systems, reproducible
infrastructure, and deterministic safety boundaries for AI-assisted software
operations.

## Social post draft — hold until publication

I built Zaibatsu: deterministic control around probabilistic workers. It turns
agentic-system boundaries into an executable architecture contract—durable
jobs, scoped capabilities, artifact gates, honest maturity labels, and no
direct model-to-production path. Local-Qwen-backed Factory Droid added and
tested the full deterministic task-flow ordering boundary.
https://github.com/adaliontech/Zaibatsu @FactoryAI

## Guild Council interview notes

### What did you build?

A public architecture kit that describes and tests the control contract around
a real self-hosted software-factory program. It is useful without access to my
private fleet: clone it and run one offline command to validate the model and
adversarial cases.

### Why does it matter?

AI engineering often focuses on the worker model while leaving task state,
permissions, side effects, and recovery implicit. Zaibatsu makes those
boundaries first-class and machine-checkable.

### Where did Factory contribute?

Factory Droid worked only inside a sanitized clone under committed `AGENTS.md`
constraints, using the local Qwen endpoint. Its bounded task produced one
inspectable contract improvement and an adversarial test. The prompt,
configuration shape, reviewed diff, session reference, and independent
validation result are retained without publishing either credential.

### What is the most important design decision?

An LLM response is never verification. Workers return artifacts and evidence;
deterministic software decides whether the job may transition or cause an
external side effect.

### What is actually deployed?

Private administration, host automation, shadow execution, and the existing
systemd scheduler have current evidence. The Dispatcher job database,
sandboxes, and Nix environments are not production claims. The Droid
contribution is validated preproduction work and has no deployment authority.

### What would you build next?

The smallest end-to-end Dispatcher slice: one project, transactional job
states and leases, one isolated worker, one artifact verifier, append-only
events, and a tested recovery path. Nix follows when the same worker toolchain
can be reproduced on multiple eligible nodes.

## Applicant-owned fields

These are personal or external artifacts and are intentionally not stored in
the public repository:

- legal first and last name;
- email;
- timezone selection;
- LinkedIn and optional social profiles;
- resume file (PDF, DOC, or DOCX, at most 10 MB);
- consent choices.

## Final release and submission checklist

- [ ] `make validate` passes on the release commit.
- [x] `make droid-preflight` passes without printing the local key.
- [x] The local endpoint completes one bounded Droid task.
- [x] Factory session reference and focused diff are recorded.
- [x] Factory contribution maturity changes from `pending_evidence` only after
      the receipt exists.
- [ ] Repository is published under the intended owner with an MIT license.
- [ ] Fresh clone passes `make validate` without network access.
- [ ] Public repository and article links resolve without authentication.
- [ ] Demo clip or screenshots show a real Factory task and validation result.
- [ ] No private host, credential, recovery, or deployment detail is exposed.
- [ ] Applicant attaches the required resume and personal fields directly in
      the official form.
- [ ] Every required readiness gate is `complete` and `submission_ready` is
      `true`.
- [ ] Submit through [the official Factory Guild form](https://factory.ai/ambassador).
