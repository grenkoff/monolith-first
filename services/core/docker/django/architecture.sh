#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
set -o xtrace

lint-imports
python -m scripts.modules
python -m scripts.relations
python -m scripts.keys
python -m scripts.transactions
python -m scripts.templates
python -m scripts.compose
