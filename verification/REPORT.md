# Validation report

Validation baseline: Claude Code `2.1.216`, Codex CLI `0.142.0`,
`game-design-skill` `0.3.0`, and `ai-native-game-design` `0.1.0`.

## Repository and provenance

- Marketplace plugins: 2.
- Canonical `SKILL.md` files: 2.
- Each plugin contains exactly one skill and can be installed independently.
- Verbatim CCGS upstream files: 38, all retained only in
  `game-design-skill`, pinned to Donchitos commit
  `984023ddac0d5e27624f2baacde6105e45de375f`, hash-checked, and routed by the
  general skill.
- The repository-authored AI-native synthesis and its focused practitioner
  source notes live only in `ai-native-game-design`.
- The specialist plugin has no file-path or installation dependency on
  `game-design-skill`.
- The Donchitos MIT notice remains in `THIRD_PARTY_NOTICES.md`.

## Static gates

- `scripts/verify_repository.py`: pass; 2 plugins, 2 skills, and all 38
  vendored references routed.
- `scripts/check_links.py`: pass; 8 authored files, 11 HTTPS URLs, and 2 local
  links checked.
- skill-creator `quick_validate.py`: pass for both skills.
- plugin-creator `validate_plugin.py`: pass for both Codex plugin manifests.
- `claude plugin validate . --strict`: pass for the Marketplace.
- `claude plugin validate <plugin> --strict`: pass for both Claude plugin
  manifests.

## Installation evidence

Both plugins were installed separately from the local Marketplace in Claude
Code and Codex. Each product reported a separate plugin ID and version:

- `game-design-skill@game-design-skill` `0.3.0`
- `ai-native-game-design@game-design-skill` `0.1.0`

For each plugin, the canonical `SKILL.md`, Claude cache copy, and Codex cache
copy had the same SHA-256:

- `game-design-skill`:
  `0e44af03580ced53f50244c24b87555d12334146e7dba87d6abaaf3a2f03e790`
- `ai-native-game-design`:
  `7470c9b0c8081c6fded47f5a60481e386d8b9b10ff9ddc4b3f4669da0f947420`

See `results/install-evidence.json`.

## Isolated forward tests

Two fresh agents received only one skill path and one fixture each:

1. The general skill produced project facts, proposals, unknowns, falsifiable
   pillars, anti-pillars, nested loops, and source attribution from the general
   concept fixture without reading AI-native assets.
2. The AI-native skill independently classified the product and its features,
   ran removal tests, specified the player-AI contract and authoritative state
   boundary, reviewed continuity, recovery, safety, privacy, and retention
   claims, prioritized falsifiable prototype cases, and recommended narrowing
   the concept without reading CCGS assets.

An additional external Codex CLI behavioral case exceeded its wrapper timeout
and was terminated. It did not produce current evidence and is not counted as
a passing gate. Older raw model transcripts under `results/` predate this
two-plugin split and are retained only as historical evidence.

## Environment restoration

Both temporary plugin installations and the local Marketplace registrations
were removed after evidence capture. The exact shared Claude and Codex cache
directories and Claude's generated local settings directory were removed
through allowlisted paths. Post-removal checks found neither plugin nor the
Marketplace. See `results/environment-restore.json`.
