# Skill audit remediation — 2026-10-06

| Skill | Remaining failed rules | Worst remaining issue |
| --- | ---: | --- |
| esphome-lvgl | 3 | Actual-model evidence and conditional prose reductions |
| esphome-validate | 2 | Actual-model evidence |
| ha-appdaemon | 2 | Actual-model evidence |
| ha-automations | 2 | Actual-model evidence |
| ha-development-roles | 3 | Actual-model evidence and conditional persona reductions |
| ha-mcp-setup | 2 | Actual-model evidence |
| ha-templates | 3 | Actual-model evidence and conditional namespace reduction |
| ha-troubleshooting | 2 | Actual-model evidence |
| ha-validate | 2 | Actual-model evidence |
| svg-rendering | 3 | Actual-model evidence and conditional generic reductions |
| update-from-docs | 2 | Actual-model evidence |

All24 proposal groups were approved. Implemented unconditional repository edits, including optional hook **proposals only**. Fix#20 conditional cuts and fix#24 executed paired model evaluations remain incomplete. All11 changed skills were rechecked against all13 rules. Structural/correctness failures found during the recheck were repaired within approved intent. Remaining26 failed-rule verdicts represent missing evaluation evidence or deliberately retained conditional material, not26 known runtime faults. No claim of full compliance.

## Executed verification and limits

- All11 entrypoint YAML frontmatters valid; body lengths105/88/222/443/34/57/308/156/46/41/132 (alphabetical skill order).
- All local Markdown links resolve; own packaged instructional references directly linked; every supporting Markdown file>100lines has opening contents. Independently discoverable sibling skills retain their own direct resource graphs.
- All10 Claude role sources, reference copies and Codex native instructions synchronized; native Codex model selection remains inherited.
- Six isolated updater behavior tests pass: payload validation/redacted errors, explicit checkout/unrelated cwd/cache alias rejection, no partial writes on source failure, preview/drift/removal/idempotence, rollback after replacement failure, output symlink protection.
- Python helper syntax checks pass; HA !input/!secret/!include syntax accepted and malformed YAML rejected; isolated Jinja filter returned[6,9]; SQLite SELECT allowed and INSERT blocked by read-only URI/query_only.
- Four actual SVG template fixtures parsed, geometry checked and rendered/visually inspected in Chromium153.0.8010.12. ESPHome2026.7.0 installed, but complete target-specific config/compile and hardware behavior not run.
- Installed-layout package copy under an unrelated temporary consumer directory retained resolving entrypoints/resources. Claude plugin and marketplace validators pass with one existing missing-version warning. Codex JSON manifests parsed; no Codex host plugin-validator command is exposed by CLI0.160.1. Actual Codex plugin activation/skill invocation not certified by static parsing.
- Claude Code2.1.278 isolated safe-mode/no-tools availability probe failed OAuth refresh, both sandboxed and unsandboxed. Codex0.160.1 availability probe returned READY, but actual used models and complete skill-discovery isolation are unspecified. Availability probes are not skill baselines. All P1–P3 model pairs remain NOT RUN. User model-set clarification requested.
- Paramiko is not installed, so unknown-host execution fixture not run; RejectPolicy/known_hosts replacement reviewed and Python example syntax checked.
- git diff --check passes. No manifests changed; no live HA changes, deployment, flashing, hook activation, commits or publishing.

## ha-validate

| Rule | Status | Evidence and result |
| --- | --- | --- |
| 1 | PASS | SKILL.md:1–49 body46; direct resources:13–14; short entrypoint. |
| 2 | NOT APPLICABLE | Own reference/enforcement.md and reference/evaluations.md both under100lines. |
| 3 | PASS | SKILL.md:7 explicit live scope; :31 project-specific checks; :34–40 exact syntax and semantic distinction. |
| 4 | FAIL | reference/evaluations.md:3–22 actual-model pairs absent. No model fitness inferred. |
| 5 | PASS | SKILL.md:3 third-person description/use trigger; :7–49 artifact-specific gate. |
| 6 | PASS | SKILL.md:17–21 numbered steps with repair/return routes; :23–28 copyable checklist. |
| 7 | PASS | SKILL.md:18–21 check/repair/recheck; :40 incomplete semantic checks explicitly bounded. |
| 8 | PASS | SKILL.md:17,30–43 Python/YAML fork and strict result labels; :45–49 input/output examples. |
| 9 | PASS | SKILL.md:10–14 requirements/install lines and runtime scope; all packaged relative links resolve in consumer fixture. |
| 10 | PASS | SKILL.md:14 directly links reference/enforcement.md with both-host event/decision/fixture proposals and limits; hooks not activated. |
| 11 | FAIL | reference/evaluations.md:5–18 defines3 approved prompts/results fields; actual baseline/with-skill artifacts not run. |
| 12 | PASS | SKILL.md:7 scope and honest validation boundary precede workflow/examples. |
| 13 | PASS | SKILL.md:1–49 and both own references inspected: evidence/result summaries only; no internal-reasoning echo request. |


| Skill | Failed rules | Worst problem |
| --- | ---: | --- |
| ha-automations | 2 | Missing actual-model paired baseline evidence |
| ha-templates | 3 | Missing actual-model paired baseline evidence |
| ha-appdaemon | 2 | Missing actual-model paired baseline evidence |
| ha-troubleshooting | 2 | Missing actual-model paired baseline evidence |
| ha-mcp-setup | 2 | Missing actual-model paired baseline evidence |

Post-change read-only review on 2026-10-06. All five entrypoints, their owned references and directly linked setup/validation/enforcement resources inspected. Claude Code and Codex marketplace consumers required. Actual used-model set unspecified; no paired model execution performed. Root reports Claude OAuth execution blocked. Structural/isolated fixture checks are not model evidence. All owned Markdown files and companion constraints inspected.

## ha-automations

Body lines: 443.

| Rule | Status | Evidence and result |
| --- | --- | --- |
| 1 | PASS | SKILL.md:1–447; reference/purpose-specific.md and keys snapshot directly linked in the purpose-specific routing section. |
| 2 | PASS | reference/purpose-specific.md:1–6; reference/purpose-specific-keys.md:6–11 contain top contents. |
| 3 | PASS | SKILL.md:12–29,timer and webhook sections; target-version fallback, scoped actions, timer completion/restoration limits and webhook exposure contract. |
| 4 | FAIL | reference/evaluations.md:1–23; three approved prompts/criteria exist but both client rows are Pending/Not run. Fix #24 remains blocked: execute equal fresh baseline/with-skill fixtures on actual used models, record client/version/model/artifacts/outcomes. Definitions do not satisfy evidence. |
| 5 | PASS | SKILL.md:3,34–447; domain discovery trigger and HA-specific schema/behavior reference. No unapproved generic deletion. |
| 6 | PASS | SKILL.md:14–23; numbered scope/verify/draft/check/report steps and copyable return-path checklist. |
| 7 | PASS | SKILL.md:17; expiry/cancellation/restart/down-expiry cases plus validation repair loop. YAML composition passed; runtime remains untested. |
| 8 | PASS | SKILL.md:29,34–447; adaptable schema contract, automation/script/blueprint branches. Examples are fragments. |
| 9 | PASS | SKILL.md:27; host tools identified, HA setup and validation provision linked; no personal-machine paths. |
| 10 | PASS | SKILL.md direct enforcement link and skills/ha-validate/reference/enforcement.md:1–end; optional cross-client event proposals and limitations documented. No active hook or guaranteed enforcement is claimed; explicit workflow checks remain required. Scope judgment/credential-output completeness cannot be guaranteed by regex. |
| 11 | FAIL | reference/evaluations.md:1–23; three approved prompts/criteria exist but both client rows are Pending/Not run. Fix #24 remains blocked: execute equal fresh baseline/with-skill fixtures on actual used models, record client/version/model/artifacts/outcomes. Definitions do not satisfy evidence. |
| 12 | PASS | SKILL.md:12–31; installed-version guard, behavior preservation, scope/checks appear before syntax examples. |
| 13 | PASS | SKILL.md:1–446 and every owned reference inspected; no instruction requests internal reasoning disclosure. Action/evidence explanations are permitted. |
## ha-templates

Body lines: 308.

| Rule | Status | Evidence and result |
| --- | --- | --- |
| 1 | PASS | SKILL.md:1–312; template snapshot and evaluations directly linked at :10/:33. |
| 2 | PASS | reference/template-functions.md:6–10; top contents before usage/index. |
| 3 | PASS | SKILL.md:14–31,36–73; sandbox/type/missing-state context precise; local Jinja filter fixture passes. |
| 4 | FAIL | reference/evaluations.md:1–23; three approved prompts/criteria exist but both client rows are Pending/Not run. Fix #24 remains blocked: execute equal fresh baseline/with-skill fixtures on actual used models, record client/version/model/artifacts/outcomes. Definitions do not satisfy evidence. |
| 5 | FAIL | SKILL.md:3,36–312; HA sandbox/helpers/state behavior. Namespace reduction retained as conditional paired-test candidate, not silently removed. |
| 6 | PASS | SKILL.md:16–25; numbered workflow, checklist and return destinations. |
| 7 | PASS | SKILL.md:19; render edge inputs, validate, repair/re-render, repeated-failure blocker; explicit offline native-type limit. |
| 8 | PASS | SKILL.md:17/:31; state-based versus trigger-based branch and adaptable fragment contract. |
| 9 | PASS | SKILL.md:29; host/browser tools plus supported HA connection/check provisioning; no private-machine paths. |
| 10 | PASS | SKILL.md direct enforcement link and skills/ha-validate/reference/enforcement.md:1–end; optional cross-client event proposals and limitations documented. No active hook or guaranteed enforcement is claimed; explicit workflow checks remain required. Scope judgment/credential-output completeness cannot be guaranteed by regex. |
| 11 | FAIL | reference/evaluations.md:1–23; three approved prompts/criteria exist but both client rows are Pending/Not run. Fix #24 remains blocked: execute equal fresh baseline/with-skill fixtures on actual used models, record client/version/model/artifacts/outcomes. Definitions do not satisfy evidence. |
| 12 | PASS | SKILL.md:10–33; helper/version verification, context/type constraints and scope/checks precede examples. |
| 13 | PASS | SKILL.md:1–311 and every owned reference inspected; no instruction requests internal reasoning disclosure. Action/evidence explanations are permitted. |
## ha-appdaemon

Body lines: 222.

| Rule | Status | Evidence and result |
| --- | --- | --- |
| 1 | PASS | SKILL.md:1–226; evaluation and shared enforcement directly linked at :31. |
| 2 | NOT APPLICABLE | reference/evaluations.md has fewer than 100 lines; no other owned reference exceeds 100. |
| 3 | PASS | SKILL.md:12–29; explicit sync/async lifecycle/API contract and scoped live actions. |
| 4 | FAIL | reference/evaluations.md:1–23; three approved prompts/criteria exist but both client rows are Pending/Not run. Fix #24 remains blocked: execute equal fresh baseline/with-skill fixtures on actual used models, record client/version/model/artifacts/outcomes. Definitions do not satisfy evidence. |
| 5 | PASS | SKILL.md:3,34–226; AppDaemon lifecycle/callback/API reference and activation trigger; no conditional unapproved cuts. |
| 6 | PASS | SKILL.md:14–23; numbered implementation/check/report workflow and return-path checklist. |
| 7 | PASS | SKILL.md:17; pure-logic/lifecycle edge checks, repair/recheck and blocker; mock versus runtime distinction. |
| 8 | PASS | SKILL.md:15/:29; explicit sync scheduling versus async awaited managed-task branch, preserve callback signatures. |
| 9 | PASS | SKILL.md:27; supported AppDaemon provisioning, HA setup, check requirements; relative marketplace links. |
| 10 | PASS | SKILL.md direct enforcement link and skills/ha-validate/reference/enforcement.md:1–end; optional cross-client event proposals and limitations documented. No active hook or guaranteed enforcement is claimed; explicit workflow checks remain required. Scope judgment/credential-output completeness cannot be guaranteed by regex. |
| 11 | FAIL | reference/evaluations.md:1–23; three approved prompts/criteria exist but both client rows are Pending/Not run. Fix #24 remains blocked: execute equal fresh baseline/with-skill fixtures on actual used models, record client/version/model/artifacts/outcomes. Definitions do not satisfy evidence. |
| 12 | PASS | SKILL.md:12–31; nonblocking/await/current-input/reload constraints near top. |
| 13 | PASS | SKILL.md:1–225 and every owned reference inspected; no instruction requests internal reasoning disclosure. Action/evidence explanations are permitted. |
## ha-troubleshooting

Body lines: 156.

| Rule | Status | Evidence and result |
| --- | --- | --- |
| 1 | PASS | SKILL.md body under 500; access/failure/evaluation/shared companions directly linked at :10; extracted details conditional. |
| 2 | PASS | reference/access.md:1–6; reference/failure-patterns.md:1–5; both long references begin with contents. |
| 3 | PASS | SKILL.md:8,14–21 and read-only SQLite example; reference/access.md SSH uses known-host loading + RejectPolicy. SQLite read allowed/write blocked fixture passed; Paramiko execution unavailable. |
| 4 | FAIL | reference/evaluations.md:1–24; three approved prompts/criteria exist but both client rows are Pending/Not run. Fix #24 remains blocked: execute equal fresh baseline/with-skill fixtures on actual used models, record client/version/model/artifacts/outcomes. Definitions do not satisfy evidence. |
| 5 | PASS | SKILL.md:3,30 onward; HA discovery trigger and concrete artifact/log/restore/DB facts; approved generic coaching reductions applied. |
| 6 | PASS | SKILL.md:18–28; numbered evidence/hypothesis/repair workflow and copyable return checklist. |
| 7 | PASS | SKILL.md:19–22; contradicting evidence returns investigation; failed validation returns hypothesis; bounded loop and diagnostics cleanup. |
| 8 | PASS | SKILL.md:16 and examples; adaptable diagnostic paths/backend/targets with strict read-only/trust guards; artifact access branches in reference/access.md. |
| 9 | PASS | SKILL.md:14; host tools, existing HA runtime, optional SSH/Paramiko install, Python stdlib identified. access.md uses portable configured inputs. |
| 10 | PASS | SKILL.md direct enforcement link and skills/ha-validate/reference/enforcement.md:1–end; optional cross-client event proposals and limitations documented. No active hook or guaranteed enforcement is claimed; explicit workflow checks remain required. Scope judgment/credential-output completeness cannot be guaranteed by regex. |
| 11 | FAIL | reference/evaluations.md:1–24; three approved prompts/criteria exist but both client rows are Pending/Not run. Fix #24 remains blocked: execute equal fresh baseline/with-skill fixtures on actual used models, record client/version/model/artifacts/outcomes. Definitions do not satisfy evidence. |
| 12 | PASS | SKILL.md:8–28; live-scope/.storage boundary, context routing and completion checks precede diagnostic background. |
| 13 | PASS | SKILL.md:1–159 and every owned reference inspected; no instruction requests internal reasoning disclosure. Action/evidence explanations are permitted. |
## ha-mcp-setup

Body lines: 57.

| Rule | Status | Evidence and result |
| --- | --- | --- |
| 1 | PASS | SKILL.md:1–60; evaluations and enforcement directly linked at :24. Compact entrypoint. |
| 2 | NOT APPLICABLE | reference/evaluations.md is below 100 lines; no long owned reference. |
| 3 | PASS | SKILL.md:12–17,28–58; private credentials, distinct config branches, target setup limits and TLS trust. |
| 4 | FAIL | reference/evaluations.md:1–24; three approved prompts/criteria exist but both client rows are Pending/Not run. Fix #24 remains blocked: execute equal fresh baseline/with-skill fixtures on actual used models, record client/version/model/artifacts/outcomes. Definitions do not satisfy evidence. |
| 5 | PASS | SKILL.md:3; third-person description plus activation trigger; body is client/HA-specific setup. |
| 6 | PASS | SKILL.md:14–22; numbered setup/live check/repair/report workflow and copyable return checklist. |
| 7 | PASS | SKILL.md:16–17; repair one evidenced cause/repeat live discovery; repeated-failure blocker; registration is separate. |
| 8 | PASS | SKILL.md:30–40; strict TOML shape/configurable values and concrete personal-input/private-output pair; Codex/Claude/auth branches. |
| 9 | PASS | SKILL.md:12; supported client provisioning links, integration/auth/reachability prerequisites, no extra package or private path. |
| 10 | PASS | SKILL.md direct enforcement link and skills/ha-validate/reference/enforcement.md:1–end; optional cross-client event proposals and limitations documented. No active hook or guaranteed enforcement is claimed; explicit workflow checks remain required. Scope judgment/credential-output completeness cannot be guaranteed by regex. |
| 11 | FAIL | reference/evaluations.md:1–24; three approved prompts/criteria exist but both client rows are Pending/Not run. Fix #24 remains blocked: execute equal fresh baseline/with-skill fixtures on actual used models, record client/version/model/artifacts/outcomes. Definitions do not satisfy evidence. |
| 12 | PASS | SKILL.md:8–17; integration capability and credential/scope constraints before configuration examples. |
| 13 | PASS | SKILL.md:1–60 and every owned reference inspected; no instruction requests internal reasoning disclosure. Action/evidence explanations are permitted. |

## Executed checks and limits

- All five entrypoints: frontmatter and under-500 body checks passed; owned references link directly, long-reference contents present.
- Automation/template/AppDaemon YAML examples composed via PyYAML SafeLoader without constructing HA tags. Offline Jinja select fixture rendered [6, 9]. This proves syntax/filter behavior only.
- Troubleshooting Python fragments compile; isolated read-only SQLite fixture allowed SELECT and blocked INSERT. Paramiko absent: unknown-host execution not run. Primary Paramiko documentation verified RejectPolicy; documentation review is not execution.
- Official timer/shell_command/Paramiko/Python sqlite3 primary documentation consulted. Target HA/AppDaemon model/device runtime checks remain unavailable; no live action performed.
- No hooks installed, activated or execution-tested. Approved #12 adds proposals only.

## Remaining approved fix

24. Record actual used models/client versions and execute three paired baseline/with-skill evaluations per skill on both clients when authorization/runtime access is available. Retain uncertain prose reductions until equivalent-or-better evidence exists. Current missing evidence remains FAIL rules 4 and 11; do not mark all skills fully passing.

Conditional unresolved fix #20: ha-templates namespace/scoping general explanation is retained until paired #24 comparisons support the shorter proposed wording. Rule 5 remains FAIL for this approved conditional cut; retaining existing prose preserves guidance while evaluation is blocked.


# Post-change audit: display skills

Scope: esphome-lvgl, esphome-validate and svg-rendering; all owned entrypoints and packaged references read, including direct companion entrypoints and shared enforcement. Independently discoverable sibling skills retain their own resource graphs; their detailed audit is provided by their owners. No private runtime font/image/build inputs are claimed to be packaged. Read-only re-audit; fixes already authorized by the 24-item report.

Executed checks: frontmatter YAML parsing; <500 body lines (105/88/41); every owned long reference starts a contents list; owned relative Markdown links resolve; original LVGL headings preserved, SVG gauge-layer title and acceptance checklist intentionally replaced; git diff --check. Actual Template A at 0/50/100 and two translated Template C copies parsed, mathematical endpoints checked, rendered in Chromium153.0.8010.12 and inspected. ESPHome CLI2026.7.0 is installed but no complete project/board fixture was supplied, so config/compile/device behavior is unverified. No paired client/model baseline executed; definitions are not results.

| Skill | Failed rules | Remaining concern |
| --- | ---: | --- |
| esphome-lvgl | 3 | Model/baseline evidence and conditional general-content cuts |
| esphome-validate | 2 | Model/baseline evidence |
| svg-rendering | 3 | Model/baseline evidence and conditional general-content cuts |

## esphome-lvgl

| Rule | Status | Evidence and result |
| --- | --- | --- |
| 1 | PASS | SKILL.md:31–47; body105; references/*.md all directly linked, contents preserved. Runtime asset paths are explicitly supplied inputs at29. |
| 2 | PASS | All10 extracted reference files:3 have contents lists; evaluations.md is29lines. |
| 3 | PASS | SKILL.md:8,12–16; references/hardware-fonts.md:102,198; fixed-dashboard scrolling93 permits intentional lists; exact action/schema preserved. |
| 4 | FAIL | references/evaluations.md:25–29: models unspecified and no executed pairs. Conditional cuts remain candidates; do not infer model fitness. |
| 5 | FAIL | Description SKILL.md:3 is corrected. references/lambdas.md:135–155 retains general conversion material pending paired evidence required by approved#20/#24. Remove only when tested shorter variant is no worse. |
| 6 | PASS | SKILL.md:10–25 numbered workflow, copyable checklist and return routes at15–16/23–24. |
| 7 | PASS | SKILL.md:15–17 config/compile repair/repeat/stop and runtime diagnosis routes. Corrected rotation references/troubleshooting.md:173 and boot priority references/ha-integration.md; no runtime pass inferred. |
| 8 | PASS | SKILL.md:14 defines adaptable fragments; image contract references/widgets.md:322; literal invalid colors removed from patterns; modern vs legacy rotation branch explicit. |
| 9 | PASS | SKILL.md:27–29 names Python/ESPHome provisioning and optional dashboard, LVGL vendoring, project-supplied fonts/images;44–47 portable sibling links. |
| 10 | PASS | SKILL.md:47 directly links optional enforcement; prose retains generated-artifact and flash/current-source invariants8. Hook events/limitations require shared reference coverage; no installation claimed. |
| 11 | FAIL | references/evaluations.md:5–27 has three exact prompts and results schema, but baseline and with-skill records are Not run. Execute genuine pairs on actual clients/models. |
| 12 | PASS | SKILL.md:8–25 places version, scope, missing states and validation before detailed resource routing. |
| 13 | PASS | All owned entrypoint/reference text scanned and inspected: no instruction to echo internal reasoning; evidence/short reporting only SKILL.md:17. |

## esphome-validate

| Rule | Status | Evidence and result |
| --- | --- | --- |
| 1 | PASS | SKILL.md:91 directly links local evaluations and companion skills/enforcement; body88, no private memory dependency. |
| 2 | NOT APPLICABLE | Only references/evaluations.md exists,29lines; no owned reference exceeds100lines. |
| 3 | PASS | SKILL.md:13–16,50,63 specifies selected build cleaning and confirmed target/action flash authorization; offline stages30/38 exact. |
| 4 | FAIL | references/evaluations.md:25–29 lacks actual models and executed pairs; no model behavior inferred. |
| 5 | PASS | SKILL.md:3 third-person gate/activation description; domain-specific validation, managed-component diagnostics and deploy boundaries remain. |
| 6 | PASS | SKILL.md:13–24 numbered workflow/checklist, failed checks return to diagnosis/repair14–16,20–23. |
| 7 | PASS | SKILL.md:14–16 config/compile/runtime repeat routes with no-progress stop; literal component diagnostic48–52; real checks distinguished17/87. |
| 8 | PASS | SKILL.md:26–45 offline vs dashboard;61–65 authorized device branch;47–52 toolchain vs YAML branch; selected config/target parameters explicit. |
| 9 | PASS | SKILL.md:44–45 install/dashboard options;91 pinned environment, portable HA setup and incident log72 instead of private memory. |
| 10 | PASS | SKILL.md:91 directly links optional enforcement; current-source/authorization and read-only artifacts16/59 retained. Enforcement is proposal/fallback guidance, not installed coverage. |
| 11 | FAIL | references/evaluations.md:5–27 three prompts present, baseline/with-skill records Not run; genuine pairs remain required. |
| 12 | PASS | SKILL.md:11–24 scope and current-source/authorized flash gates appear before commands. |
| 13 | PASS | All owned text inspected/scanned; no reasoning echo; SKILL.md:17 asks results and limitations. |

## svg-rendering

| Rule | Status | Evidence and result |
| --- | --- | --- |
| 1 | PASS | SKILL.md:38–44 directly links all five owned resources and companions; body41; absent architecture dependency removed from references/example-style.md. |
| 2 | PASS | references/svg-geometry.md:3 and references/templates.md:3 contents; other owned references below100lines. |
| 3 | PASS | SKILL.md:10,22–25 exact geometry/XML requirements; ranges/style/layout adaptable; references/pitfalls.md:7 now supports baseline or tested font offset. |
| 4 | FAIL | references/evaluations.md:25–29 actual models unspecified and pairs Not run. Chromium structural render is not a model test. |
| 5 | FAIL | Description SKILL.md:3 corrected; references/svg-geometry.md:87–96/147–153 retains generic path/basic-shape material because approved#20 conditional cuts require paired evidence. |
| 6 | PASS | SKILL.md:12–18 checklist;22–26 numbered workflow; failed parse/render returns24–25. |
| 7 | PASS | SKILL.md:24–26 parse/fix/render/repeat and no-progress stopping rule; actual XML/math/Chromium checks recorded references/evaluations.md:31–33, no model claims. |
| 8 | PASS | SKILL.md:10 two crop/needle routes,22 upper/bidirectional/compass fork,34 concrete input/output; references/templates.md:15 adaptation and unique-ID contract. |
| 9 | PASS | SKILL.md:30 stdlib/browser/CairoSVG install and platform dependency docs; project font/fallback; optional style has no private path dependency. |
| 10 | PASS | SKILL.md:44 links shared optional enforcement; XML parse24 and explicit check evidence26 retained; render/UX judgment remains explicit. |
| 11 | FAIL | references/evaluations.md:5–27 three prompts and results schema present; actual no-skill baseline is absent. Execute genuine pairs; technical render note31–33 does not satisfy this. |
| 12 | PASS | SKILL.md:8–18 geometry/paint-order and acceptance checklist precede resources. |
| 13 | PASS | All owned entrypoint/references inspected/scanned; no reasoning echo, only artifacts/checks/limits26. |

Remaining repairs within approved intent require actual paired client/model evidence (#24) before generic candidate deletions (#20). No new approval is required for the already-approved intent, but unavailable/blocked runtimes and model identities cannot be fabricated. No live/device checks, model pairs or hooks are reported as passing.


# Post-change audit: operation skills

Scope: update-from-docs and ha-development-roles; all owned entrypoints, role reference files, evaluations, helper and test script inspected. Direct companion/resource existence checked; shared domain changes are separately assessed by their owning workers. Both client manifests preserved. No live generation/network/device mutation performed. Source/reference/Codex role bodies synchronized for all ten roles; Codex models remain inherited.

## update-from-docs

| Rule | Verdict | Evidence and remaining limits |
| --- | --- | --- |
| 1 | PASS | SKILL.md:5–135 body131; helper/evaluations/tests direct at55,130,132; split domain resources directly linked44–47,70–71,134–135. All local links resolve. |
| 2 | PASS | Owned only supporting Markdown reference/evaluations.md:1–24 <100 lines. Generated headers sync_references.py:38–91 provide top Contents for long snapshots; existing snapshots checked separately. |
| 3 | PASS | SKILL.md:15–19,55–66 precise checkout/approval/version bounds; sync_references.py validate_root/output_path reject cache/symlink escapes. Isolated tests exercise rejection. |
| 4 | FAIL | reference/evaluations.md:15–20 actual client/model pairs not recorded. Three prompts defined; used models unspecified. No compatibility failure inferred. |
| 5 | PASS | SKILL.md:3 third-person activation; 13–121 domain upkeep/reference workflow. Broad fiction/automatic-semantic claims replaced. |
| 6 | PASS | SKILL.md:23–34 numbered workflow/checklist with return routes;27 bounded non-progressing loop. |
| 7 | PASS | Helper6 isolated tests passed; payload failures have source/ref/reference context, batch fetch before write, rollback tested; SKILL.md:23–27 repair loop. No runtime documentation refresh claimed. |
| 8 | PASS | SKILL.md:103–106 strict evidence fields plus flexible structure and illustrative input/output;57–64 preview/apply/version/CI branches. |
| 9 | PASS | SKILL.md:17 stdlib Python3.9+/network/Git requirements;55 explicit loaded directory, both client invocation routes, unrelated cwd fixture passed. |
| 10 | PASS WITH LIMITS | SKILL.md:129 direct shared enforcement proposal; helper deterministically checks checkout/cache/payload/removal invariants. Human semantic approval cannot be proved by source verification; retained at15,101. No hooks activated. Shared root proposal assessment controls event/matcher detail. |
| 11 | FAIL | reference/evaluations.md:5–7 prompts exist but19–20 baseline/with-skill models absent; helper tests24 are not client baselines. |
| 12 | PASS | SKILL.md:13–34 scope/human approval/requirements/checklist precede registry and commands. |
| 13 | PASS | Entire owned entrypoint/helper/eval/test and direct role texts inspected: asks for evidence/short proposals, no chain-of-thought disclosure. |

## ha-development-roles

| Rule | Verdict | Evidence and remaining limits |
| --- | --- | --- |
| 1 | PASS | SKILL.md:5–37 body33; all10 roles12–21, domain companions27–35 and enforcement/evals36–37 directly linked. No own unlinked instructional resources. |
| 2 | PASS | Six >100-line role references have top Contents at5: test-runner-validator109, ux-designer154, security-auditor177, test-writer113, planner127, design-review110. Remaining references <100. |
| 3 | PASS | planner.md:3 read-only first; test-runner-validator.md:25 evidenced shared-root-cause batches; test-writer.md:23 project coverage rather than invented quotas; esphome-coder ambiguity distinguishes cosmetic/hardware; automation-coder.md:60 tool discovery replaces fixed MCP names. |
| 4 | FAIL | references/evaluations.md:15–20 actual used-model pairs pending. Persona/scaffolding candidates remain for testing, not automatically erased. |
| 5 | FAIL, CONDITIONAL REMOVAL RETAINED | Role personas remain e.g.appdaemon-coder.md:7; generic role scaffolding intentionally retained per approved#20 until paired#24 shows no regression. DescriptionSKILL.md:3 remains third person/activation. Candidate removal is not permitted absent its approved condition. |
| 6 | PASS | Every role ends numbered completion loop/checklist, e.g.appdaemon-coder.md:56–68, planner.md:115–127; failed checks return step2 and readonly reviewers propose instead of editing. |
| 7 | PASS WITH LIMITS | appdaemon-coder.md:3–5/esphome-coder.md:3–5 explicitly require relevant recorded checks, skip unresolved, active-hook discovery; completion loops recheck. Executed source/reference/native matching validates packaging copies, not HA runtime functionality. |
| 8 | PASS | security-auditor.md:160–163/design-review.md:93–96/test-writer.md:96–99 flexible report sections plus illustrative pairs. Current-target branch and read-only role scope explicit. |
| 9 | PASS | SKILL.md:25 names selected-role provisioning, project pins/HA runtime;27–35 direct domain setup/render links. No private credentials or personal paths added. |
| 10 | PASS WITH LIMITS | SKILL.md:36 links shared proposals; role boundary/no phantom hook/secret policies retained. Proposed hooks are not enabled and semantic review remains explicit. Shared root proposal supplies event contracts/coverage limitations. |
| 11 | FAIL | references/evaluations.md:5–7 three prompts;19–20 no recorded baselines/with-skill client models. |
| 12 | PASS | SKILL.md:8 role/read-only/executed-check boundary; planner.md:3 and coding role validation gates3–5 now top-first. |
| 13 | PASS | All10 references/evals/entrypoint inspected; short explanations/evidence requested, no reasoning echo. |

## Executed verification

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s skills/update-from-docs/tests -v`: six isolated stdlib tests passed.
- Python syntax check passed for helper/test; generated bytecode removed afterward.
- All ten agent source Markdown bodies equal role-reference bodies; Codex TOML instructions contain those bodies; TOML parsed and no model fields.
- All owned Markdown resource links resolve; body/TOC lengths measured.

Remaining: exact used-model set and both client's baseline/with-skill run records are missing. Conditional persona reductions stay intact. No paid model API or live actions executed under tests.


## File-by-file change inventory

- `.codex/agents/ha_appdaemon_coder.toml` — Regenerated portable role instructions; inherits selected Codex model.
- `.codex/agents/ha_architect.toml` — Regenerated portable role instructions; inherits selected Codex model.
- `.codex/agents/ha_automation_coder.toml` — Regenerated portable role instructions; inherits selected Codex model.
- `.codex/agents/ha_design_review.toml` — Regenerated portable role instructions; inherits selected Codex model.
- `.codex/agents/ha_esphome_coder.toml` — Regenerated portable role instructions; inherits selected Codex model.
- `.codex/agents/ha_planner.toml` — Regenerated portable role instructions; inherits selected Codex model.
- `.codex/agents/ha_security_auditor.toml` — Regenerated portable role instructions; inherits selected Codex model.
- `.codex/agents/ha_test_runner_validator.toml` — Regenerated portable role instructions; inherits selected Codex model.
- `.codex/agents/ha_test_writer.toml` — Regenerated portable role instructions; inherits selected Codex model.
- `.codex/agents/ha_ux_designer.toml` — Regenerated portable role instructions; inherits selected Codex model.
- `agents/appdaemon-coder.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `agents/architect.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `agents/automation-coder.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `agents/design-review.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `agents/esphome-coder.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `agents/planner.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `agents/security-auditor.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `agents/test-runner-validator.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `agents/test-writer.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `agents/ux-designer.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `skills/esphome-lvgl/SKILL.md` — Approved workflow, scope, prerequisites, direct resource routing and relevant correctness fixes.
- `skills/esphome-lvgl/references/actions-navigation.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/esphome-lvgl/references/design-layout.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/esphome-lvgl/references/evaluations.md` — Three approved prompts, criteria/results schema and honest blocked execution evidence.
- `skills/esphome-lvgl/references/framework.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/esphome-lvgl/references/ha-integration.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/esphome-lvgl/references/hardware-fonts.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/esphome-lvgl/references/lambdas.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/esphome-lvgl/references/lvgl-core.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/esphome-lvgl/references/patterns.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/esphome-lvgl/references/troubleshooting.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/esphome-lvgl/references/widgets.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/esphome-validate/SKILL.md` — Approved workflow, scope, prerequisites, direct resource routing and relevant correctness fixes.
- `skills/esphome-validate/references/evaluations.md` — Three approved prompts, criteria/results schema and honest blocked execution evidence.
- `skills/ha-appdaemon/SKILL.md` — Approved workflow, scope, prerequisites, direct resource routing and relevant correctness fixes.
- `skills/ha-appdaemon/reference/evaluations.md` — Three approved prompts, criteria/results schema and honest blocked execution evidence.
- `skills/ha-automations/SKILL.md` — Approved workflow, scope, prerequisites, direct resource routing and relevant correctness fixes.
- `skills/ha-automations/reference/evaluations.md` — Three approved prompts, criteria/results schema and honest blocked execution evidence.
- `skills/ha-automations/reference/purpose-specific-keys.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/ha-automations/reference/purpose-specific.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/ha-development-roles/SKILL.md` — Approved workflow, scope, prerequisites, direct resource routing and relevant correctness fixes.
- `skills/ha-development-roles/references/appdaemon-coder.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `skills/ha-development-roles/references/architect.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `skills/ha-development-roles/references/automation-coder.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `skills/ha-development-roles/references/design-review.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `skills/ha-development-roles/references/esphome-coder.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `skills/ha-development-roles/references/evaluations.md` — Three approved prompts, criteria/results schema and honest blocked execution evidence.
- `skills/ha-development-roles/references/planner.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `skills/ha-development-roles/references/security-auditor.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `skills/ha-development-roles/references/test-runner-validator.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `skills/ha-development-roles/references/test-writer.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `skills/ha-development-roles/references/ux-designer.md` — Portable role constraints, proportional review guidance and synchronized copy.
- `skills/ha-mcp-setup/SKILL.md` — Approved workflow, scope, prerequisites, direct resource routing and relevant correctness fixes.
- `skills/ha-mcp-setup/reference/evaluations.md` — Three approved prompts, criteria/results schema and honest blocked execution evidence.
- `skills/ha-templates/SKILL.md` — Approved workflow, scope, prerequisites, direct resource routing and relevant correctness fixes.
- `skills/ha-templates/reference/evaluations.md` — Three approved prompts, criteria/results schema and honest blocked execution evidence.
- `skills/ha-templates/reference/template-functions.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/ha-troubleshooting/SKILL.md` — Approved workflow, scope, prerequisites, direct resource routing and relevant correctness fixes.
- `skills/ha-troubleshooting/reference/access.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/ha-troubleshooting/reference/evaluations.md` — Three approved prompts, criteria/results schema and honest blocked execution evidence.
- `skills/ha-troubleshooting/reference/failure-patterns.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/ha-validate/SKILL.md` — Approved workflow, scope, prerequisites, direct resource routing and relevant correctness fixes.
- `skills/ha-validate/reference/enforcement.md` — Both-host optional event/adapter/fixture proposals; no activation.
- `skills/ha-validate/reference/evaluations.md` — Three approved prompts, criteria/results schema and honest blocked execution evidence.
- `skills/svg-rendering/SKILL.md` — Approved workflow, scope, prerequisites, direct resource routing and relevant correctness fixes.
- `skills/svg-rendering/references/evaluations.md` — Three approved prompts, criteria/results schema and honest blocked execution evidence.
- `skills/svg-rendering/references/example-style.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/svg-rendering/references/pitfalls.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/svg-rendering/references/svg-geometry.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/svg-rendering/references/templates.md` — Directly discoverable domain reference with contents and relevant approved corrections.
- `skills/update-from-docs/SKILL.md` — Approved workflow, scope, prerequisites, direct resource routing and relevant correctness fixes.
- `skills/update-from-docs/reference/evaluations.md` — Three approved prompts, criteria/results schema and honest blocked execution evidence.
- `skills/update-from-docs/sync_references.py` — Explicit source root, staged deterministic refresh, validation and rollback.
- `skills/update-from-docs/tests/test_sync_references.py` — Explicit source root, staged deterministic refresh, validation and rollback.
- `tasks/lessons.md` — Approved work plan and project lessons.
- `tasks/todo.md` — Approved work plan and project lessons.
