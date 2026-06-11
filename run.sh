#!/bin/sh
# One-command pipeline: ./run.sh "Business Name, Town, Country" [locale]
# Anything fancier: .venv/bin/python -m socialite.cli --help
cd "$(dirname "$0")" || exit 1
exec .venv/bin/python -m socialite.cli run "$1" --locale "${2:-uk}"
