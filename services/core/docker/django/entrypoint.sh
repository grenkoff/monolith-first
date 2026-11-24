#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

readonly cmd="$*"

# Here you can place any logic that you want to execute on `entrypoint`.

stale=$(find /code/locale -name '*.po' -exec sh -c '[ ! -e "${1%.po}.mo" ] || [ "$1" -nt "${1%.po}.mo" ]' _ {} \; -print)
if [ -n "$stale" ]; then
  python /code/manage.py compilemessages --ignore mutants --verbosity 0
fi

echo "Service is up: $cmd"

# Evaluating passed command (do not touch):
# shellcheck disable=SC2086
exec $cmd
