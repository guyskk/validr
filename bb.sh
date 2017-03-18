#!/bin/bash
# build & benchmark
set -ex
rm -f validr/*.c
rm -f validr/*.so
pip install --upgrade --force-reinstall -e .
pytest -s
python benchmark/benchmark.py benchmark --validr
