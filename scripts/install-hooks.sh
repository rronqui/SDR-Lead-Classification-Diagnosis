#!/bin/sh
# Instala os hooks git do projeto (commit-msg + pre-push).
# Uso: sh scripts/install-hooks.sh
set -e
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath .githooks
echo "hooks instalados: core.hooksPath=.githooks (commit-msg, pre-push)"
