---
name: ha-mcp-setup
description: Connect Codex or Claude Code to Home Assistant through its MCP server, configure authentication, and diagnose MCP connectivity.
---

# Home Assistant MCP setup

Home Assistant exposes Streamable HTTP at `/api/mcp`. Configure **Model Context Protocol Server** under Settings → Devices & services → Add integration (not the MCP client integration). Its selected LLM API and exposed entities determine the available tools; discover tools rather than assuming history, unrestricted entity search, or configuration editing exists.

## Codex

Use `~/.codex/config.toml` for a personal connection. A trusted project's `.codex/config.toml` can scope a connection to that project, but never commit tokens.

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
