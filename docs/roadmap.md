# Roadmap

The roadmap strengthens the real system in bounded increments. It does not
authorize production migration.

## Phase 0 — Public package and Guild evidence

- validate the architecture kit — complete locally;
- connect the owner-operated Qwen 3.8 27B GGUF 3-bit model through an
  authenticated OpenAI-compatible endpoint without committing its API key —
  complete;
- authenticate headless Droid separately from the model credential — complete;
- pass the static Droid preflight, then run, review, and record one bounded
  Factory/Droid contribution — complete;
- publish the sanitized repository;
- reproduce from a clean clone;
- record a short demo and submit the public link.

Exit: every Guild claim is backed by a public artifact or explicit private
evidence class, with no pending claim disguised as complete.

## Phase 1 — Minimum Dispatcher contract

- PostgreSQL schema for jobs, transitions, attempts, leases, evidence, policy
  decisions, and append-only events;
- exact three-project enum and deny-unknown behavior;
- transactional transition and lease tests;
- backup, restore, and migration rollback tests.

Exit: jobs survive worker failure, invalid transitions fail closed, and every
terminal state retains verifier evidence.

## Phase 2 — One bounded worker path

- one project and one low-risk workflow;
- authenticated worker registry and capability matching;
- isolated job workspace;
- artifact attachment and deterministic validator;
- lease expiry, reassignment, and idempotency drill.

Exit: two interchangeable workers can complete or resume the same bounded job
without duplicate side effects.

## Phase 3 — Project sandboxes

- separate identities, repositories, credentials, networks, memory, and
  deployment permissions;
- lifecycle and cleanup policy;
- retained failed workspace and recovery drill;
- denial tests for cross-project access.

Exit: compromise of one project worker cannot access the other project or the
control plane.

## Phase 4 — Nix worker environments

- introduce one project flake only after the actual dependency contract is
  known;
- pin the toolchain and lock file;
- reproduce on at least two eligible nodes;
- prove cache-independent clean development shells;
- integrate the result into worker eligibility.

Exit: the same revision yields the same declared tool environment on multiple
workers, and a missing Nix environment makes a worker ineligible rather than
triggering improvisation.

## Phase 5 — Controlled production authority

- private monitoring and alerting;
- off-provider encrypted restore drill;
- single-writer scheduler and publication proof;
- per-unit cutover and rollback;
- observation window with explicit rollback triggers;
- owner authorization after all evidence passes.

Exit: the Dispatcher owns only the scopes that have independently passed their
full production and recovery gates.
