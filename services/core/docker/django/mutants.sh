#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail

rm -rf mutants
trap 'rm -rf mutants' EXIT

survivors () {
  mutmut results \
    | sed -n 's/^ *\([^ ]*\): \(survived\|suspicious\)$/\1/p' \
    | while read -r name; do mutmut show "$name"; done
}

mutmut run --max-children "${MUTMUT_CHILDREN:-4}"
mutmut export-cicd-stats

python - <<'PY' || { survivors; exit 1; }
import json
import sys
from pathlib import Path

stats = json.loads(Path('mutants/mutmut-cicd-stats.json').read_text())
print(json.dumps(stats, indent=2))
tested = stats['killed'] + stats['survived'] + stats['timeout']
if not tested:
    print('no mutants were tested, mutmut did not run properly')
    sys.exit(1)
if stats['survived'] or stats['suspicious']:
    print('some mutants survived, their diffs follow')
    sys.exit(1)
print(f'all {tested} mutants were killed')
PY
