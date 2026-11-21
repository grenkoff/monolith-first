#!/usr/bin/env bash

set -o nounset
set -o pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

notice() {
  printf '{"systemMessage": "%s"}\n' "$1"
}

disabled=''
case "$(uname -s)" in
  MINGW* | MSYS* | CYGWIN*)
    if [[ "$root" == //wsl* ]]; then
      disabled='TDD guard is OFF: Claude Code runs on Windows, the project is inside WSL. Run Claude Code inside WSL to enable it. CI still checks coverage and mutation testing.'
    fi
    ;;
esac
if [[ -z "$disabled" ]] && ! command -v python3 >/dev/null 2>&1; then
  disabled='TDD guard is OFF: python3 is not on PATH.'
fi

if [[ "${1:-}" == '--status' ]]; then
  if [[ -n "$disabled" ]]; then
    notice "$disabled"
  fi
  exit 0
fi

if [[ -n "$disabled" ]]; then
  exit 0
fi

exec python3 "$root/scripts/tdd_hook.py"
