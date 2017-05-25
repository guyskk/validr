#!/bin/bash
# build test & benchmark
set -ex
find ./validr -name "*.pyc" -print -delete
find ./validr -name "*.so" -print -delete
export VALIDR_DEBUG=1
pip install --upgrade --force-reinstall --verbose -e .
pytest --cov=validr --cov-report=term-missing -r w
python benchmark/benchmark.py benchmark --validr
python benchmark/benchmark.py profile
