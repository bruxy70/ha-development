# Diagnostic access

## Contents
- [Context detection](#step-0-detect-your-execution-context-do-this-first)
- [Artifact hierarchy](#access-hierarchy--route-by-what-you-are-fetching)
- [Access methods](#access-methods-reference-detail)

## Step 0: Detect your execution context (do this FIRST)

Before fetching any log, state, or file, determine **where this session runs** and **what access it has**. The best tool for each task depends entirely on this — it is the difference between reading AppDaemon logs in one second off a mounted volume and needlessly asking the user to paste them, or blindly running `ha …` as if on the HA shell while actually on a dev machine. Probe **once**, at the start; the answer holds for the whole session. State your conclusion out loud, then route every later access through the hierarchy below.

Run these cheap checks (skip any you already know from context):

| Question | Probe |
|---|---|
| On the HA host / an SSH terminal into it? | `command -v ha` succeeds **and** `/config` is a real local dir (not a network mount) |
| Inside a container (Core / add-on)? | `/.dockerenv` exists, or `/proc/1/cgroup` mentions `docker` |
| HA volume mounted on a dev machine? | try the OS default(s) first, don't just ask: **macOS** → `ls /Volumes/config` (the standard Samba/AFP mount point when the share is named "config"); **Windows** → a configured share such as `//HA/config` or a mapped drive (use the native shell's accepted spelling); **Linux** → check common bind-mount points (`/mnt/config`, `~/ha-config`) or `findmnt \| grep config`. Only ask the user for their mount path if none of these exist. AppDaemon logs then live at `<mount>/appdaemon/logs/*.log` |
| API reachable via MCP? | the `mcp__home-assistant` tool is present in this session |
| API reachable via REST? | `curl -s -o /dev/null -w '%{http_code}' -H "Authorization: Bearer $TOKEN" http://<HA_IP>:8123/api/` returns `200` |
| SSH available? | Advanced SSH & Web Terminal add-on installed, then a `paramiko` connect succeeds (Method 3). **Usually absent — never assume it; probe or ask.** |

Find credentials in the current client configuration: Codex uses `~/.codex/config.toml` → `mcp_servers.home-assistant` (configured bearer environment variable or `http_headers.Authorization`); Claude Code uses `~/.claude.json` → `mcpServers.home-assistant.headers.Authorization`. Read only the needed field in-process; never print credentials.

If a probe is ambiguous, **ask the user** ("Is SSH into HA available?" / "Is /config mounted here?") rather than guessing — a wrong guess is exactly the random behaviour this step exists to prevent.

## Access hierarchy — route by WHAT you are fetching

Once context is known, pick the **highest available tier** for each task. The ordering differs per artifact — a single global "prefer MCP" or "prefer the mount" rule is wrong (e.g. AppDaemon logs favour the mount; the Core log is not on the mount at all).

### AppDaemon logs — and any file under `/config` (packages, `secrets.yaml`, `www/`, `.storage`)
1. **Mounted volume / on-host** → read the file directly: `<mount>/appdaemon/logs/appdaemon.log` (+ rotated `.log.1`, `.log.2` for history). Fastest, complete. **Whenever a volume is mounted, do this — do NOT hit the API or ask the user.**
2. **SSH** → `tail`/`cat` the file on the host.
3. **REST API** → `/api/hassio/addons/a0d7b954_appdaemon/logs` (current session only, no rotation).
4. **Ask** the user to paste the relevant lines.

### HA Core log
For journal-backed HA OS releases, Core logs may not be written to `/config`. Verify installation type/version and route through Supervisor or host logs; a missing mounted log is not evidence that logging stopped.
1. **REST API** → `curl .../api/hassio/core/logs?lines=100` (needs Core running).
2. **SSH** → `ha core logs` (works even when Core is down/hung).
3. **Ask** the user to paste.

### Live entity state / attributes / history / service calls
1. **MCP** (`mcp__home-assistant`) → states, services, history.
2. **REST API** → `/api/states`, `/api/states/<id>`, `/api/template`, `/api/history/period/…`.
3. **On-host / SSH** → `ha` CLI + Developer Tools.
4. **Ask** for a Developer Tools → States value/screenshot.

### `.storage` files & recorder DB (`core.restore_state`, `home-assistant_v2.db`)
The API cannot read these — they need real file access.
1. **Mounted volume / on-host / SSH** → read `<config>/.storage/…` and open the SQLite DB directly (see Step 3).
2. **Ask** — no file access means requesting the specific file or a targeted query result.

### `ha` CLI / OS-level ops (config check, restart, host stats)
1. **On-host** → run `ha …` directly.
2. **SSH** → run `ha …` remotely (Method 3).
3. **REST API** → limited equivalents only, e.g. `/api/config/core/check_config`.
4. Otherwise unavailable — say so rather than pretending to run it.

## Access methods (reference detail)

The three underlying access methods referenced by the hierarchy above. Use the current client credential source described above. Do not depend on Claude configuration when working in Codex.

### Method 1: MCP Server

Discover the connected Home Assistant MCP tools and use supported operations for entity states or services. History and listing capabilities depend on the selected HA API; use REST where MCP does not expose them. This is the simplest method — no extra setup needed if the MCP server is already configured.

### Method 2: REST API

Use `curl` via the Bash tool with the long-lived access token. Useful for endpoints not exposed through MCP (logs, config validation, template rendering).

**Key diagnostic endpoints:**

| Endpoint | Method | Use |
|---|---|---|
| `/api/config` | GET | HA version, loaded components, location, unit system |
| `/api/states` | GET | All entity states — find unavailable/unknown entities |
| `/api/states/<entity_id>` | GET | Single entity state + attributes |
| `/api/error_log` | GET | Error log as plaintext (current session) |
| `/api/hassio/core/logs` | GET | Core logs via Supervisor API (HA OS 2025.11+) |
| `/api/hassio/supervisor/logs` | GET | Supervisor logs |
| `/api/hassio/addons/{slug}/logs` | GET | Add-on logs (e.g., `a0d7b954_appdaemon`) |
| `/api/config/core/check_config` | POST | Validate configuration remotely |
| `/api/template` | POST | Render a Jinja2 template (test templates) |
| `/api/history/period/<timestamp>` | GET | Historical states for entities |
| `/api/logbook/<timestamp>` | GET | Logbook entries |

```bash
# Example: fetch last 100 lines of HA core log
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://<HA_IP>:8123/api/hassio/core/logs?lines=100" \
  | sed 's/\x1b\[[0-9;]*m//g'
```

Use a network-capable tool available in the current host; for local LAN REST, curl is a fallback when browser fetching cannot reach it.

### Method 3: SSH + HA CLI via paramiko (deep access)

For OS-level diagnostics, connect to HA via SSH and use the `ha` CLI. **SSH is not available by default** — it requires the **Advanced SSH & Web Terminal** add-on (application) to be installed in Home Assistant. This is a fallback method; prefer MCP or the REST API when HA Core is responsive.

Use an existing trusted native SSH connection when available; paramiko is an optional Python alternative requiring verified host keys ([Paramiko client documentation](https://docs.paramiko.org/en/stable/api/client.html)).

**Prerequisites:**
- **Advanced SSH & Web Terminal** add-on installed and running in HA
- SSH username and password configured in the add-on settings
- Note the SSH port (default: `22`, often changed to `22222` to avoid conflicts)
- `paramiko` installed: `python -m pip install paramiko`

**Connecting and running commands:**

```python
import paramiko

client = paramiko.SSHClient()
client.load_system_host_keys()
client.set_missing_host_key_policy(paramiko.RejectPolicy())
# Provision an unknown key only after verifying its fingerprint through a trusted channel.
client.connect('<HA_IP>', port=22222, username='<USERNAME>', password='<PASSWORD>')

stdin, stdout, stderr = client.exec_command('ha core logs')
print(stdout.read().decode())
client.close()
```

**Useful HA CLI commands via SSH:**

| Command | Use |
|---|---|
| `ha core info` | Core version, state, startup time |
| `ha core logs` | Full Core log output |
| `ha core check` | Validate configuration |
| `ha core stats` | CPU, memory, network usage |
| `ha core restart` | Restart HA Core |
| `ha supervisor info` | Supervisor version and state |
| `ha supervisor logs` | Supervisor logs |
| `ha host info` | Host OS info, disk usage |
| `ha addons info <slug>` | Add-on state and config |
| `ha addons logs <slug>` | Add-on logs |

**When to use SSH over API:**
- **When HA Core is down.** SSH connects to the OS/Supervisor level, not to HA Core. MCP and the REST API both run inside HA Core — if Core is crashed, hung, or stopped, they are unavailable. SSH remains operational because the add-on runs under the Supervisor independently of Core.
- To restart or stop HA Core (`ha core restart`, `ha core stop`, `ha core start`)
- To reboot or shut down the host (`ha host reboot`, `ha host shutdown`)
- For `ha core check` (config validation with richer output than the API)
- For `ha core stats` / `ha host info` (system resource diagnostics)

