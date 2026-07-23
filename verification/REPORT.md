# Validation report

Validation baseline: Claude Code `2.1.216`, Codex CLI `0.142.0`, plugin
version `0.1.0`.

## Repository and provenance

- Marketplace plugins: 1.
- Canonical `SKILL.md` files: 1.
- Verbatim upstream files: 38, all pinned to Donchitos commit
  `984023ddac0d5e27624f2baacde6105e45de375f`.
- Every vendored file is SHA-256 checked, has an immutable source URL and full
  source-line range, and is routed by the canonical skill.
- The Donchitos MIT notice is retained in `THIRD_PARTY_NOTICES.md`.
- The canonical skill, Claude installed copy, and Codex installed copy had the
  same SHA-256 during validation:
  `fbfb5782133c0d129323ef5067439b70ecbe6060b5d79ce450c7667de9196edc`.

## Static gates

- `scripts/verify_repository.py`: pass.
- `scripts/check_links.py`: pass; 5 authored files and 10 authoritative HTTPS
  URLs checked for valid structure. Immutable GitHub source paths are checked
  separately by the repository verifier.
- skill-creator `quick_validate.py`: pass.
- `claude plugin validate . --strict`: pass.
- `claude plugin validate plugins/game-design-skill --strict`: pass.

## Real installed-skill cases

1. **Codex — concept and pillars:** completed. The result separated Project
   Facts and Design Proposals, produced testable pillars/anti-pillars and
   nested loops, and named the internal sources actually applied.
2. **Claude Code — system GDD:** completed with return code 0. The result
   included states/transitions, formulas and ranges, edge cases, dependencies,
   tuning knobs, feedback requirements, and Given-When-Then criteria. All
   sample values were labelled proposals and no files were written.
3. **Codex — cross-GDD review:** emitted the final `agent_message` and
   `turn.completed`. It found the 20/10 reward conflict, 25%/50% death-loss
   conflict, duplicated ownership, acceptance conflicts, and formula gaps. It
   correctly presented floor/cap/order as multiple plausible interpretations
   and called incomplete economy conclusions structural risks rather than
   proven failures.

The cross-GDD Codex process did not exit cleanly after `turn.completed` because
an unrelated user MCP connection hung during shutdown. The validation wrapper
terminated the process tree at its timeout. Raw JSONL proves the model turn
completed; raw stderr and timeout metadata preserve the non-clean process exit.

## Environment restoration

Claude and Codex plugin installations and Marketplace registrations were
removed after evidence capture. Post-removal plugin/Marketplace lists have no
`game-design-skill` entry. The two product caches and Claude's generated local
settings directory were also removed. See `results/environment-restore.json`.

The machine-readable overall result is `results/validation-summary.json`.
