# Security and threat model

## Security objective

Compromise or failure of one software factory, worker, model, harness, scheduler,
or user-facing interface must not grant control over another factory or the
Zaibatsu control layer. Probabilistic output and returned factory feedback are
untrusted until deterministic checks and policy authorize their use.

## Protected assets

- owner and machine identities;
- project credentials and deployment rights;
- production data and publication authority;
- task state, leases, policy decisions, and audit evidence;
- factory definitions, module contracts, harness bindings, and release lineage;
- infrastructure plans, configuration, backups, and recovery material;
- sensitive blockchain infrastructure outside the general worker plane.

## Trust boundaries

```text
public inputs and factory evidence
    |
    v
Dispatcher intake and validation
    |
    +---- economic factory A capability boundary
    |
    +---- economic factory B capability boundary
    |
    +---- control-plane capability boundary

model context != credential store
knowledge memory != operational database
worker identity != deployment identity
artifact creation != artifact release
factory feedback != shared policy promotion
source-only skeleton != deployed agent
```

## Threats and controls

| Threat | Control |
| --- | --- |
| Prompt injection asks a worker to exceed scope | Small routed context, tool policy, deny-by-default capabilities, deterministic exit checks |
| Unknown or forged factory enters the registry | Closed machine-readable registry; unknown identity, repository, credential, scheduler, and worker routing fail closed |
| Hallucinated success | Terminal success requires machine evidence; model text alone is rejected |
| Model or harness implementation is substituted | Typed ports, exact implementation/profile bindings, qualification evidence, hashes, and no default fallback |
| Portable module or factory bundle is tampered with | Canonical content digests, immutable schema-body digests, module-local paths, exact catalog/plan binding, strict JSON, in-memory USTAR verification, and rejection of traversal, links, special files, duplicate/extra members, metadata drift, and trailing bytes; inspection and comparison emit no result until every input passes the same verifier |
| Duplicate workers execute the same job | Transactional leases, expiry, attempt numbers, and idempotency keys |
| cron and systemd both own one workload | Scheduler-of-record inventory, duplicate-authority denial, and receipt-bound migration |
| Agent publishes or deploys directly | Workers return artifacts; a separate deterministic policy gate owns side effects |
| One project exposes another project’s secrets | Separate identities, repositories, credentials, network grants, databases, and memory scopes |
| Plaintext secret enters version control | SOPS/age ciphertext policy, secret scans, GitHub push protection, and separate runtime machine-secret delivery |
| One factory poisons shared templates through feedback | Returned evidence is untrusted; shared change requires versioned provenance, deterministic validation, owner policy, and reversible rollout |
| Source-only agent contracts are mistaken for deployment | Machine-enforced maturity, explicit `source_only` status, activation blockers, and sanitized evidence limitations |
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
The private design uses SOPS/age for versionable static ciphertext and bounded
machine identities for runtime delivery. It also uses destination-scoped
access, non-secret references in configuration, root-owned runtime
materialization, and narrow service exposure. Secret values never belong in
prompts, plaintext Git, logs, Kanban, documentation, or validation receipts.

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
- A correct shared improvement can still be wrong for another economic factory.
- cron and systemd semantics differ; inventory alone does not prove safe migration.
- Encrypted Git history still depends on recipient and recovery-key governance.
- Pattern-based secret detection can miss novel credential formats; native
  provider scanning and review remain independent layers.

Mitigation is layered verification, least privilege, explicit status, regular
restore drills, independent review, and reversible rollout.
