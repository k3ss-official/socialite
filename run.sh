#!/bin/sh
# One-command pipeline: ./run.sh "Business Name, Town, Country" [locale]
# Anything fancier: python -m socialite.cli --help (inside the socialite conda env)
cd "$(dirname "$0")" || exit 1
if [ "${CONDA_DEFAULT_ENV:-}" = socialite ]; then
  exec python -m socialite.cli run "$1" --locale "${2:-uk}"
fi
if [ -x .venv/bin/python ]; then
  exec .venv/bin/python -m socialite.cli run "$1" --locale "${2:-uk}"
fi
echo "Activate the environment first: conda activate socialite" >&2
exit 1
