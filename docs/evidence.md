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
| Current Dispatcher source and runtime receipts | reviewed working tree and effective state, 2026-08-29 | PostgreSQL contract, bounded coordinator lane, workers, backup/restore, and current authority boundary |
| Machine-readable readiness ledger | reviewed 2026-08-29 | Passed, pending, and deliberately blocked capability gates |

The private source contains operational detail that is intentionally not
published. Reviewers can evaluate the public invariants, validator, case study,
and redacted status ledger without receiving production access.

## Public package verification

| Evidence | Status | Receipt |
| --- | --- | --- |
| Architecture validator | Passed after Droid contribution, integration review, and branding migration | 26 required files, 12 components, 8 invariants, and 10 submission gates checked |
| Adversarial unit tests | Passed after Droid contribution and release hardening | 46 of 46 tests passed |
| Broken-link and public-safety scan | Passed after release hardening | Includes tailnet DNS, Linux/macOS/Windows home paths, private and public addresses, secret patterns, and local-link checks |
| Malformed-input robustness | Passed 2026-08-28 | 5,000 seeded JSON-like cases produced 20,000 validation calls across architecture, readiness, consistency, and preflight with zero unhandled exceptions |
| Independent secret scan | Passed after branding migration | Checksum-verified Gitleaks `8.30.1` scanned the private pre-release history, sanitized public history, release tree, Actions logs, and credential-free public clone with no leaks found |
| Official external links | Resolved 2026-08-28 | 5 of 5 Factory documentation and Guild links resolved successfully |
| Droid CLI availability | Observed | Local version `0.206.0` returned a version receipt |
| First headless Droid attempt | Stopped before model work | Factory authentication failed, zero model turns, and no repository changes |
| Factory CLI authentication | Passed | Secure CLI login completed authenticated Droid Exec sessions; credential value was not recorded |
| Droid/Qwen static preflight | Passed 2026-08-28 | Custom-model shape, private endpoint class, separate credential prerequisites, and Droid version passed without a model request or secret output |
| Local Qwen endpoint and key | Passed | Health, model alias, streaming, and native tool calls passed through an authenticated gateway; authenticated metadata confirmed a Qwen 3.8 27B GGUF and `Q4_K - Small` quantization while its path and source-bound key remained private |
| Read-only native-tool canary | Passed | One `Read` call plus exact sentinel in two turns; zero Factory credits and no file change |
| Factory/Droid contribution | Passed and reviewed | Session `46f941a9-82f8-4df3-a45c-b8158996360b`; two scoped files; 15 turns; zero Factory credits |
| Pre-change adversarial proof | Passed | Moving `policy_decision` before `verify` produced no ordering error under the original validator |
| Independent contribution validation | Passed | The accepted two-file diff passed 36 tests, the standalone validator, and `git diff --check` |
| Fresh-clone reproduction | Pending release-candidate refresh | The final candidate must pass all 46 tests, repository validation, workflow linting, strict Git checks, and history/tree secret scans from the public remote before release |
| Demo recording | Ready for owner recording | See [Demo script](demo-script.md) |

## Architecture claims

| Claim | Evidence type | Result |
| --- | --- | --- |
| Current schedules remain authoritative | Runtime plus checked-in configuration | Supported |
| Private management path exists | Tailnet, SSH, firewall, and listener checks | Supported |
| Host automation is idempotent | Ansible first/second-run evidence | Supported in preproduction |
| Publishing shadow fails closed | Disabled timers, execution guard, no-credential dry runs | Supported in preproduction |
| Dispatcher API/policy and PostgreSQL state contracts are implemented | 158 focused tests plus 104 live assertions on disposable PostgreSQL 16.15 clusters | Supported in validated preproduction |
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

## Evidence still required before external submission

The application is not represented as submitted until the final public clone
proof, a demo or screenshot, and the required applicant resume are attached.
These are tracked in [Guild application](guild-application.md).
