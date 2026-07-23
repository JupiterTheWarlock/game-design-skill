#!/usr/bin/env python3
"""Remove the temporary dual-platform installation and prove it is absent."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "verification" / "results" / "environment-restore.json"
TARGET = "game-design-skill"


def powershell(command: str) -> dict[str, object]:
    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    return {
        "command": command,
        "returncode": result.returncode,
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def json_matches(output: str) -> list[object]:
    try:
        value = json.loads(output)
    except json.JSONDecodeError:
        return [{"unparsed_output": output}] if TARGET in output else []
    matches: list[object] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            if any(TARGET in str(item) for item in node.values()):
                matches.append(node)
                return
            for item in node.values():
                walk(item)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(value)
    return matches


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Preserve prior successful removal transcripts and only re-check absence",
    )
    args = parser.parse_args()
    if args.verify_only:
        previous = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        removals = previous["removals"]
    else:
        removals = {
            "claude_plugin_uninstall": powershell(
                "claude plugin uninstall game-design-skill@game-design-skill --scope local -y"
            ),
            "claude_marketplace_remove": powershell(
                "claude plugin marketplace remove game-design-skill --scope local"
            ),
            "codex_plugin_remove": powershell(
                "codex plugin remove game-design-skill@game-design-skill --json"
            ),
            "codex_marketplace_remove": powershell(
                "codex plugin marketplace remove game-design-skill --json"
            ),
        }
    checks = {
        "claude_plugins": powershell("claude plugin list --json"),
        "claude_marketplaces": powershell("claude plugin marketplace list --json"),
        "codex_plugins": powershell("codex plugin list --available --json"),
        "codex_marketplaces": powershell("codex plugin marketplace list --json"),
    }
    matches = {
        name: json_matches(str(result["stdout"])) for name, result in checks.items()
    }
    user_profile = Path(os.environ["USERPROFILE"])
    cache_paths = {
        "claude": user_profile / ".claude" / "plugins" / "cache" / TARGET,
        "codex": user_profile / ".codex" / "plugins" / "cache" / TARGET,
    }
    caches_absent = {name: not path.exists() for name, path in cache_paths.items()}
    project_local_settings_absent = not (ROOT / ".claude").exists()
    removals_ok = all(result["returncode"] == 0 for result in removals.values())
    checks_ok = all(result["returncode"] == 0 for result in checks.values())
    no_matches = all(not found for found in matches.values())
    evidence = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "removals": removals,
        "post_removal_checks": {
            name: {
                "command": result["command"],
                "returncode": result["returncode"],
                "stderr": result["stderr"],
                "matching_entries": matches[name],
            }
            for name, result in checks.items()
        },
        "caches_absent": caches_absent,
        "project_local_settings_absent": project_local_settings_absent,
        "ok": (
            removals_ok
            and checks_ok
            and no_matches
            and all(caches_absent.values())
            and project_local_settings_absent
        ),
    }
    RESULT_PATH.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(RESULT_PATH), "ok": evidence["ok"]}, indent=2))
    return 0 if evidence["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
