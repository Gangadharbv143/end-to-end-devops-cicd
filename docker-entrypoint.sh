#!/bin/sh
set -eu

export PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus-multiproc

mkdir -p "$PROMETHEUS_MULTIPROC_DIR"
rm -f "$PROMETHEUS_MULTIPROC_DIR"/*

exec gunicorn \
    --config gunicorn.conf.py \
    --bind 0.0.0.0:5000 \
    --workers 2 \
    app:app
