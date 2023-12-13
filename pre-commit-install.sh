#!/bin/bash
set -ex

python -m venv .pre-commit/
.pre-commit/bin/pip install 'pre-commit==3.6.0'
.pre-commit/bin/pre-commit install
.pre-commit/bin/pre-commit install-hooks
