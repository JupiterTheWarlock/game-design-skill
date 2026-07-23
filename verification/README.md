# Verification

The fixtures and cases in this directory exercise the installed Marketplace
plugin rather than importing the repository's skill body directly.

## Static checks

```powershell
python scripts\verify_repository.py
python scripts\check_links.py
python C:\Users\GJM258\.codex\skills\.system\skill-creator\scripts\quick_validate.py plugins\game-design-skill\skills\game-design-skill
claude plugin validate . --strict
claude plugin validate plugins\game-design-skill --strict
```

## Real installed-skill cases

```powershell
python scripts\run_validation_case.py codex concept-and-pillars
python scripts\run_validation_case.py claude system-gdd
python scripts\run_validation_case.py codex cross-gdd-review --timeout-seconds 420
python scripts\run_validation_case.py codex ai-native-review --timeout-seconds 420
python scripts\capture_install_evidence.py
python scripts\restore_test_environment.py
python scripts\analyze_validation.py
```

Raw stdout, stderr, CLI versions, elapsed times, and deterministic assertions
are stored under `verification/results/`. The final Codex cross-GDD response
emitted both `agent_message` and `turn.completed`; its process later hung while
shutting down an unrelated user MCP connection and was terminated by the
wrapper timeout. Both the completed protocol evidence and non-clean process
exit are retained rather than conflated.
