# Evidence ledger

## Claim discipline

Evidence is attached to the narrowest claim it can actually prove. Runtime
checks prove runtime state; tests prove the paths they cover; documents prove
intent and boundaries. None substitutes for the others.

## Private source provenance

The public package was reconciled against these private, reviewed sources on
2026-08-29:

| Source | Revision or state | Supports |
| --- | --- | --- |
| Operations control repository | `489a1ed7225424dec291bc2ab61ae7fb7e91895f` | Tailscale, Ansible, OpenTofu, secret scope, shadow execution, migration gates |
| Orchestrator repository | `a3e1a96403dfbaa279b1c72fb26a68668df6aca5` | Current systemd authority, newsroom regressions, target Dispatcher architecture |
| Dispatcher owner handoff | matched local/remote private copy | Host boundary, deterministic state-machine contract, production-readiness gates |
| Current Dispatcher source and runtime receipts | reviewed working tree and effective state, 2026-08-29 | PostgreSQL contract, bounded coordinator lane, workers, backup/restore, and current authority boundary; sanitized result in [`evidence/dispatcher-validation-v1.json`](../evidence/dispatcher-validation-v1.json) |
| Machine-readable readiness ledger | reviewed 2026-08-29 | Passed, pending, and deliberately blocked capability gates |

The private source contains operational detail that is intentionally not
published. Reviewers can evaluate the public invariants, validator, case study,
and redacted status ledger without receiving production access.

## Public package verification

| Evidence | Status | Receipt |
| --- | --- | --- |
| Architecture validator | Passed after Droid contribution and skeptical release review | 29 required files, 13 components, 8 invariants, and 10 submission gates checked |
| Adversarial unit tests | Passed after release hardening | 59 of 59 tests passed |
| Broken-link and public-safety scan | Passed after release hardening | Every repository file is inspected or rejected; exact placeholder matching, all symlinks, Linux/macOS/Windows home paths, tailnet DNS, IPv4/IPv6, credential patterns, approved binary formats, and local links are checked |
| Malformed-input robustness | Passed 2026-08-28 | 5,000 seeded JSON-like cases produced 20,000 validation calls across architecture, readiness, consistency, and preflight with zero unhandled exceptions |
| Independent secret scan | Passed manually; continuous CI gate added for v1.0.1 | Checksum-pinned Gitleaks `8.30.1` scans full public Git history and the release tree; GitHub secret scanning and push protection provide a separate repository guard |
| Official external links | Resolved 2026-08-28 | 5 of 5 Factory documentation and Guild links resolved successfully |
| Droid CLI availability | Observed | Local version `0.206.0` returned a version receipt |
| First headless Droid attempt | Stopped before model work | Factory authentication failed, zero model turns, and no repository changes |
| Factory CLI authentication | Passed | Secure CLI login completed authenticated Droid Exec sessions; credential value was not recorded |
| Droid/Qwen static preflight | Passed 2026-08-28 | Custom-model shape, private endpoint class, separate credential prerequisites, and Droid version passed without a model request or secret output |
| Local Qwen endpoint and key | Passed with explicit identity limitation | Health, model alias, streaming, and native tool calls passed through an authenticated gateway; the server-reported loaded filename identifies a Qwen 3.8 27B GGUF and the server reports `Q4_K - Small`; [`evidence/qwen-model-observation-v1.json`](../evidence/qwen-model-observation-v1.json) records what this does and does not prove |
| Read-only native-tool canary | Passed | One `Read` call plus exact sentinel in two turns; zero Factory credits and no file change |
| Factory/Droid contribution | Passed and reviewed | Session `46f941a9-82f8-4df3-a45c-b8158996360b`; two scoped files; 15 turns; zero Factory credits; sanitized receipt in [`evidence/droid-contribution-v1.json`](../evidence/droid-contribution-v1.json) |
| Pre-change adversarial proof | Passed | Moving `policy_decision` before `verify` produced no ordering error under the original validator |
| Independent contribution validation | Passed | The accepted two-file diff passed 36 tests, the standalone validator, and `git diff --check` |
| Fresh-clone reproduction | v1.0.0 passed; v1.0.1 refresh pending | Candidate `44cc3c1f3811a77f0fddf71d6a34ba565d8331e7` retains its 46-test proof; the hardened v1.0.1 candidate must independently pass the 59-test suite and both Gitleaks modes before recording |
| Demo recording | Blocked on v1.0.1 clone proof | See [Demo script](demo-script.md) |

## Architecture claims

| Claim | Evidence type | Result |
| --- | --- | --- |
| Current schedules remain authoritative | Runtime plus checked-in configuration | Supported |
| Private management path exists | Tailnet, SSH, firewall, and listener checks | Supported |
| Host automation is idempotent | Ansible first/second-run evidence | Supported in preproduction |
| Publishing shadow fails closed | Disabled timers, execution guard, no-credential dry runs | Supported in preproduction |
| Dispatcher API/policy and PostgreSQL state contracts are implemented | 158 focused tests plus 104 live assertions on disposable PostgreSQL 16.15 clusters, bound by a sanitized source digest and receipt | Supported in validated preproduction; private implementation is not publicly reproducible |
| Bounded deterministic read-only coordinator lane is deployed | Effective runtime plus durable job, worker, artifact, and recovery receipts | Supported operationally at the stated narrow scope |
| Project sandboxes are deployed | No evidence | Not claimed |
| Nix environments reproduce workers | No flake or cross-node proof | Not claimed |

## Current private validation run

On 2026-08-29, the focused Dispatcher suite passed 158 of 158 tests. The
standalone acceptance harness initially exposed one stale expected row after
the API added its allowlisted workflow field. Correcting that expectation
produced a 104-of-104 pass against two disposable, Unix-socket-only PostgreSQL
16.15 clusters. The acceptance includes lease races, privilege denial,
request-replay protection, hash-chained audit events, logical backup/restore
equivalence, and post-restore continuation; it uses no production data.
The sanitized machine-readable result is
[`evidence/dispatcher-validation-v1.json`](../evidence/dispatcher-validation-v1.json).
It binds the reviewed private source content and exact results; it deliberately
does not represent private implementation as publicly reproducible.

## Official external sources

- [Factory Guild](https://factory.ai/ambassador) — program steps, form fields,
  and submission-quality guidance.
- [Droid CLI quickstart](https://docs.factory.ai/droid-cli/quickstart) —
  project-scoped review workflow and AGENTS.md use.
- [Droid Exec](https://docs.factory.ai/droid-exec/overview) — read-only default,
  explicit autonomy, working-directory scope, and headless evidence path.
- [Factory custom models](https://docs.factory.ai/model-independence/byok) —
  local OpenAI-compatible models, generic provider configuration, and local
  API-key handling.
- [Factory AGENTS.md guide](https://docs.factory.ai/harness/agents-md) — durable
  repository commands and guardrails.
- [Official Qwen3.8 repository](https://github.com/QwenLM/Qwen3.8) — confirms
  the Qwen3.8-27B family exists; it does not prove the provenance of the
  privately loaded GGUF.

## Evidence still required before external submission

The application is not represented as submitted until the v1.0.1 public-clone
proof passes, a demo or screenshot is published, and the required applicant
resume is attached. These are tracked in [Guild application](guild-application.md).
