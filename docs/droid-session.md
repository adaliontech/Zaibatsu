# Factory Droid integration

## Current state

On 2026-08-28, Droid CLI `0.206.0` authenticated successfully and used an
owner-operated Qwen 3.8 27B GGUF model through an authenticated
OpenAI-compatible gateway. On 2026-08-29, authenticated llama.cpp metadata
confirmed the loaded model filename identifies Qwen 3.8 27B and reports
`Q4_K - Small` quantization. A read-only native-tool canary and a bounded
repository contribution both completed. The contribution was reviewed and
independently validated before promotion.

The model strengthened the deterministic task-flow ordering contract and added
an adversarial test. It did not receive publication, deployment, secret, or
private-operations authority. The integration is validated preproduction
evidence for this public kit, not a production-performance claim for the 27B
model.

## Why the integration is separate

- `make validate` remains offline, deterministic, and model-independent.
- `.factory/settings.local.json` is ignored and must never be committed.
- Factory CLI authentication and the model gateway credential are separate;
  neither value is copied into documentation, logs, prompts, or evidence;
- Droid receives only this public repository, never the private operations
  sources or Dispatcher bootstrap;
- a model result becomes evidence only after human diff review and independent
  deterministic validation.

## Custom-model configuration

Factory documents
[local custom models](https://docs.factory.ai/model-independence/byok) through
the `generic-chat-completion-api` provider and an OpenAI-compatible `baseUrl`.
Prepare the ignored file on the machine that owns the endpoint:

```bash
cp .factory/settings.local.example.json .factory/settings.local.json
```

Then replace the example model identifier and endpoint. The preflight accepts
HTTP loopback or a Tailscale DNS host; the deployed URL remains ignored and is
not evidence. Supply `ZAIBATSU_QWEN_API_KEY` through the launch
credential mechanism. Authenticate Factory separately with either a secure CLI
login receipt or `FACTORY_API_KEY`. Do not type or store either secret value in
this repository. Run:

```bash
make droid-preflight
```

The tracked example contains no working credential. `make droid-preflight`
checks the configuration shape, private endpoint class, model-key reference,
Factory authentication metadata, and Droid binary without contacting the
model or printing either secret. Endpoint health, streaming, native tool calls,
and model behavior were verified separately in the recorded live sessions.

Factory’s custom-model guidance recommends 30B-or-larger models for agentic
coding. Zaibatsu therefore treats this 27B model as an experiment for one
narrow, adversarially tested change—not as a production-performance claim.
Deterministic acceptance gates decide whether its contribution is kept.

## Bounded contribution command

The successful contribution used the following public command shape from a
clean temporary clone:

```bash
droid exec \
  --cwd . \
  --model "custom:Local-Qwen-3.8-27B-0" \
  --auto low \
  --enabled-tools "Read,Grep,Glob,Edit,Create,Execute" \
  --output-format json \
  -f .factory/prompts/review.md
```

The prompt forbids network access, dependency installation, Git publication,
production or secret access, and edits beyond the validator and its tests. The
credential was injected transiently by a root-owned launch boundary after
which Droid ran as the repository user. The sanitized clone contained no ignored
settings or private operations source.

## Exact prompt

See [`.factory/prompts/review.md`](../.factory/prompts/review.md).

## Evidence record

| Field | Current value |
| --- | --- |
| CLI version | `0.206.0` |
| Model | Owner-operated GGUF whose loaded filename identifies Qwen 3.8 27B; server-reported `Q4_K - Small` |
| Model metadata | Authenticated `/props` observation with path, alias, and credential redacted; filename-level identity limitation recorded in [`evidence/qwen-model-observation-v1.json`](../evidence/qwen-model-observation-v1.json) |
| Endpoint | Authenticated OpenAI-compatible gateway; health and model alias passed |
| Local-model credential | Root-only, source-bound, and transiently injected; value never recorded |
| Factory credential | Secure CLI login, separate from the model credential; value never recorded |
| Native-tool canary | Two turns: one `Read` call and exact sentinel; zero Factory credits |
| Successful session | `46f941a9-82f8-4df3-a45c-b8158996360b` |
| Contribution baseline | Pre-public source revision retained in the owner’s private audit evidence |
| Files changed by Droid | `scripts/validate_repository.py`; `tests/test_validate_repository.py` |
| Focused contribution | Enforce `persist < execute_in_sandbox < verify < policy_decision < controlled_side_effect` |
| Adversarial test | Move `policy_decision` before `verify`; the pre-change validator accepted this mutation |
| Droid-reported validation | 36 tests and standalone validator passed; `git diff --check` clean |
| Independent validation | Same two-file diff passed 36 tests; integrated Zaibatsu package later passed 59 tests |
| Reviewed diff | 21 insertions, 9 deletions in the accepted two-file contribution |

## Promotion rule

The promotion gate was satisfied on 2026-08-28:

1. both credential boundaries, static preflight, endpoint health, streaming,
   and native tool calls passed;
2. the real command completed 15 model turns;
3. the diff was narrow, public-safe, and manually reviewed;
4. the adversarial mutation was independently shown to pass before the change;
5. independent `make validate` passed on the accepted diff;
6. this redacted record names the task, session, diff, and outcome.

The bounded machine-readable session summary is retained in
[`evidence/droid-contribution-v1.json`](../evidence/droid-contribution-v1.json).

An earlier broad audit was capped after repetitive read turns and no file
change. That model-quality failure was not promoted. The successful retry used
the narrower prompt now retained in [`.factory/prompts/review.md`](../.factory/prompts/review.md).
Factory authentication and the model credential remain separate requirements.
