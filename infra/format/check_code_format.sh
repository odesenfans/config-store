#!/usr/bin/env bash

python -m format_code --debug

git diff --exit-code
