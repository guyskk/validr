#!/bin/bash
# build test & benchmark
set -ex
export VALIDR_DEBUG=1
export VALIDR_USE_CYTHON=1
pip install --verbose -e .
pytest --cov=validr --cov-report=term-missing -r w
python benchmark/benchmark.py benchmark --validr
python benchmark/benchmark.py profile
