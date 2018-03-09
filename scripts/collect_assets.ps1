$PROJECT_ROOT = "$($pwd.path)"

function Main () {
  python "$PROJECT_ROOT/manage.py" collectstatic --no-input --verbosity 0
  python "$PROJECT_ROOT/manage.py" compress --force --verbosity 0
}

Main
