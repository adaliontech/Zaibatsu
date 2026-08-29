Read `AGENTS.md` first and obey every boundary in it.

Make exactly one focused improvement to the Zaibatsu executable contract. The
current validator only orders `persist`, `verify`, and `controlled_side_effect`.
Strengthen it so the complete deterministic boundary is ordered exactly as:

`persist < execute_in_sandbox < verify < policy_decision < controlled_side_effect`

Work only in `scripts/validate_repository.py` and
`tests/test_validate_repository.py`. Inspect only the relevant task-flow
validation and nearby architecture tests; do not repeatedly reread whole
files. Add one adversarial unit test that moves `policy_decision` before
`verify` and asserts validation rejects that flow. The test must have failed
before the validator change. Keep the error deterministic and easy to explain.

Constraints:

- Work only inside this public repository.
- Do not access the network, credentials, parent directories, private
  infrastructure, or unrelated repositories.
- Do not install dependencies or run deployment, publication, SSH, Tailscale,
  Ansible, OpenTofu, Nix, or system-service commands.
- Do not commit, push, create a remote, or publish anything.
- Do not change architecture claims or maturity labels.
- Do not modify any file other than the two named above.

After editing, run `make validate` once. Return a concise summary naming the
ordered invariant, the exact adversarial mutation, both changed files, and the
validation result.
