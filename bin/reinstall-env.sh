#!/usr/bin/env bash
# reinstall-env.sh
#
# Reinstall the pip virtualenv, useful when troubleshooting
# package dependencies.

deactivate
#shellcheck disable=SC1091
rm -rf .venv/ \
    && python3 -mvenv .venv \
    && source .venv/bin/activate \
    && pip install -e .
