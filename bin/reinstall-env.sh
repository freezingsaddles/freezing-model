#!/usr/bin/env bash
# reinstall-env.sh
#
# Reinstall the pip virtualenv, useful when troubleshooting
# package dependencies.
#
# Usage:    ./reinstall-env.sh

# Use bash unofficial strict mode http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

rm -rf .venv/
python3 -mvenv .venv
# shellcheck disable=SC1091
source .venv/bin/activate

if [[ -f requirements.txt ]]; then pip install -r requirements.txt ; fi
if [[ -f requirements-test.txt ]]; then pip install -r requirements-test.txt ; fi
# This would be better if we had something like yq available in the environment
# See https://github.com/kislyuk/yq
# but this is good enough for now
if grep -s '\[dependencies\]' pyproject.toml \
    && grep -sA 1 '\[project.optional-dependencies\]' pyproject.toml \
    | grep -s '\[dev\]'; then
    pip install -e '.[dev]'
else
    pip install -e .
fi
