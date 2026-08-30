# Demo script

The final demo must use the immutable `v1.1.0` release. Its candidate passed the
credential-free clone proof. Use only the public repository. Do not show
private terminals, history, settings, infrastructure, model credentials, or
personal data.

## Architecture cut — about 2 minutes

### 0:00–0:20 — The thesis

Show the README title and hierarchy.

> Zaibatsu is the factory of software factories. It is the reproducible control
> layer above project-specific economic factories. Each factory keeps its own
> identity, data, credentials, schedules, and production authority while
> Zaibatsu supplies shared definitions, modules, policy, evidence, and recovery.

### 0:20–0:50 — The factory lifecycle

Open `architecture/factory-model.json`. Show `project.role`, the three factory
instances, and `factory_lifecycle`.

> A factory is versioned in Git, static secret material is encrypted with
> SOPS/age, hosts are reproduced with Ansible, and worker environments will use
> Nix after cross-node proof. Work has one cron or systemd scheduler, passes
> deterministic gates, returns evidence, and cannot promote shared changes
> without review.

### 0:50–1:15 — Modular agents and models

Show `agent_policy`, `feedback_policy`, and the capability maturity rows.

> Reusable agent skeletons are typed modules and flows, not autonomous
> personalities. Different LLM harnesses can implement the same bounded port,
> but schemas, linters, tests, hashes, policies, receipts, and owner approval
> decide whether the artifact advances. The scaffold is implemented and tested
> source, not a deployed production agent system.

### 1:15–1:40 — Run the contract

```bash
make validate
```

> The adversarial suite rejects a missing or reclassified factory, promotion
> before evidence, false Nix maturity, plaintext Git secrets, model effect
> authority, factory self-promotion, component/model drift, unsafe task order,
> public leaks, and premature submission claims.

### 1:40–2:00 — Honest current state

Open `docs/implementation-status.md`.

> The closed registry, current schedulers, bounded evidence return, and one
> deterministic read-only coordination lane are operational. Ansible,
> SOPS/age, the broader Dispatcher, deterministic gates, and modular skeleton
> source have bounded validation. Nix, general agent deployment, sandboxes, and
> automatic shared promotion remain planned or designed.

## Factory/Droid insert — about 25 seconds

Show the retained public prompt, session reference, focused diff, adversarial
test, and validation output.

> Factory Droid, backed by my local Qwen endpoint, strengthened one of
> Zaibatsu's deterministic gates. It required persistence, bounded execution,
> verification, policy decision, and controlled side effect in that order. The
> old validator accepted policy before verification; the new test rejects it.
> I independently reproduced all 36 contribution-era checks, and the v1.1.0
> package now passes 70 tests.

Return to the hierarchy:

> Factory Droid is one harness inside the larger system. Zaibatsu is the layer
> that makes whole software factories reproducible, modular, verifiable, and
> capable of reviewed recursive improvement.

## Before recording

1. Use a fresh clone of the immutable `v1.1.0` tag.
2. Increase terminal font size and hide unrelated tabs and notifications.
3. Run `make validate` once off camera.
4. Prepare only the redacted Droid receipt and public diff.
5. Record at 1080p or better with readable output.

## Capture checklist

- [ ] Repository URL visible once.
- [ ] “The factory of software factories” hierarchy visible.
- [ ] `architecture/factory-model.json` lifecycle and maturity visible.
- [ ] Factory/Droid visibly doing or reporting real work.
- [ ] Shipped diff and adversarial test visible.
- [ ] Independent reproduction command legible.
- [ ] No private history, addresses, credentials, local settings, or host details.
- [ ] Captions included.
- [ ] Final clip has a public, stable link.
