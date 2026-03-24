# ha-development

A Claude Code plugin with Home Assistant development skills. Covers non-obvious syntax, common pitfalls, and best practices drawn from current HA documentation — not basic or generic knowledge you'd find in tutorials.

## Skills

- **ha-automations** — Automations, scripts, and blueprints. Modern syntax (2024+), state trigger gotchas, YAML boolean coercion, automation modes, variables/scoping, blueprint inputs and selectors, restart-safe timer patterns, polling vs event-driven architecture.
- **ha-templates** — Jinja2 templating in HA. Sandbox security restrictions, safe state access patterns, pipe operator precedence, namespace scoping in loops, time/date functions, template sensor configuration, trigger-based sensors.
- **ha-appdaemon** — AppDaemon Python apps. App lifecycle and threading model, callback signatures, `listen_state` nuances, scheduler API, service calls, async app patterns, time utilities.

## Installation

```
/plugin marketplace add bruxy70/ha-development
/plugin install ha-development@bruxy70-ha-development
```

## License

MIT
