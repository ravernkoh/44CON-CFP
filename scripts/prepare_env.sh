#!/bin/bash

set -eu
set -o pipefail

SETTINGS="$2"
VIRTUALENV_ROOT = "$HOME\Envs"
VIRTUALENV_NAME = "gambit"
ACTIVATE_VENV = "$VIRTUALENV_ROOT\$VIRTUALENV_NAME\Scripts\activate.ps1"

main() {
  export DJANGO_SETTINGS_MODULE="gambit.settings.$SETTINGS"
  $ACTIVATE_VENV
}

main
