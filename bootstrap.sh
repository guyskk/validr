#!/bin/bash
set -ex

pip install -r requirements.txt
VALIDR_SETUP_MODE=dist pip install -e .

pre-commit install
