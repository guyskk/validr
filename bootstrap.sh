#!/bin/bash
set -ex

python -m venv .pre-commit/
.pre-commit/bin/pip install 'pre-commit==1.21.0'
.pre-commit/bin/pre-commit install

pip install -r requirements.txt
pip --version
pip freeze
python -c 'import Cython as c;print("Cython="+c.__version__)'
VALIDR_SETUP_MODE=dist pip install -e .
