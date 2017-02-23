#!/bin/bash
# build & benchmark
set -ex
rm validr/*.c
rm validr/*.so
pip install --upgrade --force-reinstall -e .
pytest
python benchmark/benchmark.py benchmark --validr
