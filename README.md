# Game Design Skill

A one-plugin Marketplace for Claude Code and Codex. The plugin exposes one
canonical `game-design-skill`; both products load the same `SKILL.md` and the
same source-grounded references.

The game-design material is primarily derived from
[`Donchitos/Claude-Code-Game-Studios`](https://github.com/Donchitos/Claude-Code-Game-Studios)
under its MIT license. Vendored upstream files are pinned, hashed, and mapped
in `provenance/upstream-lock.json`. Platform-specific orchestration in those
files is source material, not an instruction to emulate Claude Code internals.

## Repository contract

- Publish exactly one plugin and one business skill: `game-design-skill`.
- Keep one canonical skill body at
  `plugins/game-design-skill/skills/game-design-skill/SKILL.md`.
- Preserve exact upstream text in `references/upstream-*.md`.
- Put compatibility behavior in the canonical `SKILL.md`, not in duplicated
  Claude- or Codex-specific skill bodies.
- Cite authoritative supplements instead of inventing theory, thresholds, or
  platform behavior.

## Install from a local clone

Replace `<repo>` with the absolute path to this checkout.

### Claude Code

```powershell
claude plugin marketplace add "<repo>" --scope local
claude plugin install game-design-skill@game-design-skill --scope local
claude plugin list
```

### Codex

```powershell
codex plugin marketplace add "<repo>"
codex plugin add game-design-skill@game-design-skill
codex plugin list --marketplace game-design-skill
```

## Validate

```powershell
python scripts/verify_repository.py
python scripts/check_links.py
python C:\Users\GJM258\.codex\skills\.system\skill-creator\scripts\quick_validate.py plugins/game-design-skill/skills/game-design-skill
claude plugin validate . --strict
```

The skill is intentionally source-heavy. Its `SKILL.md` is a compact router;
detailed workflows and templates remain verbatim references and load only when
the current task needs them.
