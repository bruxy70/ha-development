# Approved skill-audit remediation

All24 proposals in the 2026-10-06 audit are approved. Preserve Claude Code and Codex marketplace compatibility. No release, push, live HA/device actions or hook activation.

- [x] Check clean baseline and approved proposal scope.
- [x] Refactor display skills; correct SVG/ESPHome examples and validation boundaries (#1,9,10,13,14).
- [x] Refactor automation/template/AppDaemon guidance and timer examples (#6,8,15).
- [x] Repair updater checkout/write safety and role portability/copy synchronization (#3–5,11).
- [x] Repair troubleshooting/MCP/HA validation and shared enforcement guidance (#1,2,7,12).
- [x] Add direct resources, contents, workflows, prerequisites and examples (#16–19,21–23).
- [x] Add isolated evaluation definitions and record execution limits (#20,24).
- [x] Execute actual used-model pairs and then decide conditional prose reductions (blocked: model set unspecified; Claude OAuth expired).
- [x] Validate frontmatter/links/body sizes/helper behavior/role synchronization.
- [x] Reaudit all11 skills against all13 rules; repair approved-intent failures.
- [x] Record results and file-by-file changes.

## Specification and verification strategy

Entrypoints remain <500 body lines. New instructional references are directly linked; >100-line references start with contents. Preserve domain facts during extraction. Runtime/cache installations are read-only maintenance inputs; writes require an explicit source checkout. Stage/validate all generator outputs before writing and restore originals on replacement failure. Client-specific hooks are documented proposals only, with explicit validation fallback. Missing runtime/model/device checks remain unverified, never recorded as passes. Conditional prose cuts require paired evidence; keep them if that evidence is unavailable.

Baseline: clean main at49ce962. Repository changes themselves are reviewable rollback through Git diff; do not commit/reset or push implicitly. Targeted offline checks use isolated fixtures, no live services. No actual device config files are edited by this work.

## Review
Repository edits and offline checks complete. All143 rule verdicts recorded in audit-results.md. Rules4/11 remain FAIL for all11 skills; conditional rule5 remains FAIL for LVGL/SVG/templates/roles. Model evidence is blocked; no full-pass claim.
