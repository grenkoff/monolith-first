#!/usr/bin/env bash

set -o nounset
set -o pipefail

tools=(
  docker make rustup cargo-llvm-cov cargo-mutants cargo-deny cargo-machete
  protoc uv python3 buf gitleaks git-cliff biome
)
missing=0

report() {
  if [ "$2" = ok ]; then
    printf 'ok       %s\n' "$1"
  else
    printf 'missing  %s (%s)\n' "$1" "$2"
    missing=$((missing + 1))
  fi
}

for tool in "${tools[@]}"; do
  if command -v "$tool" >/dev/null 2>&1; then
    report "$tool" ok
  else
    report "$tool" 'not on PATH'
  fi
done

if docker compose version >/dev/null 2>&1; then
  report 'docker compose v2' ok
else
  report 'docker compose v2' 'docker compose version fails'
fi

if [ "$missing" -gt 0 ]; then
  printf '\n%s tool(s) missing, see "Developer environment" in AGENTS.md\n' "$missing"
  exit 1
fi
printf '\nall tools are installed\n'
