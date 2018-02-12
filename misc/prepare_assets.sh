#!/bin/bash
# If you run this outside of the CFP project root, you can deal with the consequences

set -eu
set -o pipefail

readonly PROJECT_ROOT=$(pwd)
readonly LESS_SRC="$PROJECT_ROOT/bower_components/flat-ui/less/flat-ui.less"
readonly CSS_DEST="$PROJECT_ROOT/bower_components/flat-ui/dist/css/flat-ui-44con.min.css"
readonly MISC_SRC="$PROJECT_ROOT/misc"

main() {
  echo '[+] Installing bower assets from bower.json'
  bower install --save --production "$MISC_SRC"/bower.json || { echo '[!] Failed to install bower assets'; exit 1; }
  echo '[>>] Copying less variables into flat-ui'
  cp "$MISC_SRC"/variables.less bower_components/flat-ui/less || { echo '[!] Could not copy less variables file'; exit 1; }
  echo '[+] Generating minifed CSS and source map for flat-ui'
  lessc --clean-css --source-map-less-inline --source-map-map-inline "$LESS_SRC" "$CSS_DEST" || { echo '[!] lessc could not generate CSS or source map]'; exit 1; }
  echo '[>>] Collecting bower assets to Django static directory'
  python manage.py collectstatic --clear || { echo '[!] Django could not collect static assets'; exit 1; }
  echo '[=)] Finished preparing style assets for project'
}

main
