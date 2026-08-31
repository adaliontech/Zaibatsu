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
| A checkout, moved tag, lightweight tag, Git replacement object, or repository-redirection environment variable lies about bundle lineage | The source lock requires an annotated semantic-version tag, disables replacement objects, sanitizes Git repository/config redirection, reads exact tag/commit/tree/blob objects rather than worktree files, records native object IDs and independent SHA-256 hashes of object content, enforces safe regular non-executable JSON paths, and rebuilds the byte-identical bundle; it explicitly does not claim remote ownership or signature trust |
| A weak or self-authored qualification report is treated as runtime proof | The versioned minimum policy requires content-addressed base and slot evidence, rejects removed or duplicate requirements, and treats the deterministic qualification plan as missing-evidence inventory only; bundle-derived receipts credit only exact checks rerun by the verifier. Externally supplied assertions require OpenSSH signatures over exact provenance plus evaluator-selected key/factory/scope/requirement/method/implementation/time allowlists; the public key is fixture-only, leaving 57 bindings missing and zero eligible modules |
| A runtime-evidence pack is tampered with or omits the material named by a signed receipt | Canonical in-memory USTAR verification rejects traversal, links, special files, duplicate/extra/missing members, metadata drift, trailing bytes, noncanonical JSON, schema substitution, material digest mismatch, registry or evidence replay, oversize inputs, and scalar type confusion; builders enforce the same bounds as verifiers |
| An undeclared factory, duplicate identity, class swap, or cross-factory route enters the control view | Portfolio planning fully verifies every bundle, requires one closed ordered registry with exactly one control factory, matches bundle identity and class, requires one evidence-only route per economic factory, derives disjoint intended namespaces, and rejects replay, route drift, authority inflation, self-promotion, and scalar type confusion |
| Evidence is replayed from another factory or route, or a return record is treated as permission to promote | The evidence-return verifier rebuilds the exact portfolio plan, fully verifies every bundle and the source pack, requires the named economic factory's single declared route, and fixes transport, content-safety, secret-absence, semantic, classification, promotion, activation, execution, and cross-factory-effect claims to false |
| A valid signature or intact artifact is mistaken for proof that an assertion is true or independent | The contracts state that signatures authenticate payloads and pack digests authenticate retrieved bytes only. Registry selection is an external evaluator trust decision; key ownership and organizational independence are not inferred; verifier assertions are not rerun and artifact semantic truth is not inferred. Production use requires separately reviewed and pinned trust roots, trusted verifier execution, and current-time assessment |
| A stale, future, or replayed receipt is credited to another factory or release | Each signed payload binds the exact factory, bundle, policy, qualification plan, verifier registry, module artifact, requirement, scope, method, and validity interval. Assessment uses an explicit RFC3339 time with `observed_at <= evaluated_at < valid_until`; replay and boundary-time tests fail closed or mark evidence stale |
| A forged, reordered, replayed, or authority-inflated rebuild graph is treated as permission to act | Rebuild planning fully reverifies the exact bundle, release source lock, qualification policy and plan, bundle-derived evidence, canonical runtime-evidence pack and embedded materials, registry, and runtime assessment; reproduces the nine actions, dependencies, blockers, statuses, and four gates byte-for-byte; rejects type confusion and altered inputs; and fixes every execution, side-effect, approval, activation, deployment, and recovery authority claim to false |
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
- Local Git-object lineage does not authenticate the named hosting account or
  prove who signed a release; verified remote ownership and signature policy
  would require separate trust anchors.
- A content-addressed verifier registry identifies the selected trust root but
  does not establish who selected it, who controls a listed key, whether the
  verifier was correct, or whether an unembedded artifact still exists.
- A caller can evaluate evidence at a historical time. The result is an exact
  historical assessment, not a current-health assertion; any future executor
  must supply and enforce a trusted current clock before authorization.
- A correct rebuild DAG is still only a plan; safe executors, qualified runtime
  implementations, transactional continuation, rollback, and recovery evidence
  remain separate systems and gates.
- Disjoint names in a portfolio plan do not prove disjoint operating-system
  users, processes, network policy, secret ACLs, databases, worker pools, or
  scheduler authority. Each runtime boundary still needs independent evidence.
- A route-bound evidence-return record may still contain a validly signed but
  malicious, sensitive, or semantically false artifact. The contract proves
  exact byte and route binding, not safe delivery, content inspection, secret
  absence, verifier correctness, usefulness, or promotion eligibility.

Mitigation is layered verification, least privilege, explicit status, regular
restore drills, independent review, and reversible rollout.
