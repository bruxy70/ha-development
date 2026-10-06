---
name: update-from-docs
description: Refreshes this plugin's version-sensitive references from official Home Assistant, ESPHome and AppDaemon documentation. Use after an upstream release or when requesting a documentation refresh; previews deterministic reference updates and proposes semantic changes for approval.
---

# Update From Documentation

Keep this plugin's skills current with upstream docs after a release, without
re-explaining what to check each time. Home Assistant, ESPHome, and AppDaemon
each ship on their own cadence — run this against whichever one released, using
the target registry below.

## Boundaries and requirements

Semantic changes require a source quote, current text and proposed edit for human approval. Verification supports the proposal; it does not replace approval. Preserve all unapproved semantic text. Source quotes must stay within quotation limits.

Requires Python 3.9+ (stdlib only), public GitHub network access and an explicitly selected source Git checkout with both client manifests. Use the project's existing Python or its platform's supported Python installation. No third-party package is required. Optional GITHUB_TOKEN raises API quota; never print it. Installed marketplace packages/caches are maintenance input, not write destinations.

Mechanical extraction regenerates names but still requires nonempty-source validation, review of removals and target-version matching. HTTP 200 proves a page exists, not compatibility or a guessed signature.

## Workflow and checklist

1. Identify release/version and explicit development checkout; if unknown ask for it before running the helper.
2. Preview mechanical changes using the helper below. If fetch/payload/root checks fail, diagnose the named failure and return here; no outputs should have changed.
3. Review additions/removals and authoritative release pages. Propose semantic edits in the required format; wait for human approval before applying them.
4. Apply authorized mechanical changes and only approved semantic edits. On failed checks return to the affected step; preserve unrelated work.
5. Validate syntax, references, examples and relevant companion gates. Fix within approved intent and repeat; after two non-progressing attempts report the blocker instead of declaring success.

- [ ] Confirm release/version and source checkout.
- [ ] Preview and review names, removals and compatibility.
- [ ] Record semantic proposals and approval state.
- [ ] Apply only authorized changes.
- [ ] Check changed files; repair/recheck or report unresolved limits.
- [ ] Summarize files and executed checks.

## Target registry

Work the targets that match the release. `Method` says how to update each.

| # | Target (skill) | Volatile content | Triggered by | Method |
|---|---|---|---|---|
| 1 | `ha-automations` `reference/purpose-specific-keys.md` | documented trigger/condition **keys** | HA release | **Script** (Step A) |
| 2 | `ha-templates` `reference/template-functions.md` | documented template **function/filter/test names** | HA release | **Script** (Step A) |
| 3 | [Purpose syntax](../ha-automations/reference/purpose-specific.md) | `behavior` values/defaults, `options:` nesting, `threshold` shape, `target:` types | HA release | Review (Step B) |
| 4 | [Automation entrypoint](../ha-automations/SKILL.md) | new **selectors**, blueprint/input features, automation **modes** | HA release | Review (Step B) |
| 5 | [Template signatures](../ha-templates/SKILL.md) | new/changed function **signatures**, gotchas (e.g. radians), deprecations | HA release | Review (Step B) |
| 6 | [LVGL core](../esphome-lvgl/references/lvgl-core.md), [actions](../esphome-lvgl/references/actions-navigation.md), [hardware](../esphome-lvgl/references/hardware-fonts.md) | ESPHome component syntax, **LVGL** widgets/properties/migrations | ESPHome release | Review (Step B) |
| 7 | `ha-appdaemon` | AppDaemon **API** changes | AppDaemon major release | Review (Step B) |
| 8 | `esphome-validate` / `ha-validate` / `ha-mcp-setup` | CLI flags, commands, setup steps | rarely | Review, low priority |

Review [ha-troubleshooting](../ha-troubleshooting/SKILL.md) when releases change logs, recorder/restore behavior, service schemas or endpoints. Review [svg-rendering](../svg-rendering/SKILL.md) when renderer/toolchain guidance changes.

## Step A — Mechanical regeneration (targets 1–2)

Resolve [sync_references.py](sync_references.py) from this loaded skill's directory. Claude Code can use `${CLAUDE_SKILL_DIR}/sync_references.py`; Codex uses the actual supplied filesystem path, not a Claude substitution. The checkout may contain the helper; it must be explicitly selected rather than inferred from invocation location.

```bash
python3 <resolved-script> --repo-root <source-checkout> --check
# Apply a mechanical diff authorized by the refresh request:
python3 <resolved-script> --repo-root <source-checkout>
# Optional reviewed removals: --approve-removals
# Optional selection/version: --only template-functions --ref next
# CI freshness gate: --check --fail-on-drift
```

The helper validates both manifests, Git evidence, destination containment and runtime-cache rejection including symlinks. All selected sources are validated/staged before writes; replacement failure restores prior bytes. Preview normally exits successfully on drift; only --fail-on-drift makes drift fail CI. Deterministic content includes headers/contents without capture-date churn. Never regenerate into installed plugin directories.

Regenerates both allowlists from `home-assistant/home-assistant.io` and prints
**ADDED** / **REMOVED-or-RENAMED** names per reference:
- [`../ha-automations/reference/purpose-specific-keys.md`](../ha-automations/reference/purpose-specific-keys.md) (triggers + conditions)
- [`../ha-templates/reference/template-functions.md`](../ha-templates/reference/template-functions.md) (functions/filters/tests)

If new trigger domains appeared, propose an update to the purpose-pattern common-key table with target-version evidence. Renamed names → propose semantic prose changes for approval.

An empty name diff does **not** mean "nothing changed" — signature/behavior
changes to existing names still need Step B.

## Step B — Judgment review (applicable registry targets)

Verify against the docs; do not trust the current skill text.

1. **Read the release notes** for the version (the release blog) and search for
   the volatile terms relevant to the target: `trigger`, `condition`, `action`,
   `behavior`, `options`, `threshold`, `selector`, `blueprint`, `template`,
   `filter`, `Labs`, `deprecat`; for ESPHome/AppDaemon, their own changelogs.
2. **Diff a sample of authoritative pages against the skill's claims.** Fetch the
   relevant pages and compare verbatim to what the skill says:
   - HA triggers/conditions/actions: `https://rc.home-assistant.io/{triggers,conditions,actions}/<key>/`;
     select stable/RC pages to match the target version, not RC alone as stable-version evidence;
     raw source `source/_triggers/<key>.markdown` and shared includes
     `source/_includes/triggers/{targets,behavior}.md`.
   - HA templating: the Templating documentation page (functions/filters/tests list).
   - HA selectors / blueprints: the selectors and blueprint schema pages.
   - ESPHome / LVGL: `esphome.io` component pages + LVGL upstream changelog.
   - AppDaemon: `appdaemon.readthedocs.io` API reference.
3. For each discrepancy, note: the **doc quote**, the **current skill text**, and
   the **proposed correction**.

## Step C — Apply + report

Apply authorized mechanical changes. Present every semantic change and wait for explicit approval; after approval apply only listed edits. Unverifiable claims remain unchanged and flagged.

Required report fields: release/version, authoritative source link and short quote, current file:line/text, proposed replacement, approval state. Section formatting is flexible; these evidence fields are strict.

Input example: a release note renames option A to B (illustrative, not verified release evidence).
Output: `Needs review — version <version>; source <url>, quote <short excerpt>; <file>:<line> says A; proposed B; not applied.` Use actual source/location evidence in real reports.

## Step D — Validate & finish

- Verify every example key against the snapshot or an authoritative page/schema matching the installed target version; absence from a snapshot alone does not prove invalidity.
- Run [ha-validate](../ha-validate/SKILL.md) (HA YAML) or [esphome-validate](../esphome-validate/SKILL.md) (ESPHome) if any example
  config changed.
- Summarize: which release, targets worked, mechanical edits made, semantic items
  flagged. Open a PR only when the user asks.

## Adding a new automated target

When another fact becomes deterministically extractable (e.g. a selectors
allowlist), add an entry to the `REFERENCES` config in `sync_references.py`
(source dir → output file → grouping → header), wire it into the registry as a
"Script" method target, and keep the review checklist for the rest.

## Direct review resources

- [Automation syntax](../ha-automations/SKILL.md) and [purpose patterns](../ha-automations/reference/purpose-specific.md).
- [Template signatures](../ha-templates/SKILL.md).
- [LVGL entrypoint](../esphome-lvgl/SKILL.md); follow its target-specific direct reference links.
- [AppDaemon APIs](../ha-appdaemon/SKILL.md) and [MCP setup](../ha-mcp-setup/SKILL.md).
- [Enforcement proposal and cross-client limitations](../ha-validate/reference/enforcement.md). No hook is activated by this skill.
- [Behavioral evaluations](reference/evaluations.md); missing client/model baselines remain unverified.

- [Isolated helper behavior tests](tests/test_sync_references.py); run `python3 -m unittest discover -s <loaded-skill>/tests -v`. These do not establish client/model baseline results.

- [LVGL framework](../esphome-lvgl/references/framework.md), [lambdas](../esphome-lvgl/references/lambdas.md), [HA integration](../esphome-lvgl/references/ha-integration.md), [layout](../esphome-lvgl/references/design-layout.md), [widgets](../esphome-lvgl/references/widgets.md), [patterns](../esphome-lvgl/references/patterns.md), [troubleshooting](../esphome-lvgl/references/troubleshooting.md).
- [SVG geometry](../svg-rendering/references/svg-geometry.md), [SVG pitfalls](../svg-rendering/references/pitfalls.md), [SVG templates](../svg-rendering/references/templates.md), [SVG style](../svg-rendering/references/example-style.md).
