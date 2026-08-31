# Demo script

Use only a full-history fresh clone of immutable `v1.14.0` after its release
proof passes. Do not show private terminals, history, settings,
infrastructure, model credentials, notifications, or personal data. Lead with
the real Factory
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
python3 scripts/zaibatsu.py verify-source-lock \
  examples/economic-factory.source-lock.json \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py inspect-bundle \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py bundle examples/economic-factory-cron.json \
  --output /tmp/example-product-cron.factory.tar
python3 scripts/zaibatsu.py compare-bundles \
  /tmp/example-product.factory.tar \
  /tmp/example-product-cron.factory.tar
python3 scripts/zaibatsu.py bundle examples/control-factory.json \
  --output /tmp/example-control.factory.tar
python3 scripts/zaibatsu.py bundle examples/service-factory.json \
  --output /tmp/example-service.factory.tar
python3 scripts/zaibatsu.py portfolio-plan \
  examples/factory-portfolio.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar \
  --output /tmp/example-portfolio.plan.json
python3 scripts/zaibatsu.py verify-portfolio-plan \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar
python3 scripts/zaibatsu.py qualification-plan \
  /tmp/example-product.factory.tar \
  --output /tmp/example-product.qualification-plan.json
python3 scripts/zaibatsu.py verify-qualification-plan \
  /tmp/example-product.qualification-plan.json \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py qualification-evidence \
  /tmp/example-product.qualification-plan.json \
  /tmp/example-product.factory.tar \
  --output /tmp/example-product.qualification-evidence.json
python3 scripts/zaibatsu.py qualification-assessment \
  /tmp/example-product.qualification-evidence.json \
  /tmp/example-product.qualification-plan.json \
  /tmp/example-product.factory.tar \
  --output /tmp/example-product.qualification-assessment.json
python3 scripts/zaibatsu.py verify-qualification-assessment \
  /tmp/example-product.qualification-assessment.json \
  /tmp/example-product.qualification-evidence.json \
  /tmp/example-product.qualification-plan.json \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py verify-runtime-evidence \
  examples/economic-factory.runtime-evidence.json \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py evidence-pack \
  examples/economic-factory.runtime-evidence.json \
  /tmp/example-product.factory.tar \
  --evidence-artifact examples/runtime-evidence/source-revision-fixture.json \
  --verifier-implementation examples/runtime-evidence/fixture-verifier-method.json \
  --output /tmp/example-product.runtime-evidence.tar
python3 scripts/zaibatsu.py verify-evidence-pack \
  /tmp/example-product.runtime-evidence.tar \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py evidence-return-record \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar \
  --output /tmp/example-product.evidence-return.json
python3 scripts/zaibatsu.py verify-evidence-return-record \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar
python3 scripts/zaibatsu.py improvement-proposal-record \
  examples/economic-factory.improvement-proposal-spec.json \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar \
  --output /tmp/example-product.improvement-proposal.json
python3 scripts/zaibatsu.py verify-improvement-proposal-record \
  /tmp/example-product.improvement-proposal.json \
  examples/economic-factory.improvement-proposal-spec.json \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar
python3 scripts/zaibatsu.py improvement-observation-record \
  examples/economic-factory.improvement-observation-spec.json \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar \
  --output /tmp/example-product.improvement-observation.json
python3 scripts/zaibatsu.py classify-improvement-proposal \
  policies/improvement-classification-v1.json \
  /tmp/example-product.improvement-proposal.json \
  examples/economic-factory.improvement-proposal-spec.json \
  /tmp/example-product.improvement-observation.json \
  examples/economic-factory.improvement-observation-spec.json \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar \
  --output /tmp/example-product.improvement-classification.json
python3 scripts/zaibatsu.py verify-improvement-classification \
  /tmp/example-product.improvement-classification.json \
  policies/improvement-classification-v1.json \
  /tmp/example-product.improvement-proposal.json \
  examples/economic-factory.improvement-proposal-spec.json \
  /tmp/example-product.improvement-observation.json \
  examples/economic-factory.improvement-observation-spec.json \
  /tmp/example-product.evidence-return.json \
  /tmp/example-portfolio.plan.json \
  examples/factory-portfolio.json \
  example-product \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-plan.json \
  policies/runtime-qualification-v1.json \
  /tmp/example-control.factory.tar \
  /tmp/example-product.factory.tar \
  /tmp/example-service.factory.tar
python3 scripts/zaibatsu.py runtime-assessment \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-evidence.json \
  examples/economic-factory.qualification-plan.json \
  /tmp/example-product.factory.tar \
  --as-of 2026-08-30T23:00:00Z \
  --output /tmp/example-product.runtime-assessment.json
python3 scripts/zaibatsu.py verify-runtime-assessment \
  /tmp/example-product.runtime-assessment.json \
  /tmp/example-product.runtime-evidence.tar \
  examples/economic-factory.qualification-evidence.json \
  examples/economic-factory.qualification-plan.json \
  /tmp/example-product.factory.tar
python3 scripts/zaibatsu.py rebuild-plan \
  /tmp/example-product.factory.tar \
  --runtime-evidence-pack /tmp/example-product.runtime-evidence.tar \
  --output /tmp/example-product.rebuild-plan.json
python3 scripts/zaibatsu.py verify-rebuild-plan \
  /tmp/example-product.rebuild-plan.json \
  /tmp/example-product.factory.tar \
  --runtime-evidence-pack /tmp/example-product.runtime-evidence.tar
```

> The factory definition selects policy-compatible reusable modules. The plan
> binds the complete definition, catalog, and selected module contracts by
> SHA-256 and rebuilds to the same bytes. The portable bundle also carries its
> five schemas and verifies without extraction. The annotated-release source
> lock then proves which sixteen immutable Git blobs reproduce those exact
> bytes without trusting the checkout. That local control-source proof does not
> authenticate GitHub, verify a tag signature, contain runtime source, or grant
> qualification. The comparison
> changes only the scheduling implementation from systemd to cron while the
> catalog and schemas stay fixed, making modularity directly inspectable. The
> portfolio then joins one verified control bundle and two verified economic
> factory bundles into the actual factory-of-factories view. It binds 21
> disjoint intended namespaces and permits only evidence-return routes. Those
> names do not prove runtime isolation, and the plan grants no cross-factory
> authority or execution. The
> qualification plan then lists 67 evidence bindings still missing across all
> nine modules. Bundle verification then derives nine real but narrow
> contract-conformance receipts. The signed fixture adds one fresh
> source-revision assertion under a scope that is cryptographically valid but
> permanently ineligible. Its canonical evidence pack retrieves and
> digest-verifies the exact JSON artifact and verifier descriptor. It does not
> rerun that verifier or prove the artifact or assertion semantically true. A
> route-bound return record then joins that exact pack to the product factory's
> declared evidence-only route. It proves no transport, content safety,
> classification, promotion, activation, execution, or cross-factory effect.
> The proposal record then binds one typed, untrusted deterministic-gate
> suggestion to that exact return. It records the input without authenticating,
> validating, approving, promoting, rolling out, or executing it. A separate
> observation record puts one untrusted report into a canonical evidence-bound
> shape without calling it safe or true. The deterministic classifier then
> marks the aligned pair eligible for validation planning only; it creates no
> plan and authorizes no validation, mutation, promotion, rollout, or effect. The
> combined assessment records 10 verified and 57
> missing, marks none eligible, and authorizes no activation or execution. A
> signature authenticates the assertion; it does not prove key ownership,
> verifier correctness, or artifact truth. The rebuild graph preserves the
> nine module dependencies and
> four separate gates, but every action remains blocked and has false execution
> authority. These are future action intents, not Ansible, Nix, secret,
> scheduler, model, deployment, or recovery operations. Content identity is not
> treated as broader runtime proof.

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

Pause on the final 241-test pass and 115-file validator summary.

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

1. Clone the immutable `v1.14.0` tag with full history into a new temporary
   directory after its release proof passes. Do not use `--depth 1`; source-lock
   verification requires the referenced annotated `v1.6.0` tag and objects.
2. Increase terminal font size and hide unrelated tabs and notifications.
3. Run `make validate` once off camera.
4. Prepare only the public prompt, sanitized receipt, focused diff, and status
   ledger.
5. Record at 1080p or better with readable output and captions.

## Capture checklist

- [ ] Repository URL and `v1.14.0` tag visible once.
- [ ] Real Factory/Droid session receipt and shipped diff visible first.
- [ ] Pre-change gap and adversarial post-change result are understandable.
- [ ] Portable factory scaffold and validation succeed on screen.
- [ ] Checked-in plan verification and byte-stable rebuild succeed on screen.
- [ ] Portable bundle creation and in-memory verification succeed on screen.
- [ ] Portfolio verification shows one control factory, two economic factories,
      two evidence-only routes, and false runtime-isolation/authority claims.
- [ ] Source-lock verification reports the annotated `v1.6.0` tag, sixteen
      inputs, and false qualification, eligibility, and activation flags.
- [ ] Qualification plan visibly leaves all nine modules runtime-ineligible.
- [ ] Runtime assessment shows 10 verified bindings, 57 missing runtime
      bindings, fixture-only scope, and zero eligible modules.
- [ ] Runtime-evidence-pack verification reports exact embedded materials while
      the narration preserves the no-reexecution and no-artifact-truth boundary.
- [ ] Evidence-return verification names the product-to-control route and shows
      false transport, shared-promotion eligibility, and cross-factory effects.
- [ ] Rebuild-plan verification shows nine blocked actions, four separate gates,
      and false execution, activation, deployment, and recovery authority.
- [ ] “The factory of software factories” hierarchy is visible.
- [ ] Observation verification shows canonical structure without claiming
      authentication, safety, truth, or merit.
- [ ] Classification verification shows validation-planning eligibility while
      validation, approval, promotion, rollout, and execution remain false.
- [ ] `make validate` shows all 241 tests and 115 contract files passing.
- [ ] Maturity limits are stated explicitly.
- [ ] No private history, addresses, credentials, local settings, or host details.
- [ ] Captions are included.
- [ ] Final clip has a public, stable link.
