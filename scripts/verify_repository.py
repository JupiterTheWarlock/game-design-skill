#!/usr/bin/env python3
"""Verify the one-skill Marketplace, provenance lock, and canonical content."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKETPLACE_PATH = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN_ROOT = ROOT / "plugins" / "game-design-skill"
PLUGIN_PATH = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
SKILL_ROOT = PLUGIN_ROOT / "skills" / "game-design-skill"
SKILL_PATH = SKILL_ROOT / "SKILL.md"
REFERENCE_ROOT = SKILL_ROOT / "references"
CONFIG_PATH = ROOT / "provenance" / "upstream-files.json"
LOCK_PATH = ROOT / "provenance" / "upstream-lock.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    errors: list[str] = []

    required = [
        MARKETPLACE_PATH,
        PLUGIN_PATH,
        SKILL_PATH,
        SKILL_ROOT / "agents" / "openai.yaml",
        REFERENCE_ROOT / "provenance.md",
        REFERENCE_ROOT / "authoritative-sources.md",
        CONFIG_PATH,
        LOCK_PATH,
        ROOT / "LICENSE",
        ROOT / "THIRD_PARTY_NOTICES.md",
    ]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    marketplace = json.loads(MARKETPLACE_PATH.read_text(encoding="utf-8"))
    plugin = json.loads(PLUGIN_PATH.read_text(encoding="utf-8"))
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    lock = json.loads(LOCK_PATH.read_text(encoding="utf-8"))

    if marketplace.get("name") != "game-design-skill":
        errors.append("marketplace name must be game-design-skill")
    plugins = marketplace.get("plugins", [])
    if len(plugins) != 1:
        errors.append(f"marketplace must publish exactly one plugin, found {len(plugins)}")
    elif plugins[0].get("name") != "game-design-skill":
        errors.append("the only marketplace plugin must be game-design-skill")
    elif plugins[0].get("source") != "./plugins/game-design-skill":
        errors.append("marketplace plugin source must point to the canonical plugin directory")

    if plugin.get("name") != "game-design-skill":
        errors.append("plugin manifest name must be game-design-skill")
    if marketplace.get("version") != plugin.get("version"):
        errors.append("marketplace and plugin manifest versions must match")
    if plugins and plugins[0].get("version") != plugin.get("version"):
        errors.append("marketplace entry and plugin manifest versions must match")
    if plugins and plugins[0].get("license") != plugin.get("license"):
        errors.append("marketplace entry and plugin manifest licenses must match")
    if plugin.get("license") != "MIT":
        errors.append("plugin manifest license must be MIT")

    all_skill_files = sorted(ROOT.rglob("SKILL.md"))
    if all_skill_files != [SKILL_PATH]:
        shown = ", ".join(str(path.relative_to(ROOT)) for path in all_skill_files)
        errors.append(f"repository must contain exactly one canonical SKILL.md; found: {shown}")

    config_by_destination = {item["destination"]: item for item in config.get("files", [])}
    lock_by_destination = {item["destination"]: item for item in lock.get("files", [])}
    if set(config_by_destination) != set(lock_by_destination):
        missing = sorted(set(config_by_destination) - set(lock_by_destination))
        extra = sorted(set(lock_by_destination) - set(config_by_destination))
        errors.append(f"provenance lock/config mismatch; missing={missing}, extra={extra}")

    for destination, source_entry in config_by_destination.items():
        path = ROOT / destination
        lock_entry = lock_by_destination.get(destination)
        if not path.is_file():
            errors.append(f"missing vendored file: {destination}")
            continue
        if not lock_entry:
            continue
        actual_hash = sha256(path)
        if actual_hash != lock_entry.get("sha256"):
            errors.append(f"hash mismatch for {destination}")
        if lock_entry.get("commit") != config.get("commit"):
            errors.append(f"wrong commit in lock for {destination}")
        if lock_entry.get("repository") != config.get("repository"):
            errors.append(f"wrong repository in lock for {destination}")
        if lock_entry.get("source") != source_entry.get("source"):
            errors.append(f"wrong source path in lock for {destination}")
        if lock_entry.get("status") != "verbatim":
            errors.append(f"vendored entry is not marked verbatim: {destination}")
        if not re.fullmatch(r"1-[1-9][0-9]*", str(lock_entry.get("source_lines", ""))):
            errors.append(f"invalid source line range for {destination}")
        expected_url = (
            "https://github.com/Donchitos/Claude-Code-Game-Studios/blob/"
            f"{config.get('commit')}/{source_entry.get('source')}"
        )
        if lock_entry.get("source_url") != expected_url:
            errors.append(f"source URL is not immutable or does not match for {destination}")

    skill_text = SKILL_PATH.read_text(encoding="utf-8")
    referenced_upstream = set(re.findall(r"`(upstream-[a-z0-9-]+\.md)`", skill_text))
    expected_upstream = {Path(destination).name for destination in config_by_destination}
    if referenced_upstream != expected_upstream:
        missing = sorted(expected_upstream - referenced_upstream)
        extra = sorted(referenced_upstream - expected_upstream)
        errors.append(
            "canonical routing must cover every and only vendored upstream reference; "
            f"missing={missing}, extra={extra}"
        )
    for filename in referenced_upstream:
        if not (REFERENCE_ROOT / filename).is_file():
            errors.append(f"SKILL.md references a missing file: {filename}")

    if "[TODO" in skill_text or "TODO:" in skill_text:
        errors.append("canonical SKILL.md still contains a TODO placeholder")
    if len(skill_text.splitlines()) >= 500:
        errors.append("canonical SKILL.md must remain under 500 lines")

    interface_text = (SKILL_ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if "$game-design-skill" not in interface_text:
        errors.append("openai.yaml default_prompt must mention $game-design-skill")

    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for required_notice in ("Copyright (c) 2026 Donchitos", config["commit"], "MIT License"):
        if required_notice not in notice:
            errors.append(f"third-party notice is missing: {required_notice}")
    root_license = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "MIT License" not in root_license:
        errors.append("root LICENSE does not contain the MIT license heading")

    result = {
        "ok": not errors,
        "plugin_count": len(plugins),
        "skill_count": len(all_skill_files),
        "vendored_file_count": len(config_by_destination),
        "routed_vendored_file_count": len(referenced_upstream),
        "canonical_skill_lines": len(skill_text.splitlines()),
        "errors": errors,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
