#!/bin/bash
# build & benchmark
set -ex
rm -f validr/*.c
rm -f validr/*.so
pip install --upgrade --force-reinstall -e .
pytest -s -rw
python benchmark/benchmark.py benchmark --validr
