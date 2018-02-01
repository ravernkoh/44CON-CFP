#!/bin/bash
# If you run this outside of the CFP project root, you can deal with the consequences

set -eu

readonly PROJECT_ROOT=$(pwd)
readonly SOURCE_MAP_DEST="$PROJECT_ROOT/bower_components/flat-ui/dist/css/flat-ui-44con-css.min.map"
readonly LESS_SRC="$PROJECT_ROOT/bower_components/flat-ui/less/flat-ui.less"
readonly CSS_DEST="$PROJECT_ROOT/bower_components/flat-ui/dist/css/flat-ui-44con.min.css"

main() {
  echo 'installing bower assets'
  bower install --save --production || { echo 'bower asset collection failed'; exit 1; }
  echo 'copying variables file'
  cp variables.less bower_components/flat-ui/less || { echo 'could not copy variables file to less directory'; exit 1; }
  echo 'generating css and source map'
  lessc --clean-css --source-map="$SOURCE_MAP_DEST" "$LESS_SRC" "$CSS_DEST" || { echo 'could not generate css or map'; exit 1; }
  echo 'collecting static files to static dir'
  python manage.py collectstatic --clear || { echo 'could not collect static files'; exit 1; }
}
