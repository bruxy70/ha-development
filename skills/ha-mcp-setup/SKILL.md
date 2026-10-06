---
name: ha-mcp-setup
description: Connects Codex or Claude Code to Home Assistant's MCP server, configures authentication, and diagnoses connectivity. Use when setting up or repairing a Home Assistant MCP connection in either client.
---

# Home Assistant MCP setup

Home Assistant exposes Streamable HTTP at `/api/mcp`. Configure **Model Context Protocol Server** under Settings → Devices & services → Add integration (not the MCP client integration). Its selected LLM API and exposed entities determine the available tools; discover tools rather than assuming history, unrestricted entity search, or configuration editing exists.

## Requirements and workflow

Use an installed supported client: follow [Codex installation](https://developers.openai.com/codex/quickstart/) or [Claude Code installation](https://code.claude.com/docs/en/setup), selecting its current platform-supported install method. Existing HA needs the Model Context Protocol Server integration, reachable URL and supported bearer/OAuth access. Host text/configuration tools and network access are sufficient; no Python package is required. Preserve credentials in private configuration and never print them or commit them. Resolve skill resources relative to their loaded path in either marketplace client.

1. Confirm client/version, personal versus project scope, endpoint and authentication method.
2. Preserve unrelated configuration and configure the matching client format below. If credentials or method are unknown, return to step 1 before writing.
3. Start a new session and separate registration from live initialize/tool discovery. Check advertised read-only lookup if available; do not assume tool names. If connection fails, use the matching symptom below, repair one evidenced cause and repeat step 3.
4. Stop repeated unchanged failure, report the blocker and distinguish configured, registered and live-verified states. Device-changing services remain outside setup authorization.

- [ ] Confirm client, scope, endpoint and authentication.
- [ ] Preserve private credentials and unrelated configuration; return to scope if unknown.
- [ ] Check registration and live discovery separately; repair/recheck on failure.
- [ ] Report available tools, checks and outstanding verification.

[Cross-client enforcement proposals](../ha-validate/reference/enforcement.md) describe optional hook events and explicit fallback checks; no hook activates here. [Three evaluation prompts/results](reference/evaluations.md) record client/model testing.

## Codex

Use `~/.codex/config.toml` for a personal connection. A trusted project's `.codex/config.toml` can scope a connection to that project, but never commit tokens.

TOML table/key shape is strict for the supported Codex version; server name, HA URL, token environment-variable name and timeout are configurable. Select supported OAuth or bearer authentication instead of mixing configuration formats. Preserve unrelated configuration.

Input: personal Codex connection, token already available as `HA_TOKEN`.
Output: private user-config table below; report registration versus live verification separately.

```toml
[mcp_servers.home-assistant]
url = "http://homeassistant.local:8123/api/mcp"
bearer_token_env_var = "HA_TOKEN"
startup_timeout_sec = 30
```

`HA_TOKEN` must exist in the environment of the Codex process, including when launched from a desktop app. A shell export alone does not configure an already-running desktop app. Alternatively, use Codex's supported `http_headers` configuration with an Authorization bearer header in the private user configuration (mode 0600), or configure OAuth using the current official documentation. Never print a real token into chat, terminal output, logs, or repository files.

Create a token under the HA user profile's Security → Long-lived access tokens when needed. Store it securely and use a descriptive name. Tokens can expire or be revoked; do not assume indefinite validity.

## Claude Code

Keep the existing `~/.claude.json` connection when maintaining both clients. Its `mcpServers.home-assistant` entry uses `type: "http"`, `url`, and `headers.Authorization`. Project MCP configuration belongs in `.mcp.json`; store secrets outside tracked files. Codex uses TOML rather than this JSON format.

## Verify

Start a new client session, initialize the server, and list its tools. Then perform a read-only state lookup if available. Setup verification does not authorize service calls that change devices. `codex mcp list` confirms registration, not a successful live connection.

- Timeout/refused: check LAN/VPN reachability, hostname resolution and port.
- 401/403: check token or OAuth access without printing credentials.
- 404: check that the Server integration and the selected `/api/mcp` endpoint exist.
- Missing tools/entities: inspect the selected HA LLM API and exposed entities.
- TLS errors: configure a trusted certificate; do not disable TLS verification.

References: [Home Assistant MCP Server](https://www.home-assistant.io/integrations/mcp_server/) and [Codex MCP configuration](https://developers.openai.com/codex/mcp).
