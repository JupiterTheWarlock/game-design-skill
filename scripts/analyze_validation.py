#!/usr/bin/env python3
"""Apply deterministic assertions to the preserved real-CLI cases."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "verification" / "results"
SUMMARY_PATH = RESULTS / "validation-summary.json"


def codex_result(stem: str) -> tuple[str, bool]:
    messages: list[str] = []
    completed = False
    for line in (RESULTS / f"{stem}.stdout").read_text(encoding="utf-8").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "turn.completed":
            completed = True
        item = event.get("item", {})
        if item.get("type") == "agent_message" and item.get("text"):
            messages.append(item["text"])
    return (messages[-1] if messages else "", completed)


def require(text: str, needles: list[str]) -> dict[str, bool]:
    lowered = text.lower()
    return {needle: needle.lower() in lowered for needle in needles}


def main() -> int:
    concept, concept_completed = codex_result("codex-concept-and-pillars")
    concept_checks = require(
        concept,
        ["Project Facts", "Design Proposal", "Pillars", "Sources Applied"],
    )
    concept_checks["turn.completed"] = concept_completed

    system_raw = json.loads((RESULTS / "claude-system-gdd.stdout").read_text(encoding="utf-8"))
    system = system_raw.get("result", "")
    system_checks = require(
        system,
        [
            "States and Transitions",
            "Formula 1",
            "Edge Cases",
            "Given",
            "proposal",
            "No files were written",
            "Sources Applied",
        ],
    )
    system_checks["claude_success"] = (
        system_raw.get("subtype") == "success" and not system_raw.get("is_error", False)
    )

    cross, cross_completed = codex_result("codex-cross-gdd-review")
    cross_checks = require(
        cross,
        [
            "20",
            "10",
            "25%",
            "50%",
            "duplicated tuning-knob ownership",
            "plausible readings",
            "structural concerns rather than proven balance failures",
            "Sources Applied",
        ],
    )
    cross_checks["turn.completed"] = cross_completed
    cross_checks["does_not_infer_201_hp"] = "201" not in cross

    ai_native, ai_native_completed = codex_result("codex-ai-native-review")
    ai_native_checks = require(
        ai_native,
        [
            "feature",
            "removal",
            "interface",
            "authority",
            "bounded",
            "Curator",
            "memory",
            "privacy",
            "retention",
            "unsupported",
            "narrow",
            "ai-native-game-design.md",
            "Sources Applied",
        ],
    )
    ai_native_checks["turn.completed"] = ai_native_completed

    install = json.loads((RESULTS / "install-evidence.json").read_text(encoding="utf-8"))
    install_checks = {
        "commands_ok": bool(install.get("commands_ok")),
        "canonical_sha_matches_both_installs": bool(install.get("all_skill_sha256_equal")),
    }
    links = json.loads((RESULTS / "link-check.json").read_text(encoding="utf-8"))
    restore = json.loads((RESULTS / "environment-restore.json").read_text(encoding="utf-8"))

    cases = {
        "codex_concept_and_pillars": concept_checks,
        "claude_system_gdd": system_checks,
        "codex_cross_gdd_review": cross_checks,
        "codex_ai_native_review": ai_native_checks,
        "dual_installation": install_checks,
        "authored_links": {"link_check_ok": bool(links.get("ok"))},
        "environment_restore": {"restore_ok": bool(restore.get("ok"))},
    }
    case_status = {name: all(checks.values()) for name, checks in cases.items()}
    summary = {
        "ok": all(case_status.values()),
        "cases": cases,
        "case_status": case_status,
        "environment_notes": [
            "Claude system-GDD succeeded after unrelated user MCP servers were isolated with an empty MCP fixture.",
            "The final Codex cross-GDD turn emitted agent_message and turn.completed before the wrapper stopped a hanging user-MCP shutdown; raw stderr and timeout metadata are preserved.",
            "The Codex AI-native review exercises the repository-authored practitioner synthesis through the installed Marketplace skill.",
        ],
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if summary["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
