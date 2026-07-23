# Game Design Skill

A one-plugin Marketplace for Claude Code and Codex. It exposes one canonical
`game-design-skill`; both products load the same `SKILL.md` and the same
source-grounded references.

## What this is

We distilled the reusable game-design methodology from
[`Donchitos/Claude-Code-Game-Studios`](https://github.com/Donchitos/Claude-Code-Game-Studios)
(CCGS) into a focused, dual-compatible skill. CCGS provides the primary game
design roles, workflows, review procedures, and document templates; this
repository extracts those methods from the larger multi-agent studio and
packages them as one practical skill for both Claude Code and Codex.

The extraction favors the original CCGS wording and structure. Selected
upstream files are preserved verbatim under the MIT license, pinned to a fixed
commit, hashed, and mapped in `provenance/upstream-lock.json`. The canonical
skill adds only the routing, source-safety rules, and compatibility layer
needed to use the methodology without CCGS's Claude-specific studio
orchestration.

The skill supports concept and pillar development, system decomposition,
system GDD authoring, balance and economy analysis, prototypes and playtests,
UX and accessibility work, scope control, design-change propagation, and
single- or cross-document design review.

## Repository contract

- Publish exactly one plugin and one business skill: `game-design-skill`.
- Keep one canonical skill body at
  `plugins/game-design-skill/skills/game-design-skill/SKILL.md`.
- Preserve exact upstream text in `references/upstream-*.md`.
- Put compatibility behavior in the canonical `SKILL.md`, not in duplicated
  Claude- or Codex-specific skill bodies.
- Cite authoritative supplements instead of inventing theory, thresholds, or
  platform behavior.

## Install

### Claude Code

```powershell
claude plugin marketplace add https://github.com/JupiterTheWarlock/game-design-skill
claude plugin install game-design-skill@game-design-skill --scope user
claude plugin list
```

### Codex

```powershell
codex plugin marketplace add https://github.com/JupiterTheWarlock/game-design-skill
codex plugin add game-design-skill@game-design-skill
codex plugin list --marketplace game-design-skill
```

## Install from a local clone

Replace `<repo>` with the absolute path to this checkout.

### Claude Code — local checkout

```powershell
claude plugin marketplace add "<repo>" --scope local
claude plugin install game-design-skill@game-design-skill --scope local
claude plugin list
```

### Codex — local checkout

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
