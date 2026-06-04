#!/bin/sh
set -eu

mkdir -p /app/data

if [ "${RUN_SEED_ON_STARTUP:-true}" = "true" ]; then
  python seed.py
fi

exec uvicorn main:app --host 0.0.0.0 --port 8000
