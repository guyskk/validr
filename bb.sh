#!/bin/bash
# build & benchmark
set -ex
git clean -Xdf
export VALIDR_DEBUG=1
pip install --upgrade --force-reinstall --verbose -e .
pytest --cov=validr --cov-report=term-missing -r w
python benchmark/benchmark.py benchmark --validr
python benchmark/benchmark.py profile
