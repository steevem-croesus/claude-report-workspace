#!/usr/bin/env bash
# Lists ValueProviderFunction keys referenced in ReportFoundations that are registered in neither
# the Pre nor the Post executer of ReportManagerApi. An unregistered key builds and passes unit
# tests, then is silently ignored at generation (AbstractValueProviderFunctionsExecuter.Execute returns
# the parameter untouched), so the value the C++ computed is never produced.
# Commented-out references are skipped. A parameterised key such as Name(arg) is looked up as written.
#
# Usage:
#   check-vpf-registration.sh                 # every key referenced in ReportFoundations
#   check-vpf-registration.sh --changed       # only keys in files changed vs HEAD (staged, unstaged, untracked)
#   check-vpf-registration.sh <path>...       # only keys under these paths (relative to the monolith root)
#   check-vpf-registration.sh --where <Key>   # show where a key is registered (Pre / Post) and referenced
#
# Exit code: 0 = nothing missing, 1 = at least one missing key, 2 = usage or environment error.
set -euo pipefail

ROOT="${MONOLITH_ROOT:-/c/Repos/monolith}"
EXEC_DIR="CFF/Products/ReportManagerApi/ReportManagerAPI.Infrastructure/Repositories/ValueProviderFunctions"
PRE="$EXEC_DIR/PreParamEntryValueProviderFunctionsExecuter.cs"
POST="$EXEC_DIR/PostParamEntryValueProviderFunctionsExecuter.cs"
FOUNDATIONS="CFF/ReportFoundations"
REF_RE='([Vv]alueProviderFunction *[=:] *"[^"]+")'

cd "$ROOT" 2>/dev/null || { echo "monolith root not found: $ROOT (set MONOLITH_ROOT)" >&2; exit 2; }
for f in "$PRE" "$POST"; do
  [ -f "$f" ] || { echo "executer not found: $ROOT/$f" >&2; exit 2; }
done

registered() { grep -oE 'implementationsDictionary\["[^"]+"\]' "$1" | sed -E 's/.*\["([^"]+)"\]/\1/' | sort -u; }

if [ "${1:-}" = "--where" ]; then
  key="${2:?usage: --where <Key>}"
  registered "$PRE"  | grep -qx -- "$key" && echo "Pre : registered"  || echo "Pre : -"
  registered "$POST" | grep -qx -- "$key" && echo "Post: registered" || echo "Post: -"
  echo "References:"
  git grep -nE "[Vv]alueProviderFunction *[=:] *\"$key\"" -- "$FOUNDATIONS" | cut -c1-200 || echo "  (none)"
  exit 0
fi

if [ "${1:-}" = "--changed" ]; then
  mapfile -t scope < <( { git diff --name-only HEAD -- "$FOUNDATIONS"; git ls-files --others --exclude-standard -- "$FOUNDATIONS"; } | grep '\.cs$' | sort -u )
  [ "${#scope[@]}" -gt 0 ] || { echo "No changed .cs file under $FOUNDATIONS."; exit 0; }
elif [ "$#" -gt 0 ]; then
  scope=("$@")
else
  scope=("$FOUNDATIONS")
fi

all_registered="$( { registered "$PRE"; registered "$POST"; } | sort -u )"
live_refs() { grep -rnE --include='*.cs' "$REF_RE" -- "${scope[@]}" 2>/dev/null | grep -vE '^[^:]+:[0-9]+:[[:space:]]*//' || true; }
referenced="$(live_refs | grep -oE "$REF_RE" | sed -E 's/.*"([^"]+)"/\1/' | sort -u)"

total=0; missing=0
while IFS= read -r key; do
  [ -n "$key" ] || continue
  total=$((total + 1))
  if ! grep -qx -- "$key" <<<"$all_registered"; then
    missing=$((missing + 1))
    echo "MISSING: $key"
    live_refs | grep -F -- "\"$key\"" | head -3 | sed 's/^/    /' | cut -c1-200
  fi
done <<<"$referenced"

echo "$total key(s) referenced in scope, $missing not registered in the Pre or Post executer."
[ "$missing" -eq 0 ]
