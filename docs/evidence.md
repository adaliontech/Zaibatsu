# Evidence ledger

## Claim discipline

Evidence is attached to the narrowest claim it can actually prove. Runtime
checks prove runtime state; tests prove the paths they cover; documents prove
intent and boundaries. None substitutes for the others.

## Private source provenance

The public package was reconciled against these private, reviewed sources on
2026-08-18:

| Source | Revision or state | Supports |
| --- | --- | --- |
| Operations control repository | `489a1ed7225424dec291bc2ab61ae7fb7e91895f` | Tailscale, Ansible, OpenTofu, secret scope, shadow execution, migration gates |
| Orchestrator repository | `a3e1a96403dfbaa279b1c72fb26a68668df6aca5` | Current systemd authority, newsroom regressions, target Dispatcher architecture |
| Dispatcher owner handoff | matched local/remote private copy | Host boundary, deterministic state-machine contract, production-readiness gates |
| Machine-readable readiness ledger | reviewed 2026-08-28 | Passed, pending, and deliberately blocked capability gates |

The private source contains operational detail that is intentionally not
published. Reviewers can evaluate the public invariants, validator, case study,
and redacted status ledger without receiving production access.

## Public package verification

| Evidence | Status | Receipt |
| --- | --- | --- |
| Architecture validator | Passed after Droid contribution, integration review, and branding migration | 26 required files, 12 components, 8 invariants, and 10 submission gates checked |
| Adversarial unit tests | Passed after Droid contribution, integration review, and branding migration | 40 of 40 tests passed |
| Broken-link and public-safety scan | Passed after Droid contribution | Included in `scripts/validate_repository.py` |
| Malformed-input robustness | Passed 2026-08-28 | 5,000 seeded JSON-like cases produced 20,000 validation calls across architecture, readiness, consistency, and preflight with zero unhandled exceptions |
| Independent secret scan | Passed after branding migration | Checksum-verified Gitleaks `8.30.1` scanned the private pre-release history, sanitized public history, release tree, Actions logs, and credential-free public clone with no leaks found |
| Official external links | Resolved 2026-08-28 | 5 of 5 Factory documentation and Guild links resolved successfully |
| Droid CLI availability | Observed | Local version `0.206.0` returned a version receipt |
| First headless Droid attempt | Stopped before model work | Factory authentication failed, zero model turns, and no repository changes |
| Factory CLI authentication | Passed | Secure CLI login completed authenticated Droid Exec sessions; credential value was not recorded |
| Droid/Qwen static preflight | Passed 2026-08-28 | Custom-model shape, private endpoint class, separate credential prerequisites, and Droid version passed without a model request or secret output |
| Local Qwen endpoint and key | Passed | Health, model alias, streaming, and native tool calls passed through an authenticated gateway; the source-bound key stayed root-only |
| Read-only native-tool canary | Passed | One `Read` call plus exact sentinel in two turns; zero Factory credits and no file change |
| Factory/Droid contribution | Passed and reviewed | Session `46f941a9-82f8-4df3-a45c-b8158996360b`; two scoped files; 15 turns; zero Factory credits |
| Pre-change adversarial proof | Passed | Moving `policy_decision` before `verify` produced no ordering error under the original validator |
| Independent contribution validation | Passed | The accepted two-file diff passed 36 tests, the standalone validator, and `git diff --check` |
| Fresh-clone reproduction | Passed from the public remote | A credential-free clone of release commit `f039604be4d21b9538b5647665058543dc5f0012` passed all 40 tests, repository validation, workflow linting, strict Git checks, and history/tree secret scans |
| Demo recording | Ready for owner recording | See [Demo script](demo-script.md) |

## Architecture claims

| Claim | Evidence type | Result |
| --- | --- | --- |
| Current schedules remain authoritative | Runtime plus checked-in configuration | Supported |
| Private management path exists | Tailnet, SSH, firewall, and listener checks | Supported |
| Host automation is idempotent | Ansible first/second-run evidence | Supported in preproduction |
| Publishing shadow fails closed | Disabled timers, execution guard, no-credential dry runs | Supported in preproduction |
| PostgreSQL Dispatcher is deployed | No evidence | Not claimed |
| Project sandboxes are deployed | No evidence | Not claimed |
| Nix environments reproduce workers | No flake or cross-node proof | Not claimed |

## Current private validation run

On 2026-08-18, after reconciling one stale test expectation with a now-passed
credential-readiness gate, the complete operations validation passed:

- OpenTofu formatting, initialization, and validation for both configurations;
- 12 Ansible playbook syntax checks;
- production-profile Ansible lint with zero failures and zero warnings;
- policy, YAML, shell, workflow, and secret-leak checks;
- 96 of 96 operations unit tests;
- 34 of 34 pinned newsroom regression tests in a clean detached checkout.

The one-line test correction changed no playbook, host, timer, credential,
bootstrap, or production state.

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

The application is not represented as submitted until a demo or screenshot and
the required applicant resume are attached. These are tracked in
[Guild application](guild-application.md).
