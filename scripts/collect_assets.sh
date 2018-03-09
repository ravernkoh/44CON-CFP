#!/bin/bash

set -eu
set -o pipefail

readonly PROJECT_ROOT="$(pwd)"

main() {
  python "$PROJECT_ROOT/manage.py" collectstatic --no-input --verbosity 0
  python "$PROJECT_ROOT/manage.py" compress --force --verbosity 0
}

main
