#!/bin/bash
set -e
cd "$(dirname "$0")"
PYTHONPATH=src py -3.15 -m depvis "$@"
