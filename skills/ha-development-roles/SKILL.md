---
name: ha-development-roles
description: Role-specific development and review instructions for ha-development. Use when the project requests one of these named roles or a corresponding focused review.
---

# Development roles

Role constraints apply before implementation; planner is read-only. Completion requires executed, recorded relevant checks; neither marketplace client is assumed to load source-repository hooks.

Read only the reference for the requested role. These are portable role instructions, not registered Claude subagent types. Use the current host tools, client and model; do not launch a second assistant client merely to fulfil a role. Carry out the role locally unless delegation is explicitly authorized and available. Preserve any requirement for an independent review; report it pending if no independent reviewer is available.

- [test-runner-validator](references/test-runner-validator.md)
- [automation-coder](references/automation-coder.md)
- [architect](references/architect.md)
- [esphome-coder](references/esphome-coder.md)
- [ux-designer](references/ux-designer.md)
- [security-auditor](references/security-auditor.md)
- [test-writer](references/test-writer.md)
- [planner](references/planner.md)
- [design-review](references/design-review.md)
- [appdaemon-coder](references/appdaemon-coder.md)

## Requirements and direct companions

Only the selected role's tools are needed. Use the pinned project environment. Python checks use `python3 -m py_compile <app.py>` and pytest (`python3 -m pip install pytest`). Optional compatible fixtures: `python3 -m pip install appdaemon-testing`. ESPHome checks use CLI (`python3 -m pip install esphome`) or supported dashboard Validate/Compile; HA semantic checks use the existing supported HA runtime, not a fictional generic CLI package. Renderer provisioning is in the SVG skill. Loading a role does not authorize live actions.

- [AppDaemon](../ha-appdaemon/SKILL.md)
- [Automations](../ha-automations/SKILL.md)
- [Templates](../ha-templates/SKILL.md)
- [ESPHome LVGL](../esphome-lvgl/SKILL.md)
- [ESPHome validation](../esphome-validate/SKILL.md)
- [HA validation](../ha-validate/SKILL.md)
- [HA connection](../ha-mcp-setup/SKILL.md)
- [Troubleshooting](../ha-troubleshooting/SKILL.md)
- [SVG rendering](../svg-rendering/SKILL.md)
- [Enforcement proposals](../ha-validate/reference/enforcement.md); hooks are not activated here.
- [Evaluations](references/evaluations.md); pending client/model baselines are not passing evidence.
