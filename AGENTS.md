# HA development plugin maintenance

This repository supports Codex and Claude Code. Keep shared domain skills in `skills/` and preserve both client manifests. Never put personal credentials or workspace-specific Notion data into this public plugin.

Use `ha-mcp-setup` for client-specific connection instructions. Codex loads `.codex-plugin/plugin.json`; Claude uses `.claude-plugin/`. `ha-development-roles` preserves role guidance as references without binding Codex to Claude models or tools.

After editing skills, validate YAML frontmatter and relative references. After changing manifests, run the host plugin validator. Run Python syntax checks when modifying helper scripts and ESPHome checks when changing device configs. The Claude PostToolUse hook does not run in Codex, so run relevant checks explicitly. Keep role reference copies in sync when editing the corresponding `agents/*.md` source.

## Native Codex agents

Native role definitions are installed in `.codex/agents/`. They preserve the Claude role instructions but inherit the selected Codex model. Map `ha-development:<role-name>` to `ha_<role_name>` (hyphens become underscores). Use these for independent reviews or delegated work when requested by the project workflow and permitted by the session. Role reference skills remain available for single-agent work.
