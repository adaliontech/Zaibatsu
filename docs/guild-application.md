# Guild application package

## Current submission state

**Submission type:** Open-source project

**Link to submission:** `https://github.com/adaliontech/Zaibatsu`

The application is prepared but must not be submitted yet. The official Guild
path requires real Factory work and a public link. Immutable v1.1.0 passed its
credential-disabled public-clone proof and independent GitHub CI. The v1.1.1
hardening candidate independently passed the same public boundary; the final
demo and applicant materials remain explicit gates in
[`architecture/submission-readiness.json`](../architecture/submission-readiness.json).

## Current project description

Zaibatsu is an evidence-gated architecture and toolkit for building and
governing project-scoped software factories. It models one control factory and
two economic factories, and provides a portable contract others can scaffold
and validate. Git/SOPS versioning, Ansible host reproduction, cron/systemd
scheduler ownership, modular agent skeletons, interchangeable LLM harnesses,
deterministic gates, and reviewed feedback are represented at their actual
maturities. Nix environments remain planned; the agent scaffold is tested
source but not deployed.

The core repository works without a model or Droid credentials. For the Guild
case study, authenticated Factory Droid used an owner-operated GGUF whose
loaded filename was labeled `Qwen 3.8 27B` and whose server reports
`Q4_K - Small`, on a clean sanitized clone. The label is not independently
verified model identity or parameter count. Its reviewed change
strengthened the contract from a
three-stage check to the full ordering `persist <
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
independent run reproduced all 36 before later integration, branding, release,
and meta-factory checks brought the package to 95 passing tests. No model or
Factory credential is published.

## One-line description

The evidence-gated control layer for building reproducible software factories.

## Optional public Guild bio

Independent builder creating self-hosted software factories with reproducible
infrastructure, modular agents, interchangeable model harnesses, and
deterministic operational boundaries.

## Social post draft

I built Zaibatsu, the factory of software factories: an evidence-gated control
layer for versioning, scheduling, verifying, and improving project-scoped
software factories. It includes portable schemas and a validation CLI;
Git/SOPS and Ansible have bounded evidence, Nix remains planned, and modular
agent skeletons remain tested source rather than deployed authority.
Local-Qwen-backed Factory Droid strengthened and tested one deterministic
gate-ordering invariant, with no direct model-to-production path.
https://github.com/adaliontech/Zaibatsu @FactoryAI

## Guild Council interview notes

### What did you build?

A public executable architecture and reusable validation toolkit for the
meta-factory above my real self-hosted software factories. It defines factory
identity, lifecycle, reproduction, scheduling, modular work,
harness-independent verification, feedback, and promotion. Anyone can clone
it, scaffold a new factory definition, and validate the model and adversarial
cases offline without access to my private fleet.

### Why does it matter?

Software-factory projects often focus on the model while leaving factory
identity, reproducibility, scheduler ownership, task state, feedback,
cross-project permissions, effects, and recovery implicit. Zaibatsu makes the
factory itself a versioned, modular, machine-checkable object.

### Where did Factory contribute?

Factory Droid worked only inside a sanitized clone under committed `AGENTS.md`
constraints, using the local Qwen endpoint. Its bounded task produced one
inspectable contract improvement and an adversarial test. The prompt,
configuration shape, reviewed diff, session reference, and independent
validation result are retained without publishing either credential.

### What is the most important design decision?

Feedback is recursive, but authority is not. Models and economic factories
return typed artifacts and evidence; deterministic software and owner policy
decide whether a job, effect, shared template, or cross-factory improvement may
be promoted.

### What is actually deployed?

The closed factory registry, systemd-managed shared schedules, selected
downstream cron schedules, private administration, bounded read-only
coordination, backups, and evidence return are operational at stated scopes.
Ansible, SOPS/age, broader Dispatcher contracts, deterministic gates, and the
modular agent scaffold have preproduction or source evidence. The agent
scaffold is not deployed, Nix and sandboxes remain planned, recursive shared
promotion remains designed, and the Droid contribution has no deployment
authority.

### What would you build next?

Make one complete factory definition reproducible end to end: canonical Git
lineage, SOPS/age policy, Ansible host state, a real Nix worker environment,
one scheduler owner, one source-only agent profile promoted through
qualification into an observe-only sandbox, and evidence returned to Zaibatsu.
Only after recovery and no-effect proof would I activate another profile or a
low-risk mutation.

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

- [x] `make validate` passes on the release commit.
- [x] `make droid-preflight` passes without printing the local key.
- [x] The local endpoint completes one bounded Droid task.
- [x] Factory session reference and focused diff are recorded.
- [x] Factory contribution maturity changes from `pending_evidence` only after
      the receipt exists.
- [x] Repository is published under the intended owner with an MIT license.
- [x] Immutable v1.1.0 passes `make validate` from a credential-free clone.
- [x] Hardened v1.1.1 candidate passes `make validate` and Gitleaks from a
      credential-free public clone.
- [x] Public repository and article links resolve without authentication.
- [ ] Demo clip or screenshots show a real Factory task and validation result.
- [x] No private host, credential, recovery, or deployment detail is exposed.
- [ ] Applicant attaches the required resume and personal fields directly in
      the official form.
- [ ] Every required readiness gate is `complete` and `submission_ready` is
      `true`.
- [ ] Submit through [the official Factory Guild form](https://factory.ai/ambassador).
