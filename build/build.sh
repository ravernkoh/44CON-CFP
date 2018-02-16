#!/bin/bash

set -eu
set -o pipefail

readonly BUILD_SRC="$(pwd)"
readonly PROJECT_ROOT=$(dirname "$BUILD_SRC")  # Parent of build directory
readonly LESS_SRC="$PROJECT_ROOT/bower_components/flat-ui/less/flat-ui.less"
readonly CSS_DEST="$PROJECT_ROOT/bower_components/flat-ui/dist/css/flat-ui-44con.min.css"
export DJANGO_SETTINGS_MODULE="gambit.settings.development"

prepare_db() {
  python manage.py makemigrations
  python manage.py migrate
}

prepare_assets() {
  bower install --save --production "$BUILD_SRC"/bower.json
  lessc --source-map-less-inline --source-map-map-inline --clean-css "$LESS_SRC" "$CSS_DEST"
  python manage.py collectstatic --noinput --clear --verbosity 0
  python manage.py compress --force --verbosity 0
}

run_tests() {
  coverage run --source='.' manage.py test gambit
}

main() {
  cp gambit/config.example.yaml gambit/config.yaml
  prepare_db
  prepare_assets
  run_tests
}

main
