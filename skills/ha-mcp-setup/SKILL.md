---
name: ha-mcp-setup
description: Home Assistant MCP server setup for Claude Code. Use when the user wants to connect Claude Code to their Home Assistant instance, configure the HA MCP server, create a long-lived access token, or troubleshoot MCP connectivity issues with Home Assistant.
---

# Home Assistant MCP Server Setup

This skill covers connecting Claude Code to a Home Assistant instance via the built-in MCP (Model Context Protocol) server. Once connected, Claude can query entities, call services, and interact with your HA instance directly.

## Prerequisites

- Home Assistant 2025.5.0 or later (MCP support is built-in)
- Network access from your machine to the HA instance
- A long-lived access token

## Step 1: Enable the MCP Integration in Home Assistant

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **"Model Context Protocol"** (or **"MCP"**)
3. Click to add it
4. The integration creates the `/api/mcp` endpoint on your HA instance

If the integration doesn't appear, verify your HA version is 2025.5.0+.

## Step 2: Create a Long-Lived Access Token

1. In Home Assistant, click your **user profile** (bottom-left avatar icon)
2. Scroll down to **"Long-Lived Access Tokens"**
3. Click **"Create Token"**
4. Give it a descriptive name (e.g., `claude-code`)
5. **Copy the token immediately** — it is shown only once and cannot be retrieved later
6. Store it securely (password manager, etc.)

**Token properties:**
- Does not expire (unless manually revoked)
- Has the same permissions as the user who created it
- Can be revoked anytime from the same profile page
- Each token should be used for a single purpose (create separate tokens for different tools)

**Security note:** Treat this token like a password. Anyone with the token has full API access to your HA instance with your user's permissions.

## Step 3: Configure Claude Code

Add the MCP server to your Claude Code configuration. Choose one of these locations:

### Option A: User-level config (`~/.claude.json`) — recommended

This makes the HA connection available in all projects.

Add to the `"mcpServers"` section:

```json
{
  "mcpServers": {
    "home-assistant": {
      "type": "http",
      "url": "http://<YOUR_HA_IP>:8123/api/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_LONG_LIVED_TOKEN>"
      }
    }
  }
}
```

### Option B: Project-level config (`.claude/settings.local.json`)

This limits the HA connection to a specific project.

```json
{
  "mcpServers": {
    "home-assistant": {
      "type": "http",
      "url": "http://<YOUR_HA_IP>:8123/api/mcp",
      "headers": {
        "Authorization": "Bearer <YOUR_LONG_LIVED_TOKEN>"
      }
    }
  }
}
```

**Important:** Never commit `settings.local.json` with tokens to version control. Add it to `.gitignore`.

### Replace placeholders:
- `<YOUR_HA_IP>` — your HA instance IP or hostname (e.g., `192.168.1.100`, `homeassistant.local`)
- `<YOUR_LONG_LIVED_TOKEN>` — the token from Step 2

### HTTPS / Remote Access

If accessing HA over HTTPS (e.g., via Nabu Casa or your own domain):

```json
{
  "home-assistant": {
    "type": "http",
    "url": "https://your-ha-domain.duckdns.org/api/mcp",
    "headers": {
      "Authorization": "Bearer <YOUR_LONG_LIVED_TOKEN>"
    }
  }
}
```

## Step 4: Verify the Connection

1. Restart Claude Code (or start a new session)
2. Ask Claude: "List my Home Assistant entities" or "What is the state of my living room light?"
3. Claude should be able to query your HA instance and return results

## Troubleshooting

### "Connection refused" or timeout
- Verify HA is running and accessible: `curl http://<YOUR_HA_IP>:8123/api/`
- Check firewall rules allow connections on port 8123
- If using Docker, ensure the port is exposed

### "401 Unauthorized"
- Token may be expired or revoked — create a new one
- Verify the token is copied correctly (no trailing spaces)
- Check the `Authorization` header format: must be `Bearer <token>` (with a space after Bearer)

### "404 Not Found" on `/api/mcp`
- The MCP integration may not be enabled — check Settings → Devices & Services
- Your HA version may be too old — MCP requires 2025.5.0+

### MCP server not appearing in Claude Code
- Check JSON syntax in your config file (trailing commas, missing quotes)
- Restart Claude Code after config changes
- Verify the config is in the right file (`~/.claude.json` or `.claude/settings.local.json`)

### "SSL certificate verify failed"
- For self-signed certificates, you may need to add your CA to the system trust store
- As a workaround for local networks, use `http://` instead of `https://`

## Available MCP Capabilities

Once connected, the HA MCP server exposes tools for:
- **Querying entity states** — get current state and attributes of any entity
- **Calling services** — turn on/off lights, set climate, trigger automations, etc.
- **Listing entities** — discover available entities, areas, devices
- **Getting history** — query state history for entities

The exact capabilities depend on your HA version and the MCP integration version.
