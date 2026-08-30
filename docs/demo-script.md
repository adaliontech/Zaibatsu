# Demo script

Use only a fresh clone of immutable `v1.3.0` after its release proof passes. Do
not show private terminals, history, settings, infrastructure, model
credentials, notifications, or personal data. Lead with the real Factory
result; explain the larger architecture only after the reviewer sees working
evidence.

## Main cut — about 2 minutes 30 seconds

### 0:00–0:35 — Real Factory contribution

Show the public Droid receipt, retained prompt, focused diff, and adversarial
test.

> Factory Droid, backed by my local Qwen endpoint, strengthened a deterministic
> gate in Zaibatsu. It required persistence, bounded execution, verification,
> policy decision, and controlled side effect in that order. The original
> validator accepted policy before verification; the added adversarial test
> makes that unsafe ordering fail. The two-file result was independently
> reviewed and reproduced. Droid never received production authority.

Keep the session UUID and contribution-era 36-test result visible briefly. Do
not imply the model's self-report was acceptance.

### 0:35–1:05 — Apply Zaibatsu to a new factory

From the fresh release clone, run:

```bash
demo_root="$(mktemp -d)"
python3 scripts/zaibatsu.py scaffold \
  --id demo-product \
  --class economic_factory \
  --purpose "Produce a bounded software product" \
  --output "${demo_root}/factory.json"
python3 scripts/zaibatsu.py validate "${demo_root}/factory.json"
```

> This is the reusable part: Zaibatsu creates and validates a versioned factory
> contract. The safe starting point denies plaintext secrets, assigns one
> scheduler, keeps models behind typed deterministic gates, forbids direct
> model effects, prevents factory feedback from promoting itself, and refuses
> stronger maturity without a content-addressed evidence binding.

### 1:05–1:35 — The factory-of-factories hierarchy

Show the README hierarchy and `architecture/factory-model.json`.

> Zaibatsu is the control layer above project-scoped economic factories. Each
> factory keeps its own identity, credentials, schedules, data, and production
> authority. Git and SOPS/age version intended state and encrypted static
> material. Ansible owns host reproduction. Cron or systemd owns each workload,
> but never both. Nix is the planned worker-environment boundary and is not
> presented as deployed.

Then run:

```bash
python3 scripts/zaibatsu.py verify-plan \
  examples/economic-factory.plan.json examples/economic-factory.json
python3 scripts/zaibatsu.py rebuild-check examples/economic-factory.json
python3 scripts/zaibatsu.py bundle examples/economic-factory.json \
  --output /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py verify-bundle \
  /tmp/example-product.factory.tar
```

> The factory definition selects policy-compatible reusable modules. The plan
> binds the complete definition, catalog, and selected module contracts by
> SHA-256 and rebuilds to the same bytes. The portable bundle also carries its
> five schemas and verifies without extraction. This proves deterministic
> contract packaging, not deployment or runtime recovery.

### 1:35–2:05 — Run every deterministic gate

```bash
make validate
```

> The offline suite validates the architecture, portable factory definition,
> project-owned schemas, four sanitized evidence receipts, typed submission
> proof, local links, and the entire public scan boundary. Adversarial tests
> cover false maturity, self-promotion, model effect authority, malformed
> evidence, force-added ignored files, misleading media suffixes, and premature
> readiness.

Pause on the final 136-test pass and validator summary.

### 2:05–2:30 — Honest current boundary

Open `docs/implementation-status.md`.

> The closed registry, current schedulers, bounded evidence return, and one
> deterministic read-only coordination lane are operational. Ansible,
> SOPS/age, broader Dispatcher contracts, deterministic gates, and modular
> skeleton source have bounded validation. Nix, general agent deployment,
> sandboxes, and automatic shared promotion remain planned or designed.
> Zaibatsu makes those boundaries machine-checkable instead of hiding them in
> a diagram.

## Before recording

1. Clone the immutable `v1.3.0` tag into a new temporary directory after its
   release proof passes.
2. Increase terminal font size and hide unrelated tabs and notifications.
3. Run `make validate` once off camera.
4. Prepare only the public prompt, sanitized receipt, focused diff, and status
   ledger.
5. Record at 1080p or better with readable output and captions.

## Capture checklist

- [ ] Repository URL and `v1.3.0` tag visible once.
- [ ] Real Factory/Droid session receipt and shipped diff visible first.
- [ ] Pre-change gap and adversarial post-change result are understandable.
- [ ] Portable factory scaffold and validation succeed on screen.
- [ ] Checked-in plan verification and byte-stable rebuild succeed on screen.
- [ ] Portable bundle creation and in-memory verification succeed on screen.
- [ ] “The factory of software factories” hierarchy is visible.
- [ ] `make validate` shows all 136 tests and contract checks passing.
- [ ] Maturity limits are stated explicitly.
- [ ] No private history, addresses, credentials, local settings, or host details.
- [ ] Captions are included.
- [ ] Final clip has a public, stable link.
