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
| Operations control repository | prior pinned source plus reviewed working tree, 2026-08-29 | Tailscale, Git/SOPS, Ansible, OpenTofu, secret scope, shadow execution, migration gates; sanitized current result in [`evidence/meta-factory-foundations-v1.json`](../evidence/meta-factory-foundations-v1.json) |
| Orchestrator repository | `a3e1a96403dfbaa279b1c72fb26a68668df6aca5` | Current systemd authority, newsroom regressions, target Dispatcher architecture |
| Dispatcher owner handoff | matched local/remote private copy | Host boundary, deterministic state-machine contract, production-readiness gates |
| Current Dispatcher source and runtime receipts | reviewed working tree and effective state, 2026-08-29 | PostgreSQL contract, bounded coordinator lane, workers, backup/restore, and current authority boundary; sanitized result in [`evidence/dispatcher-validation-v1.json`](../evidence/dispatcher-validation-v1.json) |
| Modular agent scaffold | reviewed source-only working tree, 2026-08-29 | Typed modules, flows, implementation profiles, deterministic gates, human approval, effect fencing, activation blockers, and 309-test pass; sanitized result in [`evidence/meta-factory-foundations-v1.json`](../evidence/meta-factory-foundations-v1.json) |
| Machine-readable readiness ledger | reviewed 2026-08-29 | Passed, pending, and deliberately blocked capability gates |

The private source contains operational detail that is intentionally not
published. Reviewers can evaluate the public invariants, validator, case study,
and redacted status ledger without receiving production access.

## Public package verification

| Evidence | Status | Receipt |
| --- | --- | --- |
| Architecture validator | Passed locally and from the public candidate | 60 required files, 13 components, 3 current software factories, 1 portable definition, 10 catalog modules and content-addressed artifacts, 1 resolved plan and bundle manifest, 11 meta-factory capabilities, 4 evidence receipts, 9 meta-factory invariants, 8 component invariants, and 10 submission gates checked |
| Adversarial unit tests | Passed locally and from the public candidate | 136 of 136 tests passed locally, in a credential-disabled public clone, and in independent GitHub Actions |
| Broken-link and public-safety scan | Passed after release hardening | Git-tracked and non-ignored files are inspected; force-added ignored paths, directory-name bypasses, all symlinks, Git submodules, Linux/macOS/Windows home paths, tailnet DNS, IPv4/IPv6, credential patterns, opaque content regardless of media suffix, invalid UTF-8, and local links fail closed |
| Malformed-input robustness | Passed 2026-08-30 | 5,000 seeded JSON-like cases produced 50,000 calls across architecture, factory, readiness, consistency, and all four evidence validators with zero unhandled exceptions (seed `20260830`) |
| Module-composition malformed-input robustness | Passed locally 2026-08-30 | 10,000 seeded JSON-like cases produced 40,000 calls across catalog, binding, plan, and portable-factory validators with zero unhandled exceptions (seed `20260830`) |
| Module-artifact and bundle malformed-input robustness | Passed locally 2026-08-30 | 20,000 deterministic malformed artifact and archive cases covered random JSON shapes, random bytes, truncation, bit flips, insertion, and trailing data with zero unhandled exceptions (seed `0x5A1BA75`) |
| Independent secret scan | Passed on v1.3.0 candidate | Checksum-pinned Gitleaks `8.30.1` found no leaks in the full public Git history or candidate tree; GitHub secret scanning and push protection provide a separate repository guard |
| Official external links | Resolved 2026-08-28 | 5 of 5 Factory documentation and Guild links resolved successfully |
| Droid CLI availability | Observed | Local version `0.206.0` returned a version receipt |
| First headless Droid attempt | Stopped before model work | Factory authentication failed, zero model turns, and no repository changes |
| Factory CLI authentication | Passed | Secure CLI login completed authenticated Droid Exec sessions; credential value was not recorded |
| Droid/Qwen static preflight | Passed 2026-08-28 | Custom-model shape, private endpoint class, separate credential prerequisites, and Droid version passed without a model request or secret output |
| Local-model endpoint and key | Passed with explicit identity limitation | Health, model alias, streaming, and native tool calls passed through an authenticated gateway; the loaded GGUF filename was labeled `Qwen 3.8 27B` and the server reports `Q4_K - Small`, but official identity and parameter count are unverified; [`evidence/qwen-model-observation-v1.json`](../evidence/qwen-model-observation-v1.json) records the boundary |
| Read-only native-tool canary | Passed | One `Read` call plus exact sentinel in two turns; zero Factory credits and no file change |
| Factory/Droid contribution | Passed and reviewed | Session `46f941a9-82f8-4df3-a45c-b8158996360b`; two scoped files; 15 turns; zero Factory credits; sanitized receipt in [`evidence/droid-contribution-v1.json`](../evidence/droid-contribution-v1.json) |
| Pre-change adversarial proof | Passed | Moving `policy_decision` before `verify` produced no ordering error under the original validator |
| Independent contribution validation | Passed | The accepted two-file diff passed 36 tests, the standalone validator, and `git diff --check` |
| Prior immutable release proof | Passed on v1.1.0 | Credential-disabled public clone of `b9a628a7d9a4910c0e5456c2930b260a96c7d864` passed all 70 tests, the prior contracts, workflow linting, strict Git checks, symlink denial, and both Gitleaks modes; [GitHub Actions run 33291506370](https://github.com/adaliontech/Zaibatsu/actions/runs/33291506370) independently passed before the immutable release |
| v1.1.1 release proof | Passed | Candidate `9f0c1a7f3e866df1e1d5d954e464d53ec96af247` passed 95 tests, schema and receipt contracts, strict Git checks, index-mode denial, and Gitleaks; [candidate CI 33319619388](https://github.com/adaliontech/Zaibatsu/actions/runs/33319619388) and [release CI 33319676893](https://github.com/adaliontech/Zaibatsu/actions/runs/33319676893) passed, then an immutable-tag clone passed again. A post-release usability review found that externally scaffolded files needed a canonical rather than relative schema URI; v1.1.2 is the bounded correction. |
| Fresh-clone reproduction | Passed for v1.1.2 candidate | Credential-disabled public clone of `03d325241c81dec4c83629d36dd4aff3b5e2cf92` passed all 95 tests, schema and receipt contracts, strict Git checks, and Gitleaks 8.30.1 history/tree scans; [GitHub Actions run 33319815603](https://github.com/adaliontech/Zaibatsu/actions/runs/33319815603) independently passed |
| v1.2.0 candidate proof | Passed | Credential-disabled public clone of `d42831e7d6fa367f225fb4a6e489391ad3856e9a` passed all 114 tests, schema and receipt contracts, strict Git checks, and Gitleaks 8.30.1 history/tree scans; [GitHub Actions run 33332863314](https://github.com/adaliontech/Zaibatsu/actions/runs/33332863314) independently passed |
| v1.3.0 candidate proof | Passed | Credential-disabled public clone of `373666ca1d107bc326e01dc8bf9d41037af53089` passed all 136 tests, schema and receipt contracts, strict Git checks, Gitleaks 8.30.1 history/tree scans, and two byte-identical bundle builds with SHA-256 `d4918fd16f55b907a0b2b9734422d7106d3030a511e5cae5d6efc1cb7b253aba`; [GitHub Actions run 33333876277](https://github.com/adaliontech/Zaibatsu/actions/runs/33333876277) independently passed |
| Demo recording | Pending immutable v1.3.0 release; applicant action follows | Record from the released tag using the [Demo script](demo-script.md) |

## Architecture claims

| Claim | Evidence type | Result |
| --- | --- | --- |
| Zaibatsu controls a closed set of one control factory and two economic factories | Machine registry plus current coordinator, scheduler, and factory-boundary evidence | Supported operationally at the named registry scope |
| Git/SOPS provide reviewed source and encrypted static-secret versioning | Private policy/ciphertext validation plus public immutable releases | Git supported operationally at reviewed scope; SOPS/age supported in validated preproduction |
| systemd and cron are current scheduler adapters | Effective scheduler inventory and authority register | Supported operationally; one scheduler of record remains mandatory |
| Modular agent skeletons are implemented source | 309 tests over 21 modules, 6 flows, 12 deployment profiles, and 23 implementation variants | Supported in validated preproduction source; deployment is not claimed |
| LLM harnesses can bind behind typed modules | Source contracts plus bounded Factory/Qwen result | Supported at validated source/contribution scope; general unattended routing is not claimed |
| Factory evidence can recursively promote shared changes without review | No general deployment evidence | Not claimed; owner-gated promotion is designed |
| Current schedules remain authoritative | Runtime plus checked-in configuration | Supported |
| Private management path exists | Tailnet, SSH, firewall, and listener checks | Supported |
| Host automation is idempotent | Ansible first/second-run evidence | Supported in preproduction |
| Publishing shadow fails closed | Disabled timers, execution guard, no-credential dry runs | Supported in preproduction |
| Dispatcher API/policy and PostgreSQL state contracts are implemented | 158 focused tests plus 104 live assertions on disposable PostgreSQL 16.15 clusters, bound by a sanitized source digest and receipt | Supported in validated preproduction; private implementation is not publicly reproducible |
| Bounded deterministic read-only coordinator lane is deployed | Effective runtime plus durable job, worker, artifact, and recovery receipts | Supported operationally at the stated narrow scope |
| Project sandboxes are deployed | No evidence | Not claimed |
| Nix environments reproduce workers | No flake or cross-node proof | Not claimed |

## Current meta-factory foundation run

On 2026-08-29, the private operations policy validator passed its current
Git/SOPS, Ansible, infrastructure, secret, and scheduler contracts. The
source-only modular agent scaffold independently passed 309 tests. The scaffold
contains 21 typed modules, 6 composed flows, 12 deployment profiles, 23
implementation variants, deterministic quality gates, human approval, and
fenced effect contracts. It has no activation or production authority. The
sanitized source digests, counts, and limitations are retained in
[`evidence/meta-factory-foundations-v1.json`](../evidence/meta-factory-foundations-v1.json).

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

The application is not represented as submitted until a demo or screenshot is
published and the required applicant resume is attached. These are tracked in
[Guild application](guild-application.md).
