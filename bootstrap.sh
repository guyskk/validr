#!/bin/bash
set -ex

pip install 'pip>=22.3.1' 'wheel>=0.38.4'
pip install -r requirements.txt
pip list
VALIDR_SETUP_MODE=dist pip install --no-build-isolation -e .
