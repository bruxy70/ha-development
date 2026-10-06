---
name: ha-validate
description: Validates Home Assistant YAML and AppDaemon changes with artifact-specific checks and explicit offline versus live results. Use after editing automations, scripts, helpers or AppDaemon apps, or when reviewing readiness for deployment.
---
# Home Assistant validation gate

Report offline checks and live observations separately. Unavailable checks are **NOT RUN**, never passes. Validation does not authorize deployment, device service calls, reloads, restarts or flashing. Use existing session authorization for the exact target and action; otherwise stop at the reviewable result.

## Requirements and resources
- Python 3: use the project's supported Python installer; verify `python --version`.
- YAML syntax: `python -m pip install PyYAML`. Optional lint/type/test tools: `python -m pip install ruff mypy pytest`; prefer the project's pinned environment.
- Live semantic checks need the complete configuration and its actual HA runtime. Use its existing installation; do not install HA into an AppDaemon environment just for checks.
- [Automation guidance](../ha-automations/SKILL.md), [templates](../ha-templates/SKILL.md), [AppDaemon](../ha-appdaemon/SKILL.md), [diagnostics](../ha-troubleshooting/SKILL.md), [MCP setup](../ha-mcp-setup/SKILL.md).
- [Optional enforcement proposals](reference/enforcement.md) and [behavioral evaluations](reference/evaluations.md).

## Workflow
1. Identify changed artifacts, project checks, complete-config availability and authorized scope. Branch to Python or YAML below; mixed changes run both.
2. Run applicable offline checks. If a check fails, fix the named problem and return here; group repairs only when they share a demonstrated cause.
3. Review business rules, lifecycle cleanup and intended trigger/action behavior. If review fails, repair and return to step 2.
4. If live validation is authorized and available, use the project's deployment procedure, reload only the necessary domain and inspect logs/traces for expected behavior. Restart only when required and authorized. If behavior fails, investigate, repair and return to step 2 before another live check.
5. Remove diagnostic logging introduced for this investigation when no longer needed; preserve existing operational logging. Recheck modified artifacts by returning to step 2, then report results and limits.

Copy and tick this checklist:
- [ ] Scope and target established.
- [ ] Applicable offline checks pass or have explicit unavailable reasons.
- [ ] Business rules and lifecycle reviewed.
- [ ] Authorized live observations recorded, or marked NOT RUN.
- [ ] Temporary investigation diagnostics cleaned up and changed files rechecked.

## Python branch
Run `python -m py_compile <app.py>`, project lint/type checks (for example `ruff check <app.py>` and `mypy <app.py>`), and meaningful pure-logic/lifecycle tests with mocked HA interactions (`python -m pytest <test-path>`). Project coverage/type policy applies; record unsupported checks honestly. Do not require new tests for trivial reversible edits.

## YAML branch
This strict **syntax-only** command accepts HA tags such as `!include`, `!secret` and blueprint `!input` without constructing or resolving them:

```bash
python -c 'import pathlib,sys,yaml; yaml.compose(pathlib.Path(sys.argv[1]).read_text(), Loader=yaml.SafeLoader)' <file.yaml>
```

For complete configuration semantics, run the installed runtime's supported config check, for example `hass --script check_config -c <ha-config-dir>`. Snippet parsing does not prove entity existence, integration support, template behavior or loaded configuration validity.

## Result contract
Keep labels exact; adapt surrounding explanation to project needs.

Input: blueprint using `!input`, with no live HA access.
Output: `Offline syntax: PASS. Complete-config semantics: NOT RUN (runtime unavailable). Live behavior: NOT RUN (no authorized target). Readiness: offline review only.`

Input: Python compiles but a scheduling test fails.
Output: `Offline syntax: PASS. Logic tests: FAIL (missed deadline case). Live behavior: NOT RUN. Readiness: repair and rerun the failed test before deployment.`
