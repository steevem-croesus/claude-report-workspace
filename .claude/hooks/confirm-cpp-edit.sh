#!/usr/bin/env bash
# PreToolUse hook (Edit|Write|NotebookEdit): the C++ repos are read-only sources of truth for the
# porting workflow. Ask the user before any write under CroesusServer or ReportServer.
# Prints nothing (normal permission flow) for every other path, and if jq is unavailable.
command -v jq >/dev/null 2>&1 || exit 0

path="$(jq -r '.tool_input.file_path // .tool_input.notebook_path // empty' 2>/dev/null | tr '\\' '/' | tr '[:upper:]' '[:lower:]')"
[ -n "$path" ] || exit 0

if printf '%s' "$path" | grep -qE '(^|/)(pm/products|repos)/(croesusserver|reportserver)/'; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"CroesusServer / ReportServer are read-only C++ sources of truth in this workspace. Confirm that this C++ edit is intended."}}
JSON
fi
exit 0
