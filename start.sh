#!/usr/bin/env bash
set -e

exec gunicorn bot:app --bind 0.0.0.0:3001
