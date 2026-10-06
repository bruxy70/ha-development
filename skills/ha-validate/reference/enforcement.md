# Optional enforcement proposals

Tool hooks are optional guardrails. Discover which client hooks are enabled and trusted. When no active hook proves the same check, run the check explicitly. Never interpret a missing/skipped hook as successful validation.

These are proposals for host-specific adapters, not installed hooks. No script, settings change or hook activation accompanies this reference. Adopt an adapter only after approving exact configuration and code, and test allowed and blocked fixtures in isolation.

## Event mapping
| Must-hold constraint | Proposed event | Check and limitation |
| --- | --- | --- |
| Authorized target/action before live writes, reloads, restarts or flashing | PreToolUse | Compare structured target/action to session authorization; reject unknown targets. Shell parsing alone cannot classify every command reliably. |
| Keep credentials and private workspace data out of public packages | PreToolUse; PostToolUse | Inspect destination/payload before writes and diff afterwards. After-checks cannot undo transmission. |
| Validate skill frontmatter and resource paths | PostToolUse | Run repository validation on changed files; name the file and failure. |
| Keep role source/reference/native copies aligned | PostToolUse | Compare generated copies against changed sources. |
| Do not edit runtime caches, generated artifacts or HA `.storage` as source | PreToolUse | Resolve destination symlinks, distinguish approved source checkout from runtime copies, and block unsupported direct writes. Permit explicitly authorized maintenance operations only. |
| AppDaemon callbacks must not block; HA changes must pass structural checks | PostToolUse | Flag blocking calls through targeted AST checks and run HA-tag-aware YAML checks; AST checks are candidates, not proof of all asynchronous behavior. |
| SVG output must be well-formed | PostToolUse | Parse changed SVG as XML and report the file/parse error; rendering and visual correctness remain separate checks. |
| Compilation/validation evidence must match final source | Stop | Compare stored source hashes and target/config identity with the final files before claiming success. Stale or absent evidence means NOT RUN. |
| Planner role stays read-only | PreToolUse | Deny writes/deployment while the selected role is planner; an implementation request changes the role explicitly rather than guessing authorization. |
| Documentation semantics require human approval | PreToolUse | Restrict changed prose ranges to recorded approvals; removal approval and explicit checkout identity are separate inputs. Source accuracy still needs human review. |
| Do not claim skipped checks as passing | Stop | Compare declared results to execution evidence; omitted tool paths and judgment remain outside complete enforcement. |

## Claude Code adapter
Use supported PreToolUse, PostToolUse and Stop events. Skill-frontmatter hooks are scoped to skill activation; plugin/project hooks have their host scope. Match Write/Edit/Bash and actual advertised MCP tools; use `${CLAUDE_PLUGIN_ROOT}` for bundled scripts. Honor host trust and permissions.

## Codex adapter
Use current supported events, aliases and tool matching. Claude skill-frontmatter hooks do not automatically run in Codex. Codex plugin registration/default discovery can use `hooks/hooks.json` and `${PLUGIN_ROOT}`. Validate its input/output schema separately; do not copy Claude's protocol blindly. Keep explicit workflow checks where equivalent coverage is unavailable.

Each proposed script accepts the host's tool JSON, derives affected canonical files and emits file:line/problem errors (XML includes column). Store authorization, source hashes and target identities as explicit structured inputs; do not infer approval with a prose regex. HA schema checks must not reject newer keys solely because a documentation snapshot is old. Unknown shell/connector routes are coverage gaps.

## Adapter acceptance checklist
- [ ] Record client/version and precise event/tool coverage.
- [ ] Allowed read-only fixture proceeds without a false block.
- [ ] Disallowed live-write fixture is blocked before execution.
- [ ] Source YAML write is allowed; generated main.cpp write is blocked.
- [ ] Read-only state access is allowed; unapproved service mutation is blocked.
- [ ] Malformed skill fixture names its file and validation error.
- [ ] Source-checkout write is allowed; the same write through a cache alias is blocked.
- [ ] Malformed SVG fails XML parsing; a valid fixture passes.
- [ ] Blocking-callback candidate is flagged; a nonblocking callback avoids a false flag.
- [ ] Matching source-hash evidence is accepted; changed-source or absent evidence prevents a validation claim.
- [ ] Current compile evidence allows an authorized flash; stale/absent evidence blocks it.
- [ ] Passed required checks support completion; unavailable checks are reported as unavailable.
- [ ] Paths work in an installed plugin outside the source checkout.
- [ ] Fixtures contain no credentials, private data or live targets.

If a fixture fails, repair and return to that fixture before adoption. Keep behavior preservation, hardware pins/power, alarm meaning, contrast/tappability and hypothesis relevance as explicit review tests. Complete credential-output prevention cannot be guaranteed by static screening. Separate script/config approval is required before implementing any adapter.

Sources: [Claude hooks](https://code.claude.com/docs/en/hooks), [Claude skills](https://code.claude.com/docs/en/skills), [Codex hooks](https://developers.openai.com/codex/hooks), [Codex plugins](https://developers.openai.com/plugins/build/plugins).
