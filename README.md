# ha-development

A Claude Code plugin for Home Assistant and ESPHome development. Provides skills with non-obvious syntax, common pitfalls, and best practices drawn from current documentation — plus specialized agents for the full development workflow.

## Skills

- **ha-automations** — Automations, scripts, and blueprints. Modern syntax (2024+), state trigger gotchas, YAML boolean coercion, automation modes, variables/scoping, blueprint inputs and selectors, restart-safe timer patterns, polling vs event-driven architecture.
- **ha-templates** — Jinja2 templating in HA. Sandbox security restrictions, safe state access patterns, pipe operator precedence, namespace scoping in loops, time/date functions, template sensor configuration, trigger-based sensors.
- **ha-appdaemon** — AppDaemon Python apps. App lifecycle and threading model, callback signatures, `listen_state` nuances, scheduler API, service calls, async app patterns, time utilities.
- **esphome-lvgl** — ESPHome-based HMI displays. Hardware configuration (ESP32-S3, display drivers, touchscreens), LVGL widgets, styles, layouts, C++ lambdas, HA integration, common patterns, and troubleshooting.
- **svg-rendering** — SVG rendering for HMI display mockups. Coordinate systems, arc math, gauge templates, gradients, clipping, common pitfalls, and rendering checklist.
- **ha-mcp-setup** — Step-by-step guide for connecting Claude Code to your Home Assistant instance via the built-in MCP server. Covers enabling the integration, creating long-lived access tokens, configuring Claude Code, and troubleshooting.

## Agents

### Domain-Specific Coders
- **esphome-coder** — ESPHome YAML developer. LVGL configurations, sensor bindings, C++ lambdas, display drivers, complete device scripts.
- **automation-coder** — HA automation developer. Modern syntax automations, scripts, blueprints, Jinja2 template sensors.
- **appdaemon-coder** — AppDaemon Python developer. App lifecycle, callbacks, state listeners, schedulers, service calls.

### Cross-Domain Agents
- **architect** — System architecture across HA/ESPHome domains. Data flow design, impact assessment, memory budgeting, integration patterns.
- **planner** — Project planning and research. Requirements gathering, task decomposition, codebase analysis, implementation planning.
- **ux-designer** — HMI display UX design. SVG mockups, ISA-101/EEMUA 201/Gestalt/Fitts' law principles, LVGL-aware layouts.

### Quality & Review
- **test-writer** — Creates tests for AppDaemon apps, ESPHome compilation checks, and automation validation.
- **test-runner-validator** — Runs tests and validates code changes. Systematic failure analysis and fix methodology.
- **security-auditor** — Security review for IoT/HA projects. Network security, secrets management, webhook hardening, authentication.
- **design-review** — UX/UI review for LVGL displays and HA dashboards. Visual design, accessibility, information hierarchy.

## Connecting to Home Assistant (MCP)

This plugin also includes setup instructions for connecting Claude Code to your HA instance via the built-in MCP server. Once connected, Claude can query entities, call services, and interact with HA directly.

Quick setup:
1. In HA: **Settings → Devices & Services → Add Integration → Model Context Protocol**
2. In HA: **Profile → Long-Lived Access Tokens → Create Token**
3. Add to `~/.claude.json`:
```json
{
  "mcpServers": {
    "home-assistant": {
      "type": "http",
      "url": "http://<YOUR_HA_IP>:8123/api/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_TOKEN>"
      }
    }
  }
}
```

See the **ha-mcp-setup** skill for full details and troubleshooting.

## Installation

```
/plugin marketplace add bruxy70/ha-development
/plugin install ha-development@bruxy70-ha-development
```

## License

MIT
