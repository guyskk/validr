#!/bin/bash
set -ex

pip install 'pip>=19.1.1'
pip install 'py>=1.8.0'  # work around pytest requirement
pip install 'cython>=3.0.6'
VALIDR_SETUP_MODE=dist pip install -e '.[dev,benchmark]' -r requirements.txt

pre-commit install
