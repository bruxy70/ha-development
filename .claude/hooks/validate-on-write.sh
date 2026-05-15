#!/usr/bin/env bash
# PostToolUse validation hook for Write/Edit.
# Reads tool-use JSON from stdin, validates relevant file types using
# authoritative external tools, and emits results back to the model.
#
# Gracefully no-ops when tools aren't installed or the file is unrelated.

set -u

input=$(cat)
FILE=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

# Bail silently if path is missing or file doesn't exist
[ -z "$FILE" ] && exit 0
[ ! -f "$FILE" ] && exit 0

case "$FILE" in
  *.yaml|*.yml)
    # Only validate as ESPHome if the file has a top-level `esphome:` block
    if head -50 "$FILE" 2>/dev/null | grep -qE '^esphome:[[:space:]]*$'; then
      if command -v esphome >/dev/null 2>&1; then
        if result=$(esphome config "$FILE" 2>&1); then
          echo "[esphome config: OK for $FILE]"
        else
          echo "[esphome config: FAILED for $FILE]"
          printf '%s\n' "$result" | tail -25
        fi
      else
        echo "[esphome CLI not installed — skipping validation of $FILE. Install with: pip install esphome]"
      fi
    fi
    ;;
  *.py)
    # Python syntax check — cheap, zero deps, silent on success
    if ! err=$(python3 -m py_compile "$FILE" 2>&1); then
      echo "[python -m py_compile: FAILED for $FILE]"
      printf '%s\n' "$err"
    fi
    ;;
esac

exit 0
