#!/bin/bash
set -ex

pip install -U pip
pip install -U py  # work around pytest requirement
pip install -e .[dev,benchmark]

pre-commit install
