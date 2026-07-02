---
name: update-from-docs
description: Update this plugin's skills from upstream documentation after a new release. Use after a Home Assistant, ESPHome, or AppDaemon release ships, or when asked to "update the plugin", "update from documentation", "sync with the docs", "refresh for the new release", or "check what changed". Walks a registry of version-volatile targets — regenerating what is deterministic (the trigger/condition key allowlist) and surfacing semantic syntax changes for human review.
---

# Update From Documentation

Keep this plugin's skills current with upstream docs after a release, without
re-explaining what to check each time. Home Assistant, ESPHome, and AppDaemon
each ship on their own cadence — run this against whichever one released, using
the target registry below.

## Two kinds of update (keep them separate)

- **Mechanical — safe to auto-apply:** deterministic, regenerated from a source
  of truth (e.g. the documented trigger/condition key allowlist). A script does
  it; the output cannot drift into fiction.
- **Judgment — must be reviewed by a human:** renamed option *values* (e.g. the
  `any` → `each` behavior rename), structural shifts (e.g. `behavior`/`threshold`
  moving under `options:`), new required fields, deprecations, new functions.
  These hide inside unchanged pages and do **not** show up in a mechanical diff.
  Never silently rewrite semantic prose — verify against a doc quote, or flag it.

## Target registry

Work the targets that match the release. `Method` says how to update each.

| # | Target (skill) | Volatile content | Triggered by | Method |
|---|---|---|---|---|
| 1 | `ha-automations` `reference/purpose-specific-keys.md` | documented trigger/condition **keys** | HA release | **Script** (Step A) |
| 2 | `ha-templates` `reference/template-functions.md` | documented template **function/filter/test names** | HA release | **Script** (Step A) |
| 3 | `ha-automations` §3 | `behavior` values/defaults, `options:` nesting, `threshold` shape, `target:` types | HA release | Review (Step B) |
| 4 | `ha-automations` §8–11 | new **selectors**, blueprint/input features, automation **modes** | HA release | Review (Step B) |
| 5 | `ha-templates` §18–21 | new/changed function **signatures**, gotchas (e.g. radians), deprecations | HA release | Review (Step B) |
| 6 | `esphome-lvgl` | ESPHome component syntax, **LVGL** widgets/properties/migrations | ESPHome release | Review (Step B) |
| 7 | `ha-appdaemon` | AppDaemon **API** changes | AppDaemon major release | Review (Step B) |
| 8 | `esphome-validate` / `ha-validate` / `ha-mcp-setup` | CLI flags, commands, setup steps | rarely | Review, low priority |

`ha-troubleshooting` and `svg-rendering` are not doc-version-volatile — skip.

## Step A — Mechanical regeneration (targets 1–2)

```bash
python3 skills/update-from-docs/sync_references.py                    # all allowlists
python3 skills/update-from-docs/sync_references.py --only template-functions
python3 skills/update-from-docs/sync_references.py --ref next --check # preview an RC
```

Regenerates both allowlists from `home-assistant/home-assistant.io` and prints
**ADDED** / **REMOVED-or-RENAMED** names per reference:
- [`../ha-automations/reference/purpose-specific-keys.md`](../ha-automations/reference/purpose-specific-keys.md) (triggers + conditions)
- [`../ha-templates/reference/template-functions.md`](../ha-templates/reference/template-functions.md) (functions/filters/tests)

If new trigger domains appeared, add/extend a row in ha-automations §3's "Common
keys by domain" table. Renamed names → fix any prose that used the old one.

An empty name diff does **not** mean "nothing changed" — signature/behavior
changes to existing names still need Step B.

## Step B — Judgment review (targets 2–7)

Verify against the docs; do not trust the current skill text.

1. **Read the release notes** for the version (the release blog) and search for
   the volatile terms relevant to the target: `trigger`, `condition`, `action`,
   `behavior`, `options`, `threshold`, `selector`, `blueprint`, `template`,
   `filter`, `Labs`, `deprecat`; for ESPHome/AppDaemon, their own changelogs.
2. **Diff a sample of authoritative pages against the skill's claims.** Fetch the
   relevant pages and compare verbatim to what the skill says:
   - HA triggers/conditions/actions: `https://rc.home-assistant.io/{triggers,conditions,actions}/<key>/`;
     raw source `source/_triggers/<key>.markdown` and shared includes
     `source/_includes/triggers/{targets,behavior}.md`.
   - HA templating: the Templating documentation page (functions/filters/tests list).
   - HA selectors / blueprints: the selectors and blueprint schema pages.
   - ESPHome / LVGL: `esphome.io` component pages + LVGL upstream changelog.
   - AppDaemon: `appdaemon.readthedocs.io` API reference.
3. For each discrepancy, note: the **doc quote**, the **current skill text**, and
   the **proposed correction**.

## Step C — Apply + report

- Apply the **mechanical** updates (Step A) and any **verified** prose fixes.
- Output a clearly-marked **"Needs review"** section for every semantic change:
  doc quote → current text → proposed edit. Apply a prose edit only after
  confirming it against the quote; when unsure, leave the text and flag it —
  treat an unverified "fix" as a hallucination risk.
- Bump any version/release references in the touched skills.

## Step D — Validate & finish

- Confirm no skill example references a key absent from the regenerated allowlist.
- Run `ha-validate` (HA YAML) or `esphome-validate` (ESPHome) if any example
  config changed.
- Summarize: which release, targets worked, mechanical edits made, semantic items
  flagged. Open a PR only when the user asks.

## Adding a new automated target

When another fact becomes deterministically extractable (e.g. a selectors
allowlist), add an entry to the `REFERENCES` config in `sync_references.py`
(source dir → output file → grouping → header), wire it into the registry as a
"Script" method target, and keep the review checklist for the rest.
