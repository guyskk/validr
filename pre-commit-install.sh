#!/bin/bash
set -ex

python -m venv .pre-commit/
.pre-commit/bin/pip install 'pre-commit==1.21.0'
.pre-commit/bin/pre-commit install
