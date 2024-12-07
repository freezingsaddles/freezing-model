#!/usr/bin/env bash
# reinstall-env.sh
#
# Reinstall the pip virtualenv, useful when troubleshooting
# package dependencies.

#shellcheck disable=SC1091
rm -rf .venv/ \
    && python3 -mvenv .venv \
    && source .venv/bin/activate \
    && pip install -r requirements.txt \
    && pip install -r requirements-test.txt \
    && pip install -e .
