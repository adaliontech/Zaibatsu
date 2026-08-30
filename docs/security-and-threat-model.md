# Security and threat model

## Security objective

Compromise or failure of one worker, model, project, or user-facing interface
must not grant control over another project or the infrastructure control
plane. Probabilistic output is treated as untrusted input until deterministic
checks and policy authorize its use.

## Protected assets

- owner and machine identities;
- project credentials and deployment rights;
- production data and publication authority;
- task state, leases, policy decisions, and audit evidence;
- infrastructure plans, configuration, backups, and recovery material;
- sensitive blockchain infrastructure outside the general worker plane.

## Trust boundaries

```text
public inputs
    |
    v
Dispatcher intake and validation
    |
    +---- project A capability boundary
    |
    +---- project B capability boundary
    |
    +---- control-plane capability boundary

model context != credential store
knowledge memory != operational database
worker identity != deployment identity
artifact creation != artifact release
```

## Threats and controls

| Threat | Control |
| --- | --- |
| Prompt injection asks a worker to exceed scope | Small routed context, tool policy, deny-by-default capabilities, deterministic exit checks |
| Hallucinated success | Terminal success requires machine evidence; model text alone is rejected |
| Duplicate workers execute the same job | Transactional leases, expiry, attempt numbers, and idempotency keys |
| Agent publishes or deploys directly | Workers return artifacts; a separate deterministic policy gate owns side effects |
| One project exposes another project’s secrets | Separate identities, repositories, credentials, network grants, databases, and memory scopes |
| Bootstrap credential becomes permanent broad authority | Short-lived or bounded machine identity, scoped secret references, root-owned materialization, deny-all default |
| Management service becomes public | Loopback or Tailscale binding, firewall verification, and listener inventory |
| Infrastructure plan changes after review | Saved artifact hash, expiry, cost record, and exact apply authorization |
| Control plane failure blocks recovery | Direct owner escape hatch, Git-defined configuration, independent backup, tested restore |
| Documentation leaks operational details | All-file public-safety validator, symlink denial, checksum-pinned Gitleaks history/tree CI, GitHub push protection, and sanitized evidence ledger |
| Model provider is unavailable | Capability routing treats providers as optional; deterministic core continues |

## Capability model

A worker receives a task-specific grant such as:

```text
allow: read one repository
allow: edit one job workspace
allow: run declared tests
allow: attach an artifact
deny: global credentials
deny: unrelated projects
deny: production shell
deny: secret rotation
deny: destructive database or infrastructure action
```

Capabilities expire with the job or lease. Provider credentials remain
isolated from project credentials.

## Secrets

This public package contains no secrets and never needs a secret to validate.
The private design uses encrypted secret storage at rest, destination-scoped
machine access, non-secret references in configuration, root-owned runtime
materialization, and narrow service exposure. Secret values never belong in
prompts, Git, logs, Kanban, documentation, or validation receipts.

## Publication boundary

The public project intentionally omits:

- exact hostnames, addresses, tags, firewall rules, and inventory;
- key fingerprints and machine-account identifiers;
- secret names or storage coordinates that aid discovery;
- production repository access and deployment commands;
- current vulnerability or recovery-window details.

The omission is part of the architecture, not missing documentation.

## Residual risks

- Deterministic checks can be incomplete or encode the wrong policy.
- A compromised control plane can misuse valid capabilities.
- A valid artifact can still have an untested business-level defect.
- Restore evidence decays as systems and data formats change.
- Model and tool supply chains introduce independent risk.
- Pattern-based secret detection can miss novel credential formats; native
  provider scanning and review remain independent layers.

Mitigation is layered verification, least privilege, explicit status, regular
restore drills, independent review, and reversible rollout.
