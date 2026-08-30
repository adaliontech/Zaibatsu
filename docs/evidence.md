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
| Architecture validator | Passed locally for v1.8.0; immutable v1.7.0 remains independently proved | 78 required files, 13 components, 3 current software factories, 2 portable definition variants, 10 catalog modules and content-addressed artifacts, 1 resolved control plan, bundle manifest, annotated-release source lock, qualification policy/plan/evidence/assessment, and deterministic rebuild DAG, plus inspection/comparison/qualification/rebuild schemas, 11 meta-factory capabilities, 4 sanitized evidence receipts, 9 meta-factory invariants, 8 component invariants, and 10 submission gates checked; v1.8.0 public-clone and CI proof remain pending |
| Adversarial unit tests | Passed locally for v1.8.0; immutable v1.7.0 candidate and tag clones remain independently proved | 183 of 183 tests passed locally; v1.8.0 public-clone and CI proof remain pending |
| Broken-link and public-safety scan | Passed after release hardening | Git-tracked and non-ignored files are inspected; force-added ignored paths, directory-name bypasses, all symlinks, Git submodules, Linux/macOS/Windows home paths, tailnet DNS, IPv4/IPv6, credential patterns, opaque content regardless of media suffix, invalid UTF-8, and local links fail closed |
| Malformed-input robustness | Passed 2026-08-30 | 5,000 seeded JSON-like cases produced 50,000 calls across architecture, factory, readiness, consistency, and all four evidence validators with zero unhandled exceptions (seed `20260830`) |
| Module-composition malformed-input robustness | Passed locally 2026-08-30 | 10,000 seeded JSON-like cases produced 40,000 calls across catalog, binding, plan, and portable-factory validators with zero unhandled exceptions (seed `20260830`) |
| Module-artifact and bundle malformed-input robustness | Passed locally 2026-08-30 | 20,000 deterministic malformed artifact and archive cases covered random JSON shapes, random bytes, truncation, bit flips, insertion, and trailing data with zero unhandled exceptions (seed `0x5A1BA75`) |
| Qualification malformed-input robustness | Passed locally 2026-08-30 | 10,000 seeded recursive shapes, 2,500 hostile bundle inputs, and 1,000 independently stronger policies produced zero unhandled exceptions or unsafe qualification results (seed `150015`) |
| Qualification-evidence malformed-input robustness | Passed locally 2026-08-30 | 10,000 seeded recursive evidence/assessment shapes, 2,500 hostile bundle inputs across all four evidence/assessment wrappers, and 1,000 independently stronger policies produced zero unhandled exceptions or unsafe eligibility results (seed `160016`) |
| Source-lock malformed-input and schema robustness | Passed locally 2026-08-30 | 10,000 seeded recursive lock shapes, 2,500 hostile bundles, and 20,000 random path/URL checks produced zero unhandled exceptions or unsafe acceptances (seed `170017`); isolated AJV 8.17.1 Draft 2020-12 accepted the checked lock and a shape-correct SHA-256 repository while rejecting nine authority, type, credential, URL, traversal, count, duplicate, mixed-OID, and extra-field controls |
| Rebuild-plan malformed-input and schema robustness | Passed locally 2026-08-30 | 10,000 seeded recursive semantic inputs, explicit cyclic and non-finite values, 2,500 hostile high-level bundle inputs, and deep-nesting CLI/archive controls produced no unhandled exception or unsafe result (seed `1800`); isolated strict AJV 8.17.1 Draft 2020-12 accepted the checked plan and rejected 10 authority, boolean/integer, count, duplicate, evidence-ID, digest, and extra-field controls |
| Independent secret scan | Passed locally for the v1.8.0 worktree and on v1.7.0 candidate/tag clones | Checksum-pinned Gitleaks `8.30.1` found no leaks in the full public Git history or current v1.8.0 tree; the prior candidate and immutable tag trees also passed, while GitHub secret scanning and push protection provide a separate repository guard |
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
| v1.4.0 candidate proof | Passed | Credential-disabled public clone of `44c29183ea6b5f7d307ccdd3ef1a37162d476752` passed all 143 tests, schema and receipt contracts, strict Git checks, Gitleaks 8.30.1 history/tree scans, canonical systemd bundle `d4918fd16f55b907a0b2b9734422d7106d3030a511e5cae5d6efc1cb7b253aba`, cron bundle `1b7b7ea21ffce65c47dae79765fbf46368e00da44ed2426791de1cc3365c2f72`, exact semantic assertions, and AJV validation of the inspection and comparison outputs; [GitHub Actions run 33335215008](https://github.com/adaliontech/Zaibatsu/actions/runs/33335215008) independently passed |
| v1.4.0 release proof | Passed | The [immutable latest release](https://github.com/adaliontech/Zaibatsu/releases/tag/v1.4.0) tags evidence roof `0ed4003bf970262b02b88c5d535a1a75c38d6bd2`; [tag Actions run 33335357062](https://github.com/adaliontech/Zaibatsu/actions/runs/33335357062) passed, both tagged schema URLs matched byte-for-byte, and a final credential-disabled tag clone repeated all 143 tests, both Gitleaks modes, artifact hashes, semantic assertions, and AJV output validation |
| v1.5.0 candidate proof | Passed | Credential-disabled public clone of `85ebee8652ee87fed986aa44c2634d166b0238c8` passed all 153 tests, 68-file validation, strict Git checks, Gitleaks 8.30.1 history/tree scans, canonical systemd bundle `d4918fd16f55b907a0b2b9734422d7106d3030a511e5cae5d6efc1cb7b253aba`, cron bundle `1b7b7ea21ffce65c47dae79765fbf46368e00da44ed2426791de1cc3365c2f72`, inspection `0ec784c98036b6b43fd8c8a41bb033ac5cb660ef39fd9f159e3720d2bf3a17a1`, comparison `252dcdfd28b3cd93449ec97f11bdcf9e3c9c19c9bc51cffbbfacc25d87486b0b`, canonical-JSON qualification-policy digest `4fd359cc6dfe3eb3b555eb26a3453939fde34efd8d65a281a81dd34041468e9a`, canonical-JSON qualification-plan digest `a9419341bf0806e1a6fc3769354e46ac6eb1c29043042ddd7eec35cca1a8ff81`, policy file SHA-256 `371f425934f23bd9803440041e4a7ea3385ef6f6a76c58e6667cb1947423b59d`, plan file SHA-256 `725d24bf778c33c4b31522d0ccf7a93cd8b4fadcfd107939e35b07624b74bc9d`, exact non-authorizing semantic assertions, and AJV validation with weakened-policy and authority-inflation negative controls; [GitHub Actions run 33336298353](https://github.com/adaliontech/Zaibatsu/actions/runs/33336298353) independently passed |
| v1.5.0 release proof | Passed | The [immutable latest release](https://github.com/adaliontech/Zaibatsu/releases/tag/v1.5.0) tags evidence roof `5240d66d198df26ef74dfb8985314e331206d8b2`; [roof Actions run 33336395437](https://github.com/adaliontech/Zaibatsu/actions/runs/33336395437) and [tag Actions run 33336424136](https://github.com/adaliontech/Zaibatsu/actions/runs/33336424136) passed, both tagged v1.5.0 schema URLs matched byte-for-byte, and a final credential-disabled tag clone repeated all 153 tests, 68-file validation, both Gitleaks modes, artifact hashes, semantic assertions, and AJV validation |
| v1.6.0 candidate proof | Passed | Credential-disabled public clone of `25f8be0fd4e042f2f723d911ff716c936ef1393a` passed all 163 tests, 72-file validation, strict Git checks, Gitleaks 8.30.1 history/tree scans, and exact reproduction of the prior systemd/cron bundles, inspection, comparison, qualification policy, and qualification plan. It reproduced canonical-JSON qualification-evidence digest `a19e1f82e13f6a7e07011c6e80e112d4981740e9188805e615ee57e12c9d1963` (file SHA-256 `0e986a355998210f1e31ece296def22fd115f9985d22d6a8522055fcf98c08c1`) and canonical-JSON qualification-assessment digest `465fc52b7941bda938480767277af39b4677cc23e5817273845e9c8e0711d8d2` (file SHA-256 `0ec2d40c351ff2add63ed62f85fbdd8cd6a36863cbef77dd7c98c59736fdd2da`), exact non-authorizing semantic assertions, and isolated AJV 8.17.1 Draft 2020-12 validation with authority, eligibility, and policy-floor negative controls; [GitHub Actions run 33337170136](https://github.com/adaliontech/Zaibatsu/actions/runs/33337170136) independently passed |
| v1.6.0 release proof | Passed | The [immutable latest release](https://github.com/adaliontech/Zaibatsu/releases/tag/v1.6.0) tags evidence roof `f514d5d197e69fce478b2ab037a3c1cc435938d1`; [roof Actions run 33337296146](https://github.com/adaliontech/Zaibatsu/actions/runs/33337296146) and [tag Actions run 33337317937](https://github.com/adaliontech/Zaibatsu/actions/runs/33337317937) passed, both tagged v1.6.0 schema URLs matched byte-for-byte, and a final credential-disabled tag clone repeated all 163 tests, 72-file validation, both Gitleaks modes, artifact hashes, exact non-authorizing assertions, and tagged AJV validation with negative controls |
| v1.7.0 source-lock candidate | Passed | Credential-disabled full-history public clone of `b9c96ba312827a2b5a09ebef1518092c33cc4a56` passed all 173 tests, 75-file validation, strict Git, both Gitleaks 8.30.1 modes, isolated AJV 8.17.1 Draft 2020-12 controls, exact non-authorizing assertions, and byte-identical regeneration of systemd bundle `d4918fd16f55b907a0b2b9734422d7106d3030a511e5cae5d6efc1cb7b253aba` and source lock `1b7880ef131987bd04e766b3c647435e0ec010d1ed1db889dc43c76894b2b919` (canonical digest `006db4c1633c559e159ee7c1eb23e3b5150bb6aaefcb4782a773e7b91504b688`) over sixteen blobs in annotated `v1.6.0` tag object `50fb6c262ded7d42a0ace55436064ab8740ca601`; [GitHub Actions run 33338396408](https://github.com/adaliontech/Zaibatsu/actions/runs/33338396408) independently passed. The lock denies remote ownership, signature, runtime-source, qualification, eligibility, activation, and deployment claims. |
| v1.7.0 release proof | Passed | The [immutable latest release](https://github.com/adaliontech/Zaibatsu/releases/tag/v1.7.0) uses annotated tag object `0a2cf65de3a2fef6a8bc895f4830b2536d3a182d` and tags evidence roof `dbc562a5926329f3fb16e4a6de75c75254235b82`; [roof Actions run 33338496754](https://github.com/adaliontech/Zaibatsu/actions/runs/33338496754) and [tag Actions run 33338520957](https://github.com/adaliontech/Zaibatsu/actions/runs/33338520957) passed. A credential-disabled full-history tag clone repeated all 173 tests, 75-file validation, strict Git, both Gitleaks modes, artifact hashes, exact non-authorizing assertions, and tagged AJV validation; the live v1.7.0 source-lock schema matched the tag byte-for-byte at SHA-256 `912fee59aeba16cf2a67c428ab773cc2cbe87f8585a396ec7ab093b0f908afb5`. |
| v1.8.0 rebuild-DAG local proof | Passed locally; public candidate proof pending | The generated rebuild plan has file SHA-256 `357e88d92d5f98f99f048835c524b6106ed2fcc77ee5cff57f41ea74a41f7553` and canonical digest `bc0e093fd97e7a2a2cfc62f8c6082d9013b5c3fa0ff0fe28dff1d819dc39e445`. It binds bundle `d4918fd16f55b907a0b2b9734422d7106d3030a511e5cae5d6efc1cb7b253aba`, source lock `006db4c1633c559e159ee7c1eb23e3b5150bb6aaefcb4782a773e7b91504b688`, qualification policy `4fd359cc6dfe3eb3b555eb26a3453939fde34efd8d65a281a81dd34041468e9a`, plan `a9419341bf0806e1a6fc3769354e46ac6eb1c29043042ddd7eec35cca1a8ff81`, evidence `a19e1f82e13f6a7e07011c6e80e112d4981740e9188805e615ee57e12c9d1963`, and assessment `465fc52b7941bda938480767277af39b4677cc23e5817273845e9c8e0711d8d2`; all 9 actions are blocked, 58 evidence bindings are missing, and execution/activation/deployment/recovery authority remains false. The schema file is SHA-256 `e08003232d1e15822105b8bba7b88aebdbfe78003a6857665fd57437c6737adb`. |
| Demo recording | Pending applicant action | Record from immutable `v1.8.0` using the [Demo script](demo-script.md) after its release proof passes |

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
