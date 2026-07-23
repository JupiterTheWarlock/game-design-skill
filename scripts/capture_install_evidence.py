#!/usr/bin/env python3
"""Capture dual-platform installation discovery and canonical SHA evidence."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT_PATH = ROOT / "verification" / "results" / "install-evidence.json"
SKILL_RELATIVE = Path("skills") / "game-design-skill" / "SKILL.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def main() -> int:
    user_profile = Path(os.environ["USERPROFILE"])
    version = json.loads(
        (ROOT / "plugins" / "game-design-skill" / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )["version"]
    canonical = (
        ROOT
        / "plugins"
        / "game-design-skill"
        / "skills"
        / "game-design-skill"
        / "SKILL.md"
    )
    claude_installed = (
        user_profile
        / ".claude"
        / "plugins"
        / "cache"
        / "game-design-skill"
        / "game-design-skill"
        / version
        / SKILL_RELATIVE
    )
    codex_installed = (
        user_profile
        / ".codex"
        / "plugins"
        / "cache"
        / "game-design-skill"
        / "game-design-skill"
        / version
        / SKILL_RELATIVE
    )

    files = {
        "canonical": canonical,
        "claude_installed": claude_installed,
        "codex_installed": codex_installed,
    }
    file_evidence: dict[str, object] = {}
    for name, path in files.items():
        file_evidence[name] = {
            "path": str(path),
            "exists": path.is_file(),
            "sha256": sha256(path) if path.is_file() else None,
        }

    commands = {
        "claude_version": powershell("claude --version"),
        "claude_plugin_details": powershell(
            "claude plugin details game-design-skill@game-design-skill"
        ),
        "claude_marketplace_match": powershell(
            "claude plugin marketplace list | Select-String -Pattern 'game-design-skill'"
        ),
        "codex_version": powershell("codex --version"),
        "codex_plugin_list": powershell(
            "codex plugin list --marketplace game-design-skill --json"
        ),
        "codex_marketplace_match": powershell(
            "codex plugin marketplace list --json | Select-String -Pattern 'game-design-skill'"
        ),
    }
    hashes = [entry["sha256"] for entry in file_evidence.values()]
    all_same = all(hashes) and len(set(hashes)) == 1
    commands_ok = all(entry["returncode"] == 0 for entry in commands.values())
    evidence = {
        "captured_at_utc": datetime.now(timezone.utc).isoformat(),
        "plugin": "game-design-skill@game-design-skill",
        "version": version,
        "files": file_evidence,
        "all_skill_sha256_equal": all_same,
        "commands": commands,
        "commands_ok": commands_ok,
        "ok": all_same and commands_ok,
    }
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULT_PATH.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(RESULT_PATH), "ok": evidence["ok"]}, indent=2))
    return 0 if evidence["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
