#!/bin/bash
set -ex

pip install -U pip
pip install -U py  # work around pytest requirement
pip install 'cython>=0.25.2'
VALIDR_SETUP_MODE=dist pip install -e .[dev,benchmark] -r requirements.txt

pre-commit install
